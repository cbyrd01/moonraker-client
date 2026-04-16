#!/usr/bin/env python3
"""Generate OpenAPI 3.1 specification from Moonraker API documentation."""
from __future__ import annotations
import argparse
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parser import parse_all_docs
from generator import generate_openapi

try:
    import yaml

    # Configure YAML to preserve OrderedDict ordering
    def represent_ordereddict(dumper, data):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())

    yaml.add_representer(OrderedDict, represent_ordereddict)

    # Custom string representer for multi-line strings
    def represent_str(dumper, data):
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, represent_str)

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    docs_dir = project_root / 'third_party' / 'moonraker' / 'docs' / 'external_api'
    output_dir = script_dir.parent

    argparser = argparse.ArgumentParser(description='Generate OpenAPI spec from Moonraker docs')
    argparser.add_argument(
        '--docs-dir', type=str, default=str(docs_dir),
        help='Path to external_api docs directory',
    )
    argparser.add_argument(
        '--output', type=str, default=str(output_dir / 'openapi.yaml'),
        help='Output file path',
    )
    argparser.add_argument(
        '--format', choices=['yaml', 'json'], default='yaml',
        help='Output format',
    )
    argparser.add_argument(
        '--stats', action='store_true',
        help='Print statistics about parsed endpoints',
    )
    args = argparser.parse_args()

    if args.format == 'yaml' and not HAS_YAML:
        print("ERROR: pyyaml is required for YAML output. Install with: pip install pyyaml")
        sys.exit(1)

    print(f"Parsing docs from: {args.docs_dir}")
    endpoints, notifications, anchors = parse_all_docs(args.docs_dir)

    if args.stats:
        print_stats(endpoints, notifications, anchors)

    print(f"Parsed {len(endpoints)} endpoints, {len(notifications)} notifications, "
          f"{len(anchors)} anchor specs")

    print("Generating OpenAPI specification...")
    spec = generate_openapi(endpoints, notifications, anchors)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    if args.format == 'yaml':
        with open(args.output, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    else:
        with open(args.output, 'w') as f:
            json.dump(spec, f, indent=2)

    print(f"OpenAPI spec written to: {args.output}")

    # Count paths and operations
    path_count = len(spec.get('paths', {}))
    op_count = sum(
        len([m for m in path_ops if m in ('get', 'post', 'delete', 'put', 'patch')])
        for path_ops in spec.get('paths', {}).values()
    )
    webhook_count = len(spec.get('webhooks', {}))
    schema_count = len(spec.get('components', {}).get('schemas', {}))

    print(f"  Paths: {path_count}")
    print(f"  Operations: {op_count}")
    print(f"  Webhooks: {webhook_count}")
    print(f"  Schemas: {schema_count}")


def print_stats(endpoints, notifications, anchors):
    """Print detailed statistics."""
    print("\n=== Parsing Statistics ===")
    print(f"\nEndpoints by source file:")
    by_file: dict[str, list] = {}
    for ep in endpoints:
        by_file.setdefault(ep.source_file, []).append(ep)
    for fname, eps in sorted(by_file.items()):
        print(f"  {fname}: {len(eps)} endpoints")
        for ep in eps:
            method = ep.http_method or 'WS'
            path = ep.http_path or ep.jsonrpc_method or '?'
            params = len(ep.parameters)
            has_response = bool(ep.response_example or ep.response_specs or ep.response_is_string)
            print(f"    {method:6s} {path:50s} params={params} response={'Y' if has_response else 'N'}")

    print(f"\nNotifications: {len(notifications)}")
    for n in notifications:
        print(f"  {n.method_name}: {len(n.fields)} fields")

    print(f"\nAnchor specs: {len(anchors)}")
    for a in anchors:
        print(f"  #{a.anchor_id} ({a.title}): {len(a.fields)} fields")
    print()


if __name__ == '__main__':
    main()
