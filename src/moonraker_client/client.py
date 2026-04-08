"""Main client classes for the Moonraker API.

Provides both sync and async clients that compose API endpoint mixins
into a single flat namespace.
"""

from __future__ import annotations

from typing import Any

import httpx

from moonraker_client._base import handle_request_error, unwrap_response
from moonraker_client._transport import AsyncHttpTransport, HttpTransport
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
        self._transport = AsyncHttpTransport(
            base_url=base_url,
            api_key=api_key,
            token=token,
            timeout=timeout,
        )

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

    async def close(self) -> None:
        """Close the underlying async HTTP connection."""
        await self._transport.close()

    async def __aenter__(self) -> AsyncMoonrakerClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
