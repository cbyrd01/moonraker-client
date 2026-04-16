"""Parse Moonraker API documentation markdown files into structured models."""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any, Optional

from models import (
    APIEndpoint, AnchorSpec, Notification, NotificationField,
    Parameter, ResponseField, ResponseSpec,
)


def parse_all_docs(docs_dir: str) -> tuple[list[APIEndpoint], list[Notification], list[AnchorSpec]]:
    """Parse all markdown files in the docs directory."""
    all_endpoints: list[APIEndpoint] = []
    all_notifications: list[Notification] = []
    all_anchors: list[AnchorSpec] = []

    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(docs_dir, filename)
        if filename == 'introduction.md':
            # Introduction has tutorial content, not standard endpoint definitions
            # But it does have the /server/jsonrpc endpoint which we add manually
            continue
        endpoints, notifications, anchors = parse_file(filepath)
        all_endpoints.extend(endpoints)
        all_notifications.extend(notifications)
        all_anchors.extend(anchors)

    return all_endpoints, all_notifications, all_anchors


def parse_file(filepath: str) -> tuple[list[APIEndpoint], list[Notification], list[AnchorSpec]]:
    """Parse a single markdown file."""
    filename = os.path.basename(filepath)
    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.split('\n')
    sections = split_into_sections(lines)

    endpoints: list[APIEndpoint] = []
    notifications: list[Notification] = []
    file_anchors: list[AnchorSpec] = []

    # Collect any anchors defined outside of sections (e.g., at top of file)
    # like the permissions table in file_manager.md
    pre_section_text = get_pre_section_text(lines)
    file_anchors.extend(extract_standalone_anchors(pre_section_text, filename))

    for section in sections:
        title = section['title']
        body = section['body']
        level = section['level']

        # Check if this section has notification content (method name block)
        if has_notification_spec(body) or has_notification_method(body):
            notif = parse_notification_section(title, body, filename)
            if notif and notif.method_name:
                notifications.append(notif)
            continue

        # Check if this section has API request blocks
        if has_api_request(body):
            result = parse_endpoint_section(title, body, filename)
            if result:
                if isinstance(result, list):
                    endpoints.extend(result)
                else:
                    endpoints.append(result)

        # Extract any anchor specs defined in this section
        anchors = extract_anchors_from_body(body, filename)
        file_anchors.extend(anchors)

    return endpoints, notifications, file_anchors


def get_pre_section_text(lines: list[str]) -> str:
    """Get text before the first H2/H3 section."""
    result = []
    for line in lines:
        if re.match(r'^#{2,3}\s', line):
            break
        result.append(line)
    return '\n'.join(result)


def split_into_sections(lines: list[str]) -> list[dict]:
    """Split markdown into sections by H2/H3 headers."""
    sections = []
    current_section = None

    for line in lines:
        header_match = re.match(r'^(#{2,3})\s+(.+)$', line)
        if header_match:
            if current_section:
                sections.append(current_section)
            level = len(header_match.group(1))
            current_section = {
                'title': header_match.group(2).strip(),
                'level': level,
                'body': []
            }
        elif current_section is not None:
            current_section['body'].append(line)

    if current_section:
        sections.append(current_section)

    # Join body lines
    for section in sections:
        section['body'] = '\n'.join(section['body'])

    return sections


def has_api_request(body: str) -> bool:
    """Check if section contains API request code blocks."""
    return '.apirequest' in body


def has_notification_spec(body: str) -> bool:
    """Check if section contains notification spec."""
    return 'api-notification-spec' in body


def has_notification_method(body: str) -> bool:
    """Check if section contains a notification method name block."""
    return 'Notification Method Name' in body


def parse_endpoint_section(title: str, body: str, filename: str) -> Optional[APIEndpoint | list[APIEndpoint]]:
    """Parse an endpoint section into one or more APIEndpoint models.

    Some sections document multiple HTTP methods (e.g., POST and GET) for the
    same endpoint. In these cases, we return a list.
    """
    description = extract_description(body)
    notes = extract_notes(body)
    parameters = extract_parameters(body)
    response_specs = extract_response_specs(body)

    # Parse all request blocks
    http_blocks = extract_code_blocks(body, '.apirequest')

    # Collect HTTP method/path pairs and JSON-RPC method
    http_requests: list[tuple[str, str, Optional[str], Optional[dict]]] = []  # (method, path, content_type, body_example)
    jsonrpc_method = None
    websocket_only = False
    http_only = False
    jsonrpc_title = ''

    for block in http_blocks:
        if '.http' in block['classes']:
            method, path, content_type, body_example = extract_http_info(block)
            if method and path:
                http_requests.append((method, path, content_type, body_example))
        elif ('.json' in block['classes'] or '{json' in block['classes']
              or 'json' in block.get('raw_attrs', '').split()[0:1]):
            content = block['content'].strip()
            if content.lower() != 'not available':
                try:
                    data = json.loads(content)
                    if isinstance(data, dict) and 'method' in data:
                        jsonrpc_method = data['method']
                except json.JSONDecodeError:
                    # Fallback: extract method via regex (handles malformed JSON)
                    method_match = re.search(r'"method"\s*:\s*"([^"]+)"', content)
                    if method_match:
                        jsonrpc_method = method_match.group(1)
            else:
                http_only = True
        elif '.text' in block['classes']:
            block_title = block.get('title', '').lower()
            if 'http' in block_title:
                if 'not available' in block['content'].lower():
                    pass  # HTTP not available
                else:
                    method, path, content_type, body_example = extract_http_info(block)
                    if method and path:
                        http_requests.append((method, path, content_type, body_example))
            elif 'json-rpc' in block_title or 'jsonrpc' in block_title:
                if 'not available' in block['content'].lower():
                    http_only = True

    # Check for websocket-only transport info
    for block in http_blocks:
        block_title = block.get('title', '')
        if 'websocket' in block_title.lower() and ('only' in block_title.lower() or 'unix' in block_title.lower()):
            websocket_only = True
            jsonrpc_title = block_title

    # Parse response info
    response_example = None
    response_is_string = False
    response_string = None
    response_blocks = extract_code_blocks(body, '.apiresponse')
    for block in response_blocks:
        if '.json' in block['classes']:
            try:
                response_example = json.loads(block['content'])
            except json.JSONDecodeError:
                cleaned = re.sub(r',\s*}', '}', block['content'])
                cleaned = re.sub(r',\s*\]', ']', cleaned)
                try:
                    response_example = json.loads(cleaned)
                except json.JSONDecodeError:
                    pass
        elif '.text' in block['classes']:
            content = block['content'].strip().strip('"')
            response_is_string = True
            response_string = content

    # Build endpoint(s)
    def make_endpoint(method, path, content_type, body_example):
        ep = APIEndpoint(
            section_title=title,
            description=description,
            http_method=method,
            http_path=path,
            jsonrpc_method=jsonrpc_method,
            parameters=parameters,
            request_body_example=body_example,
            response_example=response_example,
            response_specs=response_specs,
            response_is_string=response_is_string,
            response_string=response_string,
            notes=notes,
            content_type=content_type,
            source_file=filename,
            websocket_only=websocket_only,
            http_only=http_only,
            jsonrpc_title=jsonrpc_title,
        )
        return ep

    if not http_requests:
        # No HTTP info - websocket/RPC only
        ep = make_endpoint(None, None, None, None)
        ep.jsonrpc_method = jsonrpc_method
        return ep

    if len(http_requests) == 1:
        method, path, ct, body_ex = http_requests[0]
        return make_endpoint(method, path, ct, body_ex)

    # Multiple HTTP methods - return a list
    endpoints = []
    for method, path, ct, body_ex in http_requests:
        endpoints.append(make_endpoint(method, path, ct, body_ex))
    return endpoints


def extract_http_info(block: dict) -> tuple[Optional[str], Optional[str], Optional[str], Optional[dict]]:
    """Extract HTTP method, path, content type, and body example from a block."""
    method = None
    path = None
    content_type = None

    lines = block['content'].strip().split('\n')
    for line in lines:
        line = line.strip()
        method_match = re.match(r'^(GET|POST|DELETE|PUT|PATCH)\s+(/\S+?)[\s`]*$', line)
        if method_match:
            method = method_match.group(1)
            path = method_match.group(2).split('?')[0]
            continue
        # Only take the first Content-Type (request-level, not part-level)
        if content_type is None:
            ct_match = re.match(r'^Content-Type:\s*(.+)$', line, re.IGNORECASE)
            if ct_match:
                content_type = ct_match.group(1).strip()

    body_example = None
    if content_type and 'multipart/form-data' not in content_type:
        body_example = extract_json_from_http_block(block['content'])
    elif not content_type:
        body_example = extract_json_from_http_block(block['content'])

    return method, path, content_type, body_example


def extract_json_from_http_block(content: str) -> Optional[dict]:
    """Extract JSON body from HTTP request block."""
    lines = content.strip().split('\n')
    json_lines = []
    in_json = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('{') and not in_json:
            in_json = True
        if in_json:
            json_lines.append(line)
    if json_lines:
        try:
            return json.loads('\n'.join(json_lines))
        except json.JSONDecodeError:
            pass
    return None


def extract_description(body: str) -> str:
    """Extract description text before code blocks/directives."""
    lines = body.split('\n')
    desc_lines = []
    for line in lines:
        # Stop at first code block or directive
        if line.strip().startswith('```') or line.strip().startswith('///'):
            break
        desc_lines.append(line)
    desc = '\n'.join(desc_lines).strip()
    # Remove any leading/trailing blank lines
    return desc


def extract_code_blocks(body: str, block_type: str) -> list[dict]:
    """Extract code blocks matching a type (e.g., '.apirequest', '.apiresponse')."""
    blocks = []
    lines = body.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match code fence opening with the block type
        # Patterns: ```{.http .apirequest title="..."} or ```{.json .apiresponse ...}
        fence_match = re.match(r'^```\{(.+)\}\s*$', line)
        if not fence_match:
            # Also match: ```{json .apirequest  (missing leading dot - typo)
            fence_match = re.match(r'^```\{(\w.+)\}\s*$', line)
        if fence_match and block_type in line:
            attrs = fence_match.group(1)
            # Extract classes
            classes = re.findall(r'\.[\w-]+', attrs)
            # Also get the raw text for class detection without dot prefix
            if not classes and block_type.lstrip('.') in attrs:
                classes = [block_type]
            # Extract title
            title_match = re.search(r'title="([^"]*)"', attrs)
            title = title_match.group(1) if title_match else ''
            # Extract anchor ID
            anchor_match = re.search(r'#([\w-]+)', attrs)
            anchor_id = anchor_match.group(1) if anchor_match else None

            # Collect content until closing fence
            i += 1
            content_lines = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                content_lines.append(lines[i])
                i += 1

            blocks.append({
                'classes': classes,
                'title': title,
                'content': '\n'.join(content_lines),
                'anchor_id': anchor_id,
                'raw_attrs': attrs,
            })
        i += 1
    return blocks


def extract_parameters(body: str) -> list[Parameter]:
    """Extract parameters from /// api-parameters blocks."""
    params = []
    in_params = False
    table_lines = []

    for line in body.split('\n'):
        stripped = line.strip()
        if stripped.startswith('/// api-parameters'):
            in_params = True
            table_lines = []
            continue
        if in_params:
            if stripped == '///' and not stripped.startswith('////'):
                # End of params block
                params.extend(parse_parameter_table(table_lines))
                in_params = False
                continue
            # Skip nested //// blocks and their content
            if stripped.startswith('////'):
                continue
            table_lines.append(line)

    return params


def parse_parameter_table(lines: list[str]) -> list[Parameter]:
    """Parse a markdown table of parameters."""
    params = []
    table_rows = extract_table_rows(lines)

    for row in table_rows:
        if len(row) < 4:
            continue
        name = row[0].strip().strip('`')
        ptype = row[1].strip()
        default = row[2].strip()
        desc = row[3].strip()

        required = '**REQUIRED**' in default
        if required:
            default = None
        elif default == '':
            default = None

        params.append(Parameter(
            name=name,
            type=ptype,
            default=default,
            required=required,
            description=desc,
        ))

    return params


def extract_response_specs(body: str) -> list[ResponseSpec]:
    """Extract response specs from /// api-response-spec blocks."""
    specs = []
    in_spec = False
    spec_lines: list[str] = []
    depth = 0

    for line in body.split('\n'):
        stripped = line.strip()

        if stripped.startswith('/// api-response-spec'):
            in_spec = True
            depth = 1
            spec_lines = []
            continue

        if in_spec:
            # Track nested directive depth
            if stripped.startswith('////'):
                if depth > 0:
                    # Could be opening or closing a nested block
                    # For simplicity, just track and skip
                    pass
                spec_lines.append(line)
                continue
            if stripped == '///':
                depth -= 1
                if depth <= 0:
                    parsed = parse_response_spec_block(spec_lines)
                    specs.extend(parsed)
                    in_spec = False
                    continue
            spec_lines.append(line)

    return specs


def parse_response_spec_block(lines: list[str]) -> list[ResponseSpec]:
    """Parse the content of a response spec block into ResponseSpec objects."""
    specs = []
    current_table_lines: list[str] = []
    preamble_lines: list[str] = []
    in_table = False
    current_anchor_id = None
    current_anchor_title = None

    i = 0
    all_lines = lines
    while i < len(all_lines):
        line = all_lines[i]
        stripped = line.strip()

        # Skip option lines like "open: True"
        if re.match(r'^\s+(open|type):\s', line):
            i += 1
            continue

        # Check for table row
        if stripped.startswith('|') and '|' in stripped[1:]:
            # Check if this is a separator row
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                if not in_table:
                    in_table = True
                current_table_lines.append(stripped)
                i += 1
                continue
            if in_table or is_table_header(stripped, all_lines, i):
                in_table = True
                current_table_lines.append(stripped)
                i += 1
                continue

        # Check for anchor definition
        anchor_match = re.match(r'^\{\s*#([\w-]+)\s*\}\s*(.*?)\s*$', stripped)
        if anchor_match:
            current_anchor_id = anchor_match.group(1)
            current_anchor_title = anchor_match.group(2) if anchor_match.group(2) else None

            # Finalize current table as a spec
            if current_table_lines:
                fields = parse_response_table(current_table_lines)
                spec = ResponseSpec(
                    fields=fields,
                    anchor_id=current_anchor_id,
                    anchor_title=current_anchor_title,
                    preamble='\n'.join(preamble_lines).strip(),
                )
                specs.append(spec)
                current_table_lines = []
                preamble_lines = []
                current_anchor_id = None
                current_anchor_title = None
                in_table = False
            i += 1
            continue

        # If we have table lines and hit a non-table line, finalize the table
        if current_table_lines and not stripped.startswith('|'):
            fields = parse_response_table(current_table_lines)
            spec = ResponseSpec(
                fields=fields,
                anchor_id=current_anchor_id,
                anchor_title=current_anchor_title,
                preamble='\n'.join(preamble_lines).strip(),
            )
            specs.append(spec)
            current_table_lines = []
            preamble_lines = []
            current_anchor_id = None
            current_anchor_title = None
            in_table = False

        # Non-table, non-anchor text is preamble
        if stripped and not stripped.startswith('////'):
            preamble_lines.append(stripped)

        i += 1

    # Finalize any remaining table
    if current_table_lines:
        fields = parse_response_table(current_table_lines)
        spec = ResponseSpec(
            fields=fields,
            anchor_id=current_anchor_id,
            anchor_title=current_anchor_title,
            preamble='\n'.join(preamble_lines).strip(),
        )
        specs.append(spec)

    return specs


def is_table_header(line: str, all_lines: list[str], idx: int) -> bool:
    """Check if a line is a table header by looking for separator on next line."""
    if idx + 1 < len(all_lines):
        next_line = all_lines[idx + 1].strip()
        return bool(re.match(r'^\|[\s\-:|]+\|$', next_line))
    return False


def parse_response_table(lines: list[str]) -> list[ResponseField]:
    """Parse response table rows into ResponseField objects."""
    fields = []
    rows = extract_table_rows_from_lines(lines)

    for row in rows:
        if len(row) < 3:
            continue
        name = row[0].strip().strip('`')
        ftype = row[1].strip()
        desc = row[2].strip()

        # Check if this is a reference row (e.g., "#klippy-state-desc" with |+)
        ref_id = None
        if name.startswith('#'):
            ref_id = name
            # This is a reference to another spec, not a field
            continue
        # Check description for |+ reference marker
        if desc.endswith('|+') or (len(row) > 3 and row[-1].strip() == '+'):
            ref_id = name if name.startswith('#') else None

        fields.append(ResponseField(
            name=name,
            type=ftype,
            description=desc,
            ref_id=ref_id,
        ))

    return fields


def extract_table_rows(lines: list[str]) -> list[list[str]]:
    """Extract table data rows (skipping headers and separators) with continuation support."""
    rows: list[list[str]] = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('|'):
            if in_table:
                break
            continue
        # Skip separator rows
        if re.match(r'^\|[\s\-:|]+\|$', stripped):
            in_table = True
            continue
        if not in_table:
            # This is a header row, skip
            in_table = False  # will be set by separator
            continue

        cells = parse_table_cells(stripped)

        # Check for continuation marker |^ or reference marker |+
        is_continuation = any(
            c.strip().endswith('|^') or c.strip() == '^'
            or c.strip().endswith('|+') or c.strip() == '+'
            for c in cells
        )
        if is_continuation and rows:
            # Merge with previous row's description (last meaningful cell)
            for j, cell in enumerate(cells):
                cell_clean = cell.strip().rstrip('|^').rstrip('|+').rstrip('^').rstrip('+').strip()
                # Skip pure anchor references like #some-spec (from |+ lines)
                if cell_clean and re.match(r'^#[\w-]+$', cell_clean):
                    continue
                if cell_clean and j < len(rows[-1]):
                    rows[-1][j] = rows[-1][j].rstrip() + ' ' + cell_clean
        else:
            rows.append([c.strip() for c in cells])

    return rows


def extract_table_rows_from_lines(lines: list[str]) -> list[list[str]]:
    """Extract table rows from pre-filtered table lines."""
    rows: list[list[str]] = []
    past_header = False

    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        # Skip separator
        if re.match(r'^\|[\s\-:|]+\|$', stripped):
            past_header = True
            continue
        if not past_header:
            # Header row - check if next is separator
            continue

        cells = parse_table_cells(stripped)
        is_continuation = any(
            c.strip().endswith('|^') or c.strip() == '^'
            or c.strip().endswith('|+') or c.strip() == '+'
            for c in cells
        )
        if is_continuation and rows:
            for j, cell in enumerate(cells):
                cell_clean = cell.strip().rstrip('|^').rstrip('|+').rstrip('^').rstrip('+').strip()
                # Skip pure anchor references like #some-spec (from |+ lines)
                if cell_clean and re.match(r'^#[\w-]+$', cell_clean):
                    continue
                if cell_clean and j < len(rows[-1]):
                    rows[-1][j] = rows[-1][j].rstrip() + ' ' + cell_clean
        else:
            # Clean up cells
            cleaned = []
            for c in cells:
                c = c.strip()
                if c.endswith('|^'):
                    c = c[:-2].strip()
                elif c.endswith('|+'):
                    c = c[:-2].strip()
                cleaned.append(c)
            rows.append(cleaned)

    return rows


def parse_table_cells(line: str) -> list[str]:
    """Parse a markdown table row into cells."""
    # Remove leading/trailing pipes and split
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    # Handle |^ continuation and |+ reference - don't split on these
    line = line.replace('|^', '\x00CONT\x00')
    line = line.replace('|+', '\x00REFJ\x00')
    # Handle escaped pipes \| - don't split on these
    line = line.replace('\\|', '\x00EPIPE\x00')
    cells = line.split('|')
    # Restore markers
    cells = [c.replace('\x00CONT\x00', '|^').replace('\x00REFJ\x00', '|+').replace('\x00EPIPE\x00', '|') for c in cells]
    return cells


def extract_notes(body: str) -> list[str]:
    """Extract note/warning blocks from body."""
    notes = []
    in_note = False
    note_lines = []
    note_depth = 0

    for line in body.split('\n'):
        stripped = line.strip()

        # Match /// Note, /// note, /// warning, /// Warning, //// Note, etc.
        note_match = re.match(r'^(/{3,4})\s+(Note|note|Warning|warning|Tip|tip)\s*$', stripped)
        if note_match:
            in_note = True
            note_depth = len(note_match.group(1))
            note_lines = []
            continue

        if in_note:
            closer = '/' * note_depth
            if stripped == closer:
                note_text = '\n'.join(note_lines).strip()
                if note_text:
                    notes.append(note_text)
                in_note = False
                continue
            note_lines.append(line)

    return notes


def extract_standalone_anchors(text: str, filename: str) -> list[AnchorSpec]:
    """Extract anchor specs that appear outside of api-response-spec blocks."""
    anchors = []
    lines = text.split('\n')
    table_lines: list[str] = []
    in_table = False

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('|') and '|' in stripped[1:]:
            if re.match(r'^\|[\s\-:|]+\|$', stripped):
                in_table = True
                table_lines.append(stripped)
                i += 1
                continue
            if in_table or is_table_header(stripped, lines, i):
                in_table = True
                table_lines.append(stripped)
                i += 1
                continue

        anchor_match = re.match(r'^\{\s*#([\w-]+)\s*\}\s*(.*?)\s*$', stripped)
        if anchor_match and table_lines:
            anchor_id = anchor_match.group(1)
            anchor_title = anchor_match.group(2) or ''
            fields = parse_response_table(table_lines)
            anchors.append(AnchorSpec(
                anchor_id=anchor_id,
                title=anchor_title,
                fields=fields,
                source_file=filename,
            ))
            table_lines = []
            in_table = False
            i += 1
            continue

        if in_table and not stripped.startswith('|'):
            in_table = False
            table_lines = []

        i += 1

    return anchors


def extract_anchors_from_body(body: str, filename: str) -> list[AnchorSpec]:
    """Extract anchor definitions from response spec blocks in the body."""
    # These are already captured by extract_response_specs as part of ResponseSpec
    # This function finds anchors that are in api-response-spec blocks
    # We return them as AnchorSpec objects for the global registry
    anchors = []
    specs = extract_response_specs(body)
    for spec in specs:
        if spec.anchor_id:
            anchors.append(AnchorSpec(
                anchor_id=spec.anchor_id,
                title=spec.anchor_title or '',
                fields=spec.fields,
                source_file=filename,
            ))
    return anchors


def parse_notification_section(title: str, body: str, filename: str) -> Optional[Notification]:
    """Parse a notification section."""
    notif = Notification(
        section_title=title,
        description=extract_description(body),
        method_name='',
        source_file=filename,
    )

    # Extract method name from .text title="Notification Method Name" block
    for block in extract_code_blocks(body, 'title='):
        if 'notification method' in block.get('title', '').lower():
            notif.method_name = block['content'].strip()
            break

    # If no method name block, try to find it from text blocks
    if not notif.method_name:
        text_blocks = extract_text_blocks(body)
        for block in text_blocks:
            if block.get('title', '').lower().startswith('notification'):
                notif.method_name = block['content'].strip()
                break

    # Extract example notification
    response_blocks = extract_code_blocks(body, '.apiresponse')
    for block in response_blocks:
        if '.json' in block['classes']:
            try:
                notif.example = json.loads(block['content'])
            except json.JSONDecodeError:
                cleaned = re.sub(r',\s*}', '}', block['content'])
                cleaned = re.sub(r',\s*\]', ']', cleaned)
                try:
                    notif.example = json.loads(cleaned)
                except json.JSONDecodeError:
                    pass

    # Extract notification spec fields
    notif.fields = extract_notification_fields(body)

    # Extract response specs (for complex notification payloads)
    notif.response_specs = extract_notification_response_specs(body)

    return notif


def extract_notification_fields(body: str) -> list[NotificationField]:
    """Extract fields from /// api-notification-spec blocks."""
    fields = []
    in_spec = False
    table_lines = []

    for line in body.split('\n'):
        stripped = line.strip()
        if stripped.startswith('/// api-notification-spec'):
            in_spec = True
            table_lines = []
            continue
        if in_spec:
            if stripped == '///':
                # Parse the table
                rows = extract_table_rows(table_lines)
                for row in rows:
                    if len(row) >= 3:
                        try:
                            pos = int(row[0].strip())
                        except ValueError:
                            continue
                        fields.append(NotificationField(
                            position=pos,
                            type=row[1].strip(),
                            description=row[2].strip(),
                        ))
                in_spec = False
                continue
            table_lines.append(line)

    return fields


def extract_notification_response_specs(body: str) -> list[ResponseSpec]:
    """Extract response specs from notification spec blocks (some have nested specs)."""
    return extract_response_specs(body)


def extract_text_blocks(body: str) -> list[dict]:
    """Extract .text code blocks."""
    blocks = []
    lines = body.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        fence_match = re.match(r'^```\{(.+)\}\s*$', line)
        if fence_match:
            attrs = fence_match.group(1)
            if '.text' in attrs or ('text' in attrs and 'title=' in attrs):
                title_match = re.search(r'title="([^"]*)"', attrs)
                title = title_match.group(1) if title_match else ''
                i += 1
                content_lines = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    content_lines.append(lines[i])
                    i += 1
                blocks.append({
                    'title': title,
                    'content': '\n'.join(content_lines),
                })
        i += 1
    return blocks
