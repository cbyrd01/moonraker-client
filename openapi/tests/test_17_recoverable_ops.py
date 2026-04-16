"""Phase 11: Recoverable destructive operations -- RUN LAST.

Tests endpoints that modify printer state but are recoverable.
Each test waits for the printer to return to a healthy state.
"""

import time
from pathlib import Path

import httpx
import pytest
from conftest import validate_response, check_printer_health, wait_for_ready, BASE_URL

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


def test_health_check_before_destructive():
    state = check_printer_health()
    assert state == "ready", f"Printer must be ready before destructive tests: {state}"


def test_emergency_stop(api, spec):
    """Send emergency stop and validate response schema."""
    resp = api.post("/printer/emergency_stop")
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/emergency_stop", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_recover_from_estop(api):
    """Firmware restart to recover from emergency stop."""
    time.sleep(2)
    resp = api.post("/printer/firmware_restart")
    assert resp.status_code == 200
    time.sleep(10)
    state = wait_for_ready(timeout=30)
    assert state == "ready", f"Printer did not recover: {state}"


def test_firmware_restart(api, spec):
    """Firmware restart and validate response."""
    resp = api.post("/printer/firmware_restart")
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/firmware_restart", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"
    time.sleep(10)
    state = wait_for_ready(timeout=30)
    assert state == "ready", f"Printer did not recover: {state}"


def test_klipper_restart(api, spec):
    """Restart Klipper host software."""
    resp = api.post("/printer/restart")
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/restart", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"
    time.sleep(10)
    state = wait_for_ready(timeout=30)
    assert state == "ready", f"Printer did not recover: {state}"


def test_printer_healthy_after_all(api, spec):
    """Final verification that printer is fully operational."""
    resp = api.get("/printer/info")
    assert resp.status_code == 200
    errors = validate_response(spec, "/printer/info", resp.json())
    assert not errors, f"Schema errors: {errors}"
    assert resp.json()["result"]["state"] == "ready"

    resp = api.get("/server/info")
    assert resp.status_code == 200
    assert resp.json()["result"]["klippy_connected"] is True
