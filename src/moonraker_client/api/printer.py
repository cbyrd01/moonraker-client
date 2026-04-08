"""Printer API endpoint mixins.

Covers /printer/* endpoints for printer info, control, and gcode operations.
"""

from __future__ import annotations

from typing import Any


class PrinterMixin:
    """Mixin providing synchronous printer API methods.

    Requires the host class to implement:
        _request(method, path, **kwargs) -> Any
    """

    def printer_info(self) -> dict[str, Any]:
        """Get Klippy host information.

        Returns:
            Dict with keys: state, state_message, hostname, klipper_path,
            python_path, process_id, user_id, group_id, log_file, config_file,
            software_version, cpu_info.

        JSON-RPC method: printer.info
        """
        return self._request("GET", "/printer/info")  # type: ignore[attr-defined]

    def emergency_stop(self) -> str:
        """Immediately halt the printer.

        This will shut down the printer and put Klipper into a "shutdown" state.
        A firmware_restart or printer restart is required to recover.

        Returns:
            "ok" on success.

        JSON-RPC method: printer.emergency_stop
        """
        return self._request("POST", "/printer/emergency_stop")  # type: ignore[attr-defined]

    def printer_restart(self) -> str:
        """Request a Klipper soft restart.

        Reloads the Klippy application and configuration.
        Connected MCUs will not be reset.

        Returns:
            "ok" on success.

        JSON-RPC method: printer.restart
        """
        return self._request("POST", "/printer/restart")  # type: ignore[attr-defined]

    def firmware_restart(self) -> str:
        """Request a complete Klipper restart.

        Both the Klippy application and connected MCUs will be reset.

        Returns:
            "ok" on success.

        JSON-RPC method: printer.firmware_restart
        """
        return self._request("POST", "/printer/firmware_restart")  # type: ignore[attr-defined]


class AsyncPrinterMixin:
    """Mixin providing asynchronous printer API methods.

    Requires the host class to implement:
        async _request(method, path, **kwargs) -> Any
    """

    async def printer_info(self) -> dict[str, Any]:
        """Get Klippy host information.

        Returns:
            Dict with keys: state, state_message, hostname, klipper_path,
            python_path, process_id, user_id, group_id, log_file, config_file,
            software_version, cpu_info.

        JSON-RPC method: printer.info
        """
        return await self._request("GET", "/printer/info")  # type: ignore[attr-defined]

    async def emergency_stop(self) -> str:
        """Immediately halt the printer.

        Returns:
            "ok" on success.

        JSON-RPC method: printer.emergency_stop
        """
        return await self._request("POST", "/printer/emergency_stop")  # type: ignore[attr-defined]

    async def printer_restart(self) -> str:
        """Request a Klipper soft restart.

        Returns:
            "ok" on success.

        JSON-RPC method: printer.restart
        """
        return await self._request("POST", "/printer/restart")  # type: ignore[attr-defined]

    async def firmware_restart(self) -> str:
        """Request a complete Klipper restart.

        Returns:
            "ok" on success.

        JSON-RPC method: printer.firmware_restart
        """
        return await self._request("POST", "/printer/firmware_restart")  # type: ignore[attr-defined]
