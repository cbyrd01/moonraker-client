# Async Usage

## AsyncMoonrakerClient

The async client provides the same API as the sync client, but all methods are awaitable:

```python
import asyncio
from moonraker_client import AsyncMoonrakerClient

async def main():
    async with AsyncMoonrakerClient("http://printer.local:7125") as client:
        info = await client.printer_info()
        temps = await client.printer_objects_query({
            "extruder": ["temperature", "target"],
        })
        print(f"State: {info['state']}")
        print(f"Temp: {temps['status']['extruder']['temperature']}")

asyncio.run(main())
```

## Concurrent Requests

```python
async def get_full_status(client):
    # Run multiple queries concurrently
    info, server, temps = await asyncio.gather(
        client.printer_info(),
        client.server_info(),
        client.printer_objects_query({
            "extruder": ["temperature", "target"],
            "heater_bed": ["temperature", "target"],
        }),
    )
    return {
        "printer": info,
        "server": server,
        "temperatures": temps["status"],
    }
```

## WebSocket with Async

The WebSocket features are async-only:

```python
async with AsyncMoonrakerClient("http://printer.local:7125") as client:
    await client.connect_websocket()
    await client.identify("my-app", "1.0.0")

    # JSON-RPC directly over WebSocket
    result = await client.send_jsonrpc("printer.info")

    # Subscribe to objects
    await client.subscribe_objects({"toolhead": None})

    # Register notification handlers
    client.on("notify_status_update", lambda params: print(params))
```
