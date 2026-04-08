"""Functional tests for printer endpoints against a live Moonraker server."""

from __future__ import annotations

import pytest

from moonraker_client import MoonrakerClient

pytestmark = pytest.mark.functional


class TestPrinterInfo:
    """Test printer_info against a real Moonraker server."""

    def test_returns_valid_state(self, client: MoonrakerClient) -> None:
        info = client.printer_info()
        assert "state" in info
        assert info["state"] in ("ready", "startup", "shutdown", "error")

    def test_returns_hostname(self, client: MoonrakerClient) -> None:
        info = client.printer_info()
        assert "hostname" in info
        assert isinstance(info["hostname"], str)
        assert len(info["hostname"]) > 0

    def test_returns_software_version(self, client: MoonrakerClient) -> None:
        info = client.printer_info()
        assert "software_version" in info
        assert isinstance(info["software_version"], str)

    def test_returns_state_message(self, client: MoonrakerClient) -> None:
        info = client.printer_info()
        assert "state_message" in info
        assert isinstance(info["state_message"], str)

    def test_returns_klipper_path(self, client: MoonrakerClient) -> None:
        info = client.printer_info()
        assert "klipper_path" in info

    def test_returns_expected_keys(self, client: MoonrakerClient) -> None:
        info = client.printer_info()
        expected_keys = {
            "state",
            "state_message",
            "hostname",
            "klipper_path",
            "python_path",
            "process_id",
            "user_id",
            "group_id",
            "log_file",
            "config_file",
            "software_version",
            "cpu_info",
        }
        # All expected keys should be present (may have extras)
        assert expected_keys.issubset(set(info.keys()))
