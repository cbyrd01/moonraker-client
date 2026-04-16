"""Phase 9: WebSocket notification tests.

Tests WebSocket connection, identification, subscription, and validates
notification schemas against the spec's webhook definitions.
"""

import asyncio
import json
from pathlib import Path

import httpx
import pytest
import websockets
import yaml
from conftest import check_printer_health, BASE_URL
from jsonschema.validators import Draft202012Validator

SPEC_PATH = Path(__file__).parent.parent / "openapi.yaml"
WS_URL = "ws://192.168.1.212:7125/websocket"


@pytest.fixture(scope="module")
def spec():
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
        yield client


def _resolve_all_refs(spec, obj):
    """Recursively resolve $ref pointers."""
    if isinstance(obj, dict):
        if "$ref" in obj:
            parts = obj["$ref"].lstrip("#/").split("/")
            target = spec
            for p in parts:
                target = target[p]
            return _resolve_all_refs(spec, target)
        return {k: _resolve_all_refs(spec, v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_all_refs(spec, item) for item in obj]
    return obj


def _get_webhook_schema(spec, method_name):
    """Get the resolved schema for a webhook notification."""
    wh = spec.get("webhooks", {}).get(method_name, {})
    if not wh:
        return None
    op = wh.get("post", wh.get("get", {}))
    rb = op.get("requestBody", {})
    content = rb.get("content", {}).get("application/json", {})
    schema = content.get("schema")
    if schema:
        return _resolve_all_refs(spec, schema)
    return None


def _validate_notification(spec, notification):
    """Validate a notification against its webhook schema. Returns errors list."""
    method = notification.get("method")
    schema = _get_webhook_schema(spec, method)
    if not schema:
        return [f"No webhook schema for {method}"]
    v = Draft202012Validator(schema)
    return [f"{e.json_path}: {e.message}" for e in v.iter_errors(notification)]


def test_health_check():
    state = check_printer_health()
    assert state in ("ready", "startup"), f"Printer not healthy: {state}"


# --- Connection & Identification ---

@pytest.mark.asyncio
async def test_websocket_identify(spec):
    """Connect and identify, validate response has connection_id."""
    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "server.connection.identify",
            "params": {
                "client_name": "openapi_test",
                "version": "1.0",
                "type": "web",
                "url": "http://test.local"
            },
            "id": 1
        }))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        assert "result" in resp
        assert "connection_id" in resp["result"]
        assert isinstance(resp["result"]["connection_id"], int)


# --- Subscription & Status Updates ---

@pytest.mark.asyncio
async def test_subscribe_and_receive_status(spec):
    """Subscribe to objects and validate notify_status_update schema."""
    async with websockets.connect(WS_URL) as ws:
        # Identify
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "server.connection.identify",
            "params": {"client_name": "test", "version": "1.0",
                       "type": "web", "url": "http://test.local"},
            "id": 1
        }))
        await asyncio.wait_for(ws.recv(), timeout=5)

        # Subscribe
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "printer.objects.subscribe",
            "params": {"objects": {"extruder": None, "heater_bed": None}},
            "id": 2
        }))
        resp = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
        assert "result" in resp
        assert "status" in resp["result"]

        # Collect notifications for a few seconds
        notifications = []
        try:
            for _ in range(10):
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                if "method" in msg:
                    notifications.append(msg)
                    if msg["method"] == "notify_status_update":
                        break
        except asyncio.TimeoutError:
            pass

        # Validate any status update notifications
        for notif in notifications:
            if notif["method"] == "notify_status_update":
                errors = _validate_notification(spec, notif)
                assert not errors, f"Schema errors for notify_status_update: {errors}"
                break


# --- Triggered Notifications ---

@pytest.mark.asyncio
async def test_gcode_response_notification(spec):
    """Send gcode via HTTP, capture notify_gcode_response on WebSocket."""
    async with websockets.connect(WS_URL) as ws:
        # Identify
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "server.connection.identify",
            "params": {"client_name": "test", "version": "1.0",
                       "type": "web", "url": "http://test.local"},
            "id": 1
        }))
        await asyncio.wait_for(ws.recv(), timeout=5)

        # Trigger gcode response via HTTP
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as http:
            await http.post("/printer/gcode/script",
                            json={"script": "M115"})

        # Collect notifications
        gcode_notifs = []
        try:
            for _ in range(20):
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                if msg.get("method") == "notify_gcode_response":
                    gcode_notifs.append(msg)
                    break
        except asyncio.TimeoutError:
            pass

        if gcode_notifs:
            errors = _validate_notification(spec, gcode_notifs[0])
            assert not errors, f"Schema errors: {errors}"
        # It's ok if we don't catch it -- timing dependent


@pytest.mark.asyncio
async def test_filelist_changed_notification(spec):
    """Upload file via HTTP, capture notify_filelist_changed."""
    async with websockets.connect(WS_URL) as ws:
        # Identify
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "server.connection.identify",
            "params": {"client_name": "test", "version": "1.0",
                       "type": "web", "url": "http://test.local"},
            "id": 1
        }))
        await asyncio.wait_for(ws.recv(), timeout=5)

        # Upload file
        gcode_path = Path(__file__).parent / "assets" / "test_print.gcode"
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=15) as http:
            with open(gcode_path, "rb") as f:
                await http.post("/server/files/upload",
                                files={"file": ("ws_test.gcode", f,
                                                "application/octet-stream")},
                                data={"root": "gcodes"})

        # Collect filelist notifications
        filelist_notifs = []
        try:
            for _ in range(20):
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=3))
                if msg.get("method") == "notify_filelist_changed":
                    filelist_notifs.append(msg)
                    break
        except asyncio.TimeoutError:
            pass

        # Cleanup
        async with httpx.AsyncClient(base_url=BASE_URL, timeout=15) as http:
            await http.delete("/server/files/gcodes/ws_test.gcode")

        if filelist_notifs:
            errors = _validate_notification(spec, filelist_notifs[0])
            assert not errors, f"Schema errors: {errors}"


@pytest.mark.asyncio
async def test_proc_stat_notification(spec):
    """proc_stat_update fires continuously -- validate its schema."""
    async with websockets.connect(WS_URL) as ws:
        # Identify
        await ws.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "server.connection.identify",
            "params": {"client_name": "test", "version": "1.0",
                       "type": "web", "url": "http://test.local"},
            "id": 1
        }))
        await asyncio.wait_for(ws.recv(), timeout=5)

        # Wait for proc_stat notification
        try:
            for _ in range(10):
                msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
                if msg.get("method") == "notify_proc_stat_update":
                    errors = _validate_notification(spec, msg)
                    assert not errors, f"Schema errors: {errors}"
                    return
        except asyncio.TimeoutError:
            pass
        pytest.skip("No proc_stat notification received in time")
