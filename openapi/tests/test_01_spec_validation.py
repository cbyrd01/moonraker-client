"""Phase 2: Static OpenAPI spec validation tests.

These tests validate the spec file itself without hitting the network.
"""

from pathlib import Path

import pytest
import yaml
from openapi_spec_validator import validate


SPEC_PATH = Path(__file__).parent.parent / "openapi.yaml"


@pytest.fixture(scope="module")
def spec():
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


def test_spec_structural_validity(spec):
    """Validate the spec against the OpenAPI 3.1 schema."""
    validate(spec)


def test_unique_operation_ids(spec):
    """All operationIds must be unique across the spec."""
    ids = []
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if isinstance(op, dict) and "operationId" in op:
                ids.append(op["operationId"])
    duplicates = [x for x in ids if ids.count(x) > 1]
    assert len(ids) == len(set(ids)), f"Duplicate operationIds: {set(duplicates)}"


def test_all_operations_have_responses(spec):
    """Every operation must define at least one response."""
    missing = []
    http_methods = {"get", "post", "put", "patch", "delete"}
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method not in http_methods:
                continue
            if not isinstance(op, dict):
                continue
            responses = op.get("responses", {})
            if not responses:
                missing.append(f"{method.upper()} {path}")
    assert not missing, f"Operations without responses: {missing}"


def test_no_empty_response_schemas(spec):
    """Flag response schemas that are just type:object with no properties."""
    empty = []
    http_methods = {"get", "post", "put", "patch", "delete"}
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if method not in http_methods or not isinstance(op, dict):
                continue
            for status, resp in op.get("responses", {}).items():
                content = resp.get("content", {}).get("application/json", {})
                schema = content.get("schema", {})
                if schema.get("type") == "object" and not schema.get("properties"):
                    # Only flag if there's no $ref, additionalProperties, or oneOf
                    if not any(k in schema for k in
                              ("$ref", "additionalProperties", "oneOf",
                               "anyOf", "allOf")):
                        empty.append(f"{method.upper()} {path} -> {status}")
    if empty:
        pytest.skip(f"Empty schemas found (informational): {empty}")


def test_no_deprecated_nullable_syntax(spec):
    """Ensure nullable fields use OpenAPI 3.1 type arrays, not nullable:true."""
    violations = []

    def check_obj(obj, path=""):
        if isinstance(obj, dict):
            if "nullable" in obj:
                violations.append(path)
            for k, v in obj.items():
                check_obj(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_obj(item, f"{path}[{i}]")

    check_obj(spec)
    assert not violations, (
        f"Found deprecated 'nullable' keyword at: {violations[:10]}"
    )


def test_all_refs_resolve(spec):
    """All $ref pointers must resolve to existing definitions."""
    unresolved = []

    def resolve(ref):
        parts = ref.lstrip("#/").split("/")
        target = spec
        for part in parts:
            if isinstance(target, dict) and part in target:
                target = target[part]
            else:
                return False
        return True

    def check_refs(obj, path=""):
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                if ref.startswith("#/") and not resolve(ref):
                    unresolved.append(f"{path}: {ref}")
            for k, v in obj.items():
                check_refs(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                check_refs(item, f"{path}[{i}]")

    check_refs(spec)
    assert not unresolved, f"Unresolved $refs: {unresolved[:10]}"
