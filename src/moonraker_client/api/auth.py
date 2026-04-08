"""API endpoints for Auth operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class AuthMixin:
    """Synchronous auth API methods."""

    def access_login(
        self, username: str, password: str, source: str = "Set by configuration"
    ) -> Any:
        """Login User

        Args:
            username: The user login name.
            password: The user password.
            source: A valid [authentication source](#auth-source-desc). (optional)

        JSON-RPC method: access.login
        """
        body: dict[str, Any] = {}
        body["username"] = username
        body["password"] = password
        if source is not None:
            body["source"] = source
        return self._request("POST", "/access/login", json=body)

    def access_logout(self) -> Any:
        """Logout Current User

        JSON-RPC method: access.logout
        """
        return self._request("POST", "/access/logout")

    def access_user(self) -> Any:
        """Get Current User

        JSON-RPC method: access.get_user
        """
        return self._request("GET", "/access/user")

    def access_users_list(self) -> Any:
        """List Available Users

        JSON-RPC method: access.users.list
        """
        return self._request("GET", "/access/users/list")

    def access_user_password(self, password: str, new_password: str) -> Any:
        """Reset User Password

        Args:
            password: The user's current password.
            new_password: The user's new password.

        JSON-RPC method: access.user.password
        """
        body: dict[str, Any] = {}
        body["password"] = password
        body["new_password"] = new_password
        return self._request("POST", "/access/user/password", json=body)

    def access_refreshjwt(self, refresh_token: str) -> Any:
        """Refresh JSON Web Token

        This endpoint can be used to refresh an expired access token.  If this
        request returns an error then the refresh token is no longer valid and
        the user must login with their credentials.

        **Note:** This endpoint may be accessed by unauthorized clients.  A 401 will
        only be returned if the refresh token is invalid.

        Args:
            refresh_token: A valid `refresh_token` for the user.

        JSON-RPC method: access.refresh_jwt
        """
        body: dict[str, Any] = {}
        body["refresh_token"] = refresh_token
        return self._request("POST", "/access/refresh_jwt", json=body)

    def access_oneshottoken(self) -> Any:
        """Generate a Oneshot Token

        Javascript is not capable of modifying the headers for some HTTP requests
        (for example, the `websocket`), which is a requirement to apply JWT or API Key
        authorization.  To work around this clients may request a Oneshot Token and
        pass it via the query string for these requests.  Tokens expire in 5 seconds
        and may only be used once, making them relatively safe for inclusion in the
        query string.

        JSON-RPC method: access.oneshot_token
        """
        return self._request("GET", "/access/oneshot_token")

    def access_info(self) -> Any:
        """Get authorization module info

        JSON-RPC method: access.info
        """
        return self._request("GET", "/access/info")

    def access_apikey(self) -> Any:
        """Get the Current API Key

        JSON-RPC method: access.get_api_key
        """
        return self._request("GET", "/access/api_key")


class AsyncAuthMixin:
    """Asynchronous auth API methods."""

    async def access_login(
        self, username: str, password: str, source: str = "Set by configuration"
    ) -> Any:
        """Login User

        Args:
            username: The user login name.
            password: The user password.
            source: A valid [authentication source](#auth-source-desc). (optional)

        JSON-RPC method: access.login
        """
        body: dict[str, Any] = {}
        body["username"] = username
        body["password"] = password
        if source is not None:
            body["source"] = source
        return await self._request("POST", "/access/login", json=body)

    async def access_logout(self) -> Any:
        """Logout Current User

        JSON-RPC method: access.logout
        """
        return await self._request("POST", "/access/logout")

    async def access_user(self) -> Any:
        """Get Current User

        JSON-RPC method: access.get_user
        """
        return await self._request("GET", "/access/user")

    async def access_users_list(self) -> Any:
        """List Available Users

        JSON-RPC method: access.users.list
        """
        return await self._request("GET", "/access/users/list")

    async def access_user_password(self, password: str, new_password: str) -> Any:
        """Reset User Password

        Args:
            password: The user's current password.
            new_password: The user's new password.

        JSON-RPC method: access.user.password
        """
        body: dict[str, Any] = {}
        body["password"] = password
        body["new_password"] = new_password
        return await self._request("POST", "/access/user/password", json=body)

    async def access_refreshjwt(self, refresh_token: str) -> Any:
        """Refresh JSON Web Token

        This endpoint can be used to refresh an expired access token.  If this
        request returns an error then the refresh token is no longer valid and
        the user must login with their credentials.

        **Note:** This endpoint may be accessed by unauthorized clients.  A 401 will
        only be returned if the refresh token is invalid.

        Args:
            refresh_token: A valid `refresh_token` for the user.

        JSON-RPC method: access.refresh_jwt
        """
        body: dict[str, Any] = {}
        body["refresh_token"] = refresh_token
        return await self._request("POST", "/access/refresh_jwt", json=body)

    async def access_oneshottoken(self) -> Any:
        """Generate a Oneshot Token

        Javascript is not capable of modifying the headers for some HTTP requests
        (for example, the `websocket`), which is a requirement to apply JWT or API Key
        authorization.  To work around this clients may request a Oneshot Token and
        pass it via the query string for these requests.  Tokens expire in 5 seconds
        and may only be used once, making them relatively safe for inclusion in the
        query string.

        JSON-RPC method: access.oneshot_token
        """
        return await self._request("GET", "/access/oneshot_token")

    async def access_info(self) -> Any:
        """Get authorization module info

        JSON-RPC method: access.info
        """
        return await self._request("GET", "/access/info")

    async def access_apikey(self) -> Any:
        """Get the Current API Key

        JSON-RPC method: access.get_api_key
        """
        return await self._request("GET", "/access/api_key")
