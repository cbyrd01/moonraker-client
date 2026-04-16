#!/usr/bin/env python3
"""Code generator that reads the Moonraker OpenAPI spec and produces Python client code.

Generates:
- Model dataclasses from components/schemas
- API mixin method stubs from paths

Usage:
    python tools/generate.py [path/to/openapi.yaml]

Output goes to stdout as a report. The actual generated files are written
to src/moonraker_client/models/ and src/moonraker_client/api/.
"""

from __future__ import annotations

import re
import sys
import textwrap
from pathlib import Path
from typing import Any

import yaml


# Mapping of OpenAPI tags to Python module names and class prefixes
TAG_MODULE_MAP: dict[str, tuple[str, str]] = {
    "Printer": ("printer", "Printer"),
    "Server": ("server", "Server"),
    "File Manager": ("files", "Files"),
    "History": ("history", "History"),
    "Job Queue": ("jobs", "Jobs"),
    "Machine": ("machine", "Machine"),
    "Authorization": ("auth", "Auth"),
    "Database": ("database", "Database"),
    "Update Manager": ("updates", "Updates"),
    "Devices": ("devices", "Devices"),
    "Webcams": ("webcams", "Webcams"),
    "Announcements": ("announcements", "Announcements"),
    "Integrations": ("integrations", "Integrations"),
    "Extensions": ("extensions", "Extensions"),
    "Notifications": ("notifications", "Notifications"),
}

# OpenAPI type to Python type annotation mapping
TYPE_MAP: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "object": "dict[str, Any]",
    "array": "list[Any]",
}


def load_spec(path: str) -> dict[str, Any]:
    """Load and return the OpenAPI YAML spec."""
    with open(path) as f:
        return yaml.safe_load(f)


def operation_id_to_method_name(op_id: str) -> str:
    """Convert an operationId like 'getPrinterInfo' to 'printer_info'.

    Strips common HTTP method prefixes and converts camelCase to snake_case.
    """
    # Strip HTTP method prefix
    for prefix in ("get", "post", "delete", "put", "patch"):
        if op_id.startswith(prefix) and len(op_id) > len(prefix):
            op_id = op_id[len(prefix):]
            break

    # Insert underscore before uppercase letters and lowercase everything
    result = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", op_id)
    result = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", result)
    return result.lower().strip("_")


def resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Resolve a $ref pointer in the spec."""
    parts = ref.lstrip("#/").split("/")
    current = spec
    for part in parts:
        current = current[part]
    return current


def get_python_type(schema: dict[str, Any], spec: dict[str, Any]) -> str:
    """Convert an OpenAPI schema to a Python type annotation string."""
    if "$ref" in schema:
        resolved = resolve_ref(spec, schema["$ref"])
        ref_name = schema["$ref"].split("/")[-1]
        return ref_name
    schema_type = schema.get("type", "object")
    if isinstance(schema_type, list):
        # Handle nullable types like ["string", "null"]
        types = [t for t in schema_type if t != "null"]
        schema_type = types[0] if types else "object"
    if schema_type == "array":
        items = schema.get("items", {})
        item_type = get_python_type(items, spec)
        return f"list[{item_type}]"
    return TYPE_MAP.get(schema_type, "Any")


def extract_parameters(operation: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract and normalize parameters from an operation."""
    params = []
    for param in operation.get("parameters", []):
        if "$ref" in param:
            param = resolve_ref(spec, param["$ref"])
        schema = param.get("schema", {})
        params.append({
            "name": param["name"],
            "in": param["in"],
            "required": param.get("required", False),
            "type": get_python_type(schema, spec),
            "default": schema.get("default"),
            "description": param.get("description", ""),
        })
    return params


def extract_body_params(operation: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract parameters from a request body."""
    body = operation.get("requestBody", {})
    if not body:
        return []
    content = body.get("content", {})

    # JSON body
    json_content = content.get("application/json", {})
    if json_content:
        schema = json_content.get("schema", {})
        if "$ref" in schema:
            schema = resolve_ref(spec, schema["$ref"])
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        params = []
        for name, prop_schema in props.items():
            params.append({
                "name": name,
                "in": "body",
                "required": name in required,
                "type": get_python_type(prop_schema, spec),
                "default": prop_schema.get("default"),
                "description": prop_schema.get("description", ""),
            })
        return params

    # Multipart form data
    form_content = content.get("multipart/form-data", {})
    if form_content:
        schema = form_content.get("schema", {})
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        params = []
        for name, prop_schema in props.items():
            fmt = prop_schema.get("format", "")
            ptype = "Any" if fmt == "binary" else get_python_type(prop_schema, spec)
            params.append({
                "name": name,
                "in": "form",
                "required": name in required,
                "type": ptype,
                "default": prop_schema.get("default"),
                "description": prop_schema.get("description", ""),
            })
        return params

    return []


def generate_method_signature(
    method_name: str,
    params: list[dict[str, Any]],
    body_params: list[dict[str, Any]],
    is_async: bool = False,
) -> str:
    """Generate a Python method signature string."""
    prefix = "async " if is_async else ""
    all_params = params + body_params

    # Sort: required first, then optional
    required_params = [p for p in all_params if p["required"]]
    optional_params = [p for p in all_params if not p["required"]]

    sig_parts = ["self"]
    for p in required_params:
        sig_parts.append(f"{p['name']}: {p['type']}")
    for p in optional_params:
        default = repr(p["default"]) if p["default"] is not None else "None"
        ptype = p["type"] if p["default"] is not None else f"{p['type']} | None"
        sig_parts.append(f"{p['name']}: {ptype} = {default}")

    sig = ", ".join(sig_parts)
    return f"    {prefix}def {method_name}({sig}) -> Any:"


def generate_method_body(
    http_method: str,
    path: str,
    params: list[dict[str, Any]],
    body_params: list[dict[str, Any]],
    is_async: bool = False,
) -> str:
    """Generate the method body that calls self._request()."""
    await_prefix = "await " if is_async else ""

    # Build path with format substitution for path params
    path_params = [p for p in params if p["in"] == "path"]
    if path_params:
        for pp in path_params:
            path = path.replace(f"{{{pp['name']}}}", f"{{{pp['name']}}}")
        path_expr = f'f"{path}"'
    else:
        path_expr = f'"{path}"'

    # Query parameters
    query_params = [p for p in params if p["in"] == "query"]
    # Body parameters (JSON)
    json_body_params = [p for p in body_params if p["in"] == "body"]
    # Form parameters
    form_params = [p for p in body_params if p["in"] == "form"]

    lines = []

    if query_params:
        lines.append("        params: dict[str, Any] = {}")
        for qp in query_params:
            if qp["required"]:
                lines.append(f'        params["{qp["name"]}"] = {qp["name"]}')
            else:
                lines.append(f"        if {qp['name']} is not None:")
                lines.append(f'            params["{qp["name"]}"] = {qp["name"]}')

    if json_body_params:
        lines.append("        body: dict[str, Any] = {}")
        for bp in json_body_params:
            if bp["required"]:
                lines.append(f'        body["{bp["name"]}"] = {bp["name"]}')
            else:
                lines.append(f"        if {bp['name']} is not None:")
                lines.append(f'            body["{bp["name"]}"] = {bp["name"]}')

    # Build the _request call
    call_parts = [f'"{http_method.upper()}"', path_expr]
    kwargs = []
    if query_params:
        kwargs.append("params=params")
    if json_body_params:
        kwargs.append("json=body")

    if kwargs:
        call = f"{await_prefix}self._request({', '.join(call_parts)}, {', '.join(kwargs)})"
    else:
        call = f"{await_prefix}self._request({', '.join(call_parts)})"

    lines.append(f"        return {call}")
    return "\n".join(lines)


def generate_docstring(
    summary: str,
    description: str | None,
    params: list[dict[str, Any]],
    body_params: list[dict[str, Any]],
    jsonrpc_method: str | None,
) -> str:
    """Generate a docstring for a method."""
    lines = [f'        """{summary}']

    if description:
        lines.append("")
        for line in description.strip().split("\n"):
            lines.append(f"        {line.rstrip()}")

    all_params = params + body_params
    if all_params:
        lines.append("")
        lines.append("        Args:")
        for p in all_params:
            desc = p.get("description", "").split("\n")[0][:80]
            opt = "" if p["required"] else " (optional)"
            lines.append(f"            {p['name']}: {desc}{opt}")

    if jsonrpc_method:
        lines.append("")
        lines.append(f"        JSON-RPC method: {jsonrpc_method}")

    lines.append('        """')
    return "\n".join(lines)


def categorize_endpoints(spec: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group endpoints by their tag/module."""
    categories: dict[str, list[dict[str, Any]]] = {}

    for path, path_item in spec.get("paths", {}).items():
        for method in ("get", "post", "put", "delete", "patch"):
            operation = path_item.get(method)
            if not operation:
                continue

            tags = operation.get("tags", ["Other"])
            tag = tags[0] if tags else "Other"
            module_name = TAG_MODULE_MAP.get(tag, ("other", "Other"))[0]

            endpoint = {
                "path": path,
                "method": method,
                "operation": operation,
                "tag": tag,
                "module": module_name,
            }

            if module_name not in categories:
                categories[module_name] = []
            categories[module_name].append(endpoint)

    return categories


def generate_module(
    module_name: str,
    class_prefix: str,
    endpoints: list[dict[str, Any]],
    spec: dict[str, Any],
) -> str:
    """Generate a complete Python module for an API category."""
    lines = [
        f'"""API endpoints for {class_prefix} operations.',
        "",
        f"Auto-generated from OpenAPI spec. Hand-tune as needed.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any",
        "",
        "",
    ]

    # Generate sync mixin
    lines.append(f"class {class_prefix}Mixin:")
    lines.append(f'    """Synchronous {class_prefix.lower()} API methods."""')
    lines.append("")

    seen_methods: set[str] = set()

    for ep in endpoints:
        operation = ep["operation"]
        op_id = operation.get("operationId", "")
        if not op_id:
            continue

        method_name = operation_id_to_method_name(op_id)

        # Handle duplicate method names (GET/POST for same logical operation)
        if method_name in seen_methods:
            continue
        seen_methods.add(method_name)

        summary = operation.get("summary", "")
        description = operation.get("description")
        jsonrpc = operation.get("x-jsonrpc-method")
        params = extract_parameters(operation, spec)
        body_params = extract_body_params(operation, spec)

        sig = generate_method_signature(method_name, params, body_params, is_async=False)
        docstring = generate_docstring(summary, description, params, body_params, jsonrpc)
        body = generate_method_body(ep["method"], ep["path"], params, body_params, is_async=False)

        lines.append(sig)
        lines.append(docstring)
        lines.append(body)
        lines.append("")

    # Generate async mixin
    lines.append("")
    lines.append(f"class Async{class_prefix}Mixin:")
    lines.append(f'    """Asynchronous {class_prefix.lower()} API methods."""')
    lines.append("")

    seen_methods.clear()

    for ep in endpoints:
        operation = ep["operation"]
        op_id = operation.get("operationId", "")
        if not op_id:
            continue

        method_name = operation_id_to_method_name(op_id)
        if method_name in seen_methods:
            continue
        seen_methods.add(method_name)

        summary = operation.get("summary", "")
        description = operation.get("description")
        jsonrpc = operation.get("x-jsonrpc-method")
        params = extract_parameters(operation, spec)
        body_params = extract_body_params(operation, spec)

        sig = generate_method_signature(method_name, params, body_params, is_async=True)
        docstring = generate_docstring(summary, description, params, body_params, jsonrpc)
        body = generate_method_body(ep["method"], ep["path"], params, body_params, is_async=True)

        lines.append(sig)
        lines.append(docstring)
        lines.append(body)
        lines.append("")

    return "\n".join(lines)


def generate_models(spec: dict[str, Any]) -> str:
    """Generate dataclass models from components/schemas."""
    schemas = spec.get("components", {}).get("schemas", {})

    lines = [
        '"""Data models generated from the Moonraker OpenAPI spec.',
        "",
        "Auto-generated from OpenAPI spec. Hand-tune as needed.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass, field",
        "from typing import Any",
        "",
        "",
    ]

    for name, schema in schemas.items():
        if schema.get("type") != "object":
            continue

        props = schema.get("properties", {})
        desc = schema.get("description", name)

        lines.append("@dataclass")
        lines.append(f"class {name}:")
        lines.append(f'    """{desc}"""')
        lines.append("")

        if not props:
            lines.append("    pass")
            lines.append("")
            lines.append("")
            continue

        for prop_name, prop_schema in props.items():
            ptype = get_python_type(prop_schema, spec)
            prop_desc = prop_schema.get("description", "")
            # Make all fields optional with defaults
            lines.append(f"    {prop_name}: {ptype} | None = None")

        lines.append("")

        # Add from_dict classmethod
        lines.append("    @classmethod")
        lines.append(f"    def from_dict(cls, data: dict[str, Any]) -> {name}:")
        lines.append(f'        """Create {name} from a dict, ignoring extra keys."""')
        field_names = list(props.keys())
        lines.append("        return cls(")
        for fn in field_names:
            lines.append(f'            {fn}=data.get("{fn}"),')
        lines.append("        )")
        lines.append("")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    spec_path = sys.argv[1] if len(sys.argv) > 1 else str(
        Path(__file__).parent.parent / "openapi" / "openapi.yaml"
    )

    print(f"Loading spec from: {spec_path}")
    spec = load_spec(spec_path)

    categories = categorize_endpoints(spec)

    print(f"\nFound {sum(len(v) for v in categories.values())} endpoints in {len(categories)} categories:")
    for cat, endpoints in sorted(categories.items()):
        print(f"  {cat}: {len(endpoints)} endpoints")
        for ep in endpoints:
            op_id = ep["operation"].get("operationId", "no-op-id")
            method_name = operation_id_to_method_name(op_id)
            print(f"    {ep['method'].upper()} {ep['path']} -> {method_name}()")

    # Generate models
    models_code = generate_models(spec)
    models_path = Path(__file__).parent.parent / "src" / "moonraker_client" / "models" / "generated.py"
    models_path.write_text(models_code)
    print(f"\nWrote models to: {models_path}")

    # Generate API modules
    for module_name, endpoints in categories.items():
        if module_name not in TAG_MODULE_MAP.values():
            # Look up by module name
            class_prefix = module_name.title()
            for tag, (mod, prefix) in TAG_MODULE_MAP.items():
                if mod == module_name:
                    class_prefix = prefix
                    break
        else:
            class_prefix = module_name.title()

        # Find the correct class prefix
        for tag, (mod, prefix) in TAG_MODULE_MAP.items():
            if mod == module_name:
                class_prefix = prefix
                break

        module_code = generate_module(module_name, class_prefix, endpoints, spec)
        module_path = (
            Path(__file__).parent.parent
            / "src"
            / "moonraker_client"
            / "api"
            / f"{module_name}.py"
        )
        module_path.write_text(module_code)
        print(f"Wrote API module: {module_path}")

    print("\nDone! Review and hand-tune the generated files.")


if __name__ == "__main__":
    main()
