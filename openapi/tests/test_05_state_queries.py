"""Phase 6: State query & CRUD tests.

Tests temperature queries, object subscriptions, database CRUD,
job queue operations, gcode script, and announcements.
"""

import time
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


# --- Temperature & Object Queries ---

class TestTemperatureQueries:
    def test_temperature_store(self, api, spec):
        resp = api.get("/server/temperature_store")
        assert resp.status_code == 200
        data = resp.json()
        errors = validate_response(spec, "/server/temperature_store", data)
        assert not errors, f"Schema errors: {errors}"
        result = data["result"]
        assert "extruder" in result or "heater_bed" in result

    def test_object_query_heaters(self, api, spec):
        resp = api.get("/printer/objects/query",
                       params={"heater_bed": "", "extruder": ""})
        assert resp.status_code == 200
        errors = validate_response(spec, "/printer/objects/query", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_object_query_toolhead(self, api, spec):
        resp = api.get("/printer/objects/query",
                       params={"toolhead": ""})
        assert resp.status_code == 200
        errors = validate_response(spec, "/printer/objects/query", resp.json())
        assert not errors, f"Schema errors: {errors}"


# --- Database CRUD ---

class TestDatabaseCRUD:
    NAMESPACE = "openapi_test"
    KEY = "test_key"
    VALUE = {"greeting": "hello", "count": 42}

    def test_database_store(self, api, spec):
        resp = api.post("/server/database/item",
                        json={"namespace": self.NAMESPACE,
                              "key": self.KEY,
                              "value": self.VALUE})
        assert resp.status_code == 200, f"Store failed: {resp.text}"
        errors = validate_response(spec, "/server/database/item", resp.json(),
                                   method="post")
        assert not errors, f"Schema errors: {errors}"

    def test_database_retrieve(self, api, spec):
        resp = api.get("/server/database/item",
                       params={"namespace": self.NAMESPACE, "key": self.KEY})
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/database/item", resp.json())
        assert not errors, f"Schema errors: {errors}"
        result = resp.json()["result"]
        assert result["namespace"] == self.NAMESPACE
        assert result["value"] == self.VALUE

    def test_database_list_has_namespace(self, api, spec):
        resp = api.get("/server/database/list")
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/database/list", resp.json())
        assert not errors, f"Schema errors: {errors}"
        namespaces = resp.json()["result"]["namespaces"]
        assert self.NAMESPACE in namespaces

    def test_database_delete(self, api, spec):
        resp = api.delete("/server/database/item",
                          params={"namespace": self.NAMESPACE, "key": self.KEY})
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/database/item", resp.json(),
                                   method="delete")
        assert not errors, f"Schema errors: {errors}"


# --- Job Queue ---

class TestJobQueue:
    @pytest.fixture(autouse=True)
    def upload_file(self, api):
        with open(TEST_GCODE, "rb") as f:
            api.post("/server/files/upload",
                     files={"file": ("queue_test.gcode", f,
                                     "application/octet-stream")},
                     data={"root": "gcodes"})
        yield
        api.delete("/server/files/gcodes/queue_test.gcode")

    def test_job_queue_enqueue(self, api, spec):
        resp = api.post("/server/job_queue/job",
                        json={"filenames": ["queue_test.gcode"]})
        assert resp.status_code == 200, f"Enqueue failed: {resp.text}"
        errors = validate_response(spec, "/server/job_queue/job", resp.json(),
                                   method="post")
        assert not errors, f"Schema errors: {errors}"

    def test_job_queue_status(self, api, spec):
        resp = api.get("/server/job_queue/status")
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/job_queue/status", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_job_queue_delete(self, api, spec):
        # Get job IDs first
        status = api.get("/server/job_queue/status").json()
        job_ids = [j["job_id"] for j in status["result"]["queued_jobs"]]
        if job_ids:
            resp = api.delete("/server/job_queue/job",
                              params={"job_ids": ",".join(job_ids)})
            assert resp.status_code == 200
            errors = validate_response(spec, "/server/job_queue/job",
                                       resp.json(), method="delete")
            assert not errors, f"Schema errors: {errors}"


# --- GCode Script ---

class TestGcodeScript:
    def test_gcode_script_m115(self, api, spec):
        resp = api.post("/printer/gcode/script",
                        json={"script": "M115"})
        assert resp.status_code == 200
        errors = validate_response(spec, "/printer/gcode/script", resp.json(),
                                   method="post")
        assert not errors, f"Schema errors: {errors}"


# --- Announcements ---

class TestAnnouncements:
    def test_announcements_list(self, api, spec):
        resp = api.get("/server/announcements/list")
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/announcements/list", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_announcements_update(self, api, spec):
        resp = api.post("/server/announcements/update")
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/announcements/update",
                                   resp.json(), method="post")
        assert not errors, f"Schema errors: {errors}"
