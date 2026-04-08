"""Shared request logic and response unwrapping for Moonraker client."""

from __future__ import annotations

from typing import Any

import httpx

from moonraker_client.exceptions import (
    MoonrakerAPIError,
    MoonrakerAuthError,
    MoonrakerConnectionError,
    MoonrakerTimeoutError,
)


def unwrap_response(response: httpx.Response) -> Any:
    """Extract the result from a Moonraker API response.

    Moonraker wraps successful responses in {"result": ...} and errors in
    {"error": {"code": N, "message": "..."}}.

    Args:
        response: The httpx response to process.

    Returns:
        The unwrapped result data.

    Raises:
        MoonrakerAuthError: On 401 or 403 responses.
        MoonrakerAPIError: On other error responses.
    """
    if response.status_code in (401, 403):
        try:
            body = response.json()
            error = body.get("error", {})
            msg = error.get("message", response.text)
            code = error.get("code")
        except Exception:
            msg = response.text
            code = None
        raise MoonrakerAuthError(
            message=msg,
            status_code=response.status_code,
            error_code=code,
        )

    if response.status_code >= 400:
        try:
            body = response.json()
            error = body.get("error", {})
            msg = error.get("message", response.text)
            code = error.get("code")
        except Exception:
            msg = response.text
            code = None
        raise MoonrakerAPIError(
            message=msg,
            status_code=response.status_code,
            error_code=code,
        )

    if response.status_code == 204:
        return None

    body = response.json()

    # Moonraker wraps results in {"result": ...}
    if isinstance(body, dict) and "result" in body:
        return body["result"]

    return body


def handle_request_error(exc: Exception) -> None:
    """Convert httpx exceptions to moonraker_client exceptions.

    Args:
        exc: The httpx exception to convert.

    Raises:
        MoonrakerConnectionError: On connection failures.
        MoonrakerTimeoutError: On timeouts.
        MoonrakerError: On other transport errors.
    """
    if isinstance(exc, httpx.ConnectError):
        raise MoonrakerConnectionError(f"Failed to connect: {exc}") from exc
    if isinstance(exc, httpx.TimeoutException):
        raise MoonrakerTimeoutError(f"Request timed out: {exc}") from exc
    raise MoonrakerConnectionError(f"Request failed: {exc}") from exc
