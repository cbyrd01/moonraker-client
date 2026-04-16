"""Phase 3: Basic read-only endpoint tests.

Safe GET requests to informational endpoints. Validates response bodies
against the OpenAPI spec schemas.
"""

import pytest
from conftest import validate_response, BASE_URL

import httpx


@pytest.fixture(scope="module")
def spec():
    import yaml
    from pathlib import Path
    with open(Path(__file__).parent.parent / "openapi.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


# --- Server endpoints ---

def test_server_info(api, spec):
    resp = api.get("/server/info")
    assert resp.status_code == 200
    data = resp.json()
    errors = validate_response(spec, "/server/info", data)
    assert not errors, f"Schema errors: {errors}"
    assert data["result"]["klippy_connected"] is True


def test_server_config(api, spec):
    resp = api.get("/server/config")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/config", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_temperature_store(api, spec):
    resp = api.get("/server/temperature_store")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/temperature_store", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_gcode_store(api, spec):
    resp = api.get("/server/gcode_store")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/gcode_store", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_announcements_list(api, spec):
    resp = api.get("/server/announcements/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/announcements/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_webcams_list(api, spec):
    resp = api.get("/server/webcams/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/webcams/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_database_list(api, spec):
    resp = api.get("/server/database/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/database/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_history_list(api, spec):
    resp = api.get("/server/history/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/history/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_history_totals(api, spec):
    resp = api.get("/server/history/totals")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/history/totals", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_job_queue_status(api, spec):
    resp = api.get("/server/job_queue/status")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/job_queue/status", resp.json())
    assert not errors, f"Schema errors: {errors}"


# --- Printer endpoints ---

def test_printer_info(api, spec):
    resp = api.get("/printer/info")
    assert resp.status_code == 200
    data = resp.json()
    errors = validate_response(spec, "/printer/info", data)
    assert not errors, f"Schema errors: {errors}"
    assert data["result"]["state"] in ("ready", "startup", "shutdown", "error")


def test_printer_objects_list(api, spec):
    resp = api.get("/printer/objects/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/objects/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_printer_gcode_help(api, spec):
    resp = api.get("/printer/gcode/help")
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/gcode/help", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_printer_query_endstops(api, spec):
    resp = api.get("/printer/query_endstops/status")
    assert resp.status_code == 200
    errors = validate_response(
        spec, "/printer/query_endstops/status", resp.json()
    )
    assert not errors, f"Schema errors: {errors}"


# --- Machine endpoints ---

def test_machine_system_info(api, spec):
    resp = api.get("/machine/system_info")
    assert resp.status_code == 200
    errors = validate_response(spec, "/machine/system_info", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_machine_proc_stats(api, spec):
    resp = api.get("/machine/proc_stats")
    assert resp.status_code == 200
    errors = validate_response(spec, "/machine/proc_stats", resp.json())
    assert not errors, f"Schema errors: {errors}"


# --- File endpoints ---

def test_server_files_list(api, spec):
    resp = api.get("/server/files/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/files/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_server_files_roots(api, spec):
    resp = api.get("/server/files/roots")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/files/roots", resp.json())
    assert not errors, f"Schema errors: {errors}"
