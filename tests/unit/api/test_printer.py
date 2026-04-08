"""Unit tests for printer API endpoints."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import AsyncMoonrakerClient, MoonrakerClient

PRINTER_INFO_RESPONSE = {
    "result": {
        "state": "ready",
        "state_message": "Printer is ready",
        "hostname": "pi-debugger",
        "klipper_path": "/home/pi/klipper",
        "python_path": "/home/pi/klipper/venv/bin/python",
        "process_id": 275124,
        "user_id": 1000,
        "group_id": 1000,
        "log_file": "/home/pi/printer_data/logs/klippy.log",
        "config_file": "/home/pi/printer_data/config/printer.cfg",
        "software_version": "v0.12.0-85-gd785b396",
        "cpu_info": "4 core ?",
    }
}


class TestPrinterMixin:
    """Tests for synchronous printer API methods."""

    def test_printer_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json=PRINTER_INFO_RESPONSE)
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.printer_info()
        assert result["state"] == "ready"
        assert result["hostname"] == "pi-debugger"
        assert result["software_version"] == "v0.12.0-85-gd785b396"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "GET"
        assert request.url.path == "/printer/info"

    def test_emergency_stop(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.emergency_stop()
        assert result == "ok"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.url.path == "/printer/emergency_stop"

    def test_printer_restart(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.printer_restart()
        assert result == "ok"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.url.path == "/printer/restart"

    def test_firmware_restart(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.firmware_restart()
        assert result == "ok"

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.url.path == "/printer/firmware_restart"


class TestAsyncPrinterMixin:
    """Tests for asynchronous printer API methods."""

    @pytest.mark.asyncio
    async def test_printer_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json=PRINTER_INFO_RESPONSE)
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.printer_info()
        assert result["state"] == "ready"

    @pytest.mark.asyncio
    async def test_emergency_stop(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.emergency_stop()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_printer_restart(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.printer_restart()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_firmware_restart(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.firmware_restart()
        assert result == "ok"
