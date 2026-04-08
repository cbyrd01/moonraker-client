"""Data models generated from the Moonraker OpenAPI spec.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Agent:
    """Agent Info"""

    name: str | None = None
    version: str | None = None
    type: str | None = None
    url: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Agent:
        """Create Agent from a dict, ignoring extra keys."""
        return cls(
            name=data.get("name"),
            version=data.get("version"),
            type=data.get("type"),
            url=data.get("url"),
        )


@dataclass
class AnnouncementEntry:
    """Announcement Entry"""

    entry_id: str | None = None
    url: str | None = None
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    date: str | None = None
    dismissed: bool | None = None
    date_dismissed: float | None = None
    dismiss_wake: float | None = None
    source: str | None = None
    feed: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnnouncementEntry:
        """Create AnnouncementEntry from a dict, ignoring extra keys."""
        return cls(
            entry_id=data.get("entry_id"),
            url=data.get("url"),
            title=data.get("title"),
            description=data.get("description"),
            priority=data.get("priority"),
            date=data.get("date"),
            dismissed=data.get("dismissed"),
            date_dismissed=data.get("date_dismissed"),
            dismiss_wake=data.get("dismiss_wake"),
            source=data.get("source"),
            feed=data.get("feed"),
        )


@dataclass
class File:
    """File Info"""

    path: str | None = None
    modified: float | None = None
    size: int | None = None
    permissions: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> File:
        """Create File from a dict, ignoring extra keys."""
        return cls(
            path=data.get("path"),
            modified=data.get("modified"),
            size=data.get("size"),
            permissions=data.get("permissions"),
        )


@dataclass
class FileObject:
    """File Object"""

    filename: str | None = None
    sections: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileObject:
        """Create FileObject from a dict, ignoring extra keys."""
        return cls(
            filename=data.get("filename"),
            sections=data.get("sections"),
        )


@dataclass
class GcTrackingObj:
    """GCode Tracking Object"""

    message: str | None = None
    time: float | None = None
    type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GcTrackingObj:
        """Create GcTrackingObj from a dict, ignoring extra keys."""
        return cls(
            message=data.get("message"),
            time=data.get("time"),
            type=data.get("type"),
        )


@dataclass
class GcodeMetadata:
    """GcodeMetadata"""

    size: int | None = None
    modified: float | None = None
    uuid: str | None = None
    file_processors: list[str] | None = None
    slicer: str | None = None
    slicer_version: str | None = None
    gcode_start_byte: int | None = None
    gcode_int_byte: int | None = None
    object_height: float | None = None
    estimated_time: float | None = None
    nozzle_diameter: float | None = None
    layer_height: float | None = None
    first_layer_height: float | None = None
    first_layer_extr_temp: float | None = None
    first_layer_bed_temp: float | None = None
    chamber_temp: float | None = None
    filament_name: str | None = None
    filament_colors: list[str] | None = None
    extruder_colors: list[str] | None = None
    filament_temps: list[int] | None = None
    filament_type: str | None = None
    filament_total: float | None = None
    filament_change_count: int | None = None
    filament_weight_total: float | None = None
    filament_weights: list[float] | None = None
    printer_vendor: str | None = None
    printer_model: str | None = None
    printer_variant: str | None = None
    profile_version: str | None = None
    mmu_print: int | None = None
    referenced_tools: list[int] | None = None
    thumbnails: list[dict[str, Any]] | None = None
    job_id: str | None = None
    print_start_time: float | None = None
    filename: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GcodeMetadata:
        """Create GcodeMetadata from a dict, ignoring extra keys."""
        return cls(
            size=data.get("size"),
            modified=data.get("modified"),
            uuid=data.get("uuid"),
            file_processors=data.get("file_processors"),
            slicer=data.get("slicer"),
            slicer_version=data.get("slicer_version"),
            gcode_start_byte=data.get("gcode_start_byte"),
            gcode_int_byte=data.get("gcode_int_byte"),
            object_height=data.get("object_height"),
            estimated_time=data.get("estimated_time"),
            nozzle_diameter=data.get("nozzle_diameter"),
            layer_height=data.get("layer_height"),
            first_layer_height=data.get("first_layer_height"),
            first_layer_extr_temp=data.get("first_layer_extr_temp"),
            first_layer_bed_temp=data.get("first_layer_bed_temp"),
            chamber_temp=data.get("chamber_temp"),
            filament_name=data.get("filament_name"),
            filament_colors=data.get("filament_colors"),
            extruder_colors=data.get("extruder_colors"),
            filament_temps=data.get("filament_temps"),
            filament_type=data.get("filament_type"),
            filament_total=data.get("filament_total"),
            filament_change_count=data.get("filament_change_count"),
            filament_weight_total=data.get("filament_weight_total"),
            filament_weights=data.get("filament_weights"),
            printer_vendor=data.get("printer_vendor"),
            printer_model=data.get("printer_model"),
            printer_variant=data.get("printer_variant"),
            profile_version=data.get("profile_version"),
            mmu_print=data.get("mmu_print"),
            referenced_tools=data.get("referenced_tools"),
            thumbnails=data.get("thumbnails"),
            job_id=data.get("job_id"),
            print_start_time=data.get("print_start_time"),
            filename=data.get("filename"),
        )


@dataclass
class JobAuxiliaryTotals:
    """Auxiliary Total"""

    provider: str | None = None
    field: str | None = None
    maximum: float | None = None
    total: float | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobAuxiliaryTotals:
        """Create JobAuxiliaryTotals from a dict, ignoring extra keys."""
        return cls(
            provider=data.get("provider"),
            field=data.get("field"),
            maximum=data.get("maximum"),
            total=data.get("total"),
        )


@dataclass
class JobHistoryAuxField:
    """Auxiliary Field"""

    provider: str | None = None
    name: str | None = None
    description: str | None = None
    value: dict[str, Any] | None = None
    units: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobHistoryAuxField:
        """Create JobHistoryAuxField from a dict, ignoring extra keys."""
        return cls(
            provider=data.get("provider"),
            name=data.get("name"),
            description=data.get("description"),
            value=data.get("value"),
            units=data.get("units"),
        )


@dataclass
class JobHistoryEntry:
    """Job History"""

    job_id: str | None = None
    user: str | None = None
    filename: str | None = None
    exists: bool | None = None
    status: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    print_duration: float | None = None
    total_duration: float | None = None
    filament_used: float | None = None
    metadata: dict[str, Any] | None = None
    auxiliary_data: list[JobHistoryAuxField] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobHistoryEntry:
        """Create JobHistoryEntry from a dict, ignoring extra keys."""
        return cls(
            job_id=data.get("job_id"),
            user=data.get("user"),
            filename=data.get("filename"),
            exists=data.get("exists"),
            status=data.get("status"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            print_duration=data.get("print_duration"),
            total_duration=data.get("total_duration"),
            filament_used=data.get("filament_used"),
            metadata=data.get("metadata"),
            auxiliary_data=data.get("auxiliary_data"),
        )


@dataclass
class JobHistoryTotals:
    """Job Totals"""

    total_jobs: int | None = None
    total_time: float | None = None
    total_print_time: float | None = None
    total_filament_used: float | None = None
    longest_job: float | None = None
    longest_print: float | None = None
    auxiliary_totals: list[JobAuxiliaryTotals] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobHistoryTotals:
        """Create JobHistoryTotals from a dict, ignoring extra keys."""
        return cls(
            total_jobs=data.get("total_jobs"),
            total_time=data.get("total_time"),
            total_print_time=data.get("total_print_time"),
            total_filament_used=data.get("total_filament_used"),
            longest_job=data.get("longest_job"),
            longest_print=data.get("longest_print"),
            auxiliary_totals=data.get("auxiliary_totals"),
        )


@dataclass
class JobQueueStatusResponse:
    """JobQueueStatusResponse"""

    queued_jobs: list[dict[str, Any]] | None = None
    queue_state: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JobQueueStatusResponse:
        """Create JobQueueStatusResponse from a dict, ignoring extra keys."""
        return cls(
            queued_jobs=data.get("queued_jobs"),
            queue_state=data.get("queue_state"),
        )


@dataclass
class ListAnnouncements:
    """ListAnnouncements"""

    entries: list[AnnouncementEntry] | None = None
    feeds: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ListAnnouncements:
        """Create ListAnnouncements from a dict, ignoring extra keys."""
        return cls(
            entries=data.get("entries"),
            feeds=data.get("feeds"),
        )


@dataclass
class NotifierStatus:
    """Notifier Status"""

    name: str | None = None
    url: str | None = None
    events: list[str] | None = None
    body: str | None = None
    title: str | None = None
    attach: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NotifierStatus:
        """Create NotifierStatus from a dict, ignoring extra keys."""
        return cls(
            name=data.get("name"),
            url=data.get("url"),
            events=data.get("events"),
            body=data.get("body"),
            title=data.get("title"),
            attach=data.get("attach"),
        )


@dataclass
class ObjectQueryResponse:
    """ObjectQueryResponse"""

    eventtime: float | None = None
    status: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ObjectQueryResponse:
        """Create ObjectQueryResponse from a dict, ignoring extra keys."""
        return cls(
            eventtime=data.get("eventtime"),
            status=data.get("status"),
        )


@dataclass
class PowerDeviceStatus:
    """Power Device Status"""

    device: str | None = None
    status: str | None = None
    locked_while_printing: bool | None = None
    type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PowerDeviceStatus:
        """Create PowerDeviceStatus from a dict, ignoring extra keys."""
        return cls(
            device=data.get("device"),
            status=data.get("status"),
            locked_while_printing=data.get("locked_while_printing"),
            type=data.get("type"),
        )


@dataclass
class PrintStats:
    """Print Stats"""

    print_duration: float | None = None
    total_duration: float | None = None
    filament_used: float | None = None
    filename: str | None = None
    state: str | None = None
    message: str | None = None
    info: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PrintStats:
        """Create PrintStats from a dict, ignoring extra keys."""
        return cls(
            print_duration=data.get("print_duration"),
            total_duration=data.get("total_duration"),
            filament_used=data.get("filament_used"),
            filename=data.get("filename"),
            state=data.get("state"),
            message=data.get("message"),
            info=data.get("info"),
        )


@dataclass
class ProcStatsResponse:
    """ProcStatsResponse"""

    moonraker_stats: list[dict[str, Any]] | None = None
    throttled_state: dict[str, Any] | None = None
    cpu_temp: float | None = None
    network: dict[str, Any] | None = None
    system_cpu_usage: dict[str, Any] | None = None
    system_memory: dict[str, Any] | None = None
    system_uptime: float | None = None
    websocket_connections: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProcStatsResponse:
        """Create ProcStatsResponse from a dict, ignoring extra keys."""
        return cls(
            moonraker_stats=data.get("moonraker_stats"),
            throttled_state=data.get("throttled_state"),
            cpu_temp=data.get("cpu_temp"),
            network=data.get("network"),
            system_cpu_usage=data.get("system_cpu_usage"),
            system_memory=data.get("system_memory"),
            system_uptime=data.get("system_uptime"),
            websocket_connections=data.get("websocket_connections"),
        )


@dataclass
class Root:
    """Root Info"""

    name: str | None = None
    permissions: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Root:
        """Create Root from a dict, ignoring extra keys."""
        return cls(
            name=data.get("name"),
            permissions=data.get("permissions"),
        )


@dataclass
class SensorMeasurements:
    """Sensor Measurements.

    This is a dynamic model where keys are parameter names and values are
    measurement arrays. Use from_dict to construct from raw API data.
    """

    data: dict[str, list[float]] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorMeasurements:
        """Create SensorMeasurements from a dict."""
        return cls(data=data)


@dataclass
class SensorObj:
    """Sensor Object"""

    temperatures: list[float] | None = None
    targets: list[float] | None = None
    speeds: list[float] | None = None
    powers: list[float] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorObj:
        """Create SensorObj from a dict, ignoring extra keys."""
        return cls(
            temperatures=data.get("temperatures"),
            targets=data.get("targets"),
            speeds=data.get("speeds"),
            powers=data.get("powers"),
        )


@dataclass
class SensorStatus:
    """Sensor Status"""

    id: str | None = None
    friendly_name: str | None = None
    type: str | None = None
    values: dict[str, Any] | None = None
    parameter_info: list[dict[str, Any]] | None = None
    history_fields: list[dict[str, Any]] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SensorStatus:
        """Create SensorStatus from a dict, ignoring extra keys."""
        return cls(
            id=data.get("id"),
            friendly_name=data.get("friendly_name"),
            type=data.get("type"),
            values=data.get("values"),
            parameter_info=data.get("parameter_info"),
            history_fields=data.get("history_fields"),
        )


@dataclass
class Sys:
    """System Info"""

    python: dict[str, Any] | None = None
    cpu_info: dict[str, Any] | None = None
    sd_info: dict[str, Any] | None = None
    distribution: dict[str, Any] | None = None
    virtualization: dict[str, Any] | None = None
    network: dict[str, Any] | None = None
    canbus: dict[str, Any] | None = None
    provider: str | None = None
    available_services: list[str] | None = None
    service_state: dict[str, Any] | None = None
    instance_ids: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sys:
        """Create Sys from a dict, ignoring extra keys."""
        return cls(
            python=data.get("python"),
            cpu_info=data.get("cpu_info"),
            sd_info=data.get("sd_info"),
            distribution=data.get("distribution"),
            virtualization=data.get("virtualization"),
            network=data.get("network"),
            canbus=data.get("canbus"),
            provider=data.get("provider"),
            available_services=data.get("available_services"),
            service_state=data.get("service_state"),
            instance_ids=data.get("instance_ids"),
        )


@dataclass
class ThumbnailDetails:
    """Thumbnail Details"""

    width: int | None = None
    height: int | None = None
    size: int | None = None
    thumbnail_path: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThumbnailDetails:
        """Create ThumbnailDetails from a dict, ignoring extra keys."""
        return cls(
            width=data.get("width"),
            height=data.get("height"),
            size=data.get("size"),
            thumbnail_path=data.get("thumbnail_path"),
        )


@dataclass
class UpdateStatus:
    """UpdateStatus"""

    busy: bool | None = None
    github_rate_limit: int | None = None
    github_requests_remaining: int | None = None
    github_limit_reset_time: int | None = None
    version_info: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UpdateStatus:
        """Create UpdateStatus from a dict, ignoring extra keys."""
        return cls(
            busy=data.get("busy"),
            github_rate_limit=data.get("github_rate_limit"),
            github_requests_remaining=data.get("github_requests_remaining"),
            github_limit_reset_time=data.get("github_limit_reset_time"),
            version_info=data.get("version_info"),
        )


@dataclass
class Version2Success:
    """Version 2 response"""

    response: dict[str, Any] | None = None
    error: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Version2Success:
        """Create Version2Success from a dict, ignoring extra keys."""
        return cls(
            response=data.get("response"),
            error=data.get("error"),
        )


@dataclass
class WebcamEntry:
    """Webcam Entry"""

    name: str | None = None
    location: str | None = None
    service: str | None = None
    enabled: bool | None = None
    icon: str | None = None
    target_fps: int | None = None
    target_fps_idle: int | None = None
    stream_url: str | None = None
    snapshot_url: str | None = None
    flip_horizontal: bool | None = None
    flip_vertical: bool | None = None
    rotation: int | None = None
    aspect_ratio: str | None = None
    extra_data: dict[str, Any] | None = None
    source: str | None = None
    uid: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WebcamEntry:
        """Create WebcamEntry from a dict, ignoring extra keys."""
        return cls(
            name=data.get("name"),
            location=data.get("location"),
            service=data.get("service"),
            enabled=data.get("enabled"),
            icon=data.get("icon"),
            target_fps=data.get("target_fps"),
            target_fps_idle=data.get("target_fps_idle"),
            stream_url=data.get("stream_url"),
            snapshot_url=data.get("snapshot_url"),
            flip_horizontal=data.get("flip_horizontal"),
            flip_vertical=data.get("flip_vertical"),
            rotation=data.get("rotation"),
            aspect_ratio=data.get("aspect_ratio"),
            extra_data=data.get("extra_data"),
            source=data.get("source"),
            uid=data.get("uid"),
        )


@dataclass
class WledStripStatus:
    """WLED Strip Status"""

    strip: str | None = None
    status: str | None = None
    chain_count: int | None = None
    preset: int | None = None
    brightness: int | None = None
    intensity: int | None = None
    speed: int | None = None
    error: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WledStripStatus:
        """Create WledStripStatus from a dict, ignoring extra keys."""
        return cls(
            strip=data.get("strip"),
            status=data.get("status"),
            chain_count=data.get("chain_count"),
            preset=data.get("preset"),
            brightness=data.get("brightness"),
            intensity=data.get("intensity"),
            speed=data.get("speed"),
            error=data.get("error"),
        )


@dataclass
class ErrorResponse:
    """ErrorResponse"""

    error: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ErrorResponse:
        """Create ErrorResponse from a dict, ignoring extra keys."""
        return cls(
            error=data.get("error"),
        )


@dataclass
class ResultOk:
    """Standard success response wrapping a string result (typically "ok")."""

    result: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResultOk:
        """Create ResultOk from a dict, ignoring extra keys."""
        return cls(
            result=data.get("result"),
        )

