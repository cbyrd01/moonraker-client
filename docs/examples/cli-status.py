#!/usr/bin/env python3
"""Simple CLI tool showing printer dashboard status."""

import sys

from moonraker_client import MoonrakerClient
from moonraker_client.helpers import (
    get_print_progress,
    get_printer_status,
    get_system_health,
    get_temperatures,
    is_printing,
)


def main(url: str) -> None:
    with MoonrakerClient(url) as client:
        status = get_printer_status(client)
        temps = get_temperatures(client)
        health = get_system_health(client)

        print(f"{'=' * 50}")
        print(f"  Printer: {status.hostname}")
        print(f"  Klipper: {status.software_version}")
        print(f"  State:   {status.state} ({status.state_message})")
        print(f"{'=' * 50}")

        print("\nTemperatures:")
        for name, reading in temps.items():
            bar = "#" * int(reading.current / 5)
            print(f"  {name:12s}: {reading.current:6.1f}C / {reading.target:6.1f}C  {bar}")

        if is_printing(client):
            progress = get_print_progress(client)
            if progress:
                print(f"\nPrint Job:")
                print(f"  File:     {progress.filename}")
                print(f"  Progress: {progress.progress_pct:.1f}%")
                elapsed_min = progress.elapsed / 60
                print(f"  Elapsed:  {elapsed_min:.0f} min")
        else:
            print("\nNo active print job.")

        print(f"\nSystem:")
        if health.get("cpu_temp"):
            print(f"  CPU Temp: {health['cpu_temp']:.1f}C")
        if health.get("system_uptime"):
            hours = health["system_uptime"] / 3600
            print(f"  Uptime:   {hours:.1f} hours")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7125"
    main(url)
