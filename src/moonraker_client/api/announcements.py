"""API endpoints for Announcements operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class AnnouncementsMixin:
    """Synchronous announcements API methods."""

    def server_announcements_list(self, include_dismissed: bool = True) -> Any:
        """List announcements

        Retrieves a list of current announcements.

        Args:
            include_dismissed: When set to false dismissed entries will be excluded from the returned list of c (optional)

        JSON-RPC method: server.announcements.list
        """
        params: dict[str, Any] = {}
        if include_dismissed is not None:
            params["include_dismissed"] = include_dismissed
        return self._request("GET", "/server/announcements/list", params=params)

    def server_announcements_update(self) -> Any:
        """Update announcements

        Requests that Moonraker check for announcement updates.  This is generally
        not required in production, as Moonraker will automatically check for
        updates every 30 minutes.  However, during development this endpoint is
        useful to force an update when it is necessary to perform integration
        tests.

        JSON-RPC method: server.announcements.update
        """
        return self._request("POST", "/server/announcements/update")

    def server_announcements_dismiss(self, entry_id: str, wake_time: float | None = None) -> Any:
        """Dismiss an announcement

        Sets the dismiss flag of an announcement to `true`.
        
        **Note:** The `entry_id` typically contains forward slashes. Remember to escape this value
        if including it in the query string of an HTTP request.

        Args:
            entry_id: The entry ID of the announcement to dismiss.
            wake_time: A time, in seconds, after which the entry's `dismiss` flag will revert to `true` (optional)

        JSON-RPC method: server.announcements.dismiss
        """
        body: dict[str, Any] = {}
        body["entry_id"] = entry_id
        if wake_time is not None:
            body["wake_time"] = wake_time
        return self._request("POST", "/server/announcements/dismiss", json=body)

    def server_announcements_feeds(self) -> Any:
        """List announcement feeds

        JSON-RPC method: server.announcements.feeds
        """
        return self._request("GET", "/server/announcements/feeds")

    def server_announcements_feed(self, name: str) -> Any:
        """Subscribe to an announcement feed

        Subscribes Moonraker to the announcement feed specified in the request.

        Args:
            name: The name of the announcement feed to subscribe to.

        JSON-RPC method: server.announcements.post_feed
        """
        body: dict[str, Any] = {}
        body["name"] = name
        return self._request("POST", "/server/announcements/feed", json=body)


class AsyncAnnouncementsMixin:
    """Asynchronous announcements API methods."""

    async def server_announcements_list(self, include_dismissed: bool = True) -> Any:
        """List announcements

        Retrieves a list of current announcements.

        Args:
            include_dismissed: When set to false dismissed entries will be excluded from the returned list of c (optional)

        JSON-RPC method: server.announcements.list
        """
        params: dict[str, Any] = {}
        if include_dismissed is not None:
            params["include_dismissed"] = include_dismissed
        return await self._request("GET", "/server/announcements/list", params=params)

    async def server_announcements_update(self) -> Any:
        """Update announcements

        Requests that Moonraker check for announcement updates.  This is generally
        not required in production, as Moonraker will automatically check for
        updates every 30 minutes.  However, during development this endpoint is
        useful to force an update when it is necessary to perform integration
        tests.

        JSON-RPC method: server.announcements.update
        """
        return await self._request("POST", "/server/announcements/update")

    async def server_announcements_dismiss(self, entry_id: str, wake_time: float | None = None) -> Any:
        """Dismiss an announcement

        Sets the dismiss flag of an announcement to `true`.
        
        **Note:** The `entry_id` typically contains forward slashes. Remember to escape this value
        if including it in the query string of an HTTP request.

        Args:
            entry_id: The entry ID of the announcement to dismiss.
            wake_time: A time, in seconds, after which the entry's `dismiss` flag will revert to `true` (optional)

        JSON-RPC method: server.announcements.dismiss
        """
        body: dict[str, Any] = {}
        body["entry_id"] = entry_id
        if wake_time is not None:
            body["wake_time"] = wake_time
        return await self._request("POST", "/server/announcements/dismiss", json=body)

    async def server_announcements_feeds(self) -> Any:
        """List announcement feeds

        JSON-RPC method: server.announcements.feeds
        """
        return await self._request("GET", "/server/announcements/feeds")

    async def server_announcements_feed(self, name: str) -> Any:
        """Subscribe to an announcement feed

        Subscribes Moonraker to the announcement feed specified in the request.

        Args:
            name: The name of the announcement feed to subscribe to.

        JSON-RPC method: server.announcements.post_feed
        """
        body: dict[str, Any] = {}
        body["name"] = name
        return await self._request("POST", "/server/announcements/feed", json=body)
