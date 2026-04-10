"""Unit tests for transport-layer additions (Phase 4).

Covers:
- Permanent-vs-transient WebSocket error classification used by the
  reconnect loop.
- Configurable request timeout propagation into ``WebSocketTransport``.
- Notification-handler error callback hook.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import websockets

from moonraker_client._transport import WebSocketTransport, _is_permanent_ws_error


class TestPermanentWsErrorClassifier:
    """4xx handshakes are permanent; everything else is transient."""

    def test_invalid_uri_is_permanent(self) -> None:
        exc = websockets.exceptions.InvalidURI("not-a-uri", "bad scheme")
        assert _is_permanent_ws_error(exc) is True

    def test_connection_closed_is_transient(self) -> None:
        exc = websockets.exceptions.ConnectionClosed(None, None)
        assert _is_permanent_ws_error(exc) is False

    def test_os_error_is_transient(self) -> None:
        assert _is_permanent_ws_error(OSError("conn refused")) is False

    def test_401_invalid_status_is_permanent(self) -> None:
        invalid_status = getattr(websockets.exceptions, "InvalidStatus", None)
        if invalid_status is None:
            # Older websockets version - classifier still tolerates via getattr.
            return
        response = MagicMock()
        response.status_code = 401
        exc = invalid_status(response)
        assert _is_permanent_ws_error(exc) is True

    def test_502_invalid_status_is_transient(self) -> None:
        invalid_status = getattr(websockets.exceptions, "InvalidStatus", None)
        if invalid_status is None:
            return
        response = MagicMock()
        response.status_code = 502
        exc = invalid_status(response)
        assert _is_permanent_ws_error(exc) is False


class TestRequestTimeoutPropagation:
    """WebSocketTransport must use the constructor-supplied request timeout."""

    def test_default_timeout_is_30s(self) -> None:
        ws = WebSocketTransport("ws://example.invalid/websocket")
        assert ws._request_timeout == 30.0

    def test_custom_timeout_stored(self) -> None:
        ws = WebSocketTransport("ws://example.invalid/websocket", request_timeout=5.0)
        assert ws._request_timeout == 5.0


class TestHandlerErrorCallback:
    """Notification-handler exceptions must be dispatchable to an observer."""

    def test_register_and_dispatch(self) -> None:
        ws = WebSocketTransport("ws://example.invalid/websocket")
        seen: list[tuple[str, Exception]] = []

        def observer(method: str, exc: Exception) -> None:
            seen.append((method, exc))

        ws.add_handler_error_callback(observer)
        err = RuntimeError("boom")
        ws._notify_handler_error("notify_status_update", err)
        assert seen == [("notify_status_update", err)]

    def test_broken_observer_does_not_raise(self) -> None:
        """A broken handler-error observer must not kill the listener."""
        ws = WebSocketTransport("ws://example.invalid/websocket")

        def angry(method: str, exc: Exception) -> None:
            raise ValueError("callback is broken")

        ws.add_handler_error_callback(angry)
        # Must not raise:
        ws._notify_handler_error("notify_status_update", RuntimeError("boom"))

    def test_remove_handler_error_callback(self) -> None:
        ws = WebSocketTransport("ws://example.invalid/websocket")
        seen: list[str] = []

        def observer(method: str, exc: Exception) -> None:
            seen.append(method)

        ws.add_handler_error_callback(observer)
        ws.remove_handler_error_callback(observer)
        ws._notify_handler_error("notify_status_update", RuntimeError("boom"))
        assert seen == []
