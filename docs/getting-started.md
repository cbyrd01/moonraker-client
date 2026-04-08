# Getting Started

## Installation

```bash
pip install moonraker-client
```

For development:

```bash
git clone https://github.com/cbyrd01/moonraker-client.git
cd moonraker-client
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Requirements

- Python 3.10+
- A running Moonraker instance (typically alongside Klipper on a Raspberry Pi or similar)

## First Connection

### Synchronous Client

```python
from moonraker_client import MoonrakerClient

# Connect to your printer
with MoonrakerClient("http://your-printer-ip:7125") as client:
    info = client.printer_info()
    print(f"Printer: {info['hostname']}")
    print(f"State: {info['state']}")
    print(f"Klipper: {info['software_version']}")
```

### Asynchronous Client

```python
import asyncio
from moonraker_client import AsyncMoonrakerClient

async def main():
    async with AsyncMoonrakerClient("http://your-printer-ip:7125") as client:
        info = await client.printer_info()
        print(f"State: {info['state']}")

asyncio.run(main())
```

### With Authentication

```python
# API Key authentication
client = MoonrakerClient(
    "http://your-printer-ip:7125",
    api_key="your-api-key-here"
)

# JWT authentication
client = MoonrakerClient(
    "http://your-printer-ip:7125",
    token="your-jwt-token-here"
)
```

## Using Helper Functions

For common operations, the `helpers` module provides high-level functions:

```python
from moonraker_client import MoonrakerClient
from moonraker_client.helpers import (
    get_printer_status,
    get_temperatures,
    is_printing,
)

with MoonrakerClient("http://your-printer-ip:7125") as client:
    # Get comprehensive status
    status = get_printer_status(client)
    print(f"State: {status.state}")
    print(f"Klippy: {status.klippy_state}")

    # Check temperatures
    temps = get_temperatures(client)
    for name, reading in temps.items():
        print(f"{name}: {reading.current}C / {reading.target}C")

    # Check if printing
    if is_printing(client):
        from moonraker_client.helpers import get_print_progress
        progress = get_print_progress(client)
        if progress:
            print(f"Printing {progress.filename}: {progress.progress_pct}%")
```

## Next Steps

- [Configuration](configuration.md) - Authentication and connection options
- [Printer Control](usage/printer-control.md) - Start prints, send GCode, control the printer
- [WebSocket](advanced/websocket.md) - Real-time monitoring with WebSocket subscriptions
