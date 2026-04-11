"""Moonraker API client library for Python.

A typed, ergonomic client for the Moonraker API that provides HTTP and
WebSocket interfaces for controlling 3D printers running Klipper firmware.
"""

from moonraker_client._jsonrpc import JsonRpcError
from moonraker_client.client import (
    AsyncMoonrakerClient,
    MoonrakerClient,
    NotificationHandler,
    ProgressCallback,
)
from moonraker_client.exceptions import (
    MoonrakerAPIError,
    MoonrakerAuthError,
    MoonrakerConnectionError,
    MoonrakerError,
    MoonrakerTimeoutError,
)

__version__ = "0.1.0"

from moonraker_client import helpers

__all__ = [
    "AsyncMoonrakerClient",
    "JsonRpcError",
    "MoonrakerAPIError",
    "MoonrakerAuthError",
    "MoonrakerClient",
    "MoonrakerConnectionError",
    "MoonrakerError",
    "MoonrakerTimeoutError",
    "NotificationHandler",
    "ProgressCallback",
    "helpers",
]
