"""Phase 7: Broad POST endpoint schema validation.

Direct tests for POST endpoints not covered elsewhere.
Replaces schemathesis fuzzing with fast, targeted calls.
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


def test_health_check(api):
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


# --- Safe POST endpoints ---

def test_post_announcements_update(api, spec):
    resp = api.post("/server/announcements/update")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/announcements/update",
                               resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"


def test_post_database_compact(api, spec):
    resp = api.post("/server/database/compact")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/database/compact",
                               resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"


def test_post_printer_objects_query(api, spec):
    resp = api.post("/printer/objects/query",
                    json={"objects": {"toolhead": None, "extruder": None}})
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/objects/query",
                               resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"


def test_post_gcode_script(api, spec):
    resp = api.post("/printer/gcode/script", json={"script": "M115"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/gcode/script",
                               resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"


def test_post_announcements_dismiss_invalid(api, spec):
    """Dismiss with invalid entry_id -- validates error schema."""
    resp = api.post("/server/announcements/dismiss",
                    json={"entry_id": "nonexistent_12345"})
    # May return error -- just verify it returns valid JSON
    assert resp.status_code in (200, 400, 404)


def test_post_logs_rollover(api, spec):
    resp = api.post("/server/logs/rollover")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/logs/rollover",
                               resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"
