"""HTTP and WebSocket transport layer for the Moonraker client."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Callable
from typing import Any

import httpx
import websockets
from websockets.asyncio.client import ClientConnection

from moonraker_client._jsonrpc import (
    JsonRpcIdGenerator,
    JsonRpcRequest,
    extract_notification,
    extract_result,
    is_notification,
    is_response,
    parse_jsonrpc_message,
)
from moonraker_client.auth import build_auth

logger = logging.getLogger(__name__)


class HttpTransport:
    """Manages the httpx client lifecycle for sync HTTP requests."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._auth = build_auth(api_key=api_key, token=token)
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                base_url=self.base_url,
                auth=self._auth,
                timeout=self.timeout,
            )
        return self._client

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
    ) -> httpx.Response:
        """Send an HTTP request.

        Args:
            method: HTTP method (GET, POST, DELETE, etc.).
            path: URL path relative to base_url.
            params: Query parameters.
            json: JSON body payload.
            data: Form data payload.
            files: File upload payload.

        Returns:
            The httpx.Response object.
        """
        return self.client.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
        )

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None and not self._client.is_closed:
            self._client.close()
            self._client = None


class AsyncHttpTransport:
    """Manages the httpx async client lifecycle for async HTTP requests."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._auth = build_auth(api_key=api_key, token=token)
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                auth=self._auth,
                timeout=self.timeout,
            )
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
    ) -> httpx.Response:
        """Send an async HTTP request."""
        return await self.client.request(
            method,
            path,
            params=params,
            json=json,
            data=data,
            files=files,
        )

    async def close(self) -> None:
        """Close the underlying async HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


class WebSocketTransport:
    """Manages a WebSocket connection to Moonraker for JSON-RPC communication.

    Handles:
    - Connection lifecycle (connect, disconnect, reconnect with backoff)
    - JSON-RPC request/response matching by ID
    - Notification dispatch to registered handlers
    """

    def __init__(
        self,
        ws_url: str,
        api_key: str | None = None,
        token: str | None = None,
        reconnect: bool = True,
        max_reconnect_delay: float = 60.0,
    ) -> None:
        self.ws_url = ws_url
        self._api_key = api_key
        self._token = token
        self._reconnect = reconnect
        self._max_reconnect_delay = max_reconnect_delay
        self._id_gen = JsonRpcIdGenerator()
        self._connection: ClientConnection | None = None
        self._pending: dict[int, asyncio.Future[Any]] = {}
        self._notification_handlers: dict[str, list[Callable[..., Any]]] = {}
        self._listener_task: asyncio.Task[None] | None = None
        self._connected = asyncio.Event()
        self._closing = False

    @property
    def is_connected(self) -> bool:
        """Whether the WebSocket is currently connected."""
        return self._connection is not None and self._connected.is_set()

    def on_notification(self, method: str, handler: Callable[..., Any]) -> None:
        """Register a handler for a JSON-RPC notification type.

        Args:
            method: The notification method name (e.g. "notify_status_update").
            handler: Callback function. Will receive the notification params.
        """
        if method not in self._notification_handlers:
            self._notification_handlers[method] = []
        self._notification_handlers[method].append(handler)

    def remove_notification_handler(self, method: str, handler: Callable[..., Any]) -> None:
        """Remove a previously registered notification handler."""
        if method in self._notification_handlers:
            self._notification_handlers[method] = [
                h for h in self._notification_handlers[method] if h is not handler
            ]

    async def connect(self) -> None:
        """Establish the WebSocket connection and start the message listener."""
        self._closing = False
        extra_headers: dict[str, str] = {}
        if self._api_key:
            extra_headers["X-Api-Key"] = self._api_key
        if self._token:
            extra_headers["Authorization"] = f"Bearer {self._token}"

        self._connection = await websockets.connect(
            self.ws_url,
            additional_headers=extra_headers if extra_headers else None,
        )
        self._connected.set()
        self._listener_task = asyncio.create_task(self._listen())
        logger.info("WebSocket connected to %s", self.ws_url)

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        self._closing = True
        self._connected.clear()
        if self._listener_task is not None:
            self._listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener_task
            self._listener_task = None
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
        # Cancel any pending requests
        for future in self._pending.values():
            if not future.done():
                future.cancel()
        self._pending.clear()
        self._id_gen.reset()
        logger.info("WebSocket disconnected")

    async def send_jsonrpc(self, method: str, params: dict[str, Any] | None = None) -> Any:
        """Send a JSON-RPC request and wait for the response.

        Args:
            method: The JSON-RPC method name.
            params: Optional parameters dict.

        Returns:
            The result from the JSON-RPC response.

        Raises:
            ConnectionError: If not connected.
            JsonRpcError: If the server returns an error.
        """
        if not self.is_connected or self._connection is None:
            raise ConnectionError("WebSocket is not connected")

        request_id = self._id_gen.next()
        request = JsonRpcRequest(method=method, params=params, id=request_id)

        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        self._pending[request_id] = future

        try:
            await self._connection.send(request.to_json())
            return await asyncio.wait_for(future, timeout=30.0)
        except asyncio.TimeoutError as exc:
            self._pending.pop(request_id, None)
            raise TimeoutError(f"JSON-RPC request {method} (id={request_id}) timed out") from exc
        except Exception:
            self._pending.pop(request_id, None)
            raise

    async def _listen(self) -> None:
        """Background task that reads messages from the WebSocket."""
        reconnect_delay = 1.0
        while not self._closing:
            try:
                if self._connection is None:
                    break
                async for raw_message in self._connection:
                    reconnect_delay = 1.0  # Reset on successful message
                    try:
                        message = parse_jsonrpc_message(raw_message)
                    except Exception:
                        logger.warning("Failed to parse WebSocket message: %s", raw_message[:200])
                        continue

                    if is_response(message):
                        request_id = message["id"]
                        future = self._pending.pop(request_id, None)
                        if future is not None and not future.done():
                            try:
                                result = extract_result(message)
                                future.set_result(result)
                            except Exception as exc:
                                future.set_exception(exc)
                    elif is_notification(message):
                        method, params = extract_notification(message)
                        handlers = self._notification_handlers.get(method, [])
                        for handler in handlers:
                            try:
                                result = handler(params)
                                if asyncio.iscoroutine(result):
                                    await result
                            except Exception:
                                logger.exception("Error in notification handler for %s", method)
            except websockets.ConnectionClosed:
                self._connected.clear()
                if self._closing or not self._reconnect:
                    break
                logger.info("WebSocket disconnected, reconnecting in %.1fs...", reconnect_delay)
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, self._max_reconnect_delay)
                try:
                    await self.connect()
                except Exception:
                    logger.warning("Reconnection failed, retrying...")
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Unexpected error in WebSocket listener")
                break
