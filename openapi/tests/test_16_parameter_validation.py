"""Phase 10: Parameter validation & edge case tests.

Tests that the API properly rejects invalid input and that error
responses match the spec's ErrorResponse schema.
"""

from pathlib import Path

import httpx
import pytest
from conftest import check_printer_health, BASE_URL
from jsonschema.validators import Draft202012Validator

SPEC_PATH = Path(__file__).parent.parent / "openapi.yaml"


@pytest.fixture(scope="module")
def spec():
    import yaml
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        yield client


def _validate_error(spec, data):
    schema = spec["components"]["schemas"]["ErrorResponse"]
    v = Draft202012Validator(schema)
    return [f"{e.json_path}: {e.message}" for e in v.iter_errors(data)]


def test_health_check():
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


def test_missing_required_param(api, spec):
    """GET metadata without required filename param."""
    resp = api.get("/server/files/metadata")
    assert resp.status_code >= 400
    errors = _validate_error(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_empty_post_body(api, spec):
    """POST print/start with empty body."""
    resp = api.post("/printer/print/start", json={})
    assert resp.status_code >= 400
    errors = _validate_error(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_nonexistent_endpoint(api, spec):
    """Request to a path that doesn't exist."""
    resp = api.get("/nonexistent/endpoint/12345")
    assert resp.status_code == 404
    errors = _validate_error(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_wrong_method(api):
    """PUT to an endpoint that only accepts GET/POST."""
    resp = api.put("/server/info")
    assert resp.status_code in (404, 405)


def test_invalid_gcode_script(api, spec):
    """Send invalid gcode command."""
    resp = api.post("/printer/gcode/script",
                    json={"script": "INVALID_COMMAND_XYZ_12345"})
    # Klipper may accept unknown commands or return error
    assert resp.status_code in (200, 400)


def test_database_missing_namespace(api, spec):
    """GET database item without namespace."""
    resp = api.get("/server/database/item")
    assert resp.status_code >= 400
    errors = _validate_error(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_path_traversal_attempt(api, spec):
    """Attempt path traversal in file request."""
    resp = api.get("/server/files/gcodes/../../../etc/passwd")
    assert resp.status_code >= 400
