"""Common data models shared across API responses."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any


@dataclass
class ErrorResponse:
    """Moonraker API error response body."""

    code: int
    message: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ErrorResponse:
        return cls(code=data.get("code", 0), message=data.get("message", "Unknown error"))


def from_dict(cls: type, data: dict[str, Any]) -> Any:
    """Construct a dataclass from a dict, ignoring extra keys.

    Args:
        cls: The dataclass type to construct.
        data: Raw dict from the API response.

    Returns:
        An instance of cls populated with matching keys from data.
    """
    field_names = {f.name for f in dataclasses.fields(cls)}
    filtered = {k: v for k, v in data.items() if k in field_names}
    return cls(**filtered)
