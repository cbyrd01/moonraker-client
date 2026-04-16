"""Generate OpenAPI 3.1 specification from parsed API models."""
from __future__ import annotations
import re
from collections import OrderedDict
from typing import Any, Optional

from models import (
    APIEndpoint, AnchorSpec, Notification, NotificationField,
    Parameter, ResponseField, ResponseSpec,
)
from type_mapping import anchor_to_schema_name, map_type


def generate_openapi(
    endpoints: list[APIEndpoint],
    notifications: list[Notification],
    anchors: list[AnchorSpec],
) -> dict[str, Any]:
    """Generate a complete OpenAPI 3.1 specification."""
    # Build anchor registry for $ref resolution
    anchor_registry: dict[str, AnchorSpec] = {}
    for anchor in anchors:
        anchor_registry[anchor.anchor_id] = anchor
    # Also collect anchors from endpoint response specs
    for ep in endpoints:
        for spec in ep.response_specs:
            if spec.anchor_id and spec.anchor_id not in anchor_registry:
                anchor_registry[spec.anchor_id] = AnchorSpec(
                    anchor_id=spec.anchor_id,
                    title=spec.anchor_title or '',
                    fields=spec.fields,
                    source_file=ep.source_file,
                )

    spec: dict[str, Any] = OrderedDict()
    spec['openapi'] = '3.1.0'
    spec['info'] = {
        'title': 'Moonraker API',
        'description': (
            'Moonraker provides APIs over two protocols, HTTP and JSON-RPC. '
            'Most endpoints have corresponding APIs over both protocols. '
            'This specification documents the HTTP REST API with JSON-RPC '
            'method names included as extensions.'
        ),
        'version': '1.0.0',
        'license': {
            'name': 'GNU General Public License v3.0',
            'identifier': 'GPL-3.0',
        },
    }

    spec['servers'] = [
        {
            'url': 'http://{host}:{port}',
            'description': 'Moonraker Server',
            'variables': {
                'host': {'default': 'localhost'},
                'port': {'default': '7125'},
            },
        }
    ]

    # Security schemes
    spec['components'] = OrderedDict()
    spec['components']['securitySchemes'] = {
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-Api-Key',
            'description': 'API Key authentication',
        },
        'BearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JSON Web Token authentication',
        },
        'OneshotToken': {
            'type': 'apiKey',
            'in': 'query',
            'name': 'token',
            'description': 'Oneshot token for single-use authentication',
        },
    }
    spec['security'] = [
        {'ApiKeyAuth': []},
        {'BearerAuth': []},
    ]

    # Build schemas from anchors
    schemas = build_schemas(anchor_registry)
    if schemas:
        spec['components']['schemas'] = schemas

    # Add error response schema and shared response components
    spec['components']['schemas'] = spec['components'].get('schemas', OrderedDict())
    spec['components']['schemas']['ErrorResponse'] = {
        'type': 'object',
        'properties': {
            'error': {
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer'},
                    'message': {'type': 'string'},
                },
                'required': ['code', 'message'],
            },
        },
        'required': ['error'],
    }
    spec['components']['schemas']['ResultOk'] = {
        'type': 'object',
        'properties': {
            'result': {'type': 'string'},
        },
        'description': 'Standard success response wrapping a string result (typically "ok").',
    }

    # Shared response definitions
    spec['components']['responses'] = OrderedDict()
    spec['components']['responses']['Error'] = {
        'description': 'An error occurred processing the request.',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/ErrorResponse'},
            },
        },
    }
    spec['components']['responses']['ResultOk'] = {
        'description': 'Successful operation',
        'content': {
            'application/json': {
                'schema': {'$ref': '#/components/schemas/ResultOk'},
                'example': {'result': 'ok'},
            },
        },
    }

    # Deduplicate schemas with identical property sets
    _deduplicate_schemas(spec['components']['schemas'])

    # Build paths
    paths = build_paths(endpoints, anchor_registry)

    # Add the JSON-RPC over HTTP endpoint (from introduction.md)
    paths['/server/jsonrpc'] = OrderedDict({
        'post': OrderedDict({
            'summary': 'JSON-RPC over HTTP',
            'operationId': 'postServerJsonrpc',
            'tags': ['Server'],
            'description': (
                'Exposes the JSON-RPC interface over HTTP. Most JSON-RPC methods '
                'with corresponding HTTP APIs are available. Methods exclusive to '
                'other transports, such as Identify Connection, are not available.'
            ),
            'requestBody': {
                'required': True,
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'jsonrpc': {'type': 'string', 'const': '2.0'},
                                'method': {'type': 'string', 'description': 'The JSON-RPC method name'},
                                'params': {'type': 'object', 'description': 'Method parameters'},
                                'id': {'type': 'integer', 'description': 'Request identifier'},
                            },
                            'required': ['jsonrpc', 'method', 'id'],
                        },
                        'example': {
                            'jsonrpc': '2.0',
                            'method': 'printer.info',
                            'id': 5153,
                        },
                    },
                },
            },
            'responses': {
                '200': {
                    'description': 'JSON-RPC response',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'jsonrpc': {'type': 'string'},
                                    'result': {},
                                    'id': {'type': 'integer'},
                                },
                            },
                        },
                    },
                },
            },
        }),
    })

    spec['paths'] = paths

    # Build webhooks from notifications
    webhooks = build_webhooks(notifications, anchor_registry)
    if webhooks:
        spec['webhooks'] = webhooks

    # Add tags based on source files
    tags = build_tags(endpoints, notifications)
    if tags:
        spec['tags'] = tags

    # Prune schemas that are never referenced
    _prune_unreferenced_schemas(spec)

    return spec


def _prune_unreferenced_schemas(spec: dict[str, Any]) -> None:
    """Remove schemas from components/schemas that are never referenced."""
    def collect_refs(obj: Any) -> set[str]:
        refs = set()
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == '$ref' and isinstance(v, str) and v.startswith('#/components/schemas/'):
                    refs.add(v.split('/')[-1])
                refs.update(collect_refs(v))
        elif isinstance(obj, list):
            for v in obj:
                refs.update(collect_refs(v))
        return refs

    schemas = spec['components'].get('schemas', {})
    # Collect all $ref targets from non-schema parts of the spec
    external_refs = set()
    for key in ('paths', 'webhooks'):
        external_refs.update(collect_refs(spec.get(key, {})))
    external_refs.update(collect_refs(spec.get('components', {}).get('responses', {})))

    # Iteratively resolve: keep schemas referenced externally or by other kept schemas
    kept = set(external_refs)
    changed = True
    while changed:
        changed = False
        for name in list(kept):
            if name in schemas:
                new_refs = collect_refs(schemas[name])
                for ref in new_refs:
                    if ref not in kept and ref in schemas:
                        kept.add(ref)
                        changed = True

    to_remove = [name for name in schemas if name not in kept]
    for name in to_remove:
        del schemas[name]


def _deduplicate_schemas(schemas: OrderedDict) -> None:
    """Merge schemas with identical property name sets into a single canonical schema."""
    # Group schemas by their frozenset of property names
    groups: dict[frozenset, list[str]] = {}
    for name, schema in schemas.items():
        props = schema.get('properties', {})
        if not props or name in ('ErrorResponse', 'ResultOk'):
            continue
        key = frozenset(props.keys())
        groups.setdefault(key, []).append(name)

    # For groups with multiple schemas, pick the shortest name as canonical
    for prop_set, names in groups.items():
        if len(names) < 3:
            # Only merge groups of 3+ to avoid over-aggressive dedup
            continue
        canonical = min(names, key=len)
        for name in names:
            if name != canonical:
                # Replace duplicate with a $ref to canonical
                schemas[name] = {
                    'allOf': [{'$ref': f'#/components/schemas/{canonical}'}],
                    'description': schemas[name].get('description', ''),
                }


def build_tags(
    endpoints: list[APIEndpoint],
    notifications: list[Notification],
) -> list[dict[str, str]]:
    """Build tag list from source files."""
    tag_map: dict[str, str] = {}
    file_to_tag = {
        'printer.md': 'Printer',
        'server.md': 'Server',
        'file_manager.md': 'File Manager',
        'authorization.md': 'Authorization',
        'machine.md': 'Machine',
        'history.md': 'History',
        'database.md': 'Database',
        'job_queue.md': 'Job Queue',
        'update_manager.md': 'Update Manager',
        'webcams.md': 'Webcams',
        'announcements.md': 'Announcements',
        'devices.md': 'Devices',
        'extensions.md': 'Extensions',
        'integrations.md': 'Integrations',
        'jsonrpc_notifications.md': 'Notifications',
    }
    for ep in endpoints:
        tag = file_to_tag.get(ep.source_file, ep.source_file.replace('.md', '').replace('_', ' ').title())
        tag_map[tag] = tag
    if notifications:
        tag_map['Notifications'] = 'Notifications'

    return [{'name': name} for name in sorted(tag_map.keys())]


def get_tag_for_file(filename: str) -> str:
    """Get tag name for a source file."""
    file_to_tag = {
        'printer.md': 'Printer',
        'server.md': 'Server',
        'file_manager.md': 'File Manager',
        'authorization.md': 'Authorization',
        'machine.md': 'Machine',
        'history.md': 'History',
        'database.md': 'Database',
        'job_queue.md': 'Job Queue',
        'update_manager.md': 'Update Manager',
        'webcams.md': 'Webcams',
        'announcements.md': 'Announcements',
        'devices.md': 'Devices',
        'extensions.md': 'Extensions',
        'integrations.md': 'Integrations',
        'jsonrpc_notifications.md': 'Notifications',
    }
    return file_to_tag.get(filename, filename.replace('.md', '').replace('_', ' ').title())


def build_schemas(anchor_registry: dict[str, AnchorSpec]) -> OrderedDict:
    """Build component schemas from anchor specs."""
    schemas = OrderedDict()
    for anchor_id, anchor in sorted(anchor_registry.items()):
        schema_name = anchor_to_schema_name(anchor_id)
        if not anchor.fields:
            continue
        schema = fields_to_schema(anchor.fields, anchor_registry)
        if anchor.title:
            schema['description'] = anchor.title
        schemas[schema_name] = schema
    return schemas


def fields_to_schema(
    fields: list[ResponseField],
    anchor_registry: dict[str, AnchorSpec],
) -> dict[str, Any]:
    """Convert a list of ResponseFields to a JSON Schema object."""
    properties = OrderedDict()
    additional_props = None
    for field in fields:
        # Handle _variable_ fields as additionalProperties
        if field.name in ('_variable_', '*variable*'):
            additional_props = _resolve_field_type(field, anchor_registry)
            continue
        prop = _resolve_field_type(field, anchor_registry)
        properties[field.name] = prop

    schema: dict[str, Any] = {'type': 'object'}
    if properties:
        schema['properties'] = properties
    if additional_props is not None:
        schema['additionalProperties'] = additional_props
    return schema


def _resolve_field_type(
    field: ResponseField,
    anchor_registry: dict[str, AnchorSpec],
) -> dict[str, Any]:
    """Resolve a field to its JSON Schema type, using $ref when an anchor is referenced."""
    base_type = map_type(field.type)
    desc = field.description or ''

    # Look for anchor references in description: [Text](#anchor-id) or bare #anchor-id
    ref_match = re.search(r'\[.*?\]\(#([\w-]+)\)', desc)
    if not ref_match:
        ref_match = re.search(r'(?<!\w)#([\w-]+(?:-spec|(?=-)))[\w-]*', desc)

    if ref_match:
        anchor_id = ref_match.group(1)
        # Only use $ref if the anchor exists in the registry and has fields
        if anchor_id in anchor_registry and anchor_registry[anchor_id].fields:
            schema_name = anchor_to_schema_name(anchor_id)
            ref_schema = {'$ref': f'#/components/schemas/{schema_name}'}

            # Handle array of objects → array with $ref items
            if base_type.get('type') == 'array':
                prop: dict[str, Any] = {'type': 'array', 'items': ref_schema}
                if desc:
                    prop['description'] = desc
                return prop

            # Handle object → $ref directly (with allOf if we need description)
            if base_type.get('type') == 'object' or base_type.get('type') == ['object', 'null']:
                if base_type.get('type') == ['object', 'null']:
                    prop = {'oneOf': [ref_schema, {'type': 'null'}]}
                else:
                    prop = dict(ref_schema)
                if desc:
                    prop['description'] = desc
                return prop

    # No anchor reference — use the plain type
    if desc:
        base_type['description'] = desc
    return base_type


def build_paths(
    endpoints: list[APIEndpoint],
    anchor_registry: dict[str, AnchorSpec],
) -> OrderedDict:
    """Build OpenAPI paths from endpoints."""
    paths: OrderedDict = OrderedDict()

    for ep in endpoints:
        if not ep.http_path or not ep.http_method:
            # WebSocket-only or no HTTP info - still include if we have jsonrpc
            if ep.jsonrpc_method and not ep.http_path:
                # Create a synthetic path for websocket-only endpoints
                synthetic_path = '/' + ep.jsonrpc_method.replace('.', '/')
                method = 'post'
                operation = build_operation(ep, anchor_registry, is_synthetic=True)
                if synthetic_path not in paths:
                    paths[synthetic_path] = OrderedDict()
                paths[synthetic_path][method] = operation
            continue

        path = ep.http_path
        method = ep.http_method.lower()

        if path not in paths:
            paths[path] = OrderedDict()

        operation = build_operation(ep, anchor_registry)
        paths[path][method] = operation

    return paths


def build_operation(
    ep: APIEndpoint,
    anchor_registry: dict[str, AnchorSpec],
    is_synthetic: bool = False,
) -> dict[str, Any]:
    """Build an OpenAPI operation from an endpoint."""
    operation: dict[str, Any] = OrderedDict()
    operation['summary'] = ep.section_title
    operation['operationId'] = generate_operation_id(ep)
    operation['tags'] = [get_tag_for_file(ep.source_file)]

    if ep.description:
        desc = ep.description
        if ep.notes:
            desc += '\n\n' + '\n\n'.join(f'**Note:** {n}' for n in ep.notes)
        operation['description'] = desc

    # Extensions
    if ep.jsonrpc_method:
        operation['x-jsonrpc-method'] = ep.jsonrpc_method

    transports = []
    if not ep.websocket_only:
        transports.append('http')
    if not ep.http_only:
        transports.append('websocket')
    if transports:
        operation['x-transports'] = transports

    if is_synthetic:
        operation['x-websocket-only'] = True

    if ep.websocket_only and ep.jsonrpc_title:
        operation['description'] = (
            (operation.get('description', '') + '\n\n').strip()
            + f'\n\n*Transport: {ep.jsonrpc_title}*'
        )

    # Path parameters (from {param} in URL)
    path_params = extract_path_params(ep.http_path or '')
    all_params = []
    if path_params:
        all_params.extend(path_params)

    # Parameters and request body
    if ep.content_type and 'multipart/form-data' in ep.content_type:
        operation['requestBody'] = build_multipart_request_body(ep)
    elif ep.parameters and ep.http_method in ('GET', 'DELETE'):
        all_params.extend(build_parameters(ep.parameters))
    elif ep.parameters and (ep.http_method == 'POST' or is_synthetic):
        operation['requestBody'] = build_request_body(ep)
    elif ep.request_body_example and (ep.http_method == 'POST' or is_synthetic):
        operation['requestBody'] = build_json_request_body(ep)

    if all_params:
        operation['parameters'] = all_params

    # Responses
    operation['responses'] = build_responses(ep, anchor_registry)

    return operation


def generate_operation_id(ep: APIEndpoint) -> str:
    """Generate a unique operation ID from endpoint info."""
    if ep.http_path:
        # Convert path to camelCase operation ID
        parts = ep.http_path.strip('/').split('/')
        method = (ep.http_method or 'get').lower()
        # Combine method and path parts
        op_id = method
        for part in parts:
            part = part.strip('{}')
            op_id += part.capitalize().replace('_', '')
        return op_id
    elif ep.jsonrpc_method:
        return ep.jsonrpc_method.replace('.', '_')
    return ep.section_title.lower().replace(' ', '_')


def extract_path_params(path: str) -> list[dict[str, Any]]:
    """Extract path parameters from URL template like /files/{root}/{filename}."""
    params = []
    for match in re.finditer(r'\{(\w+)\}', path):
        param_name = match.group(1)
        params.append(OrderedDict([
            ('name', param_name),
            ('in', 'path'),
            ('required', True),
            ('schema', {'type': 'string'}),
        ]))
    return params


def build_parameters(params: list[Parameter]) -> list[dict[str, Any]]:
    """Build OpenAPI parameter objects for query parameters."""
    result = []
    for param in params:
        p: dict[str, Any] = OrderedDict()
        name = param.name.strip('*')  # Remove wildcard markers
        p['name'] = name
        p['in'] = 'query'
        desc = param.description or ''
        if param.name.startswith('*') and param.name.endswith('*'):
            desc = f'(Dynamic parameter name) {desc}'.strip()
        if desc:
            p['description'] = desc
        p['required'] = param.required
        schema = map_type(param.type)
        # Handle null type - these are typically dynamic key parameters
        if schema.get('type') == 'null':
            schema = {'type': ['string', 'null']}
        if param.default and not param.required:
            default = coerce_default(param.default, param.type)
            if default is not None:
                schema['default'] = default
        p['schema'] = schema
        result.append(p)
    return result


def build_request_body(ep: APIEndpoint) -> dict[str, Any]:
    """Build a JSON request body from parameters."""
    properties = OrderedDict()
    required = []
    for param in ep.parameters:
        prop = map_type(param.type)
        if param.description:
            prop['description'] = param.description
        if param.default and not param.required:
            prop['default'] = coerce_default(param.default, param.type)
        properties[param.name] = prop
        if param.required:
            required.append(param.name)

    schema: dict[str, Any] = {
        'type': 'object',
        'properties': properties,
    }
    if required:
        schema['required'] = required

    body: dict[str, Any] = {
        'content': {
            'application/json': {
                'schema': schema,
            },
        },
    }

    if ep.request_body_example:
        body['content']['application/json']['example'] = ep.request_body_example

    return body


def build_multipart_request_body(ep: APIEndpoint) -> dict[str, Any]:
    """Build a multipart/form-data request body."""
    properties: dict[str, Any] = OrderedDict()
    properties['file'] = {
        'type': 'string',
        'format': 'binary',
        'description': 'The file to upload',
    }
    required = ['file']

    for param in ep.parameters:
        prop = map_type(param.type)
        if param.description:
            prop['description'] = param.description
        if param.default and not param.required:
            prop['default'] = coerce_default(param.default, param.type)
        properties[param.name] = prop
        if param.required:
            required.append(param.name)

    return {
        'content': {
            'multipart/form-data': {
                'schema': {
                    'type': 'object',
                    'properties': properties,
                    'required': required,
                },
            },
        },
    }


def build_json_request_body(ep: APIEndpoint) -> dict[str, Any]:
    """Build a JSON request body from example."""
    body: dict[str, Any] = {
        'content': {
            'application/json': {
                'schema': {'type': 'object'},
            },
        },
    }
    if ep.request_body_example:
        body['content']['application/json']['example'] = ep.request_body_example
    return body


def build_responses(
    ep: APIEndpoint,
    anchor_registry: dict[str, AnchorSpec],
) -> dict[str, Any]:
    """Build response objects."""
    responses: dict[str, Any] = OrderedDict()
    is_upload = bool(ep.content_type and 'multipart/form-data' in ep.content_type)

    if is_upload and (ep.response_specs or ep.response_example is not None):
        # Upload endpoints return 201 without a result wrapper
        if ep.response_specs:
            result_schema = build_result_schema(ep.response_specs, anchor_registry)
        elif ep.response_example is not None:
            result_schema = infer_schema_from_example(ep.response_example)
        else:
            result_schema = {'type': 'object'}
        content: dict[str, Any] = {'schema': result_schema}
        if ep.response_example is not None:
            content['example'] = ep.response_example
        responses['201'] = {
            'description': 'File successfully uploaded',
            'content': {
                'application/json': content,
            },
        }
        responses['default'] = {'$ref': '#/components/responses/Error'}
        return responses

    if ep.response_is_string:
        # Use shared ResultOk response reference
        responses['200'] = {'$ref': '#/components/responses/ResultOk'}
    elif ep.response_specs:
        # Build schema from response spec
        result_schema = build_result_schema(ep.response_specs, anchor_registry)
        wrapped_schema: dict[str, Any] = {
            'type': 'object',
            'properties': {
                'result': result_schema,
            },
        }
        content: dict[str, Any] = {'schema': wrapped_schema}
        if ep.response_example is not None:
            content['example'] = {'result': ep.response_example}

        responses['200'] = {
            'description': 'Successful operation',
            'content': {
                'application/json': content,
            },
        }
    elif ep.response_example is not None:
        # We have an example but no spec - infer schema from example
        wrapped_schema = {
            'type': 'object',
            'properties': {
                'result': infer_schema_from_example(ep.response_example),
            },
        }
        content = {'schema': wrapped_schema}
        content['example'] = {'result': ep.response_example}

        responses['200'] = {
            'description': 'Successful operation',
            'content': {
                'application/json': content,
            },
        }
    else:
        # No response info at all
        responses['200'] = {
            'description': 'Successful operation',
        }

    # Shared error response
    responses['default'] = {'$ref': '#/components/responses/Error'}

    return responses


def build_result_schema(
    specs: list[ResponseSpec],
    anchor_registry: dict[str, AnchorSpec],
) -> dict[str, Any]:
    """Build JSON Schema from response specs."""
    if not specs:
        return {'type': 'object'}

    # Check preamble for array indicator
    first_spec = specs[0]
    is_array = False
    if first_spec.preamble:
        lower_preamble = first_spec.preamble.lower()
        if 'array of' in lower_preamble or 'result is an array' in lower_preamble:
            is_array = True

    # If spec has an anchor, we can reference it
    if first_spec.anchor_id and first_spec.fields:
        schema_name = anchor_to_schema_name(first_spec.anchor_id)
        ref_schema: dict[str, Any] = {'$ref': f'#/components/schemas/{schema_name}'}
        if is_array:
            return {'type': 'array', 'items': ref_schema}
        return ref_schema

    # Build inline schema from fields
    if first_spec.fields:
        schema = fields_to_schema_inline(first_spec.fields, anchor_registry)
        if is_array:
            return {'type': 'array', 'items': schema}
        return schema

    # Check if preamble references another spec
    if first_spec.preamble:
        ref_match = re.search(r'#([\w-]+)', first_spec.preamble)
        if ref_match:
            ref_id = ref_match.group(1)
            schema_name = anchor_to_schema_name(ref_id)
            ref_schema = {'$ref': f'#/components/schemas/{schema_name}'}
            if is_array:
                return {'type': 'array', 'items': ref_schema}
            return ref_schema

    return {'type': 'object'}


def fields_to_schema_inline(
    fields: list[ResponseField],
    anchor_registry: dict[str, AnchorSpec],
) -> dict[str, Any]:
    """Convert response fields to inline JSON Schema."""
    properties = OrderedDict()
    additional_props = None
    for field in fields:
        if field.name in ('_variable_', '*variable*'):
            additional_props = _resolve_field_type(field, anchor_registry)
            continue
        prop = _resolve_field_type(field, anchor_registry)
        properties[field.name] = prop

    schema: dict[str, Any] = {'type': 'object'}
    if properties:
        schema['properties'] = properties
    if additional_props is not None:
        schema['additionalProperties'] = additional_props
    return schema


def infer_schema_from_example(example: Any) -> dict[str, Any]:
    """Infer a basic JSON Schema from an example value."""
    if isinstance(example, dict):
        properties = OrderedDict()
        for key, value in example.items():
            properties[key] = infer_schema_from_example(value)
        return {'type': 'object', 'properties': properties}
    elif isinstance(example, list):
        if example:
            return {'type': 'array', 'items': infer_schema_from_example(example[0])}
        return {'type': 'array'}
    elif isinstance(example, bool):
        return {'type': 'boolean'}
    elif isinstance(example, int):
        return {'type': 'integer'}
    elif isinstance(example, float):
        return {'type': 'number'}
    elif isinstance(example, str):
        return {'type': 'string'}
    elif example is None:
        return {'type': 'null'}
    return {}


def build_webhooks(
    notifications: list[Notification],
    anchor_registry: dict[str, AnchorSpec],
) -> OrderedDict:
    """Build OpenAPI webhooks section from JSON-RPC notifications."""
    webhooks = OrderedDict()

    for notif in notifications:
        if not notif.method_name:
            continue

        operation: dict[str, Any] = OrderedDict()
        operation['summary'] = notif.section_title
        operation['tags'] = ['Notifications']
        operation['x-jsonrpc-notification'] = True

        if notif.description:
            operation['description'] = notif.description

        # Build the notification payload schema
        if notif.fields:
            params_schema = build_notification_params_schema(notif.fields)
            payload = {
                'type': 'object',
                'properties': {
                    'jsonrpc': {'type': 'string', 'const': '2.0'},
                    'method': {'type': 'string', 'const': notif.method_name},
                    'params': params_schema,
                },
                'required': ['jsonrpc', 'method'],
            }
        else:
            payload = {
                'type': 'object',
                'properties': {
                    'jsonrpc': {'type': 'string', 'const': '2.0'},
                    'method': {'type': 'string', 'const': notif.method_name},
                },
                'required': ['jsonrpc', 'method'],
            }

        content: dict[str, Any] = {'schema': payload}
        if notif.example:
            content['example'] = notif.example

        operation['requestBody'] = {
            'content': {
                'application/json': content,
            },
        }

        operation['responses'] = {
            '200': {'description': 'Notification received'},
        }

        webhooks[notif.method_name] = {'post': operation}

    return webhooks


def build_notification_params_schema(fields: list[NotificationField]) -> dict[str, Any]:
    """Build schema for notification params array."""
    if not fields:
        return {'type': 'array'}

    items: list[dict[str, Any]] = []
    for field in sorted(fields, key=lambda f: f.position):
        item = map_type(field.type)
        if field.description:
            item['description'] = field.description
        items.append(item)

    if len(items) == 1:
        return {
            'type': 'array',
            'items': items[0],
            'minItems': 1,
            'maxItems': 1,
        }

    return {
        'type': 'array',
        'prefixItems': items,
        'minItems': len(items),
    }


def coerce_default(default_str: str, type_str: str) -> Any:
    """Coerce a default value string to its appropriate type."""
    if not default_str:
        return None
    # Remove backticks and surrounding quotes
    default_str = default_str.strip('`')
    default_str = default_str.strip('"').strip("'")
    # Handle null/None/undefined
    if default_str.lower() in ('null', 'none', 'undefined'):
        return None
    # Handle descriptive defaults (surrounded by *, or containing non-numeric text for numeric types)
    lower_type = type_str.lower().strip()
    try:
        if lower_type in ('int', 'integer'):
            return int(default_str)
        elif lower_type in ('float', 'number'):
            return float(default_str)
        elif lower_type in ('bool', 'boolean'):
            return default_str.lower() in ('true', '1', 'yes')
        else:
            return default_str
    except (ValueError, TypeError):
        # Can't coerce to expected type - this is a descriptive default, skip it
        return None
