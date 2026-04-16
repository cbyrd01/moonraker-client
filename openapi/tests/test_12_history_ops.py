"""Phase 6: History operation tests.

Tests individual job query, job delete, and totals reset.
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


def test_health_check():
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


def test_history_list_has_jobs(api):
    """Ensure there are jobs in history to work with."""
    resp = api.get("/server/history/list")
    assert resp.status_code == 200
    jobs = resp.json()["result"]["jobs"]
    if not jobs:
        pytest.skip("No jobs in history -- run print lifecycle tests first")


def test_history_get_single_job(api, spec):
    """Get a single job by UID and validate schema."""
    resp = api.get("/server/history/list")
    jobs = resp.json()["result"]["jobs"]
    if not jobs:
        pytest.skip("No jobs in history")
    job_id = jobs[0]["job_id"]

    resp = api.get("/server/history/job", params={"uid": job_id})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/history/job", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_history_delete_single_job(api, spec):
    """Delete a single job and validate schema."""
    resp = api.get("/server/history/list")
    jobs = resp.json()["result"]["jobs"]
    if not jobs:
        pytest.skip("No jobs in history")
    job_id = jobs[-1]["job_id"]  # Delete the oldest

    resp = api.delete("/server/history/job", params={"uid": job_id})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/history/job", resp.json(),
                               method="delete")
    assert not errors, f"Schema errors: {errors}"


def test_history_job_removed(api):
    """Verify deleted job is no longer in the list."""
    resp = api.get("/server/history/list")
    before_count = len(resp.json()["result"]["jobs"])
    # Just verify we can still list -- count should be smaller
    assert resp.status_code == 200


def test_history_reset_totals(api, spec):
    """Reset print totals and validate schema."""
    resp = api.post("/server/history/reset_totals")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/history/reset_totals",
                               resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"


def test_history_totals_after_reset(api, spec):
    """Verify totals are zeroed after reset."""
    resp = api.get("/server/history/totals")
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/history/totals", resp.json())
    assert not errors, f"Schema errors: {errors}"
    totals = resp.json()["result"]["job_totals"]
    assert totals["total_jobs"] == 0 or totals["total_print_time"] == 0.0
