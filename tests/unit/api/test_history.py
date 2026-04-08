"""Unit tests for history API endpoints."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import MoonrakerClient, AsyncMoonrakerClient


class TestHistoryMixin:
    def test_history_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {
            "count": 2,
            "jobs": [
                {"job_id": "001", "filename": "a.gcode", "status": "completed"},
                {"job_id": "002", "filename": "b.gcode", "status": "cancelled"},
            ],
        }})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_history_list(limit=10, order="asc")
        assert result["count"] == 2
        assert len(result["jobs"]) == 2

        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["limit"] == "10"
        assert request.url.params["order"] == "asc"

    def test_history_totals(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {
            "total_jobs": 50,
            "total_time": 180000.0,
            "total_filament_used": 25000.0,
        }})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_history_totals()
        assert result["total_jobs"] == 50

    def test_history_job(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {
            "job": {"job_id": "001", "filename": "test.gcode"},
        }})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_history_job(uid="001")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["uid"] == "001"

    def test_history_reset_totals(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_history_resettotals()
        assert result == "ok"


class TestAsyncHistoryMixin:
    @pytest.mark.asyncio
    async def test_history_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"count": 0, "jobs": []}})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.server_history_list()
        assert result["count"] == 0
