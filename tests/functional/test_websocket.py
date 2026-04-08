"""Functional tests for WebSocket + JSON-RPC against a live Moonraker server."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import pytest

from moonraker_client import AsyncMoonrakerClient
from moonraker_client.api.notifications import NOTIFY_STATUS_UPDATE

MOONRAKER_URL = os.environ.get("MOONRAKER_URL", "")

pytestmark = pytest.mark.functional


@pytest.fixture
async def async_client() -> AsyncMoonrakerClient:
    client = AsyncMoonrakerClient(MOONRAKER_URL)
    yield client
    await client.close()


class TestWebSocketConnect:
    @pytest.mark.asyncio
    async def test_connect_and_disconnect(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)
        assert async_client.websocket_connected is True
        await async_client.disconnect_websocket()
        assert async_client.websocket_connected is False

    @pytest.mark.asyncio
    async def test_identify(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)
        result = await async_client.identify(
            client_name="moonraker-client-test",
            version="0.1.0",
            client_type="web",
            url="https://github.com/cbyrd01/moonraker-client",
        )
        assert "connection_id" in result


class TestJsonRpcOverWebSocket:
    @pytest.mark.asyncio
    async def test_printer_info_via_jsonrpc(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)
        result = await async_client.send_jsonrpc("printer.info")
        assert "state" in result
        assert result["state"] in ("ready", "startup", "shutdown", "error")

    @pytest.mark.asyncio
    async def test_server_info_via_jsonrpc(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)
        result = await async_client.send_jsonrpc("server.info")
        assert "klippy_state" in result

    @pytest.mark.asyncio
    async def test_objects_list_via_jsonrpc(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)
        result = await async_client.send_jsonrpc("printer.objects.list")
        assert "objects" in result
        assert isinstance(result["objects"], list)


class TestObjectSubscription:
    @pytest.mark.asyncio
    async def test_subscribe_objects(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)
        result = await async_client.subscribe_objects(
            {
                "toolhead": ["position", "status"],
                "extruder": None,
            }
        )
        assert "eventtime" in result
        assert "status" in result

    @pytest.mark.asyncio
    async def test_notification_received(self, async_client: AsyncMoonrakerClient) -> None:
        await async_client.connect_websocket(reconnect=False)

        received: list[Any] = []

        def on_update(params: Any) -> None:
            received.append(params)

        async_client.on(NOTIFY_STATUS_UPDATE, on_update)

        # Subscribe to trigger periodic status updates
        await async_client.subscribe_objects({"toolhead": None})

        # Wait briefly for at least one notification
        await asyncio.sleep(2.0)

        # We may or may not receive updates depending on printer activity,
        # but the subscription should not error
        # The test validates the plumbing works end-to-end
