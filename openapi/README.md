# OpenAPI

`openapi.yaml` is the OpenAPI 3.1 specification for the Moonraker API. It is generated — do not hand-edit.

## Pipeline

```
third_party/moonraker/docs/external_api/*.md   (submodule, Arksine/moonraker)
        │
        ▼
openapi/scripts/generate_openapi.py
        │
        ▼
openapi/openapi.yaml                           (committed artifact)
        │
        ▼
tools/generate.py
        │
        ▼
src/moonraker_client/api/*.py
src/moonraker_client/models/generated.py
```

## Regenerating

```bash
pip install -e ".[codegen]"
git submodule update --init --recursive
./tools/regenerate_openapi.sh
```

See `docs/contributing.md` for the full workflow, including how to reapply hand-tunes (e.g. `files.py` `_ProgressReader`) if the regenerator overwrites them.

## Contents

- `openapi.yaml` — the spec (OpenAPI 3.1.0)
- `index.html` — Redoc viewer; open directly in a browser to render `openapi.yaml`
- `scripts/` — generator that parses markdown API docs into the spec
- `tests/` — conformance tests that exercise a live Moonraker against the spec (not run by default; see their own `pytest.ini`)

## Viewing

```bash
# Serve openapi/ over HTTP and open index.html in a browser
python -m http.server --directory openapi 8080
# then visit http://localhost:8080/
```

`index.html` is a static Redoc viewer — it loads Redoc from CDN and renders `./openapi.yaml`. No build step required.
