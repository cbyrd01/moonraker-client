"""High-level convenience functions for common 3D printer operations.

These helpers wrap multiple API calls into single ergonomic functions,
designed to simplify building CLI tools and scripts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO

from moonraker_client.exceptions import MoonrakerError

if TYPE_CHECKING:
    from moonraker_client.client import AsyncMoonrakerClient, MoonrakerClient


@dataclass
class PrinterStatus:
    """Combined printer status snapshot."""

    state: str
    state_message: str
    hostname: str
    software_version: str
    filename: str | None
    progress: float
    print_duration: float
    temperatures: dict[str, TemperatureReading]
    klippy_connected: bool
    klippy_state: str


@dataclass
class TemperatureReading:
    """Temperature reading for a heater."""

    current: float
    target: float
    power: float


@dataclass
class PrintProgress:
    """Current print progress details."""

    filename: str
    progress_pct: float
    elapsed: float
    state: str
    message: str


def get_printer_status(client: MoonrakerClient) -> PrinterStatus:
    """Get a comprehensive printer status snapshot.

    Combines printer/info, server/info, and object queries into a single
    status object.

    Args:
        client: A connected MoonrakerClient.

    Returns:
        PrinterStatus with all relevant info.
    """
    printer_info = client.printer_info()
    server_info = client.server_info()
    temps = get_temperatures(client)

    # Query print stats if available
    filename = None
    progress = 0.0
    print_duration = 0.0
    try:
        result = client.printer_objects_query(
            {
                "print_stats": None,
                "virtual_sdcard": None,
            }
        )
        status = result.get("status", {})
        print_stats = status.get("print_stats", {})
        vsd = status.get("virtual_sdcard", {})
        filename = print_stats.get("filename") or None
        progress = vsd.get("progress", 0.0)
        print_duration = print_stats.get("print_duration", 0.0)
    except MoonrakerError:
        pass

    return PrinterStatus(
        state=printer_info.get("state", "unknown"),
        state_message=printer_info.get("state_message", ""),
        hostname=printer_info.get("hostname", ""),
        software_version=printer_info.get("software_version", ""),
        filename=filename,
        progress=progress,
        print_duration=print_duration,
        temperatures=temps,
        klippy_connected=server_info.get("klippy_connected", False),
        klippy_state=server_info.get("klippy_state", "unknown"),
    )


def get_temperatures(client: MoonrakerClient) -> dict[str, TemperatureReading]:
    """Get current temperatures for all heaters.

    Args:
        client: A connected MoonrakerClient.

    Returns:
        Dict mapping heater names to TemperatureReading objects.
        Typical keys: "extruder", "heater_bed".
    """
    try:
        result = client.printer_objects_query(
            {
                "extruder": ["temperature", "target", "power"],
                "heater_bed": ["temperature", "target", "power"],
            }
        )
    except MoonrakerError:
        return {}

    status = result.get("status", {})
    temps: dict[str, TemperatureReading] = {}
    for name, data in status.items():
        if isinstance(data, dict) and "temperature" in data:
            temps[name] = TemperatureReading(
                current=data.get("temperature", 0.0),
                target=data.get("target", 0.0),
                power=data.get("power", 0.0),
            )
    return temps


def is_printing(client: MoonrakerClient) -> bool:
    """Check if the printer is currently printing.

    Args:
        client: A connected MoonrakerClient.

    Returns:
        True if a print is in progress.
    """
    try:
        result = client.printer_objects_query({"print_stats": ["state"]})
        state: str = result.get("status", {}).get("print_stats", {}).get("state", "")
        return state == "printing"
    except MoonrakerError:
        return False


def get_print_progress(client: MoonrakerClient) -> PrintProgress | None:
    """Get current print job progress.

    Args:
        client: A connected MoonrakerClient.

    Returns:
        PrintProgress if a file is loaded, None otherwise.
    """
    try:
        result = client.printer_objects_query(
            {
                "print_stats": None,
                "virtual_sdcard": None,
            }
        )
    except MoonrakerError:
        return None

    status = result.get("status", {})
    print_stats = status.get("print_stats", {})
    vsd = status.get("virtual_sdcard", {})

    filename = print_stats.get("filename", "")
    if not filename:
        return None

    return PrintProgress(
        filename=filename,
        progress_pct=round(vsd.get("progress", 0.0) * 100, 1),
        elapsed=print_stats.get("print_duration", 0.0),
        state=print_stats.get("state", "unknown"),
        message=print_stats.get("message", ""),
    )


def start_print(client: MoonrakerClient, filename: str) -> str:
    """Start printing a file after verifying it exists.

    Args:
        client: A connected MoonrakerClient.
        filename: Path to gcode file relative to gcodes root.

    Returns:
        "ok" on success.

    Raises:
        FileNotFoundError: If the file doesn't exist on the printer.
    """
    try:
        client.files_metadata(filename)
    except MoonrakerError:
        raise FileNotFoundError(f"File not found on printer: {filename}")
    return client.print_start(filename)


def upload_and_print(
    client: MoonrakerClient,
    file: str | Path | BinaryIO,
    remote_path: str | None = None,
) -> dict[str, Any]:
    """Upload a gcode file and optionally start printing it.

    Args:
        client: A connected MoonrakerClient.
        file: Local file path or file-like object.
        remote_path: Optional subdirectory on the printer.

    Returns:
        Upload response dict.
    """
    return client.files_upload(file, path=remote_path, start_print=True)


def send_gcode(client: MoonrakerClient, command: str) -> str:
    """Send a GCode command to the printer.

    Args:
        client: A connected MoonrakerClient.
        command: GCode command string. Multiple commands can be
            separated with newlines.

    Returns:
        "ok" on success.
    """
    return client.gcode_script(command)


def set_hotend_temp(client: MoonrakerClient, target: float, tool: int = 0) -> str:
    """Set the hotend temperature.

    Args:
        client: A connected MoonrakerClient.
        target: Target temperature in Celsius.
        tool: Tool index (default 0).

    Returns:
        "ok" on success.
    """
    return client.gcode_script(f"M104 S{target} T{tool}")


def set_bed_temp(client: MoonrakerClient, target: float) -> str:
    """Set the heated bed temperature.

    Args:
        client: A connected MoonrakerClient.
        target: Target temperature in Celsius.

    Returns:
        "ok" on success.
    """
    return client.gcode_script(f"M140 S{target}")


def wait_for_temps(
    client: MoonrakerClient,
    targets: dict[str, float],
    tolerance: float = 2.0,
    timeout: float = 300.0,
    poll_interval: float = 2.0,
) -> bool:
    """Wait for heaters to reach target temperatures.

    Args:
        client: A connected MoonrakerClient.
        targets: Dict of heater names to target temps (e.g. {"extruder": 200}).
        tolerance: Acceptable deviation in degrees.
        timeout: Maximum wait time in seconds.
        poll_interval: Time between temperature polls.

    Returns:
        True if all targets reached within timeout, False otherwise.
    """
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        temps = get_temperatures(client)
        all_reached = True
        for name, target in targets.items():
            reading = temps.get(name)
            if reading is None or abs(reading.current - target) > tolerance:
                all_reached = False
                break
        if all_reached:
            return True
        time.sleep(poll_interval)
    return False


def list_gcode_files(client: MoonrakerClient, sort_by: str = "modified") -> list[dict[str, Any]]:
    """List gcode files, sorted by the specified field.

    Args:
        client: A connected MoonrakerClient.
        sort_by: Field to sort by ("modified", "size", "path").

    Returns:
        List of file dicts sorted by the requested field.
    """
    files = client.files_list(root="gcodes")
    reverse = sort_by == "modified"  # Most recent first
    return sorted(files, key=lambda f: f.get(sort_by, 0), reverse=reverse)


def upload_gcode(
    client: MoonrakerClient,
    local_path: str | Path,
    remote_path: str | None = None,
    start: bool = False,
) -> dict[str, Any]:
    """Upload a gcode file to the printer.

    Args:
        client: A connected MoonrakerClient.
        local_path: Path to the local gcode file.
        remote_path: Optional subdirectory on the printer.
        start: If True, start printing after upload.

    Returns:
        Upload response dict with item info.
    """
    return client.files_upload(local_path, path=remote_path, start_print=start)


def get_system_health(client: MoonrakerClient) -> dict[str, Any]:
    """Get a system health summary.

    Combines proc_stats and system_info for a quick health overview.

    Args:
        client: A connected MoonrakerClient.

    Returns:
        Dict with cpu_temp, system_uptime, memory, cpu_usage, etc.
    """
    stats = client.machine_procstats()
    info = client.machine_systeminfo()

    return {
        "cpu_temp": stats.get("cpu_temp"),
        "system_uptime": stats.get("system_uptime"),
        "system_memory": stats.get("system_memory"),
        "system_cpu_usage": stats.get("system_cpu_usage"),
        "websocket_connections": stats.get("websocket_connections"),
        "cpu_info": info.get("system_info", {}).get("cpu_info"),
    }


def restart_firmware(
    client: MoonrakerClient,
    timeout: float = 30.0,
    poll_interval: float = 2.0,
) -> bool:
    """Restart Klipper firmware and wait for it to become ready.

    Args:
        client: A connected MoonrakerClient.
        timeout: Max seconds to wait for ready state.
        poll_interval: Seconds between status checks.

    Returns:
        True if Klipper reached ready state, False on timeout.
    """
    client.firmware_restart()
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        time.sleep(poll_interval)
        try:
            info = client.printer_info()
            if info.get("state") == "ready":
                return True
        except MoonrakerError:
            # Server may be temporarily unreachable during firmware restart
            continue
    return False


# ---------------------------------------------------------------------------
# Async variants of key helpers
# ---------------------------------------------------------------------------


async def async_get_printer_status(client: AsyncMoonrakerClient) -> PrinterStatus:
    """Async version of get_printer_status."""
    printer_info = await client.printer_info()
    server_info = await client.server_info()
    temps = await async_get_temperatures(client)

    filename = None
    progress = 0.0
    print_duration = 0.0
    try:
        result = await client.printer_objects_query(
            {"print_stats": None, "virtual_sdcard": None}
        )
        status = result.get("status", {})
        print_stats = status.get("print_stats", {})
        vsd = status.get("virtual_sdcard", {})
        filename = print_stats.get("filename") or None
        progress = vsd.get("progress", 0.0)
        print_duration = print_stats.get("print_duration", 0.0)
    except MoonrakerError:
        pass

    return PrinterStatus(
        state=printer_info.get("state", "unknown"),
        state_message=printer_info.get("state_message", ""),
        hostname=printer_info.get("hostname", ""),
        software_version=printer_info.get("software_version", ""),
        filename=filename,
        progress=progress,
        print_duration=print_duration,
        temperatures=temps,
        klippy_connected=server_info.get("klippy_connected", False),
        klippy_state=server_info.get("klippy_state", "unknown"),
    )


async def async_get_temperatures(client: AsyncMoonrakerClient) -> dict[str, TemperatureReading]:
    """Async version of get_temperatures."""
    try:
        result = await client.printer_objects_query(
            {
                "extruder": ["temperature", "target", "power"],
                "heater_bed": ["temperature", "target", "power"],
            }
        )
    except MoonrakerError:
        return {}

    status = result.get("status", {})
    temps: dict[str, TemperatureReading] = {}
    for name, data in status.items():
        if isinstance(data, dict) and "temperature" in data:
            temps[name] = TemperatureReading(
                current=data.get("temperature", 0.0),
                target=data.get("target", 0.0),
                power=data.get("power", 0.0),
            )
    return temps


async def async_get_print_progress(client: AsyncMoonrakerClient) -> PrintProgress | None:
    """Async version of get_print_progress."""
    try:
        result = await client.printer_objects_query(
            {"print_stats": None, "virtual_sdcard": None}
        )
    except MoonrakerError:
        return None

    status = result.get("status", {})
    print_stats = status.get("print_stats", {})
    vsd = status.get("virtual_sdcard", {})

    filename = print_stats.get("filename", "")
    if not filename:
        return None

    return PrintProgress(
        filename=filename,
        progress_pct=round(vsd.get("progress", 0.0) * 100, 1),
        elapsed=print_stats.get("print_duration", 0.0),
        state=print_stats.get("state", "unknown"),
        message=print_stats.get("message", ""),
    )


async def async_is_printing(client: AsyncMoonrakerClient) -> bool:
    """Async version of is_printing."""
    try:
        result = await client.printer_objects_query({"print_stats": ["state"]})
        state: str = result.get("status", {}).get("print_stats", {}).get("state", "")
        return state == "printing"
    except MoonrakerError:
        return False
