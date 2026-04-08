"""Unit tests for server API endpoints."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import AsyncMoonrakerClient, MoonrakerClient


class TestServerMixin:
    def test_server_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "klippy_connected": True,
                    "klippy_state": "ready",
                    "components": ["server", "file_manager"],
                    "moonraker_version": "v0.9.0",
                }
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_info()
        assert result["klippy_state"] == "ready"
        assert result["klippy_connected"] is True

    def test_server_config(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"config": {}, "orig": {}}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_config()
        assert "config" in result

    def test_server_temperature_store(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"extruder": {"temperatures": [200.0]}}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_temperaturestore(include_monitors=True)
        assert "extruder" in result
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["include_monitors"].lower() == "true"

    def test_server_gcode_store(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"gcode_store": []}})
        with MoonrakerClient("http://localhost:7125") as client:
            client.server_gcodestore(count=10)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["count"] == "10"

    def test_server_restart(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_restart()
        assert result == "ok"


class TestAsyncServerMixin:
    @pytest.mark.asyncio
    async def test_server_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"klippy_state": "ready"}})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.server_info()
        assert result["klippy_state"] == "ready"
