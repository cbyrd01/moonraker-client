"""JSON-RPC 2.0 protocol handling for Moonraker WebSocket communication.

Moonraker's WebSocket API uses JSON-RPC 2.0 for request/response and
server-initiated notifications.
"""

from __future__ import annotations

import json
import threading
from typing import Any


class JsonRpcError(Exception):
    """Raised when a JSON-RPC error response is received."""

    def __init__(self, code: int, message: str, data: Any = None) -> None:
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"JSON-RPC error {code}: {message}")


class JsonRpcRequest:
    """Represents a JSON-RPC 2.0 request."""

    def __init__(self, method: str, params: dict[str, Any] | None = None, id: int = 0) -> None:
        self.method = method
        self.params = params or {}
        self.id = id

    def to_json(self) -> str:
        """Serialize to JSON string."""
        msg: dict[str, Any] = {
            "jsonrpc": "2.0",
            "method": self.method,
            "id": self.id,
        }
        if self.params:
            msg["params"] = self.params
        return json.dumps(msg)


class JsonRpcIdGenerator:
    """Thread-safe auto-incrementing ID generator for JSON-RPC requests."""

    def __init__(self) -> None:
        self._counter = 0
        self._lock = threading.Lock()

    def next(self) -> int:
        with self._lock:
            self._counter += 1
            return self._counter

    def reset(self) -> None:
        with self._lock:
            self._counter = 0


def parse_jsonrpc_message(raw: str | bytes) -> dict[str, Any]:
    """Parse a raw JSON-RPC message.

    Returns a dict with the parsed message. The dict will have one of:
    - "result" key: successful response
    - "error" key: error response
    - "method" key without "id": notification

    Args:
        raw: Raw JSON string or bytes from WebSocket.

    Returns:
        Parsed JSON-RPC message dict.
    """
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    result: dict[str, Any] = json.loads(raw)
    return result


def is_notification(message: dict[str, Any]) -> bool:
    """Check if a JSON-RPC message is a notification (no id field)."""
    return "method" in message and "id" not in message


def is_response(message: dict[str, Any]) -> bool:
    """Check if a JSON-RPC message is a response (has id field)."""
    return "id" in message and ("result" in message or "error" in message)


def extract_result(message: dict[str, Any]) -> Any:
    """Extract the result from a JSON-RPC response, or raise on error.

    Args:
        message: Parsed JSON-RPC response message.

    Returns:
        The result value.

    Raises:
        JsonRpcError: If the response contains an error.
    """
    if "error" in message:
        error = message["error"]
        raise JsonRpcError(
            code=error.get("code", -1),
            message=error.get("message", "Unknown error"),
            data=error.get("data"),
        )
    return message.get("result")


def extract_notification(message: dict[str, Any]) -> tuple[str, list[Any]]:
    """Extract method name and params from a JSON-RPC notification.

    Args:
        message: Parsed JSON-RPC notification message.

    Returns:
        Tuple of (method_name, params_list).
    """
    method = message["method"]
    params = message.get("params", [])
    if not isinstance(params, list):
        params = [params]
    return method, params
