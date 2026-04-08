# Error Handling

## Exception Hierarchy

```
MoonrakerError (base)
  MoonrakerConnectionError  # Cannot connect to server
  MoonrakerTimeoutError     # Request timed out
  MoonrakerAPIError         # Server returned an error response
    MoonrakerAuthError      # 401/403 authentication errors
```

## Handling Errors

```python
from moonraker_client import (
    MoonrakerClient,
    MoonrakerAPIError,
    MoonrakerAuthError,
    MoonrakerConnectionError,
    MoonrakerTimeoutError,
    MoonrakerError,
)

try:
    with MoonrakerClient("http://printer:7125") as client:
        client.printer_info()
except MoonrakerConnectionError:
    print("Cannot connect to printer")
except MoonrakerTimeoutError:
    print("Request timed out")
except MoonrakerAuthError as e:
    print(f"Authentication failed: {e.message} (HTTP {e.status_code})")
except MoonrakerAPIError as e:
    print(f"API error: {e.message} (HTTP {e.status_code}, code={e.error_code})")
except MoonrakerError as e:
    print(f"Unexpected error: {e}")
```

## API Error Details

`MoonrakerAPIError` includes:

- `status_code` - HTTP status code (400, 404, 500, etc.)
- `error_code` - Moonraker-specific error code from the response body
- `message` - Human-readable error description

## WebSocket Errors

JSON-RPC errors over WebSocket raise `JsonRpcError`:

```python
from moonraker_client._jsonrpc import JsonRpcError

try:
    result = await client.send_jsonrpc("invalid.method")
except JsonRpcError as e:
    print(f"JSON-RPC error {e.code}: {e.message}")
```
