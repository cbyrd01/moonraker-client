"""Functional tests for helper functions against a live Moonraker server."""

from __future__ import annotations

import pytest

from moonraker_client import MoonrakerClient
from moonraker_client.helpers import (
    get_print_progress,
    get_printer_status,
    get_system_health,
    get_temperatures,
    is_printing,
    list_gcode_files,
    set_bed_temp,
    set_hotend_temp,
)

pytestmark = pytest.mark.functional


class TestGetPrinterStatus:
    def test_returns_status(self, client: MoonrakerClient) -> None:
        status = get_printer_status(client)
        assert status.state in ("ready", "startup", "shutdown", "error")
        assert isinstance(status.hostname, str)
        assert isinstance(status.klippy_connected, bool)

    def test_has_temperatures(self, client: MoonrakerClient) -> None:
        status = get_printer_status(client)
        # Should have at least extruder or heater_bed
        assert isinstance(status.temperatures, dict)


class TestGetTemperatures:
    def test_returns_readings(self, client: MoonrakerClient) -> None:
        temps = get_temperatures(client)
        assert isinstance(temps, dict)
        # At minimum, extruder should exist
        if "extruder" in temps:
            assert isinstance(temps["extruder"].current, float)
            assert isinstance(temps["extruder"].target, float)


class TestIsPrinting:
    def test_returns_bool(self, client: MoonrakerClient) -> None:
        result = is_printing(client)
        assert isinstance(result, bool)


class TestGetPrintProgress:
    def test_returns_progress_or_none(self, client: MoonrakerClient) -> None:
        result = get_print_progress(client)
        # Either None (no print) or a PrintProgress object
        if result is not None:
            assert isinstance(result.filename, str)
            assert 0.0 <= result.progress_pct <= 100.0


class TestListGcodeFiles:
    def test_returns_list(self, client: MoonrakerClient) -> None:
        files = list_gcode_files(client)
        assert isinstance(files, list)


class TestGetSystemHealth:
    def test_returns_health(self, client: MoonrakerClient) -> None:
        health = get_system_health(client)
        assert "cpu_temp" in health or "system_uptime" in health
        assert "cpu_info" in health


class TestSetTemperature:
    """Tests that verify temperature setting actually changes the target.

    Uses safe low temperatures and always cleans up to 0.
    """

    def test_set_hotend_temp(self, client: MoonrakerClient) -> None:
        try:
            set_hotend_temp(client, 50.0)
            temps = get_temperatures(client)
            assert "extruder" in temps
            assert temps["extruder"].target == pytest.approx(50.0, abs=0.1)
        finally:
            set_hotend_temp(client, 0)

    def test_set_bed_temp(self, client: MoonrakerClient) -> None:
        try:
            set_bed_temp(client, 40.0)
            temps = get_temperatures(client)
            assert "heater_bed" in temps
            assert temps["heater_bed"].target == pytest.approx(40.0, abs=0.1)
        finally:
            set_bed_temp(client, 0)

    def test_cooldown(self, client: MoonrakerClient) -> None:
        set_hotend_temp(client, 0)
        set_bed_temp(client, 0)
        temps = get_temperatures(client)
        if "extruder" in temps:
            assert temps["extruder"].target == pytest.approx(0.0, abs=0.1)
        if "heater_bed" in temps:
            assert temps["heater_bed"].target == pytest.approx(0.0, abs=0.1)
