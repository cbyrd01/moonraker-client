# WebSocket Communication

## Overview

Moonraker's WebSocket interface uses JSON-RPC 2.0 for bidirectional communication. The client supports:

- JSON-RPC requests with automatic response matching
- Server-initiated notifications (26 types)
- Auto-reconnection with exponential backoff
- Printer object subscriptions for real-time status updates

## Connection Lifecycle

```python
async with AsyncMoonrakerClient("http://printer.local:7125") as client:
    # Connect (auto-reconnect enabled by default)
    await client.connect_websocket()

    # Identify your client to Moonraker
    conn_info = await client.identify(
        client_name="my-tool",
        version="1.0.0",
        client_type="web",  # or "mobile", "desktop", "agent"
        url="https://github.com/my/project",
    )
    print(f"Connection ID: {conn_info['connection_id']}")

    # ... use the connection ...

    # Disconnect
    await client.disconnect_websocket()
```

## JSON-RPC Requests

Any Moonraker JSON-RPC method can be called directly:

```python
# These are equivalent:
result = await client.send_jsonrpc("printer.info")
result = await client.printer_info()  # HTTP version

# With parameters
result = await client.send_jsonrpc("printer.objects.query", {
    "objects": {"toolhead": ["position"]}
})
```

## Notification Handlers

```python
from moonraker_client.api.notifications import (
    NOTIFY_KLIPPY_READY,
    NOTIFY_KLIPPY_SHUTDOWN,
    NOTIFY_STATUS_UPDATE,
)

def on_ready(params):
    print("Klipper is ready!")

def on_shutdown(params):
    print("Klipper shut down!")

async def on_status(params):
    # Handlers can be async
    status = params[0] if params else {}
    print(f"Status update: {status}")

client.on(NOTIFY_KLIPPY_READY, on_ready)
client.on(NOTIFY_KLIPPY_SHUTDOWN, on_shutdown)
client.on(NOTIFY_STATUS_UPDATE, on_status)

# Remove a handler
client.off(NOTIFY_KLIPPY_READY, on_ready)
```

## Object Subscriptions

Subscribe to Klipper printer objects for real-time updates:

```python
# Subscribe returns initial state
initial = await client.subscribe_objects({
    "toolhead": ["position", "homed_axes", "status"],
    "extruder": ["temperature", "target", "power"],
    "heater_bed": None,  # All attributes
    "print_stats": ["state", "filename"],
    "virtual_sdcard": ["progress"],
})

# Subsequent changes arrive as notify_status_update notifications
```

## Reconnection

The WebSocket transport auto-reconnects with exponential backoff (1s, 2s, 4s, ... up to 60s):

```python
# Enable reconnection (default)
await client.connect_websocket(reconnect=True)

# Disable for one-shot connections
await client.connect_websocket(reconnect=False)
```
