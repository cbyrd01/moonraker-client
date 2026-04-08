"""Unit tests for JSON-RPC protocol handling."""

from __future__ import annotations

import json

import pytest

from moonraker_client._jsonrpc import (
    JsonRpcError,
    JsonRpcIdGenerator,
    JsonRpcRequest,
    extract_notification,
    extract_result,
    is_notification,
    is_response,
    parse_jsonrpc_message,
)


class TestJsonRpcRequest:
    def test_basic_request(self) -> None:
        req = JsonRpcRequest(method="printer.info", id=1)
        data = json.loads(req.to_json())
        assert data["jsonrpc"] == "2.0"
        assert data["method"] == "printer.info"
        assert data["id"] == 1
        assert "params" not in data

    def test_request_with_params(self) -> None:
        req = JsonRpcRequest(
            method="printer.objects.query",
            params={"objects": {"toolhead": None}},
            id=42,
        )
        data = json.loads(req.to_json())
        assert data["params"] == {"objects": {"toolhead": None}}
        assert data["id"] == 42

    def test_request_empty_params_omitted(self) -> None:
        req = JsonRpcRequest(method="printer.info", params={}, id=1)
        data = json.loads(req.to_json())
        assert "params" not in data


class TestJsonRpcIdGenerator:
    def test_auto_increment(self) -> None:
        gen = JsonRpcIdGenerator()
        assert gen.next() == 1
        assert gen.next() == 2
        assert gen.next() == 3

    def test_reset(self) -> None:
        gen = JsonRpcIdGenerator()
        gen.next()
        gen.next()
        gen.reset()
        assert gen.next() == 1


class TestParseMessage:
    def test_parse_string(self) -> None:
        msg = '{"jsonrpc": "2.0", "result": "ok", "id": 1}'
        data = parse_jsonrpc_message(msg)
        assert data["result"] == "ok"

    def test_parse_bytes(self) -> None:
        msg = b'{"jsonrpc": "2.0", "result": "ok", "id": 1}'
        data = parse_jsonrpc_message(msg)
        assert data["result"] == "ok"


class TestIsNotification:
    def test_notification(self) -> None:
        msg = {"jsonrpc": "2.0", "method": "notify_klippy_ready", "params": []}
        assert is_notification(msg) is True

    def test_response_is_not_notification(self) -> None:
        msg = {"jsonrpc": "2.0", "result": "ok", "id": 1}
        assert is_notification(msg) is False

    def test_request_with_id_is_not_notification(self) -> None:
        msg = {"jsonrpc": "2.0", "method": "printer.info", "id": 1}
        assert is_notification(msg) is False


class TestIsResponse:
    def test_success_response(self) -> None:
        msg = {"jsonrpc": "2.0", "result": {"state": "ready"}, "id": 1}
        assert is_response(msg) is True

    def test_error_response(self) -> None:
        msg = {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid"}, "id": 1}
        assert is_response(msg) is True

    def test_notification_is_not_response(self) -> None:
        msg = {"jsonrpc": "2.0", "method": "notify_klippy_ready"}
        assert is_response(msg) is False


class TestExtractResult:
    def test_success(self) -> None:
        msg = {"jsonrpc": "2.0", "result": {"state": "ready"}, "id": 1}
        result = extract_result(msg)
        assert result == {"state": "ready"}

    def test_string_result(self) -> None:
        msg = {"jsonrpc": "2.0", "result": "ok", "id": 1}
        assert extract_result(msg) == "ok"

    def test_error_raises(self) -> None:
        msg = {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request"},
            "id": 1,
        }
        with pytest.raises(JsonRpcError) as exc_info:
            extract_result(msg)
        assert exc_info.value.code == -32600
        assert "Invalid Request" in str(exc_info.value)

    def test_error_with_data(self) -> None:
        msg = {
            "jsonrpc": "2.0",
            "error": {"code": -1, "message": "fail", "data": {"detail": "extra"}},
            "id": 1,
        }
        with pytest.raises(JsonRpcError) as exc_info:
            extract_result(msg)
        assert exc_info.value.data == {"detail": "extra"}


class TestExtractNotification:
    def test_basic(self) -> None:
        msg = {"jsonrpc": "2.0", "method": "notify_klippy_ready", "params": []}
        method, params = extract_notification(msg)
        assert method == "notify_klippy_ready"
        assert params == []

    def test_with_params(self) -> None:
        msg = {
            "jsonrpc": "2.0",
            "method": "notify_status_update",
            "params": [{"toolhead": {"position": [0, 0, 0, 0]}}],
        }
        method, params = extract_notification(msg)
        assert method == "notify_status_update"
        assert len(params) == 1
        assert "toolhead" in params[0]

    def test_dict_params_wrapped_in_list(self) -> None:
        msg = {"jsonrpc": "2.0", "method": "notify_test", "params": {"key": "value"}}
        _method, params = extract_notification(msg)
        assert params == [{"key": "value"}]

    def test_no_params(self) -> None:
        msg = {"jsonrpc": "2.0", "method": "notify_klippy_ready"}
        _method, params = extract_notification(msg)
        assert params == []
