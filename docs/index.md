# moonraker-client

A typed, ergonomic Python client library for the [Moonraker API](https://moonraker.readthedocs.io/), providing HTTP and WebSocket interfaces for controlling 3D printers running [Klipper](https://www.klipper3d.org/) firmware.

## Features

- **Complete API coverage** - All 133+ Moonraker REST endpoints across 12 API categories
- **Sync + Async** - Both `MoonrakerClient` and `AsyncMoonrakerClient` with identical APIs
- **WebSocket support** - JSON-RPC 2.0 over WebSocket with notification subscriptions
- **Helper functions** - High-level convenience functions for common printer operations
- **Type-safe** - Full type annotations, dataclass models, PEP 561 compatible
- **Minimal dependencies** - Only `httpx` and `websockets`

## Quick Start

```python
from moonraker_client import MoonrakerClient

with MoonrakerClient("http://printer.local:7125") as client:
    # Get printer status
    info = client.printer_info()
    print(f"Printer state: {info['state']}")

    # Query temperatures
    result = client.printer_objects_query({
        "extruder": ["temperature", "target"],
        "heater_bed": ["temperature", "target"],
    })
    print(result["status"])
```

## Documentation

- [Getting Started](getting-started.md) - Installation and first connection
- [Configuration](configuration.md) - Authentication and connection options
- **Usage Guides:**
  - [Printer Control](usage/printer-control.md)
  - [Temperature Management](usage/temperature-management.md)
  - [File Management](usage/file-management.md)
  - [Monitoring](usage/monitoring.md)
  - [Job Queue](usage/job-queue.md)
  - [System Administration](usage/system-admin.md)
- **Advanced:**
  - [Async Usage](advanced/async-usage.md)
  - [WebSocket](advanced/websocket.md)
  - [Authentication](advanced/authentication.md)
  - [Error Handling](advanced/error-handling.md)
- [API Reference](api-reference/)
- [Contributing](contributing.md)
- [Changelog](changelog.md)
