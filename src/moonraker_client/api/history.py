"""API endpoints for History operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class HistoryMixin:
    """Synchronous history API methods."""

    def server_history_list(self, limit: int = 50, start: int = 0, before: float | None = None, since: float | None = None, order: str = 'desc') -> Any:
        """Get job list

        Args:
            limit: Maximum number of job entries to return. (optional)
            start: The record number indicating the first entry of the returned list. (optional)
            before: A timestamp in unix time. When specified, the returned list will only contain en (optional)
            since: A timestamp in unix time. When specified, the returned list will only contain en (optional)
            order: The order of the list returned.  May be `asc` (ascending) or `desc` (descending) (optional)

        JSON-RPC method: server.history.list
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if start is not None:
            params["start"] = start
        if before is not None:
            params["before"] = before
        if since is not None:
            params["since"] = since
        if order is not None:
            params["order"] = order
        return self._request("GET", "/server/history/list", params=params)

    def server_history_totals(self) -> Any:
        """Get job totals

        JSON-RPC method: server.history.totals
        """
        return self._request("GET", "/server/history/totals")

    def server_history_resettotals(self) -> Any:
        """Reset totals

        Resets the persistent "job totals" to zero.

        JSON-RPC method: server.history.reset_totals
        """
        return self._request("POST", "/server/history/reset_totals")

    def server_history_job(self, uid: str) -> Any:
        """Get a single job

        Args:
            uid: The unique identifier for the requested job history.

        JSON-RPC method: server.history.get_job
        """
        params: dict[str, Any] = {}
        params["uid"] = uid
        return self._request("GET", "/server/history/job", params=params)


class AsyncHistoryMixin:
    """Asynchronous history API methods."""

    async def server_history_list(self, limit: int = 50, start: int = 0, before: float | None = None, since: float | None = None, order: str = 'desc') -> Any:
        """Get job list

        Args:
            limit: Maximum number of job entries to return. (optional)
            start: The record number indicating the first entry of the returned list. (optional)
            before: A timestamp in unix time. When specified, the returned list will only contain en (optional)
            since: A timestamp in unix time. When specified, the returned list will only contain en (optional)
            order: The order of the list returned.  May be `asc` (ascending) or `desc` (descending) (optional)

        JSON-RPC method: server.history.list
        """
        params: dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if start is not None:
            params["start"] = start
        if before is not None:
            params["before"] = before
        if since is not None:
            params["since"] = since
        if order is not None:
            params["order"] = order
        return await self._request("GET", "/server/history/list", params=params)

    async def server_history_totals(self) -> Any:
        """Get job totals

        JSON-RPC method: server.history.totals
        """
        return await self._request("GET", "/server/history/totals")

    async def server_history_resettotals(self) -> Any:
        """Reset totals

        Resets the persistent "job totals" to zero.

        JSON-RPC method: server.history.reset_totals
        """
        return await self._request("POST", "/server/history/reset_totals")

    async def server_history_job(self, uid: str) -> Any:
        """Get a single job

        Args:
            uid: The unique identifier for the requested job history.

        JSON-RPC method: server.history.get_job
        """
        params: dict[str, Any] = {}
        params["uid"] = uid
        return await self._request("GET", "/server/history/job", params=params)
