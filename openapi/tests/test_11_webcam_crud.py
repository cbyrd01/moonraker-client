"""Phase 5: Webcam CRUD tests.

Full create/read/update/delete lifecycle for webcam entries.
"""

from pathlib import Path

import httpx
import pytest
from conftest import validate_response, check_printer_health, BASE_URL


@pytest.fixture(scope="module")
def spec():
    import yaml
    with open(Path(__file__).parent.parent / "openapi.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
def cleanup(api):
    yield
    # Best-effort cleanup
    api.delete("/server/webcams/item", params={"name": "openapi_test_cam"})


def test_health_check():
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


WEBCAM_DATA = {
    "name": "openapi_test_cam",
    "location": "printer",
    "service": "mjpegstreamer",
    "enabled": True,
    "icon": "mdiWebcam",
    "target_fps": 15,
    "target_fps_idle": 5,
    "stream_url": "/webcam/?action=stream",
    "snapshot_url": "/webcam/?action=snapshot",
    "flip_horizontal": False,
    "flip_vertical": False,
    "rotation": 0,
    "aspect_ratio": "4:3",
    "extra_data": {},
}


def test_webcam_create(api, spec):
    resp = api.post("/server/webcams/item", json=WEBCAM_DATA)
    assert resp.status_code == 200, f"Create failed: {resp.text}"
    errors = validate_response(spec, "/server/webcams/item", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_webcam_list_after_create(api, spec):
    resp = api.get("/server/webcams/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/webcams/list", resp.json())
    assert not errors, f"Schema errors: {errors}"
    names = [w["name"] for w in resp.json()["result"]["webcams"]]
    assert "openapi_test_cam" in names


def test_webcam_get_by_name(api, spec):
    resp = api.get("/server/webcams/item",
                   params={"name": "openapi_test_cam"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/webcams/item", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_webcam_update(api, spec):
    updated = {**WEBCAM_DATA, "target_fps": 30}
    resp = api.post("/server/webcams/item", json=updated)
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/webcams/item", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_webcam_delete(api, spec):
    resp = api.delete("/server/webcams/item",
                      params={"name": "openapi_test_cam"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/webcams/item", resp.json(),
                               method="delete")
    assert not errors, f"Schema errors: {errors}"


def test_webcam_gone_after_delete(api):
    resp = api.get("/server/webcams/list")
    names = [w["name"] for w in resp.json()["result"]["webcams"]]
    assert "openapi_test_cam" not in names
