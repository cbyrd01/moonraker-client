"""Printer API endpoint mixins.

Covers /printer/* endpoints for printer info, control, gcode, and object queries.
Generated from OpenAPI spec and hand-tuned.
"""

from __future__ import annotations

from typing import Any


class PrinterMixin:
    """Synchronous printer API methods."""

    def printer_info(self) -> dict[str, Any]:
        """Get Klippy host information.

        Returns dict with: state, state_message, hostname, klipper_path,
        python_path, process_id, user_id, group_id, log_file, config_file,
        software_version, cpu_info.

        JSON-RPC method: printer.info
        """
        return self._request("GET", "/printer/info")  # type: ignore[attr-defined]

    def emergency_stop(self) -> str:
        """Immediately halt the printer.

        Shuts down the printer and puts Klipper into a "shutdown" state.
        A firmware_restart or printer restart is required to recover.

        JSON-RPC method: printer.emergency_stop
        """
        return self._request("POST", "/printer/emergency_stop")  # type: ignore[attr-defined]

    def printer_restart(self) -> str:
        """Request a Klipper soft restart.

        Reloads the Klippy application and configuration.
        Connected MCUs will not be reset.

        JSON-RPC method: printer.restart
        """
        return self._request("POST", "/printer/restart")  # type: ignore[attr-defined]

    def firmware_restart(self) -> str:
        """Request a complete Klipper restart.

        Both the Klippy application and connected MCUs will be reset.

        JSON-RPC method: printer.firmware_restart
        """
        return self._request("POST", "/printer/firmware_restart")  # type: ignore[attr-defined]

    def printer_objects_list(self) -> list[str]:
        """List loaded printer objects.

        Returns a list of Klipper printer objects that are currently loaded.
        Useful for determining what is available for query/subscription.

        JSON-RPC method: printer.objects.list
        """
        return self._request("GET", "/printer/objects/list")  # type: ignore[attr-defined]

    def printer_objects_query(self, objects: dict[str, list[str] | None]) -> dict[str, Any]:
        """Query printer object status.

        Args:
            objects: Dict mapping object names to lists of attributes to query,
                or None for all attributes. E.g. {"toolhead": ["position", "status"],
                "extruder": None}

        JSON-RPC method: printer.objects.query
        """
        return self._request("POST", "/printer/objects/query", json={"objects": objects})  # type: ignore[attr-defined]

    def query_endstops(self) -> dict[str, str]:
        """Query endstop status.

        Returns dict mapping endstop names to their status ("open" or "TRIGGERED").

        JSON-RPC method: printer.query_endstops.status
        """
        return self._request("GET", "/printer/query_endstops/status")  # type: ignore[attr-defined]

    def gcode_script(self, script: str) -> str:
        """Execute a GCode command.

        Multiple commands may be separated with newlines.

        Args:
            script: GCode command(s) to execute.

        JSON-RPC method: printer.gcode.script
        """
        return self._request("POST", "/printer/gcode/script", json={"script": script})  # type: ignore[attr-defined]

    def gcode_help(self) -> dict[str, str]:
        """Get registered GCode command descriptions.

        Returns dict mapping command names to their help text.

        JSON-RPC method: printer.gcode.help
        """
        return self._request("GET", "/printer/gcode/help")  # type: ignore[attr-defined]

    def print_start(self, filename: str) -> str:
        """Start a print job.

        Args:
            filename: Path to the gcode file relative to the gcodes root.

        JSON-RPC method: printer.print.start
        """
        return self._request("POST", "/printer/print/start", json={"filename": filename})  # type: ignore[attr-defined]

    def print_pause(self) -> str:
        """Pause the current print job.

        JSON-RPC method: printer.print.pause
        """
        return self._request("POST", "/printer/print/pause")  # type: ignore[attr-defined]

    def print_resume(self) -> str:
        """Resume the current print job.

        JSON-RPC method: printer.print.resume
        """
        return self._request("POST", "/printer/print/resume")  # type: ignore[attr-defined]

    def print_cancel(self) -> str:
        """Cancel the current print job.

        JSON-RPC method: printer.print.cancel
        """
        return self._request("POST", "/printer/print/cancel")  # type: ignore[attr-defined]


class AsyncPrinterMixin:
    """Asynchronous printer API methods."""

    async def printer_info(self) -> dict[str, Any]:
        """Get Klippy host information.

        JSON-RPC method: printer.info
        """
        return await self._request("GET", "/printer/info")  # type: ignore[attr-defined]

    async def emergency_stop(self) -> str:
        """Immediately halt the printer.

        JSON-RPC method: printer.emergency_stop
        """
        return await self._request("POST", "/printer/emergency_stop")  # type: ignore[attr-defined]

    async def printer_restart(self) -> str:
        """Request a Klipper soft restart.

        JSON-RPC method: printer.restart
        """
        return await self._request("POST", "/printer/restart")  # type: ignore[attr-defined]

    async def firmware_restart(self) -> str:
        """Request a complete Klipper restart.

        JSON-RPC method: printer.firmware_restart
        """
        return await self._request("POST", "/printer/firmware_restart")  # type: ignore[attr-defined]

    async def printer_objects_list(self) -> list[str]:
        """List loaded printer objects.

        JSON-RPC method: printer.objects.list
        """
        return await self._request("GET", "/printer/objects/list")  # type: ignore[attr-defined]

    async def printer_objects_query(self, objects: dict[str, list[str] | None]) -> dict[str, Any]:
        """Query printer object status.

        Args:
            objects: Dict mapping object names to attribute lists or None.

        JSON-RPC method: printer.objects.query
        """
        return await self._request("POST", "/printer/objects/query", json={"objects": objects})  # type: ignore[attr-defined]

    async def query_endstops(self) -> dict[str, str]:
        """Query endstop status.

        JSON-RPC method: printer.query_endstops.status
        """
        return await self._request("GET", "/printer/query_endstops/status")  # type: ignore[attr-defined]

    async def gcode_script(self, script: str) -> str:
        """Execute a GCode command.

        Args:
            script: GCode command(s) to execute.

        JSON-RPC method: printer.gcode.script
        """
        return await self._request("POST", "/printer/gcode/script", json={"script": script})  # type: ignore[attr-defined]

    async def gcode_help(self) -> dict[str, str]:
        """Get registered GCode command descriptions.

        JSON-RPC method: printer.gcode.help
        """
        return await self._request("GET", "/printer/gcode/help")  # type: ignore[attr-defined]

    async def print_start(self, filename: str) -> str:
        """Start a print job.

        Args:
            filename: Path to the gcode file relative to the gcodes root.

        JSON-RPC method: printer.print.start
        """
        return await self._request("POST", "/printer/print/start", json={"filename": filename})  # type: ignore[attr-defined]

    async def print_pause(self) -> str:
        """Pause the current print job.

        JSON-RPC method: printer.print.pause
        """
        return await self._request("POST", "/printer/print/pause")  # type: ignore[attr-defined]

    async def print_resume(self) -> str:
        """Resume the current print job.

        JSON-RPC method: printer.print.resume
        """
        return await self._request("POST", "/printer/print/resume")  # type: ignore[attr-defined]

    async def print_cancel(self) -> str:
        """Cancel the current print job.

        JSON-RPC method: printer.print.cancel
        """
        return await self._request("POST", "/printer/print/cancel")  # type: ignore[attr-defined]
