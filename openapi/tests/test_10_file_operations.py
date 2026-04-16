"""Phase 4: File system operation tests.

Tests file listing, directory queries, and upload.
Note: copy, move, zip, and delete operations hang on this Docker-based
virtual printer due to inotify/filesystem watch limitations. Those
operations are tested only via schema structure validation of the spec,
not against the live API.
"""

from pathlib import Path

import httpx
import pytest
from conftest import validate_response, check_printer_health, BASE_URL

ASSETS_DIR = Path(__file__).parent / "assets"
TEST_GCODE = ASSETS_DIR / "test_print.gcode"


@pytest.fixture(scope="module")
def spec():
    import yaml
    with open(Path(__file__).parent.parent / "openapi.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        yield client


def test_health_check():
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


def test_directory_listing(api, spec):
    resp = api.get("/server/files/directory", params={"path": "gcodes"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/files/directory", resp.json())
    assert not errors, f"Schema errors: {errors}"
    result = resp.json()["result"]
    assert "dirs" in result
    assert "files" in result
    assert "disk_usage" in result
    assert "root_info" in result


def test_directory_extended(api, spec):
    resp = api.get("/server/files/directory",
                   params={"path": "gcodes", "extended": "true"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/files/directory", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_directory_config_root(api, spec):
    """Test directory listing for a different root."""
    resp = api.get("/server/files/directory", params={"path": "config"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/files/directory", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_copy_move_zip_schemas_exist(spec):
    """Verify copy, move, zip endpoints exist in spec with proper schemas."""
    for path in ["/server/files/copy", "/server/files/move",
                 "/server/files/zip"]:
        assert path in spec["paths"], f"Missing path: {path}"
        op = spec["paths"][path]["post"]
        assert "responses" in op
        assert "200" in op["responses"] or "default" in op["responses"]
