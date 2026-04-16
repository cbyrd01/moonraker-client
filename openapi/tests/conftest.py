"""Shared fixtures for OpenAPI conformance tests."""

import json
import time
from pathlib import Path

import httpx
import pytest
import yaml
from jsonschema import ValidationError, validate
from jsonschema.validators import Draft202012Validator

BASE_URL = "http://192.168.1.212:7125"
SPEC_PATH = Path(__file__).parent.parent / "openapi.yaml"
ASSETS_DIR = Path(__file__).parent / "assets"


def check_printer_health(base_url: str = BASE_URL, timeout: float = 5.0) -> str:
    """Quick health check -- returns printer state or raises."""
    resp = httpx.get(f"{base_url}/printer/info", timeout=timeout)
    resp.raise_for_status()
    return resp.json()["result"]["state"]


def wait_for_ready(base_url: str = BASE_URL, timeout: int = 30) -> str:
    """Wait for printer to reach ready state. Returns final state."""
    for _ in range(timeout * 2):
        try:
            state = check_printer_health(base_url)
            if state == "ready":
                return state
        except Exception:
            pass
        time.sleep(0.5)
    return check_printer_health(base_url)


@pytest.fixture(scope="session")
def spec():
    """Load the OpenAPI spec once per session."""
    with open(SPEC_PATH) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def api():
    """HTTP client pointed at the live Moonraker instance."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


def _resolve_ref(spec: dict, ref: str) -> dict:
    """Resolve a $ref pointer within the spec."""
    parts = ref.lstrip("#/").split("/")
    target = spec
    for part in parts:
        target = target[part]
    return target


def _resolve_all_refs(spec: dict, obj: dict) -> dict:
    """Recursively resolve all $ref pointers in an object."""
    if isinstance(obj, dict):
        if "$ref" in obj:
            resolved = _resolve_ref(spec, obj["$ref"])
            return _resolve_all_refs(spec, resolved)
        return {k: _resolve_all_refs(spec, v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_resolve_all_refs(spec, item) for item in obj]
    return obj


def get_response_schema(spec: dict, path: str, method: str = "get",
                        status: str = "200") -> dict | None:
    """Extract and resolve the response schema for a given endpoint."""
    path_item = spec.get("paths", {}).get(path)
    if not path_item:
        return None
    operation = path_item.get(method)
    if not operation:
        return None
    responses = operation.get("responses", {})
    response = responses.get(status) or responses.get("default")
    if not response:
        return None
    if "$ref" in response:
        response = _resolve_ref(spec, response["$ref"])
    content = response.get("content", {}).get("application/json", {})
    schema = content.get("schema")
    if schema:
        return _resolve_all_refs(spec, schema)
    return None


def validate_response(spec: dict, path: str, response_json: dict,
                      method: str = "get", status: str = "200"):
    """Validate an API response against the spec schema.

    Returns a list of validation errors (empty if valid).
    """
    schema = get_response_schema(spec, path, method, status)
    if schema is None:
        return [f"No schema found for {method.upper()} {path} -> {status}"]

    errors = []
    v = Draft202012Validator(schema)
    for error in v.iter_errors(response_json):
        errors.append(f"{error.json_path}: {error.message}")
    return errors
