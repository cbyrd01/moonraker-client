"""Phase 4: File management tests.

Tests file upload, listing, metadata, download, and delete cycle.
Validates all responses against the OpenAPI spec schemas.
"""

from pathlib import Path

import httpx
import pytest
from conftest import validate_response, BASE_URL

ASSETS_DIR = Path(__file__).parent / "assets"
TEST_GCODE = ASSETS_DIR / "test_print.gcode"


@pytest.fixture(scope="module")
def spec():
    import yaml
    with open(Path(__file__).parent.parent / "openapi.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="module")
def uploaded_file(api):
    """Upload test gcode and yield filename, then clean up."""
    with open(TEST_GCODE, "rb") as f:
        resp = api.post(
            "/server/files/upload",
            files={"file": ("test_print.gcode", f, "application/octet-stream")},
            data={"root": "gcodes"},
        )
    assert resp.status_code == 201, f"Upload failed: {resp.status_code} {resp.text}"
    yield "test_print.gcode"
    # Cleanup
    api.delete("/server/files/gcodes/test_print.gcode")


def test_file_upload(api, spec):
    """Test file upload and validate response schema."""
    with open(TEST_GCODE, "rb") as f:
        resp = api.post(
            "/server/files/upload",
            files={"file": ("test_print.gcode", f, "application/octet-stream")},
            data={"root": "gcodes"},
        )
    assert resp.status_code == 201, f"Upload failed: {resp.status_code} {resp.text}"
    data = resp.json()
    errors = validate_response(spec, "/server/files/upload", data, method="post",
                               status="201")
    assert not errors, f"Schema errors: {errors}"
    assert "item" in data and "action" in data, f"Unexpected upload response: {data}"


def test_file_list_after_upload(api, spec, uploaded_file):
    """Verify uploaded file appears in file listing."""
    resp = api.get("/server/files/list")
    assert resp.status_code == 200
    data = resp.json()
    errors = validate_response(spec, "/server/files/list", data)
    assert not errors, f"Schema errors: {errors}"
    filenames = [f.get("filename", f.get("path", ""))
                 for f in data["result"]]
    assert uploaded_file in filenames, (
        f"{uploaded_file} not found in file list: {filenames}"
    )


@pytest.mark.xfail(
    reason=(
        "Upstream Arksine/moonraker spec declares print_start_time as `number` but "
        "Moonraker returns null when no print has started. Fixed in cbyrd01/moonraker "
        "(nullable); remove this xfail once the fix is upstreamed."
    ),
    strict=False,
)
def test_file_metadata(api, spec, uploaded_file):
    """Validate file metadata response schema."""
    import time
    # Metadata may take a moment to be generated
    for _ in range(5):
        resp = api.get(f"/server/files/metadata?filename={uploaded_file}")
        if resp.status_code == 200:
            break
        time.sleep(1)
    assert resp.status_code == 200, f"Metadata failed: {resp.status_code} {resp.text}"
    errors = validate_response(spec, "/server/files/metadata", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_file_roots(api, spec):
    """Validate file roots listing schema."""
    resp = api.get("/server/files/roots")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/files/roots", resp.json())
    assert not errors, f"Schema errors: {errors}"
    roots = [r["name"] for r in resp.json()["result"]]
    assert "gcodes" in roots


def test_file_download(api, uploaded_file):
    """Download uploaded file and verify contents match."""
    resp = api.get(f"/server/files/gcodes/{uploaded_file}")
    assert resp.status_code == 200
    original = TEST_GCODE.read_text()
    assert resp.text == original, "Downloaded file content doesn't match original"


def test_file_delete(api, spec):
    """Test file deletion and validate response schema."""
    # Upload a temp file to delete
    with open(TEST_GCODE, "rb") as f:
        api.post(
            "/server/files/upload",
            files={"file": ("delete_test.gcode", f, "application/octet-stream")},
            data={"root": "gcodes"},
        )
    resp = api.delete("/server/files/gcodes/delete_test.gcode")
    assert resp.status_code == 200
    errors = validate_response(
        spec, "/server/files/{root}/{filename}", resp.json(), method="delete"
    )
    assert not errors, f"Schema errors: {errors}"


def test_file_gone_after_delete(api):
    """Confirm deleted file no longer appears in listing."""
    resp = api.get("/server/files/list")
    assert resp.status_code == 200
    filenames = [f.get("filename", f.get("path", ""))
                 for f in resp.json()["result"]]
    assert "delete_test.gcode" not in filenames
