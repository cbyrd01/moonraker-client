# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`moonraker-client` is a Python client library for the Moonraker API, providing HTTP and WebSocket interfaces for controlling 3D printers running Klipper firmware. It supports both sync (`MoonrakerClient`) and async (`AsyncMoonrakerClient`) usage.

## Build & Run Commands

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Unit tests (no server needed)
pytest tests/unit/

# Functional tests (requires a live Moonraker server)
MOONRAKER_URL=http://your-printer:7125 pytest tests/functional/ --functional

# All tests
MOONRAKER_URL=http://your-printer:7125 pytest tests/ --functional

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/moonraker_client/

# Regenerate the OpenAPI spec and Python client code
# (requires: pip install -e ".[codegen]" and `git submodule update --init`)
./tools/regenerate_openapi.sh
```

## Architecture

### Package Layout

- `src/moonraker_client/client.py` - Main client classes (`MoonrakerClient`, `AsyncMoonrakerClient`)
- `src/moonraker_client/_base.py` - Response unwrapping (`{"result": ...}` -> data), error mapping
- `src/moonraker_client/_transport.py` - HTTP (httpx) + WebSocket (websockets) transport layer
- `src/moonraker_client/_jsonrpc.py` - JSON-RPC 2.0 protocol handling
- `src/moonraker_client/auth.py` - API key + Bearer JWT auth via httpx auth hooks
- `src/moonraker_client/exceptions.py` - Exception hierarchy (MoonrakerError -> APIError, AuthError, etc.)
- `src/moonraker_client/helpers.py` - High-level convenience functions (sync + async variants: get_temperatures, start_print, etc.)
- `src/moonraker_client/models/` - Dataclass models generated from OpenAPI schemas
- `src/moonraker_client/api/` - Endpoint mixin classes (one per API category, 12 total)

### Key Patterns

- **Mixin composition**: Each `api/*.py` defines sync + async mixin classes. The client classes inherit all mixins, giving a flat `client.method()` API.
- **Response unwrapping**: Moonraker wraps all responses in `{"result": ...}`. The `_base.py:unwrap_response()` handles this automatically.
- **Generated code, two-stage pipeline**: `third_party/moonraker` (submodule → Arksine/moonraker) supplies `docs/external_api/*.md`; `openapi/scripts/generate_openapi.py` writes `openapi/openapi.yaml`; `tools/generate.py` consumes that YAML to write `api/*.py` and `models/generated.py`. Both stages are wrapped by `tools/regenerate_openapi.sh`. The YAML and Python output are committed; `api/*.py` files are hand-tuned after generation (e.g. `files.py` `_ProgressReader`).
- **WebSocket is optional**: HTTP works standalone. WebSocket requires explicit `connect_websocket()` and is async-only.
- **Error handling**: Helpers catch `MoonrakerError` (not bare `Exception`) for expected failure modes. `JsonRpcError` is exported from the public API for WebSocket error handling.
- **Async helpers**: Key helpers have async variants prefixed with `async_` (e.g., `async_get_printer_status`, `async_get_temperatures`).

### Dependencies

- `httpx>=0.27` - HTTP client (sync + async)
- `websockets>=13.0` - WebSocket client
- Dev: `pytest`, `pytest-asyncio`, `pytest-httpx`, `ruff`, `mypy`

### Test Structure

- `tests/unit/` - Mock-based unit tests (pytest-httpx mocks)
- `tests/functional/` - Tests against a live Moonraker server (skipped without `MOONRAKER_URL` + `--functional`)
- Functional test server configured via `MOONRAKER_URL` env var

## CI / Release

### Workflows

- `.github/workflows/ci.yml` — runs on every PR and push to `main`. Matrix across Python 3.10–3.13: `ruff check`, `ruff format --check`, `mypy`, `pytest tests/unit/`. Functional tests are not run in CI.
- `.github/workflows/release.yml` — triggered on `v*.*.*` tag push (and `workflow_dispatch` for TestPyPI-only dry-runs). Three jobs: `build` (sdist + wheel via `python -m build`) → `publish-testpypi` → `publish-pypi`. The PyPI job is gated on a tag ref, so manual dispatch can never reach prod PyPI.

### PyPI Trusted Publishing (OIDC — no API tokens)

Publishing is configured via [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — short-lived OIDC credentials minted by GitHub per job. No long-lived API tokens live in the repo or anywhere else.

Configured on both `pypi.org` and `test.pypi.org` (separate accounts) under *Your projects → Publishing*:

| Field | Value |
| --- | --- |
| Project name | `moonraker-client` |
| Owner | `cbyrd01` |
| Repository | `moonraker-client` |
| Workflow | `release.yml` |
| Environment | `pypi` (prod) / `testpypi` (test) |

GitHub environments (*Settings → Environments*):

- `testpypi` — no restrictions.
- `pypi` — required reviewer (cbyrd01); deployment refs restricted to `v*.*.*` tags on branch `main`.

Attestations (PEP 740) are emitted automatically by `pypa/gh-action-pypi-publish@release/v1`; no separate Sigstore step.

### Cutting a release

1. Bump the version in **both** places (they must match; the build job verifies this):
   - `pyproject.toml` → `[project] version = "X.Y.Z"`
   - `src/moonraker_client/__init__.py` → `__version__ = "X.Y.Z"`
2. Commit: `release: vX.Y.Z`.
3. Tag and push:
   ```bash
   git tag vX.Y.Z
   git push origin main
   git push origin vX.Y.Z
   ```
4. GitHub Actions runs `build` → `publish-testpypi` automatically.
5. Approve the `pypi` environment deployment in the Actions UI. The `publish-pypi` job will then upload to PyPI.
6. Verify at <https://pypi.org/project/moonraker-client/>.

To smoke-test the release pipeline without cutting a real release, run `release.yml` via *Actions → Release → Run workflow*. This publishes to TestPyPI only; the PyPI job is skipped because there's no tag ref.
