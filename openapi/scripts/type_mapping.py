"""Map Moonraker doc types to JSON Schema types."""
from __future__ import annotations
import re
from typing import Any


def map_type(doc_type: str) -> dict[str, Any]:
    """Convert a documentation type string to a JSON Schema type dict."""
    doc_type = doc_type.strip()

    # Handle nullable types: "string | null", "int | null", etc.
    nullable_match = re.match(r'^(.+?)\s*\|\s*null$', doc_type)
    if nullable_match:
        base = map_type(nullable_match.group(1).strip())
        if '$ref' in base:
            return {"oneOf": [base, {"type": "null"}]}
        base_type = base.get("type")
        if isinstance(base_type, str):
            base["type"] = [base_type, "null"]
        elif isinstance(base_type, list):
            if "null" not in base_type:
                base["type"].append("null")
        return base

    # Handle nullable suffix: "float?", "string?", "int?", etc.
    nullable_suffix = re.match(r'^(.+?)\?$', doc_type)
    if nullable_suffix:
        base = map_type(nullable_suffix.group(1).strip())
        if '$ref' in base:
            return {"oneOf": [base, {"type": "null"}]}
        base_type = base.get("type")
        if isinstance(base_type, str):
            base["type"] = [base_type, "null"]
        elif isinstance(base_type, list):
            if "null" not in base_type:
                base["type"].append("null")
        return base

    # Handle array types: [string], [object], [int], etc.
    array_match = re.match(r'^\[(.+)\]$', doc_type)
    if array_match:
        inner = array_match.group(1).strip()
        return {
            "type": "array",
            "items": map_type(inner)
        }

    # Simple type mappings
    type_map = {
        "string": {"type": "string"},
        "str": {"type": "string"},
        "int": {"type": "integer"},
        "integer": {"type": "integer"},
        "float": {"type": "number"},
        "number": {"type": "number"},
        "bool": {"type": "boolean"},
        "boolean": {"type": "boolean"},
        "object": {"type": "object"},
        "dict": {"type": "object"},
        "array": {"type": "array"},
        "list": {"type": "array"},
        "null": {"type": "null"},
        "any": {},
    }

    lower = doc_type.lower()
    if lower in type_map:
        return dict(type_map[lower])

    # If unrecognized, default to string
    return {"type": "string"}


def anchor_to_schema_name(anchor_id: str) -> str:
    """Convert an anchor ID like 'gcode-metadata-spec' to a schema name like 'GcodeMetadata'."""
    # Remove leading # if present
    anchor_id = anchor_id.lstrip('#')
    # Remove common suffixes
    for suffix in ['-spec', '-desc', '-info']:
        if anchor_id.endswith(suffix):
            anchor_id = anchor_id[:-len(suffix)]
    # Convert kebab-case to PascalCase
    parts = anchor_id.split('-')
    return ''.join(p.capitalize() for p in parts if p)
