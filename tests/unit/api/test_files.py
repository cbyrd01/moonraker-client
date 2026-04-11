"""Unit tests for files API endpoints."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import AsyncMoonrakerClient, MoonrakerClient


class TestFilesMixin:
    def test_files_list(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": [
                    {"path": "test.gcode", "modified": 1700000000.0, "size": 1024},
                ]
            }
        )
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
        httpx_mock.add_response(
            json={
                "result": [
                    {"name": "gcodes", "permissions": "rw"},
                    {"name": "config", "permissions": "rw"},
                ]
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_roots()
        assert len(result) == 2

    def test_files_metadata(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "filename": "test.gcode",
                    "slicer": "PrusaSlicer",
                    "estimated_time": 3600.0,
                }
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_metadata("test.gcode")
        assert result["slicer"] == "PrusaSlicer"
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.params["filename"] == "test.gcode"

    def test_files_directory(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "dirs": [{"dirname": "subdir", "modified": 1700000000.0}],
                    "files": [{"filename": "test.gcode", "modified": 1700000000.0, "size": 1024}],
                }
            }
        )
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

    def test_files_download_returns_raw_bytes(self, httpx_mock: HTTPXMock) -> None:
        """Download must return raw bytes, not parse them as JSON.

        Regression: before Phase 4b this method went through the
        generic response-unwrap path and called ``response.json()``
        on binary gcode, crashing with ``JSONDecodeError``.
        """
        payload = b"; klipperctl test gcode\nG28\nG1 X10\n"
        httpx_mock.add_response(
            content=payload,
            headers={"content-length": str(len(payload))},
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_download("gcodes", "test.gcode")
        assert result == payload
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/server/files/gcodes/test.gcode"

    def test_files_download_fires_progress_callback(self, httpx_mock: HTTPXMock) -> None:
        """Progress callback must fire at least once with (total, total)."""
        payload = b"X" * 4096
        httpx_mock.add_response(
            content=payload,
            headers={"content-length": str(len(payload))},
        )
        ticks: list[tuple[int, int | None]] = []

        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_download(
                "gcodes", "big.gcode", progress=lambda done, total: ticks.append((done, total))
            )

        assert result == payload
        assert ticks, "progress callback was never invoked"
        # First tick must be (0, total), last must be (total, total).
        assert ticks[0] == (0, len(payload))
        assert ticks[-1] == (len(payload), len(payload))
        # Monotonic progress.
        done_values = [t[0] for t in ticks]
        assert done_values == sorted(done_values)

    def test_files_upload_fires_progress_callback(
        self, httpx_mock: HTTPXMock, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Progress callback must fire for uploads with monotonic bytes-done."""
        from pathlib import Path

        httpx_mock.add_response(
            json={"result": {"item": {"path": "test.gcode"}, "action": "create_file"}}
        )
        local = Path(str(tmp_path)) / "test.gcode"  # type: ignore[arg-type]
        local.write_bytes(b"G28\n" * 256)  # 1024 bytes

        seen: list[tuple[int, int | None]] = []

        with MoonrakerClient("http://localhost:7125") as client:
            result = client.files_upload(str(local), progress=lambda d, t: seen.append((d, t)))

        assert result["item"]["path"] == "test.gcode"
        assert seen, "progress callback was never invoked"
        # First tick at (0, total), final cumulative must equal total.
        total = local.stat().st_size
        assert seen[0] == (0, total)
        # At least one tick should report full completion.
        assert any(done == total for done, _ in seen), (
            f"expected a tick at ({total}, {total}); got {seen}"
        )
        # Monotonic.
        done_values = [d for d, _ in seen]
        assert done_values == sorted(done_values)

    def test_files_delete(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"item": {}, "action": "delete_file"}})
        with MoonrakerClient("http://localhost:7125") as client:
            client.files_delete("gcodes", "test.gcode")
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

    @pytest.mark.asyncio
    async def test_files_download_returns_raw_bytes(self, httpx_mock: HTTPXMock) -> None:
        payload = b"G28\nG1 X0 Y0\n"
        httpx_mock.add_response(content=payload)
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.files_download("gcodes", "a.gcode")
        assert result == payload

    @pytest.mark.asyncio
    async def test_files_download_fires_progress_callback(self, httpx_mock: HTTPXMock) -> None:
        payload = b"Y" * 2048
        httpx_mock.add_response(content=payload, headers={"content-length": str(len(payload))})
        ticks: list[tuple[int, int | None]] = []
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.files_download(
                "gcodes", "y.gcode", progress=lambda d, t: ticks.append((d, t))
            )
        assert result == payload
        assert ticks[0] == (0, len(payload))
        assert ticks[-1] == (len(payload), len(payload))

    @pytest.mark.asyncio
    async def test_files_upload_fires_progress_callback(
        self, httpx_mock: HTTPXMock, tmp_path
    ) -> None:
        from pathlib import Path

        httpx_mock.add_response(
            json={"result": {"item": {"path": "a.gcode"}, "action": "create_file"}}
        )
        local = Path(str(tmp_path)) / "a.gcode"
        local.write_bytes(b"M117\n" * 200)  # 1000 bytes

        seen: list[tuple[int, int | None]] = []
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            await client.files_upload(str(local), progress=lambda d, t: seen.append((d, t)))

        total = local.stat().st_size
        assert seen[0] == (0, total)
        assert any(d == total for d, _ in seen)


class TestProgressReader:
    """Unit tests for the internal _ProgressReader multipart helper."""

    def test_read_all_fires_callback(self) -> None:
        from moonraker_client.api.files import _ProgressReader

        data = b"ABCDEFGHIJ"
        ticks: list[tuple[int, int | None]] = []
        r = _ProgressReader(data, lambda d, t: ticks.append((d, t)), len(data))
        out = r.read()
        assert out == data
        # Must see an opening (0, total) tick and a final (total, total) tick.
        assert ticks[0] == (0, len(data))
        assert ticks[-1] == (len(data), len(data))

    def test_read_chunked_reports_monotonic(self) -> None:
        from moonraker_client.api.files import _ProgressReader

        data = b"0123456789"
        ticks: list[tuple[int, int | None]] = []
        r = _ProgressReader(data, lambda d, t: ticks.append((d, t)), len(data))
        assert r.read(3) == b"012"
        assert r.read(3) == b"345"
        assert r.read(100) == b"6789"
        # First tick is the (0, total) announcement; after that, monotonic.
        done_values = [d for d, _ in ticks]
        assert done_values == sorted(done_values)
        assert done_values[-1] == len(data)

    def test_seek_rewind_resets_announcement(self) -> None:
        from moonraker_client.api.files import _ProgressReader

        data = b"abc"
        ticks: list[tuple[int, int | None]] = []
        r = _ProgressReader(data, lambda d, t: ticks.append((d, t)), len(data))
        r.read()  # consumes everything, emits (0, 3) + (3, 3)
        r.seek(0)
        r.read()  # must re-announce (0, 3) after rewind
        # Expect at least two (0, total) ticks — one per pass.
        zero_ticks = [t for t in ticks if t[0] == 0]
        assert len(zero_ticks) >= 2
