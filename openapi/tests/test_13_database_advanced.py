"""Phase 7: Database advanced operation tests.

Tests backup, restore, and compact operations.
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
    api.delete("/server/database/item",
               params={"namespace": "openapi_backup_test", "key": "data"})


def test_health_check():
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


NAMESPACE = "openapi_backup_test"


def test_store_test_data(api, spec):
    resp = api.post("/server/database/item",
                    json={"namespace": NAMESPACE, "key": "data",
                          "value": {"test": True, "num": 42}})
    assert resp.status_code == 200
    errors = validate_response(spec, "/server/database/item", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_database_backup(api, spec):
    resp = api.post("/server/database/backup")
    assert resp.status_code == 200, f"Backup failed: {resp.text}"
    errors = validate_response(spec, "/server/database/backup", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"
    result = resp.json()["result"]
    assert "backup_path" in result
    # Store backup name for restore test
    import os
    test_database_backup.backup_name = os.path.basename(result["backup_path"])


def test_database_compact(api, spec):
    resp = api.post("/server/database/compact")
    assert resp.status_code == 200, f"Compact failed: {resp.text}"
    errors = validate_response(spec, "/server/database/compact", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_delete_test_data(api):
    resp = api.delete("/server/database/item",
                      params={"namespace": NAMESPACE, "key": "data"})
    assert resp.status_code == 200


def test_database_restore(api, spec):
    backup_name = getattr(test_database_backup, "backup_name", None)
    if not backup_name:
        pytest.skip("No backup name from backup test")
    resp = api.post("/server/database/restore",
                    params={"filename": backup_name})
    assert resp.status_code == 200, f"Restore failed: {resp.text}"
    errors = validate_response(spec, "/server/database/restore", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_data_restored(api):
    resp = api.get("/server/database/item",
                   params={"namespace": NAMESPACE, "key": "data"})
    assert resp.status_code == 200
    assert resp.json()["result"]["value"] == {"test": True, "num": 42}


def test_final_cleanup(api):
    api.delete("/server/database/item",
               params={"namespace": NAMESPACE, "key": "data"})
