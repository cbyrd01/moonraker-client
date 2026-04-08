"""Unit tests for job queue API endpoints."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import AsyncMoonrakerClient, MoonrakerClient


class TestJobsMixin:
    def test_jobqueue_status(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "queued_jobs": [],
                    "queue_state": "ready",
                }
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_jobqueue_status()
        assert result["queue_state"] == "ready"
        assert result["queued_jobs"] == []

    def test_jobqueue_enqueue(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "queued_jobs": [{"filename": "test.gcode", "job_id": "001"}],
                    "queue_state": "ready",
                }
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_jobqueue_job(filenames=["test.gcode"])
        assert len(result["queued_jobs"]) == 1

        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["filenames"] == ["test.gcode"]

    def test_jobqueue_pause(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_jobqueue_pause()
        assert result == "ok"

    def test_jobqueue_start(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.server_jobqueue_start()
        assert result == "ok"

    def test_jobqueue_jump(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            client.server_jobqueue_jump(job_id="001")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["job_id"] == "001"


class TestAsyncJobsMixin:
    @pytest.mark.asyncio
    async def test_jobqueue_status(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"queued_jobs": [], "queue_state": "ready"}})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.server_jobqueue_status()
        assert result["queue_state"] == "ready"
