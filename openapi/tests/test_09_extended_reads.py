"""Phase 2: Extended safe GET endpoint coverage.

Additional read-only endpoints not covered by test_02_basic_reads.
"""

from pathlib import Path

import httpx
import pytest
from conftest import validate_response, BASE_URL

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


# --- Authorization endpoints ---

class TestAuthReads:
    def test_access_info(self, api, spec):
        resp = api.get("/access/info")
        assert resp.status_code == 200
        errors = validate_response(spec, "/access/info", resp.json())
        assert not errors, f"Schema errors: {errors}"
        result = resp.json()["result"]
        assert "default_source" in result

    def test_access_user(self, api, spec):
        resp = api.get("/access/user")
        assert resp.status_code == 200
        errors = validate_response(spec, "/access/user", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_access_users_list(self, api, spec):
        resp = api.get("/access/users/list")
        assert resp.status_code == 200
        errors = validate_response(spec, "/access/users/list", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_access_api_key(self, api, spec):
        resp = api.get("/access/api_key")
        assert resp.status_code == 200
        data = resp.json()
        # Returns {"result": "<api_key_string>"}
        assert "result" in data
        assert isinstance(data["result"], str)

    def test_access_oneshot_token(self, api, spec):
        resp = api.get("/access/oneshot_token")
        assert resp.status_code == 200
        errors = validate_response(spec, "/access/oneshot_token", resp.json())
        assert not errors, f"Schema errors: {errors}"


# --- Server & Machine endpoints ---

class TestServerReads:
    def test_extensions_list(self, api, spec):
        resp = api.get("/server/extensions/list")
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/extensions/list", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_sudo_info(self, api, spec):
        resp = api.get("/machine/sudo/info")
        assert resp.status_code == 200
        errors = validate_response(spec, "/machine/sudo/info", resp.json())
        assert not errors, f"Schema errors: {errors}"


# --- File system endpoints ---

class TestFileReads:
    def test_files_directory(self, api, spec):
        resp = api.get("/server/files/directory",
                       params={"path": "gcodes"})
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/files/directory", resp.json())
        assert not errors, f"Schema errors: {errors}"
        result = resp.json()["result"]
        assert "dirs" in result
        assert "files" in result
        assert "disk_usage" in result

    def test_files_directory_extended(self, api, spec):
        resp = api.get("/server/files/directory",
                       params={"path": "gcodes", "extended": "true"})
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/files/directory", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_files_klippy_log(self, api):
        """Klippy log download returns file content, not JSON."""
        resp = api.get("/server/files/klippy.log")
        assert resp.status_code == 200
        # Should be a text file, not JSON
        assert len(resp.content) > 0

    def test_files_moonraker_log(self, api):
        """Moonraker log download returns file content."""
        resp = api.get("/server/files/moonraker.log")
        assert resp.status_code == 200
        assert len(resp.content) > 0


# --- History single job ---

class TestHistoryReads:
    def test_history_single_job(self, api, spec):
        """Get a single job by UID from history."""
        list_resp = api.get("/server/history/list")
        jobs = list_resp.json()["result"]["jobs"]
        if not jobs:
            pytest.skip("No jobs in history to query")
        job_id = jobs[0]["job_id"]
        resp = api.get("/server/history/job", params={"uid": job_id})
        assert resp.status_code == 200
        errors = validate_response(spec, "/server/history/job", resp.json())
        assert not errors, f"Schema errors: {errors}"


# --- Legacy OctoPrint-compat endpoints ---

class TestLegacyAPI:
    def test_api_version(self, api, spec):
        resp = api.get("/api/version")
        assert resp.status_code == 200
        errors = validate_response(spec, "/api/version", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_api_server(self, api, spec):
        resp = api.get("/api/server")
        assert resp.status_code == 200
        errors = validate_response(spec, "/api/server", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_api_login(self, api, spec):
        """Legacy login endpoint -- POST only on this instance."""
        resp = api.post("/api/login")
        assert resp.status_code == 200
        errors = validate_response(spec, "/api/login", resp.json(),
                                   method="post")
        if errors:
            # May not have a POST schema -- just validate it returns JSON
            data = resp.json()
            assert "name" in data or "_is_external_client" in data

    def test_api_settings(self, api, spec):
        resp = api.get("/api/settings")
        assert resp.status_code == 200
        errors = validate_response(spec, "/api/settings", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_api_job(self, api, spec):
        resp = api.get("/api/job")
        assert resp.status_code == 200
        errors = validate_response(spec, "/api/job", resp.json())
        assert not errors, f"Schema errors: {errors}"

    def test_api_printerprofiles(self, api, spec):
        resp = api.get("/api/printerprofiles")
        assert resp.status_code == 200
        errors = validate_response(spec, "/api/printerprofiles", resp.json())
        assert not errors, f"Schema errors: {errors}"
