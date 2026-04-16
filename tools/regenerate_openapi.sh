#!/usr/bin/env bash
# Regenerate openapi/openapi.yaml from the moonraker submodule, then regenerate
# the Python client code from the spec. Run from the repo root.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -d third_party/moonraker/docs/external_api ]]; then
    echo "==> Initializing moonraker submodule"
    git submodule update --init --recursive third_party/moonraker
fi

echo "==> Generating openapi/openapi.yaml from third_party/moonraker"
python openapi/scripts/generate_openapi.py

echo "==> Generating Python client code from openapi/openapi.yaml"
python tools/generate.py

echo "==> Done. Review with: git diff openapi/openapi.yaml src/moonraker_client/"
echo "    Reapply any hand-tunes (e.g. _ProgressReader in api/files.py) if clobbered."
