# moonraker-client

A typed, ergonomic Python client library for the [Moonraker API](https://moonraker.readthedocs.io/), providing HTTP and WebSocket interfaces for controlling 3D printers running [Klipper](https://www.klipper3d.org/) firmware.

## Features

- **Complete API coverage** - All 133+ Moonraker REST endpoints across 12 API categories
- **Sync + Async** - Both `MoonrakerClient` and `AsyncMoonrakerClient` with identical APIs
- **WebSocket support** - JSON-RPC 2.0 over WebSocket with real-time notification subscriptions
- **Helper functions** - High-level convenience functions for common printer operations
- **Type-safe** - Full type annotations, dataclass models, PEP 561 compatible (`py.typed`)
- **Minimal dependencies** - Only `httpx` and `websockets`
- **Well tested** - 155 tests (unit + functional against a live Moonraker server)

## Installation

```bash
pip install moonraker-client
```

**Requires Python 3.10+**

## Quick Start

### Synchronous

```python
from moonraker_client import MoonrakerClient

with MoonrakerClient("http://printer.local:7125") as client:
    # Printer info
    info = client.printer_info()
    print(f"State: {info['state']}")

    # Query temperatures
    result = client.printer_objects_query({
        "extruder": ["temperature", "target"],
        "heater_bed": ["temperature", "target"],
    })
    temps = result["status"]
    print(f"Hotend: {temps['extruder']['temperature']}C")

    # Send GCode
    client.gcode_script("G28")  # Home all axes

    # Start a print
    client.print_start("my_model.gcode")
```

### Asynchronous

```python
import asyncio
from moonraker_client import AsyncMoonrakerClient

async def main():
    async with AsyncMoonrakerClient("http://printer.local:7125") as client:
        info = await client.printer_info()
        print(f"State: {info['state']}")

        # WebSocket for real-time monitoring
        await client.connect_websocket()
        await client.identify("my-app", "1.0.0")
        await client.subscribe_objects({"toolhead": None, "extruder": None})

        client.on("notify_status_update", lambda params: print(params))
        await asyncio.sleep(10)  # Listen for updates

asyncio.run(main())
```

### Helper Functions

```python
from moonraker_client import MoonrakerClient
from moonraker_client.helpers import (
    get_printer_status,
    get_temperatures,
    is_printing,
    set_hotend_temp,
    wait_for_temps,
    start_print,
    get_system_health,
)

with MoonrakerClient("http://printer.local:7125") as client:
    status = get_printer_status(client)
    print(f"{status.hostname}: {status.state}")

    temps = get_temperatures(client)
    for name, t in temps.items():
        print(f"  {name}: {t.current}C / {t.target}C")

    if not is_printing(client):
        set_hotend_temp(client, 210.0)
        wait_for_temps(client, {"extruder": 210.0})
        start_print(client, "benchy.gcode")
```

## API Coverage

| Category | Methods | Examples |
|----------|---------|---------|
| Printer | 13 | `printer_info()`, `gcode_script()`, `print_start()`, `emergency_stop()` |
| Server | 9 | `server_info()`, `server_config()`, `server_temperaturestore()` |
| Files | 16 | `files_list()`, `files_upload()`, `files_metadata()`, `files_move()` |
| History | 5 | `server_history_list()`, `server_history_totals()` |
| Job Queue | 6 | `server_jobqueue_status()`, `server_jobqueue_job()` |
| Machine | 13 | `machine_systeminfo()`, `machine_procstats()`, `machine_services_restart()` |
| Auth | 9 | `access_login()`, `access_refreshjwt()`, `access_oneshottoken()` |
| Database | 8+ | `server_database_list()`, `server_database_item()` |
| Updates | 10 | `machine_update_status()`, `machine_update_refresh()` |
| Devices | 15 | `power_on()`, `power_off()`, `wled_on()`, `sensors_list()` |
| Webcams | 4 | `server_webcams_list()`, `server_webcams_item()` |
| Announcements | 5 | `server_announcements_list()`, `server_announcements_dismiss()` |

## Authentication

```python
# API Key
client = MoonrakerClient("http://printer:7125", api_key="your-key")

# JWT Token
client = MoonrakerClient("http://printer:7125", token="your-jwt")
```

## Documentation

See the [docs/](docs/) directory for complete documentation:

- [Getting Started](docs/getting-started.md) - Installation and first connection
- [Configuration](docs/configuration.md) - Authentication and connection options
- [Printer Control](docs/usage/printer-control.md) - Print management and GCode
- [Temperature Management](docs/usage/temperature-management.md) - Heating and cooling
- [File Management](docs/usage/file-management.md) - Upload, download, and organize files
- [Real-Time Monitoring](docs/usage/monitoring.md) - WebSocket subscriptions
- [WebSocket Guide](docs/advanced/websocket.md) - JSON-RPC and notifications
- [Error Handling](docs/advanced/error-handling.md) - Exception hierarchy
- [Contributing](docs/contributing.md) - Development setup and guidelines

## Development

```bash
git clone https://github.com/cbyrd01/moonraker-client.git
cd moonraker-client
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Tests
pytest tests/unit/
MOONRAKER_URL=http://printer:7125 pytest tests/functional/ --functional

# Quality
ruff check src/ tests/
mypy src/moonraker_client/
```

To regenerate the OpenAPI spec and Python client code from upstream Moonraker, see [docs/contributing.md](docs/contributing.md#code-generator).

## License

GPL-3.0 - See [LICENSE](LICENSE) for details.
