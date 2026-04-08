"""Unit tests for helper functions."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from moonraker_client.exceptions import MoonrakerConnectionError
from moonraker_client.helpers import (
    get_print_progress,
    get_printer_status,
    get_system_health,
    get_temperatures,
    is_printing,
    list_gcode_files,
    send_gcode,
    set_bed_temp,
    set_hotend_temp,
    start_print,
)


@pytest.fixture
def mock_client() -> MagicMock:
    return MagicMock()


class TestGetTemperatures:
    def test_returns_heater_readings(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.return_value = {
            "status": {
                "extruder": {"temperature": 200.5, "target": 210.0, "power": 0.8},
                "heater_bed": {"temperature": 60.0, "target": 60.0, "power": 0.1},
            }
        }
        temps = get_temperatures(mock_client)
        assert "extruder" in temps
        assert temps["extruder"].current == 200.5
        assert temps["extruder"].target == 210.0
        assert temps["heater_bed"].power == 0.1

    def test_returns_empty_on_error(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.side_effect = MoonrakerConnectionError(
            "connection failed"
        )
        temps = get_temperatures(mock_client)
        assert temps == {}


class TestIsPrinting:
    def test_true_when_printing(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.return_value = {
            "status": {"print_stats": {"state": "printing"}}
        }
        assert is_printing(mock_client) is True

    def test_false_when_standby(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.return_value = {
            "status": {"print_stats": {"state": "standby"}}
        }
        assert is_printing(mock_client) is False

    def test_false_on_error(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.side_effect = MoonrakerConnectionError("fail")
        assert is_printing(mock_client) is False


class TestGetPrintProgress:
    def test_returns_progress(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.return_value = {
            "status": {
                "print_stats": {
                    "filename": "benchy.gcode",
                    "state": "printing",
                    "print_duration": 1200.0,
                    "message": "",
                },
                "virtual_sdcard": {"progress": 0.456},
            }
        }
        progress = get_print_progress(mock_client)
        assert progress is not None
        assert progress.filename == "benchy.gcode"
        assert progress.progress_pct == 45.6
        assert progress.elapsed == 1200.0
        assert progress.state == "printing"

    def test_returns_none_when_no_file(self, mock_client: MagicMock) -> None:
        mock_client.printer_objects_query.return_value = {
            "status": {
                "print_stats": {"filename": "", "state": "standby"},
                "virtual_sdcard": {"progress": 0.0},
            }
        }
        assert get_print_progress(mock_client) is None


class TestGetPrinterStatus:
    def test_returns_full_status(self, mock_client: MagicMock) -> None:
        mock_client.printer_info.return_value = {
            "state": "ready",
            "state_message": "Printer is ready",
            "hostname": "pi",
            "software_version": "v0.12.0",
        }
        mock_client.server_info.return_value = {
            "klippy_connected": True,
            "klippy_state": "ready",
        }
        mock_client.printer_objects_query.return_value = {
            "status": {
                "extruder": {"temperature": 25.0, "target": 0.0, "power": 0.0},
                "heater_bed": {"temperature": 25.0, "target": 0.0, "power": 0.0},
                "print_stats": {"filename": "", "print_duration": 0.0},
                "virtual_sdcard": {"progress": 0.0},
            }
        }
        status = get_printer_status(mock_client)
        assert status.state == "ready"
        assert status.klippy_connected is True
        assert "extruder" in status.temperatures


class TestStartPrint:
    def test_starts_print_when_file_exists(self, mock_client: MagicMock) -> None:
        mock_client.files_metadata.return_value = {"filename": "test.gcode"}
        mock_client.print_start.return_value = "ok"
        result = start_print(mock_client, "test.gcode")
        assert result == "ok"
        mock_client.print_start.assert_called_once_with("test.gcode")

    def test_raises_when_file_not_found(self, mock_client: MagicMock) -> None:
        mock_client.files_metadata.side_effect = MoonrakerConnectionError("not found")
        with pytest.raises(FileNotFoundError, match=r"test\.gcode"):
            start_print(mock_client, "test.gcode")


class TestGcodeHelpers:
    def test_send_gcode(self, mock_client: MagicMock) -> None:
        mock_client.gcode_script.return_value = "ok"
        result = send_gcode(mock_client, "G28")
        mock_client.gcode_script.assert_called_once_with("G28")
        assert result == "ok"

    def test_set_hotend_temp(self, mock_client: MagicMock) -> None:
        mock_client.gcode_script.return_value = "ok"
        set_hotend_temp(mock_client, 210.0)
        mock_client.gcode_script.assert_called_once_with("M104 S210.0 T0")

    def test_set_hotend_temp_tool1(self, mock_client: MagicMock) -> None:
        mock_client.gcode_script.return_value = "ok"
        set_hotend_temp(mock_client, 200.0, tool=1)
        mock_client.gcode_script.assert_called_once_with("M104 S200.0 T1")

    def test_set_bed_temp(self, mock_client: MagicMock) -> None:
        mock_client.gcode_script.return_value = "ok"
        set_bed_temp(mock_client, 60.0)
        mock_client.gcode_script.assert_called_once_with("M140 S60.0")


class TestListGcodeFiles:
    def test_sorts_by_modified_desc(self, mock_client: MagicMock) -> None:
        mock_client.files_list.return_value = [
            {"path": "old.gcode", "modified": 100.0},
            {"path": "new.gcode", "modified": 200.0},
        ]
        files = list_gcode_files(mock_client)
        assert files[0]["path"] == "new.gcode"
        assert files[1]["path"] == "old.gcode"

    def test_sorts_by_size(self, mock_client: MagicMock) -> None:
        mock_client.files_list.return_value = [
            {"path": "big.gcode", "size": 5000},
            {"path": "small.gcode", "size": 100},
        ]
        files = list_gcode_files(mock_client, sort_by="size")
        assert files[0]["path"] == "small.gcode"


class TestGetSystemHealth:
    def test_returns_health(self, mock_client: MagicMock) -> None:
        mock_client.machine_procstats.return_value = {
            "cpu_temp": 45.0,
            "system_uptime": 86400.0,
            "system_memory": {"total": 4096, "used": 2048},
            "system_cpu_usage": {"cpu": 25.0},
            "websocket_connections": 3,
        }
        mock_client.machine_systeminfo.return_value = {
            "system_info": {"cpu_info": {"cpu_count": 4}},
        }
        health = get_system_health(mock_client)
        assert health["cpu_temp"] == 45.0
        assert health["system_uptime"] == 86400.0
        assert health["websocket_connections"] == 3
