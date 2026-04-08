"""Devices API endpoint mixins.

Covers /machine/device_power/*, /machine/wled/*, /server/sensors/* endpoints.
Generated from OpenAPI spec and hand-tuned.
"""

from __future__ import annotations

from typing import Any


class DevicesMixin:
    """Synchronous devices API methods."""

    def power_devices_list(self) -> list[dict[str, Any]]:
        """List configured power devices.

        JSON-RPC method: machine.device_power.devices
        """
        return self._request("GET", "/machine/device_power/devices")  # type: ignore[attr-defined]

    def power_device_status(self, device: str) -> dict[str, Any]:
        """Get the status of a power device.

        Args:
            device: The name of the device to query.

        JSON-RPC method: machine.device_power.get_device
        """
        return self._request("GET", "/machine/device_power/device", params={"device": device})  # type: ignore[attr-defined]

    def power_device_set(self, device: str, action: str) -> dict[str, Any]:
        """Set the state of a power device.

        Args:
            device: The name of the device.
            action: The action to take ("on" or "off").

        JSON-RPC method: machine.device_power.post_device
        """
        return self._request("POST", "/machine/device_power/device", json={device: action})  # type: ignore[attr-defined]

    def power_on(self, **devices: Any) -> dict[str, str]:
        """Turn on power devices.

        Pass device names as keyword arguments. E.g. power_on(printer=None)

        JSON-RPC method: machine.device_power.on
        """
        return self._request("POST", "/machine/device_power/on", json=devices)  # type: ignore[attr-defined]

    def power_off(self, **devices: Any) -> dict[str, str]:
        """Turn off power devices.

        Pass device names as keyword arguments. E.g. power_off(printer=None)

        JSON-RPC method: machine.device_power.off
        """
        return self._request("POST", "/machine/device_power/off", json=devices)  # type: ignore[attr-defined]

    def wled_strips(self) -> dict[str, Any]:
        """List configured WLED strips.

        JSON-RPC method: machine.wled.strips
        """
        return self._request("GET", "/machine/wled/strips")  # type: ignore[attr-defined]

    def wled_status(self, strip: str | None = None) -> dict[str, Any]:
        """Get WLED strip status.

        Args:
            strip: Strip name to query. If None, returns all.

        JSON-RPC method: machine.wled.status
        """
        params: dict[str, Any] = {}
        if strip is not None:
            params["strip"] = strip
        return self._request("GET", "/machine/wled/status", params=params)  # type: ignore[attr-defined]

    def wled_on(self, strip: str, preset: int | None = None, brightness: int | None = None) -> dict[str, Any]:
        """Turn on a WLED strip.

        Args:
            strip: Name of the strip.
            preset: WLED preset to activate.
            brightness: Brightness level (0-255).

        JSON-RPC method: machine.wled.on
        """
        body: dict[str, Any] = {"strip": strip}
        if preset is not None:
            body["preset"] = preset
        if brightness is not None:
            body["brightness"] = brightness
        return self._request("POST", "/machine/wled/on", json=body)  # type: ignore[attr-defined]

    def wled_off(self, strip: str) -> dict[str, Any]:
        """Turn off a WLED strip.

        Args:
            strip: Name of the strip.

        JSON-RPC method: machine.wled.off
        """
        return self._request("POST", "/machine/wled/off", json={"strip": strip})  # type: ignore[attr-defined]

    def wled_toggle(self, strip: str) -> dict[str, Any]:
        """Toggle a WLED strip on/off.

        Args:
            strip: Name of the strip.

        JSON-RPC method: machine.wled.toggle
        """
        return self._request("POST", "/machine/wled/toggle", json={"strip": strip})  # type: ignore[attr-defined]

    def sensors_list(self) -> dict[str, Any]:
        """List configured sensors.

        JSON-RPC method: server.sensors.list
        """
        return self._request("GET", "/server/sensors/list")  # type: ignore[attr-defined]

    def sensors_info(self, sensor: str | None = None) -> dict[str, Any]:
        """Get sensor info.

        Args:
            sensor: Sensor name. If None, returns all.

        JSON-RPC method: server.sensors.info
        """
        params: dict[str, Any] = {}
        if sensor is not None:
            params["sensor"] = sensor
        return self._request("GET", "/server/sensors/info", params=params)  # type: ignore[attr-defined]

    def sensors_measurements(self, sensor: str | None = None) -> dict[str, Any]:
        """Get sensor measurements.

        Args:
            sensor: Sensor name. If None, returns all.

        JSON-RPC method: server.sensors.measurements
        """
        params: dict[str, Any] = {}
        if sensor is not None:
            params["sensor"] = sensor
        return self._request("GET", "/server/sensors/measurements", params=params)  # type: ignore[attr-defined]


class AsyncDevicesMixin:
    """Asynchronous devices API methods."""

    async def power_devices_list(self) -> list[dict[str, Any]]:
        """List configured power devices."""
        return await self._request("GET", "/machine/device_power/devices")  # type: ignore[attr-defined]

    async def power_device_status(self, device: str) -> dict[str, Any]:
        """Get the status of a power device."""
        return await self._request("GET", "/machine/device_power/device", params={"device": device})  # type: ignore[attr-defined]

    async def power_device_set(self, device: str, action: str) -> dict[str, Any]:
        """Set the state of a power device."""
        return await self._request("POST", "/machine/device_power/device", json={device: action})  # type: ignore[attr-defined]

    async def power_on(self, **devices: Any) -> dict[str, str]:
        """Turn on power devices."""
        return await self._request("POST", "/machine/device_power/on", json=devices)  # type: ignore[attr-defined]

    async def power_off(self, **devices: Any) -> dict[str, str]:
        """Turn off power devices."""
        return await self._request("POST", "/machine/device_power/off", json=devices)  # type: ignore[attr-defined]

    async def wled_strips(self) -> dict[str, Any]:
        """List configured WLED strips."""
        return await self._request("GET", "/machine/wled/strips")  # type: ignore[attr-defined]

    async def wled_status(self, strip: str | None = None) -> dict[str, Any]:
        """Get WLED strip status."""
        params: dict[str, Any] = {}
        if strip is not None:
            params["strip"] = strip
        return await self._request("GET", "/machine/wled/status", params=params)  # type: ignore[attr-defined]

    async def wled_on(self, strip: str, preset: int | None = None, brightness: int | None = None) -> dict[str, Any]:
        """Turn on a WLED strip."""
        body: dict[str, Any] = {"strip": strip}
        if preset is not None:
            body["preset"] = preset
        if brightness is not None:
            body["brightness"] = brightness
        return await self._request("POST", "/machine/wled/on", json=body)  # type: ignore[attr-defined]

    async def wled_off(self, strip: str) -> dict[str, Any]:
        """Turn off a WLED strip."""
        return await self._request("POST", "/machine/wled/off", json={"strip": strip})  # type: ignore[attr-defined]

    async def wled_toggle(self, strip: str) -> dict[str, Any]:
        """Toggle a WLED strip on/off."""
        return await self._request("POST", "/machine/wled/toggle", json={"strip": strip})  # type: ignore[attr-defined]

    async def sensors_list(self) -> dict[str, Any]:
        """List configured sensors."""
        return await self._request("GET", "/server/sensors/list")  # type: ignore[attr-defined]

    async def sensors_info(self, sensor: str | None = None) -> dict[str, Any]:
        """Get sensor info."""
        params: dict[str, Any] = {}
        if sensor is not None:
            params["sensor"] = sensor
        return await self._request("GET", "/server/sensors/info", params=params)  # type: ignore[attr-defined]

    async def sensors_measurements(self, sensor: str | None = None) -> dict[str, Any]:
        """Get sensor measurements."""
        params: dict[str, Any] = {}
        if sensor is not None:
            params["sensor"] = sensor
        return await self._request("GET", "/server/sensors/measurements", params=params)  # type: ignore[attr-defined]
