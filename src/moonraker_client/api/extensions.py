"""API endpoints for Extensions operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class ExtensionsMixin:
    """Synchronous extensions API methods."""

    def server_extensions_list(self) -> Any:
        """List Extensions

        Returns a list of all available extensions.  Currently Moonraker can only
        be officially extended through connected `agents`.

        JSON-RPC method: server.extensions.list
        """
        return self._request("GET", "/server/extensions/list")

    def server_extensions_request(self, agent: str, method: str, arguments: str | None = None) -> Any:
        """Call an extension method

        This endpoint may be used to call a method on a connected agent.
        The request effectively relays a JSON-RPC request from a front end
        or other client to the agent.  Agents should document their
        available methods so Moonraker client developers can interact
        with them.

        Args:
            agent: The name of the registered agent hosting the requested method.
            method: The name of the method to call.
            arguments: The arguments to send with the method.  This may be an array containing position (optional)

        JSON-RPC method: server.extensions.request
        """
        body: dict[str, Any] = {}
        body["agent"] = agent
        body["method"] = method
        if arguments is not None:
            body["arguments"] = arguments
        return self._request("POST", "/server/extensions/request", json=body)

    def connection_send_event(self, event: str, data: dict[str, Any] | None = None) -> Any:
        """Send an agent event

        Sends a [JSON-RPC notification](./jsonrpc_notifications.md#agent-events)
        containing the supplied event info to all of Moonraker's persistent
        connections.
        
        **Note:** The `connected` and `disconnected` events are reserved for use
        by Moonraker and may not be sent from agents.
        
        **Note:** An agent may send an event without specifying the JSON-RPC `id` field.
        In this case Moonraker will not return a response.

        Args:
            event: The name of the event.  This may be any name other than those reserved by Moonra
            data: The data to send with the event. This can be any valid JSON decodable value.  If (optional)

        JSON-RPC method: connection.send_event
        """
        body: dict[str, Any] = {}
        body["event"] = event
        if data is not None:
            body["data"] = data
        return self._request("POST", "/connection/send_event", json=body)

    def connection_register_remote_method(self, method_name: str) -> Any:
        """Register a method with Klipper

        Registers a "remote method" with Klipper that can be called
        from GCode Macros.
        
        **Note:** Methods registered by agents will persist until the agent disconnects.
        Upon connection it is only necessary that they register their desired
        methods once.
        
        **Note:** Remote methods called from Klipper never contain the JSON-RPC "id" field,
        as Klipper does not accept return values to remote methods.

        Args:
            method_name: The name of the remote method to register with Klipper.  It is recommended for a

        JSON-RPC method: connection.register_remote_method
        """
        body: dict[str, Any] = {}
        body["method_name"] = method_name
        return self._request("POST", "/connection/register_remote_method", json=body)


class AsyncExtensionsMixin:
    """Asynchronous extensions API methods."""

    async def server_extensions_list(self) -> Any:
        """List Extensions

        Returns a list of all available extensions.  Currently Moonraker can only
        be officially extended through connected `agents`.

        JSON-RPC method: server.extensions.list
        """
        return await self._request("GET", "/server/extensions/list")

    async def server_extensions_request(self, agent: str, method: str, arguments: str | None = None) -> Any:
        """Call an extension method

        This endpoint may be used to call a method on a connected agent.
        The request effectively relays a JSON-RPC request from a front end
        or other client to the agent.  Agents should document their
        available methods so Moonraker client developers can interact
        with them.

        Args:
            agent: The name of the registered agent hosting the requested method.
            method: The name of the method to call.
            arguments: The arguments to send with the method.  This may be an array containing position (optional)

        JSON-RPC method: server.extensions.request
        """
        body: dict[str, Any] = {}
        body["agent"] = agent
        body["method"] = method
        if arguments is not None:
            body["arguments"] = arguments
        return await self._request("POST", "/server/extensions/request", json=body)

    async def connection_send_event(self, event: str, data: dict[str, Any] | None = None) -> Any:
        """Send an agent event

        Sends a [JSON-RPC notification](./jsonrpc_notifications.md#agent-events)
        containing the supplied event info to all of Moonraker's persistent
        connections.
        
        **Note:** The `connected` and `disconnected` events are reserved for use
        by Moonraker and may not be sent from agents.
        
        **Note:** An agent may send an event without specifying the JSON-RPC `id` field.
        In this case Moonraker will not return a response.

        Args:
            event: The name of the event.  This may be any name other than those reserved by Moonra
            data: The data to send with the event. This can be any valid JSON decodable value.  If (optional)

        JSON-RPC method: connection.send_event
        """
        body: dict[str, Any] = {}
        body["event"] = event
        if data is not None:
            body["data"] = data
        return await self._request("POST", "/connection/send_event", json=body)

    async def connection_register_remote_method(self, method_name: str) -> Any:
        """Register a method with Klipper

        Registers a "remote method" with Klipper that can be called
        from GCode Macros.
        
        **Note:** Methods registered by agents will persist until the agent disconnects.
        Upon connection it is only necessary that they register their desired
        methods once.
        
        **Note:** Remote methods called from Klipper never contain the JSON-RPC "id" field,
        as Klipper does not accept return values to remote methods.

        Args:
            method_name: The name of the remote method to register with Klipper.  It is recommended for a

        JSON-RPC method: connection.register_remote_method
        """
        body: dict[str, Any] = {}
        body["method_name"] = method_name
        return await self._request("POST", "/connection/register_remote_method", json=body)
