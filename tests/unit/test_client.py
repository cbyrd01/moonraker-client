"""Unit tests for MoonrakerClient and AsyncMoonrakerClient."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import (
    AsyncMoonrakerClient,
    MoonrakerAPIError,
    MoonrakerAuthError,
    MoonrakerClient,
)


class TestMoonrakerClient:
    """Tests for the synchronous MoonrakerClient."""

    def test_init_default(self) -> None:
        client = MoonrakerClient("http://localhost:7125")
        assert client._transport.base_url == "http://localhost:7125"
        assert client._transport.timeout == 30.0
        client.close()

    def test_init_strips_trailing_slash(self) -> None:
        client = MoonrakerClient("http://localhost:7125/")
        assert client._transport.base_url == "http://localhost:7125"
        client.close()

    def test_init_custom_timeout(self) -> None:
        client = MoonrakerClient("http://localhost:7125", timeout=60.0)
        assert client._transport.timeout == 60.0
        client.close()

    def test_context_manager(self) -> None:
        with MoonrakerClient("http://localhost:7125") as client:
            assert client._transport.base_url == "http://localhost:7125"
        # Client should be closed after exiting context
        assert client._transport._client is None

    def test_request_unwraps_result(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"state": "ready"}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client._request("GET", "/printer/info")
        assert result == {"state": "ready"}

    def test_request_returns_ok_string(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client._request("POST", "/printer/restart")
        assert result == "ok"

    def test_request_raises_api_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"code": 400, "message": "Bad request"}},
        )
        with MoonrakerClient("http://localhost:7125") as client:
            with pytest.raises(MoonrakerAPIError) as exc_info:
                client._request("POST", "/printer/gcode/script")
            assert exc_info.value.status_code == 400
            assert exc_info.value.message == "Bad request"

    def test_request_raises_auth_error_on_401(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            status_code=401,
            json={"error": {"code": 401, "message": "Unauthorized"}},
        )
        with MoonrakerClient("http://localhost:7125") as client:
            with pytest.raises(MoonrakerAuthError) as exc_info:
                client._request("GET", "/printer/info")
            assert exc_info.value.status_code == 401

    def test_request_raises_auth_error_on_403(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            status_code=403,
            json={"error": {"code": 403, "message": "Forbidden"}},
        )
        with MoonrakerClient("http://localhost:7125") as client, pytest.raises(MoonrakerAuthError):
            client._request("GET", "/printer/info")

    def test_request_handles_error_without_json_body(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(status_code=500, text="Internal Server Error")
        with MoonrakerClient("http://localhost:7125") as client:
            with pytest.raises(MoonrakerAPIError) as exc_info:
                client._request("GET", "/printer/info")
            assert exc_info.value.status_code == 500
            assert "Internal Server Error" in exc_info.value.message

    def test_request_passes_query_params(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            client._request("GET", "/server/files/list", params={"root": "gcodes"})
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["root"] == "gcodes"

    def test_request_passes_json_body(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            client._request("POST", "/printer/gcode/script", json={"script": "G28"})
        request = httpx_mock.get_request()
        assert request is not None
        import json

        assert json.loads(request.content) == {"script": "G28"}


class TestAsyncMoonrakerClient:
    """Tests for the async client."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            assert client._transport.base_url == "http://localhost:7125"

    @pytest.mark.asyncio
    async def test_async_request_unwraps_result(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"state": "ready"}})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client._request("GET", "/printer/info")
        assert result == {"state": "ready"}

    @pytest.mark.asyncio
    async def test_async_request_raises_api_error(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"code": 400, "message": "Bad request"}},
        )
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            with pytest.raises(MoonrakerAPIError):
                await client._request("POST", "/test")
