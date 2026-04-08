"""Unit tests for files API endpoints."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import MoonrakerClient, AsyncMoonrakerClient


class TestFilesMixin:
    def test_files_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": [
            {"path": "test.gcode", "modified": 1700000000.0, "size": 1024},
        ]})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_list()
        assert len(result) == 1
        assert result[0]["path"] == "test.gcode"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["root"] == "gcodes"

    def test_files_list_custom_root(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": []})
        with MoonrakerClient("http://localhost:7125") as client:
            client.files_list(root="config")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["root"] == "config"

    def test_files_roots(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": [
            {"name": "gcodes", "permissions": "rw"},
            {"name": "config", "permissions": "rw"},
        ]})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_roots()
        assert len(result) == 2

    def test_files_metadata(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {
            "filename": "test.gcode",
            "slicer": "PrusaSlicer",
            "estimated_time": 3600.0,
        }})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_metadata("test.gcode")
        assert result["slicer"] == "PrusaSlicer"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["filename"] == "test.gcode"

    def test_files_directory(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {
            "dirs": [{"dirname": "subdir", "modified": 1700000000.0}],
            "files": [{"filename": "test.gcode", "modified": 1700000000.0, "size": 1024}],
        }})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_directory(path="gcodes")
        assert "dirs" in result
        assert "files" in result

    def test_files_move(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"item": {}, "action": "move_file"}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_move("gcodes/old.gcode", "gcodes/new.gcode")
        assert result["action"] == "move_file"

    def test_files_copy(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"item": {}, "action": "copy_file"}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_copy("gcodes/src.gcode", "gcodes/dst.gcode")
        assert result["action"] == "copy_file"

    def test_files_download(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "file-content"})
        with MoonrakerClient("http://localhost:7125") as client:
            client.files_download("gcodes", "test.gcode")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/server/files/gcodes/test.gcode"

    def test_files_delete(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"item": {}, "action": "delete_file"}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_delete("gcodes", "test.gcode")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"
        assert request.url.path == "/server/files/gcodes/test.gcode"


class TestAsyncFilesMixin:
    @pytest.mark.asyncio
    async def test_files_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": []})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.files_list()
        assert result == []
