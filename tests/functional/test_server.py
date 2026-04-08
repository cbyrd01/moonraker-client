"""Functional tests for server endpoints against a live Moonraker server."""

from __future__ import annotations

import pytest

from moonraker_client import MoonrakerClient

pytestmark = pytest.mark.functional


class TestServerInfo:
    def test_returns_klippy_state(self, client: MoonrakerClient) -> None:
        info = client.server_info()
        assert "klippy_state" in info
        assert info["klippy_state"] in ("ready", "startup", "shutdown", "error")

    def test_returns_moonraker_version(self, client: MoonrakerClient) -> None:
        info = client.server_info()
        assert "moonraker_version" in info

    def test_returns_components(self, client: MoonrakerClient) -> None:
        info = client.server_info()
        assert "components" in info
        assert isinstance(info["components"], list)


class TestServerConfig:
    def test_returns_config(self, client: MoonrakerClient) -> None:
        config = client.server_config()
        assert "config" in config


class TestTemperatureStore:
    def test_returns_temperature_data(self, client: MoonrakerClient) -> None:
        temps = client.server_temperaturestore()
        assert isinstance(temps, dict)


class TestGcodeStore:
    def test_returns_gcode_responses(self, client: MoonrakerClient) -> None:
        store = client.server_gcodestore(count=5)
        assert isinstance(store, dict)
