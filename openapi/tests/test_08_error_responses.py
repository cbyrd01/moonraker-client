"""Phase 1: Error response schema validation.

Verifies that API error responses match the spec's ErrorResponse schema.
"""

from pathlib import Path

import httpx
import pytest
from conftest import BASE_URL

SPEC_PATH = Path(__file__).parent.parent / "openapi.yaml"


@pytest.fixture(scope="module")
def spec():
    import yaml
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


def _get_error_schema(spec):
    """Get the resolved ErrorResponse schema."""
    schema = spec["components"]["schemas"]["ErrorResponse"]
    return schema


def _validate_error_body(spec, data):
    """Validate an error response body against the ErrorResponse schema."""
    from jsonschema.validators import Draft202012Validator
    schema = _get_error_schema(spec)
    v = Draft202012Validator(schema)
    errors = [f"{e.json_path}: {e.message}" for e in v.iter_errors(data)]
    return errors


# --- 404 errors ---

def test_error_nonexistent_file_metadata(api, spec):
    """GET metadata for nonexistent file -> error response."""
    resp = api.get("/server/files/metadata",
                   params={"filename": "nonexistent_file_12345.gcode"})
    assert resp.status_code >= 400
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"
    assert resp.json()["error"]["code"] >= 400


def test_error_delete_nonexistent_file(api, spec):
    """DELETE nonexistent file -> error response."""
    resp = api.delete("/server/files/gcodes/absolutely_nonexistent_xyz.gcode")
    assert resp.status_code >= 400, f"Expected error, got {resp.status_code}"
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_error_nonexistent_database_item(api, spec):
    """GET nonexistent database item -> error response."""
    resp = api.get("/server/database/item",
                   params={"namespace": "nonexistent_ns_12345", "key": "x"})
    assert resp.status_code >= 400
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_error_nonexistent_history_job(api, spec):
    """GET nonexistent history job -> error response."""
    resp = api.get("/server/history/job", params={"uid": "ZZZZZZ"})
    assert resp.status_code >= 400
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


# --- 404 for unloaded components ---

def test_error_unloaded_component_update_status(api, spec):
    """Endpoint for unloaded component -> 404."""
    resp = api.get("/machine/update/status")
    assert resp.status_code == 404
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_error_unloaded_component_spoolman(api, spec):
    """Spoolman not loaded -> 404."""
    resp = api.get("/server/spoolman/status")
    assert resp.status_code == 404
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


# --- 400 bad request ---

def test_error_print_start_nonexistent_file(api, spec):
    """Start print with nonexistent file -> error."""
    resp = api.post("/printer/print/start",
                    json={"filename": "nonexistent_12345.gcode"})
    assert resp.status_code >= 400
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"


def test_error_print_start_empty_body(api, spec):
    """Start print with empty body -> error."""
    resp = api.post("/printer/print/start", json={})
    assert resp.status_code >= 400
    errors = _validate_error_body(spec, resp.json())
    assert not errors, f"Error schema mismatch: {errors}"
