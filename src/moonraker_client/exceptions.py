"""Exception hierarchy for the Moonraker client library."""

from __future__ import annotations


class MoonrakerError(Exception):
    """Base exception for all Moonraker client errors."""


class MoonrakerConnectionError(MoonrakerError):
    """Raised when the client cannot connect to the Moonraker server."""


class MoonrakerAPIError(MoonrakerError):
    """Raised when the Moonraker API returns an error response.

    Attributes:
        status_code: HTTP status code from the response.
        error_code: Moonraker-specific error code from the JSON error body, if present.
        message: Human-readable error message.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: int | None = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        parts = []
        if self.status_code is not None:
            parts.append(f"HTTP {self.status_code}")
        if self.error_code is not None:
            parts.append(f"code={self.error_code}")
        parts.append(self.message)
        return " - ".join(parts)


class MoonrakerAuthError(MoonrakerAPIError):
    """Raised when authentication fails (401/403)."""


class MoonrakerTimeoutError(MoonrakerError):
    """Raised when a request times out."""
