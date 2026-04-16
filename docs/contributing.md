# Contributing

## Development Setup

```bash
git clone https://github.com/cbyrd01/moonraker-client.git
cd moonraker-client
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

The API endpoint methods and data models are generated from the Moonraker API docs via a two-stage pipeline:

```
third_party/moonraker/docs/external_api/*.md   (submodule → Arksine/moonraker)
        │
        ▼
openapi/scripts/generate_openapi.py
        │
        ▼
openapi/openapi.yaml                           (committed)
        │
        ▼
tools/generate.py
        │
        ▼
src/moonraker_client/api/*.py
src/moonraker_client/models/generated.py       (committed, hand-tuned)
```

### Setup

```bash
pip install -e ".[codegen]"
git submodule update --init --recursive
```

### Regenerating

```bash
# Pull the latest markdown docs from upstream moonraker
git -C third_party/moonraker pull origin master

# Run both stages
./tools/regenerate_openapi.sh

# Review diffs before committing
git diff openapi/openapi.yaml src/moonraker_client/
```

### Viewing the API docs

`openapi/index.html` is a static Redoc viewer that renders `openapi/openapi.yaml`. To browse:

```bash
python -m http.server --directory openapi 8080
# visit http://localhost:8080/
```

No build step — Redoc loads from CDN.

### Hand-tunes

Some files under `src/moonraker_client/api/` are hand-tuned after generation (e.g. `files.py` contains a `_ProgressReader` helper for upload progress). If the regenerator overwrites them, reapply the hand-tune manually and include it in the commit.

### Commit convention

Bundle the submodule bump, `openapi/openapi.yaml` changes, and regenerated Python code in a single commit so the tree stays consistent.

### TODO

When the openapi work lands in `Arksine/moonraker` canonical, add a CI job that runs `tools/regenerate_openapi.sh` weekly and fails if `git diff` is non-empty — surfaces spec drift automatically.

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
