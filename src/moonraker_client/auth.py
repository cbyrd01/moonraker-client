"""Authentication handlers for Moonraker API.

Supports three auth schemes:
- API Key: X-Api-Key header
- Bearer JWT: Authorization: Bearer <token> header
- Oneshot Token: ?token=<token> query parameter
"""

from __future__ import annotations

import httpx


class ApiKeyAuth(httpx.Auth):
    """Authenticate requests using an API key in the X-Api-Key header."""

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def auth_flow(self, request: httpx.Request) -> httpx.Request:  # type: ignore[override]
        request.headers["X-Api-Key"] = self.api_key
        yield request


class BearerAuth(httpx.Auth):
    """Authenticate requests using a Bearer JWT token."""

    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: httpx.Request) -> httpx.Request:  # type: ignore[override]
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def build_auth(
    api_key: str | None = None,
    token: str | None = None,
) -> httpx.Auth | None:
    """Build the appropriate auth handler from provided credentials.

    Args:
        api_key: Moonraker API key for X-Api-Key header auth.
        token: JWT token for Bearer auth.

    Returns:
        An httpx.Auth instance, or None if no credentials provided.

    Raises:
        ValueError: If both api_key and token are provided.
    """
    if api_key and token:
        raise ValueError("Provide either api_key or token, not both")
    if api_key:
        return ApiKeyAuth(api_key)
    if token:
        return BearerAuth(token)
    return None
