"""API endpoints for Server operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class ServerMixin:
    """Synchronous server API methods."""

    def server_info(self) -> Any:
        """Query Server Info

        JSON-RPC method: server.info
        """
        return self._request("GET", "/server/info")

    def server_config(self) -> Any:
        """Get Server Configuration

        JSON-RPC method: server.config
        """
        return self._request("GET", "/server/config")

    def server_temperaturestore(self, include_monitors: bool = False) -> Any:
        """Request Cached Temperature Data

        Args:
            include_monitors: When set to `true` the response will include sensors reported as `temperature mo (optional)

        JSON-RPC method: server.temperature_store
        """
        params: dict[str, Any] = {}
        if include_monitors is not None:
            params["include_monitors"] = include_monitors
        return self._request("GET", "/server/temperature_store", params=params)

    def server_gcodestore(self, count: int | None = None) -> Any:
        """Request Cached GCode Responses

        Args:
            count: The number of cached gcode responses to return. The default is to return all cac (optional)

        JSON-RPC method: server.gcode_store
        """
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = count
        return self._request("GET", "/server/gcode_store", params=params)

    def server_logs_rollover(self, application: str = '*all*') -> Any:
        """Rollover Logs

        Requests a manual rollover for log files registered with Moonraker's
        log management facility.  Currently these are limited to `moonraker.log`
        and `klippy.log`.
        
        **Note:** Moonraker must be able to manage Klipper's systemd service to
        perform a manual rollover.  The rollover will fail under the following
        conditions:
        
        - Moonraker cannot detect Klipper's systemd unit
        - Moonraker cannot detect the location of Klipper's files
        - A print is in progress

        Args:
            application: The name of the application for which the log should be rolled over.  Can be `mo (optional)

        JSON-RPC method: server.logs.rollover
        """
        body: dict[str, Any] = {}
        if application is not None:
            body["application"] = application
        return self._request("POST", "/server/logs/rollover", json=body)

    def server_restart(self) -> Any:
        """Restart Server

        JSON-RPC method: server.restart
        """
        return self._request("POST", "/server/restart")

    def server_connection_identify(self, client_name: str, version: str, type: str, url: str, access_token: str | None = None, api_key: str | None = None) -> Any:
        """Identify Connection

        This method provides a way for applications with persistent connections
        to identify themselves to Moonraker.  This information may be used by
        Moonraker perform an action or present information based on if a specific
        type of frontend is connected.  Currently this method is only available
        to websocket and unix socket connections.  Once this endpoint returns
        success it cannot be called again, repeated calls will result in an error.
        
        **Note:** When identifying as an `agent`, only one instance should be connected
        to Moonraker at a time.  If multiple agents of the same `client_name`
        attempt to identify themselves this endpoint will return an error.
        See the [extensions](./extensions.md) document for more information about
        `agents`.
        
        **Note:** See the authorization API documentation for details on JWT and API Key authentication.
        
        *Transport: JSON-RPC request (Websocket/Unix Socket Only)*

        Args:
            client_name: The name of the application identifying itself, ie: `Mainsail`, `Fluidd`, `Klipp
            version: The version of the application identifying itself.
            type: The type of the application.  Expand for available values.
            url: The project URL or homepage for the application.
            access_token: An optional JSON Web Token used to authenticate the websocket connection.  Only  (optional)
            api_key: An optional API Key used to authenticate the connection.  Only needed when the A (optional)

        JSON-RPC method: server.connection.identify
        """
        body: dict[str, Any] = {}
        body["client_name"] = client_name
        body["version"] = version
        body["type"] = type
        body["url"] = url
        if access_token is not None:
            body["access_token"] = access_token
        if api_key is not None:
            body["api_key"] = api_key
        return self._request("POST", "/server/connection/identify", json=body)

    def server_websocket_id(self) -> Any:
        """Get Websocket ID

        !!! Warning
            This method is deprecated.  Please use the
            [identify endpoint](#identify-connection) to retrieve the
            Websocket's UID
        
        *Transport: JSON-RPC request (Websocket/Unix Socket Only)*

        JSON-RPC method: server.websocket.id
        """
        return self._request("POST", "/server/websocket/id")

    def server_jsonrpc(self, jsonrpc: str, method: str, id: int, params: dict[str, Any] | None = None) -> Any:
        """JSON-RPC over HTTP

        Exposes the JSON-RPC interface over HTTP. Most JSON-RPC methods with corresponding HTTP APIs are available. Methods exclusive to other transports, such as Identify Connection, are not available.

        Args:
            jsonrpc: 
            method: The JSON-RPC method name
            params: Method parameters (optional)
            id: Request identifier
        """
        body: dict[str, Any] = {}
        body["jsonrpc"] = jsonrpc
        body["method"] = method
        if params is not None:
            body["params"] = params
        body["id"] = id
        return self._request("POST", "/server/jsonrpc", json=body)


class AsyncServerMixin:
    """Asynchronous server API methods."""

    async def server_info(self) -> Any:
        """Query Server Info

        JSON-RPC method: server.info
        """
        return await self._request("GET", "/server/info")

    async def server_config(self) -> Any:
        """Get Server Configuration

        JSON-RPC method: server.config
        """
        return await self._request("GET", "/server/config")

    async def server_temperaturestore(self, include_monitors: bool = False) -> Any:
        """Request Cached Temperature Data

        Args:
            include_monitors: When set to `true` the response will include sensors reported as `temperature mo (optional)

        JSON-RPC method: server.temperature_store
        """
        params: dict[str, Any] = {}
        if include_monitors is not None:
            params["include_monitors"] = include_monitors
        return await self._request("GET", "/server/temperature_store", params=params)

    async def server_gcodestore(self, count: int | None = None) -> Any:
        """Request Cached GCode Responses

        Args:
            count: The number of cached gcode responses to return. The default is to return all cac (optional)

        JSON-RPC method: server.gcode_store
        """
        params: dict[str, Any] = {}
        if count is not None:
            params["count"] = count
        return await self._request("GET", "/server/gcode_store", params=params)

    async def server_logs_rollover(self, application: str = '*all*') -> Any:
        """Rollover Logs

        Requests a manual rollover for log files registered with Moonraker's
        log management facility.  Currently these are limited to `moonraker.log`
        and `klippy.log`.
        
        **Note:** Moonraker must be able to manage Klipper's systemd service to
        perform a manual rollover.  The rollover will fail under the following
        conditions:
        
        - Moonraker cannot detect Klipper's systemd unit
        - Moonraker cannot detect the location of Klipper's files
        - A print is in progress

        Args:
            application: The name of the application for which the log should be rolled over.  Can be `mo (optional)

        JSON-RPC method: server.logs.rollover
        """
        body: dict[str, Any] = {}
        if application is not None:
            body["application"] = application
        return await self._request("POST", "/server/logs/rollover", json=body)

    async def server_restart(self) -> Any:
        """Restart Server

        JSON-RPC method: server.restart
        """
        return await self._request("POST", "/server/restart")

    async def server_connection_identify(self, client_name: str, version: str, type: str, url: str, access_token: str | None = None, api_key: str | None = None) -> Any:
        """Identify Connection

        This method provides a way for applications with persistent connections
        to identify themselves to Moonraker.  This information may be used by
        Moonraker perform an action or present information based on if a specific
        type of frontend is connected.  Currently this method is only available
        to websocket and unix socket connections.  Once this endpoint returns
        success it cannot be called again, repeated calls will result in an error.
        
        **Note:** When identifying as an `agent`, only one instance should be connected
        to Moonraker at a time.  If multiple agents of the same `client_name`
        attempt to identify themselves this endpoint will return an error.
        See the [extensions](./extensions.md) document for more information about
        `agents`.
        
        **Note:** See the authorization API documentation for details on JWT and API Key authentication.
        
        *Transport: JSON-RPC request (Websocket/Unix Socket Only)*

        Args:
            client_name: The name of the application identifying itself, ie: `Mainsail`, `Fluidd`, `Klipp
            version: The version of the application identifying itself.
            type: The type of the application.  Expand for available values.
            url: The project URL or homepage for the application.
            access_token: An optional JSON Web Token used to authenticate the websocket connection.  Only  (optional)
            api_key: An optional API Key used to authenticate the connection.  Only needed when the A (optional)

        JSON-RPC method: server.connection.identify
        """
        body: dict[str, Any] = {}
        body["client_name"] = client_name
        body["version"] = version
        body["type"] = type
        body["url"] = url
        if access_token is not None:
            body["access_token"] = access_token
        if api_key is not None:
            body["api_key"] = api_key
        return await self._request("POST", "/server/connection/identify", json=body)

    async def server_websocket_id(self) -> Any:
        """Get Websocket ID

        !!! Warning
            This method is deprecated.  Please use the
            [identify endpoint](#identify-connection) to retrieve the
            Websocket's UID
        
        *Transport: JSON-RPC request (Websocket/Unix Socket Only)*

        JSON-RPC method: server.websocket.id
        """
        return await self._request("POST", "/server/websocket/id")

    async def server_jsonrpc(self, jsonrpc: str, method: str, id: int, params: dict[str, Any] | None = None) -> Any:
        """JSON-RPC over HTTP

        Exposes the JSON-RPC interface over HTTP. Most JSON-RPC methods with corresponding HTTP APIs are available. Methods exclusive to other transports, such as Identify Connection, are not available.

        Args:
            jsonrpc: 
            method: The JSON-RPC method name
            params: Method parameters (optional)
            id: Request identifier
        """
        body: dict[str, Any] = {}
        body["jsonrpc"] = jsonrpc
        body["method"] = method
        if params is not None:
            body["params"] = params
        body["id"] = id
        return await self._request("POST", "/server/jsonrpc", json=body)
