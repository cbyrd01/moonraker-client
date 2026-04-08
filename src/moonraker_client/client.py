"""Main client classes for the Moonraker API.

Provides both sync and async clients that compose API endpoint mixins
into a single flat namespace.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import httpx

from moonraker_client._base import handle_request_error, unwrap_response
from moonraker_client._transport import AsyncHttpTransport, HttpTransport, WebSocketTransport
from moonraker_client.api.announcements import AsyncAnnouncementsMixin, AnnouncementsMixin
from moonraker_client.api.auth import AsyncAuthMixin, AuthMixin
from moonraker_client.api.database import AsyncDatabaseMixin, DatabaseMixin
from moonraker_client.api.devices import AsyncDevicesMixin, DevicesMixin
from moonraker_client.api.files import AsyncFilesMixin, FilesMixin
from moonraker_client.api.history import AsyncHistoryMixin, HistoryMixin
from moonraker_client.api.jobs import AsyncJobsMixin, JobsMixin
from moonraker_client.api.machine import AsyncMachineMixin, MachineMixin
from moonraker_client.api.printer import AsyncPrinterMixin, PrinterMixin
from moonraker_client.api.server import AsyncServerMixin, ServerMixin
from moonraker_client.api.updates import AsyncUpdatesMixin, UpdatesMixin
from moonraker_client.api.webcams import AsyncWebcamsMixin, WebcamsMixin


class MoonrakerClient(
    PrinterMixin,
    ServerMixin,
    FilesMixin,
    HistoryMixin,
    JobsMixin,
    MachineMixin,
    AuthMixin,
    DatabaseMixin,
    UpdatesMixin,
    DevicesMixin,
    WebcamsMixin,
    AnnouncementsMixin,
):
    """Synchronous client for the Moonraker API.

    Usage::

        with MoonrakerClient("http://printer.local:7125") as client:
            info = client.printer_info()
            print(info["state"])

    Args:
        base_url: Base URL of the Moonraker server (e.g. "http://localhost:7125").
        api_key: API key for X-Api-Key header authentication.
        token: JWT token for Bearer authentication.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._transport = HttpTransport(
            base_url=base_url,
            api_key=api_key,
            token=token,
            timeout=timeout,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
    ) -> Any:
        """Send an HTTP request and return the unwrapped result."""
        try:
            response = self._transport.request(
                method, path, params=params, json=json, data=data, files=files
            )
        except httpx.HTTPError as exc:
            handle_request_error(exc)
        return unwrap_response(response)

    def close(self) -> None:
        """Close the underlying HTTP connection."""
        self._transport.close()

    def __enter__(self) -> MoonrakerClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncMoonrakerClient(
    AsyncPrinterMixin,
    AsyncServerMixin,
    AsyncFilesMixin,
    AsyncHistoryMixin,
    AsyncJobsMixin,
    AsyncMachineMixin,
    AsyncAuthMixin,
    AsyncDatabaseMixin,
    AsyncUpdatesMixin,
    AsyncDevicesMixin,
    AsyncWebcamsMixin,
    AsyncAnnouncementsMixin,
):
    """Asynchronous client for the Moonraker API.

    Usage::

        async with AsyncMoonrakerClient("http://printer.local:7125") as client:
            info = await client.printer_info()
            print(info["state"])

    Args:
        base_url: Base URL of the Moonraker server.
        api_key: API key for X-Api-Key header authentication.
        token: JWT token for Bearer authentication.
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        token: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._token = token
        self._transport = AsyncHttpTransport(
            base_url=base_url,
            api_key=api_key,
            token=token,
            timeout=timeout,
        )
        self._ws: WebSocketTransport | None = None

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: dict[str, Any] | None = None,
        files: Any | None = None,
    ) -> Any:
        """Send an async HTTP request and return the unwrapped result."""
        try:
            response = await self._transport.request(
                method, path, params=params, json=json, data=data, files=files
            )
        except httpx.HTTPError as exc:
            handle_request_error(exc)
        return unwrap_response(response)

    # -- WebSocket methods --

    def _make_ws_url(self) -> str:
        """Convert the HTTP base URL to a WebSocket URL."""
        return re.sub(r"^http", "ws", self._base_url) + "/websocket"

    async def connect_websocket(self, reconnect: bool = True) -> None:
        """Establish a WebSocket connection to the Moonraker server.

        Args:
            reconnect: If True, automatically reconnect on disconnection.
        """
        if self._ws is not None and self._ws.is_connected:
            return
        self._ws = WebSocketTransport(
            ws_url=self._make_ws_url(),
            api_key=self._api_key,
            token=self._token,
            reconnect=reconnect,
        )
        await self._ws.connect()

    async def disconnect_websocket(self) -> None:
        """Close the WebSocket connection."""
        if self._ws is not None:
            await self._ws.disconnect()
            self._ws = None

    @property
    def websocket_connected(self) -> bool:
        """Whether the WebSocket is currently connected."""
        return self._ws is not None and self._ws.is_connected

    async def send_jsonrpc(
        self, method: str, params: dict[str, Any] | None = None
    ) -> Any:
        """Send a JSON-RPC request over the WebSocket.

        Args:
            method: JSON-RPC method name (e.g. "printer.info").
            params: Optional parameters.

        Returns:
            The result from the JSON-RPC response.
        """
        if self._ws is None:
            raise ConnectionError("WebSocket is not connected. Call connect_websocket() first.")
        return await self._ws.send_jsonrpc(method, params)

    async def identify(
        self,
        client_name: str,
        version: str,
        client_type: str = "web",
        url: str = "",
    ) -> dict[str, Any]:
        """Identify this client to Moonraker over WebSocket.

        Should be called after connect_websocket() to register this connection.

        Args:
            client_name: Name of the application (e.g. "my-cli-tool").
            version: Version string.
            client_type: Client type ("web", "mobile", "desktop", "agent").
            url: URL to the client application.

        Returns:
            Connection info from Moonraker.
        """
        return await self.send_jsonrpc("server.connection.identify", {
            "client_name": client_name,
            "version": version,
            "type": client_type,
            "url": url,
        })

    async def subscribe_objects(
        self, objects: dict[str, list[str] | None]
    ) -> dict[str, Any]:
        """Subscribe to printer object status updates over WebSocket.

        Args:
            objects: Dict mapping object names to attribute lists (or None for all).
                E.g. {"toolhead": ["position"], "extruder": None}

        Returns:
            Initial status snapshot for the subscribed objects.
        """
        return await self.send_jsonrpc("printer.objects.subscribe", {
            "objects": objects,
        })

    def on(self, event: str, handler: Callable[..., Any]) -> None:
        """Register a handler for WebSocket notification events.

        Args:
            event: Notification method name (e.g. "notify_status_update").
            handler: Callback function receiving the notification params.
        """
        if self._ws is None:
            raise ConnectionError("WebSocket is not connected. Call connect_websocket() first.")
        self._ws.on_notification(event, handler)

    def off(self, event: str, handler: Callable[..., Any]) -> None:
        """Remove a notification handler.

        Args:
            event: Notification method name.
            handler: The handler to remove.
        """
        if self._ws is not None:
            self._ws.remove_notification_handler(event, handler)

    async def close(self) -> None:
        """Close both HTTP and WebSocket connections."""
        await self.disconnect_websocket()
        await self._transport.close()

    async def __aenter__(self) -> AsyncMoonrakerClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
