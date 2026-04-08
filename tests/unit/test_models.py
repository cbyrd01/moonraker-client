"""Unit tests for generated data models."""

from __future__ import annotations

from moonraker_client.models import (
    AnnouncementEntry,
    File,
    GcodeMetadata,
    JobHistoryEntry,
    JobHistoryTotals,
    ObjectQueryResponse,
    PrintStats,
    ProcStatsResponse,
    SensorMeasurements,
    Sys,
    UpdateStatus,
    WebcamEntry,
)


class TestFileModel:
    def test_from_dict(self) -> None:
        data = {"path": "test.gcode", "modified": 1700000000.0, "size": 1024, "permissions": "rw"}
        f = File.from_dict(data)
        assert f.path == "test.gcode"
        assert f.modified == 1700000000.0
        assert f.size == 1024
        assert f.permissions == "rw"

    def test_from_dict_ignores_extra_keys(self) -> None:
        data = {"path": "test.gcode", "unknown_field": "ignored"}
        f = File.from_dict(data)
        assert f.path == "test.gcode"

    def test_from_dict_missing_keys(self) -> None:
        f = File.from_dict({})
        assert f.path is None
        assert f.size is None


class TestJobHistoryEntry:
    def test_from_dict(self) -> None:
        data = {
            "job_id": "000001",
            "filename": "test.gcode",
            "status": "completed",
            "print_duration": 3600.5,
            "filament_used": 1500.0,
        }
        entry = JobHistoryEntry.from_dict(data)
        assert entry.job_id == "000001"
        assert entry.filename == "test.gcode"
        assert entry.status == "completed"
        assert entry.print_duration == 3600.5


class TestJobHistoryTotals:
    def test_from_dict(self) -> None:
        data = {
            "total_jobs": 100,
            "total_time": 360000.0,
            "total_print_time": 300000.0,
            "total_filament_used": 50000.0,
            "longest_job": 7200.0,
            "longest_print": 6000.0,
        }
        totals = JobHistoryTotals.from_dict(data)
        assert totals.total_jobs == 100
        assert totals.longest_print == 6000.0


class TestPrintStats:
    def test_from_dict(self) -> None:
        data = {
            "print_duration": 1200.0,
            "filename": "benchy.gcode",
            "state": "printing",
            "message": "",
        }
        stats = PrintStats.from_dict(data)
        assert stats.state == "printing"
        assert stats.filename == "benchy.gcode"


class TestObjectQueryResponse:
    def test_from_dict(self) -> None:
        data = {
            "eventtime": 1700000000.0,
            "status": {"toolhead": {"position": [0, 0, 0, 0]}},
        }
        resp = ObjectQueryResponse.from_dict(data)
        assert resp.eventtime == 1700000000.0
        assert resp.status is not None
        assert "toolhead" in resp.status


class TestGcodeMetadata:
    def test_from_dict(self) -> None:
        data = {
            "filename": "benchy.gcode",
            "size": 2048000,
            "slicer": "PrusaSlicer",
            "estimated_time": 3600.0,
            "layer_height": 0.2,
            "filament_total": 5000.0,
        }
        meta = GcodeMetadata.from_dict(data)
        assert meta.slicer == "PrusaSlicer"
        assert meta.estimated_time == 3600.0
        assert meta.layer_height == 0.2


class TestSensorMeasurements:
    def test_from_dict(self) -> None:
        data = {"temperature": [20.1, 20.2, 20.3], "humidity": [45.0, 45.1]}
        m = SensorMeasurements.from_dict(data)
        assert m.data is not None
        assert "temperature" in m.data


class TestAnnouncementEntry:
    def test_from_dict(self) -> None:
        data = {
            "entry_id": "abc123",
            "title": "Test Announcement",
            "priority": "normal",
            "dismissed": False,
        }
        entry = AnnouncementEntry.from_dict(data)
        assert entry.entry_id == "abc123"
        assert entry.dismissed is False


class TestUpdateStatus:
    def test_from_dict(self) -> None:
        data = {
            "busy": False,
            "github_rate_limit": 60,
            "github_requests_remaining": 55,
        }
        status = UpdateStatus.from_dict(data)
        assert status.busy is False
        assert status.github_rate_limit == 60


class TestWebcamEntry:
    def test_from_dict(self) -> None:
        data = {
            "name": "webcam",
            "enabled": True,
            "target_fps": 15,
            "stream_url": "/webcam/?action=stream",
        }
        cam = WebcamEntry.from_dict(data)
        assert cam.name == "webcam"
        assert cam.target_fps == 15
