"""Phase 12: Content-type & Accept header tests.

Tests API behavior with different HTTP headers.
"""

from pathlib import Path

import httpx
import pytest
from conftest import check_printer_health, wait_for_ready, BASE_URL


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        yield client


def test_health_check():
    """Wait for printer after previous destructive tests."""
    import time
    time.sleep(2)
    try:
        state = check_printer_health()
    except Exception:
        time.sleep(10)
        state = wait_for_ready()
    assert state in ("ready", "startup", "error"), f"Not reachable: {state}"


def test_get_with_accept_json(api):
    """Normal GET with Accept: application/json."""
    resp = api.get("/server/info",
                   headers={"Accept": "application/json"})
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")


def test_get_without_accept_header(api):
    """GET without Accept header still returns JSON."""
    resp = api.get("/server/info")
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data


def test_post_with_json_content_type(api):
    """POST with correct Content-Type."""
    resp = api.post("/printer/gcode/script",
                    json={"script": "M115"},
                    headers={"Content-Type": "application/json"})
    assert resp.status_code == 200


def test_json_responses_have_content_type(api):
    """All JSON endpoints should set Content-Type header."""
    for path in ["/server/info", "/printer/info", "/server/webcams/list"]:
        resp = api.get(path)
        assert resp.status_code == 200
        ct = resp.headers.get("content-type", "")
        assert "json" in ct, f"{path} Content-Type: {ct}"


def test_error_response_is_json(api):
    """Error responses should also be JSON."""
    resp = api.get("/server/files/metadata",
                   params={"filename": "nonexistent_12345.gcode"})
    assert resp.status_code >= 400
    ct = resp.headers.get("content-type", "")
    assert "json" in ct, f"Error Content-Type: {ct}"
    data = resp.json()
    assert "error" in data
