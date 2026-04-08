"""API endpoints for Webcams operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class WebcamsMixin:
    """Synchronous webcams API methods."""

    def server_webcams_list(self) -> Any:
        """List Webcams

        JSON-RPC method: server.webcams.list
        """
        return self._request("GET", "/server/webcams/list")

    def server_webcams_item(self, uid: str, name: str = '**DEPRECATED**') -> Any:
        """Get Webcam Information

        Args:
            uid: The requested webcam's unique ID. While this parameter is considered required, i
            name: The requested webcam's friendly name. This parameter is deprecated, all future i (optional)

        JSON-RPC method: server.webcams.get_item
        """
        params: dict[str, Any] = {}
        params["uid"] = uid
        if name is not None:
            params["name"] = name
        return self._request("GET", "/server/webcams/item", params=params)

    def server_webcams_test(self, uid: str, name: str = '**DEPRECATED**') -> Any:
        """Test a webcam

        Resolves a webcam's stream and snapshot urls.  If the snapshot
        is served over http, a test is performed to see if the url is
        reachable.

        Args:
            uid: The requested webcam's unique ID. While this parameter is considered required, i
            name: The requested webcam's friendly name. This parameter is deprecated, all future i (optional)

        JSON-RPC method: server.webcams.test
        """
        body: dict[str, Any] = {}
        body["uid"] = uid
        if name is not None:
            body["name"] = name
        return self._request("POST", "/server/webcams/test", json=body)


class AsyncWebcamsMixin:
    """Asynchronous webcams API methods."""

    async def server_webcams_list(self) -> Any:
        """List Webcams

        JSON-RPC method: server.webcams.list
        """
        return await self._request("GET", "/server/webcams/list")

    async def server_webcams_item(self, uid: str, name: str = '**DEPRECATED**') -> Any:
        """Get Webcam Information

        Args:
            uid: The requested webcam's unique ID. While this parameter is considered required, i
            name: The requested webcam's friendly name. This parameter is deprecated, all future i (optional)

        JSON-RPC method: server.webcams.get_item
        """
        params: dict[str, Any] = {}
        params["uid"] = uid
        if name is not None:
            params["name"] = name
        return await self._request("GET", "/server/webcams/item", params=params)

    async def server_webcams_test(self, uid: str, name: str = '**DEPRECATED**') -> Any:
        """Test a webcam

        Resolves a webcam's stream and snapshot urls.  If the snapshot
        is served over http, a test is performed to see if the url is
        reachable.

        Args:
            uid: The requested webcam's unique ID. While this parameter is considered required, i
            name: The requested webcam's friendly name. This parameter is deprecated, all future i (optional)

        JSON-RPC method: server.webcams.test
        """
        body: dict[str, Any] = {}
        body["uid"] = uid
        if name is not None:
            body["name"] = name
        return await self._request("POST", "/server/webcams/test", json=body)
