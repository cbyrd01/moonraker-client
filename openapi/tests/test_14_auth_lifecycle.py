"""Phase 8: Authorization lifecycle tests.

Full auth CRUD: user creation, login, JWT refresh, password change, logout, deletion.
Virtual printer has login_required=false and trusted=true.
"""

from pathlib import Path

import httpx
import pytest
from conftest import validate_response, check_printer_health, BASE_URL

TEST_USER = "openapi_test_user"
TEST_PASS = "testpass123"
NEW_PASS = "newpass456"


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
    # Pre-clean: remove user if left over from prior run
    api.request("DELETE", "/access/user",
                json={"username": TEST_USER})
    yield
    # Post-clean
    api.request("DELETE", "/access/user",
                json={"username": TEST_USER})


def test_health_check():
    """Wait for API to be available (may restart after database restore)."""
    from conftest import wait_for_ready
    import time
    time.sleep(2)  # Brief pause in case Moonraker is restarting
    try:
        state = check_printer_health()
    except Exception:
        # Server may be restarting -- wait longer
        time.sleep(10)
        state = wait_for_ready()
    assert state in ("ready", "startup", "error"), f"Printer not reachable: {state}"


def test_access_info(api, spec):
    resp = api.get("/access/info")
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/info", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_get_api_key(api, spec):
    resp = api.get("/access/api_key")
    assert resp.status_code == 200


def test_generate_new_api_key(api, spec):
    resp = api.post("/access/api_key")
    assert resp.status_code == 200
    data = resp.json()
    # Returns {"result": "<new_api_key_string>"}
    assert "result" in data
    assert isinstance(data["result"], str)
    assert len(data["result"]) > 10


def test_oneshot_token(api, spec):
    resp = api.get("/access/oneshot_token")
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/oneshot_token", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_current_user(api, spec):
    resp = api.get("/access/user")
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/user", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_users_list(api, spec):
    resp = api.get("/access/users/list")
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/users/list", resp.json())
    assert not errors, f"Schema errors: {errors}"


def test_create_user(api, spec):
    resp = api.post("/access/user",
                    json={"username": TEST_USER, "password": TEST_PASS})
    assert resp.status_code == 200, f"Create user failed: {resp.text}"
    errors = validate_response(spec, "/access/user", resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"


def test_login(api, spec):
    resp = api.post("/access/login",
                    json={"username": TEST_USER, "password": TEST_PASS,
                          "source": "moonraker"})
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    errors = validate_response(spec, "/access/login", resp.json(), method="post")
    assert not errors, f"Schema errors: {errors}"
    result = resp.json()["result"]
    assert "token" in result
    assert "refresh_token" in result
    # Store tokens for subsequent tests
    test_login.token = result["token"]
    test_login.refresh_token = result["refresh_token"]


def test_refresh_jwt(api, spec):
    token = getattr(test_login, "refresh_token", None)
    if not token:
        pytest.skip("No refresh token -- trusted mode doesn't issue tokens")
    resp = api.post("/access/refresh_jwt",
                    json={"refresh_token": token})
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/refresh_jwt", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_change_password(api, spec):
    token = getattr(test_login, "token", None)
    if not token:
        pytest.skip("No JWT token -- trusted mode doesn't issue tokens")
    resp = api.post("/access/user/password",
                    json={"password": TEST_PASS, "new_password": NEW_PASS},
                    headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/user/password", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_logout(api, spec):
    token = getattr(test_login, "token", None)
    if not token:
        pytest.skip("No JWT token -- trusted mode doesn't issue tokens")
    resp = api.post("/access/logout",
                    headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/logout", resp.json(),
                               method="post")
    assert not errors, f"Schema errors: {errors}"


def test_delete_user(api, spec):
    resp = api.request("DELETE", "/access/user",
                       json={"username": TEST_USER})
    assert resp.status_code == 200
    errors = validate_response(spec, "/access/user", resp.json(),
                               method="delete")
    assert not errors, f"Schema errors: {errors}"


def test_user_gone(api):
    resp = api.get("/access/users/list")
    users = [u["username"] for u in resp.json()["result"]["users"]]
    assert TEST_USER not in users
