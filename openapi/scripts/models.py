from __future__ import annotations
import dataclasses
from typing import Any, Optional


@dataclasses.dataclass
class Parameter:
    name: str
    type: str
    default: Optional[str]
    required: bool
    description: str


@dataclasses.dataclass
class ResponseField:
    name: str
    type: str
    description: str
    ref_id: Optional[str] = None  # anchor reference like #klippy-state-desc


@dataclasses.dataclass
class ResponseSpec:
    """A response specification table, possibly with a name/anchor."""
    fields: list[ResponseField] = dataclasses.field(default_factory=list)
    anchor_id: Optional[str] = None
    anchor_title: Optional[str] = None
    preamble: str = ""  # text before the table within the spec block


@dataclasses.dataclass
class NotificationField:
    position: int
    type: str
    description: str


@dataclasses.dataclass
class APIEndpoint:
    section_title: str
    description: str
    http_method: Optional[str]  # GET, POST, DELETE or None if HTTP not available
    http_path: Optional[str]
    jsonrpc_method: Optional[str]  # None if JSON-RPC not available
    parameters: list[Parameter] = dataclasses.field(default_factory=list)
    request_body_example: Optional[dict[str, Any]] = None
    response_example: Optional[Any] = None
    response_specs: list[ResponseSpec] = dataclasses.field(default_factory=list)
    response_is_string: bool = False  # True for "ok" responses
    response_string: Optional[str] = None
    notes: list[str] = dataclasses.field(default_factory=list)
    transports: list[str] = dataclasses.field(default_factory=list)
    content_type: Optional[str] = None  # multipart/form-data for uploads
    source_file: str = ""
    websocket_only: bool = False
    http_only: bool = False
    jsonrpc_title: str = ""  # title from the code fence


@dataclasses.dataclass
class Notification:
    section_title: str
    description: str
    method_name: str
    example: Optional[Any] = None
    fields: list[NotificationField] = dataclasses.field(default_factory=list)
    response_specs: list[ResponseSpec] = dataclasses.field(default_factory=list)
    source_file: str = ""


@dataclasses.dataclass
class AnchorSpec:
    """A named spec table that can be referenced by anchor ID."""
    anchor_id: str
    title: str
    fields: list[ResponseField] = dataclasses.field(default_factory=list)
    source_file: str = ""
