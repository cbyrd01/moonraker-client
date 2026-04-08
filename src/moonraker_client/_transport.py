"""HTTP transport layer for the Moonraker client."""

from __future__ import annotations

from typing import Any

import httpx

from moonraker_client.auth import build_auth


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
