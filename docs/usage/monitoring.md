# Real-Time Monitoring

## WebSocket Subscriptions

For real-time printer monitoring, use the async client with WebSocket:

```python
import asyncio
from moonraker_client import AsyncMoonrakerClient
from moonraker_client.api.notifications import NOTIFY_STATUS_UPDATE

async def monitor():
    async with AsyncMoonrakerClient("http://printer.local:7125") as client:
        await client.connect_websocket()
        await client.identify("my-monitor", "1.0.0")

        # Subscribe to printer objects
        initial = await client.subscribe_objects({
            "toolhead": ["position", "status"],
            "extruder": ["temperature", "target"],
            "heater_bed": ["temperature", "target"],
            "print_stats": ["state", "filename", "print_duration"],
            "virtual_sdcard": ["progress"],
        })
        print(f"Initial status: {initial['status']}")

        # Handle real-time updates
        def on_status(params):
            status = params[0] if params else {}
            if "extruder" in status:
                print(f"Hotend: {status['extruder'].get('temperature', '?')}C")
            if "virtual_sdcard" in status:
                pct = status["virtual_sdcard"].get("progress", 0) * 100
                print(f"Progress: {pct:.1f}%")

        client.on(NOTIFY_STATUS_UPDATE, on_status)

        # Keep running
        await asyncio.sleep(60)

asyncio.run(monitor())
```

## Available Notifications

All 26 notification types are defined in `moonraker_client.api.notifications`:

| Notification | Description |
|---|---|
| `NOTIFY_KLIPPY_READY` | Klipper entered ready state |
| `NOTIFY_KLIPPY_SHUTDOWN` | Klipper shut down |
| `NOTIFY_KLIPPY_DISCONNECTED` | Lost connection to Klipper |
| `NOTIFY_STATUS_UPDATE` | Subscribed object data changed |
| `NOTIFY_GCODE_RESPONSE` | GCode response from Klipper |
| `NOTIFY_FILELIST_CHANGED` | File system change detected |
| `NOTIFY_HISTORY_CHANGED` | Print history modified |
| `NOTIFY_JOB_QUEUE_CHANGED` | Job queue state changed |
| `NOTIFY_PROC_STAT_UPDATE` | System stats updated |
| `NOTIFY_SENSOR_UPDATE` | Sensor readings updated |

See `moonraker_client.api.notifications` for the complete list.

## Polling Approach

For simpler use cases, poll with the sync client:

```python
import time
from moonraker_client import MoonrakerClient
from moonraker_client.helpers import get_print_progress, is_printing

with MoonrakerClient("http://printer.local:7125") as client:
    while is_printing(client):
        progress = get_print_progress(client)
        if progress:
            print(f"{progress.filename}: {progress.progress_pct}% ({progress.state})")
        time.sleep(5)
```
