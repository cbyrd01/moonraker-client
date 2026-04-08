"""API endpoints for Devices operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class DevicesMixin:
    """Synchronous devices API methods."""

    def machine_devicepower_devices(self) -> Any:
        """Get Device List

        JSON-RPC method: machine.device_power.devices
        """
        return self._request("GET", "/machine/device_power/devices")

    def machine_devicepower_device(self) -> Any:
        """Get Device State

        Requests the device state for a single configured device.

        JSON-RPC method: machine.device_power.get_device
        """
        return self._request("GET", "/machine/device_power/device")

    def machine_devicepower_status(self, device: str | None = None) -> Any:
        """Get Batch Device Status

        Get power status for the requested devices.  At least one device must be
        specified.
        
        **Note:** The strangeness of this parameter specification is an artifact
        from an early attempt to simplify the query string and maintain
        compatibility with JSON parameters.

        Args:
            device: (Dynamic parameter name) There may be multiple devices specified, where the keys (optional)

        JSON-RPC method: machine.device_power.status
        """
        params: dict[str, Any] = {}
        if device is not None:
            params["device"] = device
        return self._request("GET", "/machine/device_power/status", params=params)

    def machine_devicepower_on(self, *device*: Any | None = None) -> Any:
        """Batch Power On Devices

        Power on the requested devices.  At least one device must be
        specified.
        
        **Note:** The strangeness of this parameter specification is an artifact
        from an early attempt to simplify query string parameters and maintain
        compatibility with JSON parameters.

        Args:
            *device*: There may be multiple devices specified, where the keys the requested device nam (optional)

        JSON-RPC method: machine.device_power.on
        """
        body: dict[str, Any] = {}
        if *device* is not None:
            body["*device*"] = *device*
        return self._request("POST", "/machine/device_power/on", json=body)

    def machine_devicepower_off(self, *device*: Any | None = None) -> Any:
        """Batch Power Off Devices

        Power off the requested devices.  At least one device must be
        specified.
        
        **Note:** The strangeness of this parameter specification is an artifact
        from an early attempt to simplify query string parameters and maintain
        compatibility with JSON parameters.

        Args:
            *device*: There may be multiple devices specified, where the keys the requested device nam (optional)

        JSON-RPC method: machine.device_power.off
        """
        body: dict[str, Any] = {}
        if *device* is not None:
            body["*device*"] = *device*
        return self._request("POST", "/machine/device_power/off", json=body)

    def machine_wled_strips(self) -> Any:
        """Get strips

        JSON-RPC method: machine.wled.strips
        """
        return self._request("GET", "/machine/wled/strips")

    def machine_wled_status(self, strip: str | None = None) -> Any:
        """Get strip status

        Args:
            strip: (Dynamic parameter name) There may be multiple strips specified, where the keys  (optional)

        JSON-RPC method: machine.wled.status
        """
        params: dict[str, Any] = {}
        if strip is not None:
            params["strip"] = strip
        return self._request("GET", "/machine/wled/status", params=params)

    def machine_wled_on(self) -> Any:
        """Turn strip on

        Turns the specified strips on to the initial colors or initial preset.

        JSON-RPC method: machine.wled.on
        """
        return self._request("POST", "/machine/wled/on")

    def machine_wled_off(self, *strip*: Any | None = None) -> Any:
        """Turn strip off

        Turns off all specified strips.

        Args:
            *strip*: There may be multiple strips specified, where the keys the requested strip names (optional)

        JSON-RPC method: machine.wled.off
        """
        body: dict[str, Any] = {}
        if *strip* is not None:
            body["*strip*"] = *strip*
        return self._request("POST", "/machine/wled/off", json=body)

    def machine_wled_toggle(self, *strip*: Any | None = None) -> Any:
        """Toggle strip on/off state

        Toggles the current enabled state for the requested strips.

        Args:
            *strip*: There may be multiple strips specified, where the keys the requested strip names (optional)

        JSON-RPC method: machine.wled.toggle
        """
        body: dict[str, Any] = {}
        if *strip* is not None:
            body["*strip*"] = *strip*
        return self._request("POST", "/machine/wled/toggle", json=body)

    def machine_wled_strip(self) -> Any:
        """Get individual strip state

        JSON-RPC method: machine.wled.get_strip
        """
        return self._request("GET", "/machine/wled/strip")

    def server_sensors_list(self, extended: bool = False) -> Any:
        """Get Sensor List

        Args:
            extended: When set to `true` the status for each sensor will include `parameter_info` and  (optional)

        JSON-RPC method: server.sensors.list
        """
        params: dict[str, Any] = {}
        if extended is not None:
            params["extended"] = extended
        return self._request("GET", "/server/sensors/list", params=params)

    def server_sensors_info(self, sensor: str, extended: bool = False) -> Any:
        """Get Sensor Information

        Returns the status for a single configured sensor.

        Args:
            sensor: The ID of the requested sensor.
            extended: When set to `true` the status for the sensor will include `parameter_info` and ` (optional)

        JSON-RPC method: server.sensors.info
        """
        params: dict[str, Any] = {}
        params["sensor"] = sensor
        if extended is not None:
            params["extended"] = extended
        return self._request("GET", "/server/sensors/info", params=params)

    def server_sensors_measurements(self) -> Any:
        """Get Batch Sensor Measurements

        Returns recorded measurements for all sensors.

        JSON-RPC method: server.sensors.measurements
        """
        return self._request("GET", "/server/sensors/measurements")

    def server_mqtt_publish(self, topic: str, payload: dict[str, Any] | None = None, qos: int | None = None, retain: bool = False, timeout: float | None = None) -> Any:
        """Publish a topic

        Args:
            topic: The topic to publish to the network.
            payload: The payload to send with the topic. May be a boolean, float, integer, object, or (optional)
            qos: The QOS level to use when publishing a topic.  Valid range is 0-2. (optional)
            retain: When set to `true` the topic's retain flag is set. (optional)
            timeout: A timeout, in seconds, in which Moonraker will wait for acknowledgement from the (optional)

        JSON-RPC method: server.mqtt.publish
        """
        body: dict[str, Any] = {}
        body["topic"] = topic
        if payload is not None:
            body["payload"] = payload
        if qos is not None:
            body["qos"] = qos
        if retain is not None:
            body["retain"] = retain
        if timeout is not None:
            body["timeout"] = timeout
        return self._request("POST", "/server/mqtt/publish", json=body)

    def server_mqtt_subscribe(self, topic: str, qos: int | None = None, timeout: float | None = None) -> Any:
        """Subscribe to a topic

        Args:
            topic: The topic to subscribe to.  Wildcards are **not** allowed.
            qos: The QOS level to use for the subscription. Valid range is 0-2. (optional)
            timeout: A timeout, in seconds, to wait until a response is received.  The request will r (optional)

        JSON-RPC method: server.mqtt.subscribe
        """
        body: dict[str, Any] = {}
        body["topic"] = topic
        if qos is not None:
            body["qos"] = qos
        if timeout is not None:
            body["timeout"] = timeout
        return self._request("POST", "/server/mqtt/subscribe", json=body)


class AsyncDevicesMixin:
    """Asynchronous devices API methods."""

    async def machine_devicepower_devices(self) -> Any:
        """Get Device List

        JSON-RPC method: machine.device_power.devices
        """
        return await self._request("GET", "/machine/device_power/devices")

    async def machine_devicepower_device(self) -> Any:
        """Get Device State

        Requests the device state for a single configured device.

        JSON-RPC method: machine.device_power.get_device
        """
        return await self._request("GET", "/machine/device_power/device")

    async def machine_devicepower_status(self, device: str | None = None) -> Any:
        """Get Batch Device Status

        Get power status for the requested devices.  At least one device must be
        specified.
        
        **Note:** The strangeness of this parameter specification is an artifact
        from an early attempt to simplify the query string and maintain
        compatibility with JSON parameters.

        Args:
            device: (Dynamic parameter name) There may be multiple devices specified, where the keys (optional)

        JSON-RPC method: machine.device_power.status
        """
        params: dict[str, Any] = {}
        if device is not None:
            params["device"] = device
        return await self._request("GET", "/machine/device_power/status", params=params)

    async def machine_devicepower_on(self, *device*: Any | None = None) -> Any:
        """Batch Power On Devices

        Power on the requested devices.  At least one device must be
        specified.
        
        **Note:** The strangeness of this parameter specification is an artifact
        from an early attempt to simplify query string parameters and maintain
        compatibility with JSON parameters.

        Args:
            *device*: There may be multiple devices specified, where the keys the requested device nam (optional)

        JSON-RPC method: machine.device_power.on
        """
        body: dict[str, Any] = {}
        if *device* is not None:
            body["*device*"] = *device*
        return await self._request("POST", "/machine/device_power/on", json=body)

    async def machine_devicepower_off(self, *device*: Any | None = None) -> Any:
        """Batch Power Off Devices

        Power off the requested devices.  At least one device must be
        specified.
        
        **Note:** The strangeness of this parameter specification is an artifact
        from an early attempt to simplify query string parameters and maintain
        compatibility with JSON parameters.

        Args:
            *device*: There may be multiple devices specified, where the keys the requested device nam (optional)

        JSON-RPC method: machine.device_power.off
        """
        body: dict[str, Any] = {}
        if *device* is not None:
            body["*device*"] = *device*
        return await self._request("POST", "/machine/device_power/off", json=body)

    async def machine_wled_strips(self) -> Any:
        """Get strips

        JSON-RPC method: machine.wled.strips
        """
        return await self._request("GET", "/machine/wled/strips")

    async def machine_wled_status(self, strip: str | None = None) -> Any:
        """Get strip status

        Args:
            strip: (Dynamic parameter name) There may be multiple strips specified, where the keys  (optional)

        JSON-RPC method: machine.wled.status
        """
        params: dict[str, Any] = {}
        if strip is not None:
            params["strip"] = strip
        return await self._request("GET", "/machine/wled/status", params=params)

    async def machine_wled_on(self) -> Any:
        """Turn strip on

        Turns the specified strips on to the initial colors or initial preset.

        JSON-RPC method: machine.wled.on
        """
        return await self._request("POST", "/machine/wled/on")

    async def machine_wled_off(self, *strip*: Any | None = None) -> Any:
        """Turn strip off

        Turns off all specified strips.

        Args:
            *strip*: There may be multiple strips specified, where the keys the requested strip names (optional)

        JSON-RPC method: machine.wled.off
        """
        body: dict[str, Any] = {}
        if *strip* is not None:
            body["*strip*"] = *strip*
        return await self._request("POST", "/machine/wled/off", json=body)

    async def machine_wled_toggle(self, *strip*: Any | None = None) -> Any:
        """Toggle strip on/off state

        Toggles the current enabled state for the requested strips.

        Args:
            *strip*: There may be multiple strips specified, where the keys the requested strip names (optional)

        JSON-RPC method: machine.wled.toggle
        """
        body: dict[str, Any] = {}
        if *strip* is not None:
            body["*strip*"] = *strip*
        return await self._request("POST", "/machine/wled/toggle", json=body)

    async def machine_wled_strip(self) -> Any:
        """Get individual strip state

        JSON-RPC method: machine.wled.get_strip
        """
        return await self._request("GET", "/machine/wled/strip")

    async def server_sensors_list(self, extended: bool = False) -> Any:
        """Get Sensor List

        Args:
            extended: When set to `true` the status for each sensor will include `parameter_info` and  (optional)

        JSON-RPC method: server.sensors.list
        """
        params: dict[str, Any] = {}
        if extended is not None:
            params["extended"] = extended
        return await self._request("GET", "/server/sensors/list", params=params)

    async def server_sensors_info(self, sensor: str, extended: bool = False) -> Any:
        """Get Sensor Information

        Returns the status for a single configured sensor.

        Args:
            sensor: The ID of the requested sensor.
            extended: When set to `true` the status for the sensor will include `parameter_info` and ` (optional)

        JSON-RPC method: server.sensors.info
        """
        params: dict[str, Any] = {}
        params["sensor"] = sensor
        if extended is not None:
            params["extended"] = extended
        return await self._request("GET", "/server/sensors/info", params=params)

    async def server_sensors_measurements(self) -> Any:
        """Get Batch Sensor Measurements

        Returns recorded measurements for all sensors.

        JSON-RPC method: server.sensors.measurements
        """
        return await self._request("GET", "/server/sensors/measurements")

    async def server_mqtt_publish(self, topic: str, payload: dict[str, Any] | None = None, qos: int | None = None, retain: bool = False, timeout: float | None = None) -> Any:
        """Publish a topic

        Args:
            topic: The topic to publish to the network.
            payload: The payload to send with the topic. May be a boolean, float, integer, object, or (optional)
            qos: The QOS level to use when publishing a topic.  Valid range is 0-2. (optional)
            retain: When set to `true` the topic's retain flag is set. (optional)
            timeout: A timeout, in seconds, in which Moonraker will wait for acknowledgement from the (optional)

        JSON-RPC method: server.mqtt.publish
        """
        body: dict[str, Any] = {}
        body["topic"] = topic
        if payload is not None:
            body["payload"] = payload
        if qos is not None:
            body["qos"] = qos
        if retain is not None:
            body["retain"] = retain
        if timeout is not None:
            body["timeout"] = timeout
        return await self._request("POST", "/server/mqtt/publish", json=body)

    async def server_mqtt_subscribe(self, topic: str, qos: int | None = None, timeout: float | None = None) -> Any:
        """Subscribe to a topic

        Args:
            topic: The topic to subscribe to.  Wildcards are **not** allowed.
            qos: The QOS level to use for the subscription. Valid range is 0-2. (optional)
            timeout: A timeout, in seconds, to wait until a response is received.  The request will r (optional)

        JSON-RPC method: server.mqtt.subscribe
        """
        body: dict[str, Any] = {}
        body["topic"] = topic
        if qos is not None:
            body["qos"] = qos
        if timeout is not None:
            body["timeout"] = timeout
        return await self._request("POST", "/server/mqtt/subscribe", json=body)
