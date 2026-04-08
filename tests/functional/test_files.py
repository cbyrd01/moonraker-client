"""Functional tests for file manager endpoints against a live Moonraker server."""

from __future__ import annotations

import pytest

from moonraker_client import MoonrakerClient

pytestmark = pytest.mark.functional


class TestFilesList:
    def test_list_gcodes(self, client: MoonrakerClient) -> None:
        files = client.files_list(root="gcodes")
        assert isinstance(files, list)

    def test_list_config(self, client: MoonrakerClient) -> None:
        files = client.files_list(root="config")
        assert isinstance(files, list)


class TestFilesRoots:
    def test_returns_roots(self, client: MoonrakerClient) -> None:
        roots = client.files_roots()
        assert isinstance(roots, list)
        assert len(roots) > 0
        root_names = [r["name"] for r in roots]
        assert "gcodes" in root_names
        assert "config" in root_names


class TestFilesDirectory:
    def test_get_gcodes_directory(self, client: MoonrakerClient) -> None:
        result = client.files_directory(path="gcodes")
        assert "dirs" in result or "files" in result
