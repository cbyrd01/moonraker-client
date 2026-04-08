# Contributing

## Development Setup

```bash
git clone https://github.com/cbyrd01/moonraker-api-client.git
cd moonraker-api-client
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
# Unit tests (no server needed)
pytest tests/unit/

# Functional tests (requires a live Moonraker server)
MOONRAKER_URL=http://your-printer:7125 pytest tests/functional/ --functional

# All tests
MOONRAKER_URL=http://your-printer:7125 pytest tests/ --functional
```

## Code Quality

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/moonraker_client/
```

## Code Generator

The API endpoint methods and data models are generated from the Moonraker OpenAPI spec:

```bash
python tools/generate.py /path/to/openapi.yaml
```

Generated files:
- `src/moonraker_client/api/*.py` - Endpoint method stubs
- `src/moonraker_client/models/generated.py` - Dataclass models

Generated output is committed and hand-tuned. Re-run when the upstream spec changes.

## Project Structure

```
src/moonraker_client/
  __init__.py          # Public exports
  client.py            # MoonrakerClient, AsyncMoonrakerClient
  _base.py             # Response unwrapping, error mapping
  _transport.py        # HTTP + WebSocket transport
  _jsonrpc.py          # JSON-RPC 2.0 protocol
  auth.py              # Authentication handlers
  exceptions.py        # Exception hierarchy
  helpers.py           # High-level convenience functions
  models/              # Dataclass models from API schemas
  api/                 # Endpoint mixins (one per API category)
```

## Architecture

- **Mixin pattern**: Each `api/*.py` defines sync + async mixin classes. The client inherits all mixins.
- **Response unwrapping**: Moonraker wraps responses in `{"result": ...}`. The client unwraps automatically.
- **WebSocket**: Optional async-only WebSocket with JSON-RPC request/response matching and notification dispatch.
