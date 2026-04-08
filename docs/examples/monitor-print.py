#!/usr/bin/env python3
"""Monitor a print job with real-time progress updates via WebSocket."""

import asyncio
import sys

from moonraker_client import AsyncMoonrakerClient
from moonraker_client.api.notifications import NOTIFY_STATUS_UPDATE


async def monitor_print(url: str) -> None:
    async with AsyncMoonrakerClient(url) as client:
        await client.connect_websocket()
        await client.identify("print-monitor", "1.0.0")

        # Subscribe to print-related objects
        initial = await client.subscribe_objects({
            "print_stats": ["state", "filename", "print_duration"],
            "virtual_sdcard": ["progress"],
            "extruder": ["temperature", "target"],
            "heater_bed": ["temperature", "target"],
        })

        status = initial.get("status", {})
        state = status.get("print_stats", {}).get("state", "unknown")
        filename = status.get("print_stats", {}).get("filename", "")
        print(f"Current state: {state}")
        if filename:
            progress = status.get("virtual_sdcard", {}).get("progress", 0) * 100
            print(f"File: {filename} ({progress:.1f}%)")

        def on_update(params: list) -> None:
            if not params:
                return
            data = params[0]
            parts = []
            if "virtual_sdcard" in data:
                pct = data["virtual_sdcard"].get("progress", 0) * 100
                parts.append(f"Progress: {pct:.1f}%")
            if "extruder" in data:
                temp = data["extruder"].get("temperature")
                if temp is not None:
                    parts.append(f"Hotend: {temp:.1f}C")
            if "print_stats" in data:
                new_state = data["print_stats"].get("state")
                if new_state:
                    parts.append(f"State: {new_state}")
            if parts:
                print(" | ".join(parts))

        client.on(NOTIFY_STATUS_UPDATE, on_update)

        # Run until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7125"
    try:
        asyncio.run(monitor_print(url))
    except KeyboardInterrupt:
        print("\nStopped.")
