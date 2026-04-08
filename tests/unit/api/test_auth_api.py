"""Unit tests for auth API endpoints."""

from __future__ import annotations

import json

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import AsyncMoonrakerClient, MoonrakerClient


class TestAuthMixin:
    def test_login(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "username": "testuser",
                    "token": "jwt-token-here",
                    "refresh_token": "refresh-token-here",
                    "action": "user_logged_in",
                }
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_login("testuser", "password123")
        assert result["username"] == "testuser"
        assert "token" in result

        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["username"] == "testuser"
        assert body["password"] == "password123"

    def test_logout(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={"result": {"username": "testuser", "action": "user_logged_out"}}
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_logout()
        assert result["action"] == "user_logged_out"

    def test_get_user(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={"result": {"username": "testuser", "created_on": 1700000000.0}}
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_user()
        assert result["username"] == "testuser"

    def test_list_users(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"users": [{"username": "admin"}]}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_users_list()
        assert "users" in result

    def test_refresh_jwt(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            json={
                "result": {
                    "username": "testuser",
                    "token": "new-jwt-token",
                    "action": "user_jwt_refresh",
                }
            }
        )
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_refreshjwt("old-refresh-token")
        assert "token" in result

    def test_oneshot_token(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "oneshot-token-abc123"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_oneshottoken()
        assert result == "oneshot-token-abc123"

    def test_get_api_key(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ABCDEF1234567890"})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_apikey()
        assert result == "ABCDEF1234567890"

    def test_auth_info(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"default_source": "moonraker"}})
        with MoonrakerClient("http://localhost:7125") as client:
            result = client.access_info()
        assert "default_source" in result


class TestAsyncAuthMixin:
    @pytest.mark.asyncio
    async def test_login(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": {"username": "test", "token": "jwt"}})
        async with AsyncMoonrakerClient("http://localhost:7125") as client:
            result = await client.access_login("test", "pass")
        assert result["username"] == "test"
