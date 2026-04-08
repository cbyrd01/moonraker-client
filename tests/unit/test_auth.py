"""Unit tests for authentication handlers."""

from __future__ import annotations

import pytest
from pytest_httpx import HTTPXMock

from moonraker_client import MoonrakerClient
from moonraker_client.auth import ApiKeyAuth, BearerAuth, build_auth


class TestBuildAuth:
    """Tests for the build_auth factory function."""

    def test_returns_none_when_no_credentials(self) -> None:
        assert build_auth() is None

    def test_returns_api_key_auth(self) -> None:
        auth = build_auth(api_key="test-key")
        assert isinstance(auth, ApiKeyAuth)
        assert auth.api_key == "test-key"

    def test_returns_bearer_auth(self) -> None:
        auth = build_auth(token="jwt-token")
        assert isinstance(auth, BearerAuth)
        assert auth.token == "jwt-token"

    def test_raises_on_both_credentials(self) -> None:
        with pytest.raises(ValueError, match="Provide either"):
            build_auth(api_key="key", token="token")


class TestApiKeyAuth:
    """Tests for API key authentication."""

    def test_sends_api_key_header(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125", api_key="test-api-key") as client:
            client.printer_info()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["X-Api-Key"] == "test-api-key"


class TestBearerAuth:
    """Tests for Bearer JWT authentication."""

    def test_sends_bearer_header(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125", token="my-jwt") as client:
            client.printer_info()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.headers["Authorization"] == "Bearer my-jwt"


class TestNoAuth:
    """Tests for unauthenticated requests."""

    def test_no_auth_headers(self, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(json={"result": "ok"})
        with MoonrakerClient("http://localhost:7125") as client:
            client.printer_info()
        request = httpx_mock.get_request()
        assert request is not None
        assert "X-Api-Key" not in request.headers
        assert "Authorization" not in request.headers
