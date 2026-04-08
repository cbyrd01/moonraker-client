"""Unit tests for machine API endpoints."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import MoonrakerClient, AsyncMoonrakerClient


class TestMachineMixin:
    def test_system_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"system_info": {
            "cpu_info": {"cpu_count": 4},
        }}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.machine_systeminfo()
        assert "system_info" in result

    def test_proc_stats(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {
            "moonraker_stats": [],
            "cpu_temp": 45.0,
            "system_uptime": 86400.0,
        }})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.machine_procstats()
        assert result["cpu_temp"] == 45.0
        assert result["system_uptime"] == 86400.0

    def test_services_restart(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.machine_services_restart(service="klipper")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["service"] == "klipper"

    def test_peripherals_usb(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"usb_devices": []}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.machine_peripherals_usb()
        assert "usb_devices" in result

    def test_peripherals_serial(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"serial_devices": []}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.machine_peripherals_serial()
        assert "serial_devices" in result


class TestAsyncMachineMixin:
    @pytest.mark.asyncio
    async def test_system_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"system_info": {}}})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.machine_systeminfo()
        assert "system_info" in result
