"""API endpoints for Machine operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class MachineMixin:
    """Synchronous machine API methods."""

    def machine_systeminfo(self) -> Any:
        """Get System Info

        JSON-RPC method: machine.system_info
        """
        return self._request("GET", "/machine/system_info")

    def machine_shutdown(self) -> Any:
        """Shutdown the Operating System

        Commands the Operating System to shutdown.  The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must be `systemd_cli` or `systemd_dbus`.
        - Moonraker must have permission to shutdown the host.
        - Moonraker must not be running inside a container.

        JSON-RPC method: machine.shutdown
        """
        return self._request("POST", "/machine/shutdown")

    def machine_reboot(self) -> Any:
        """Reboot the Operating System

        Commands the Operating System to shutdown.  The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must be `systemd_cli` or `systemd_dbus`.
        - Moonraker must have permission to reboot the host.
        - Moonraker must not be running inside a container.

        JSON-RPC method: machine.reboot
        """
        return self._request("POST", "/machine/reboot")

    def machine_services_restart(self, service: str) -> Any:
        """Restart a system service

        Commands a service to restart. The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must NOT be `none`.
        - The service must be present in the list of `allowed_services`.
        - Moonraker must have the necessary permissions to manage services.

        Args:
            service: The name of the service to restart.

        JSON-RPC method: machine.services.restart
        """
        body: dict[str, Any] = {}
        body["service"] = service
        return self._request("POST", "/machine/services/restart", json=body)

    def machine_services_stop(self, service: str) -> Any:
        """Stop a system service

        Commands a service to stop. The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must NOT be `none`.
        - The service must be present in the list of `allowed_services`.
        - Moonraker must have the necessary permissions to manage services.

        Args:
            service: The name of the service to stop.

        JSON-RPC method: machine.services.stop
        """
        body: dict[str, Any] = {}
        body["service"] = service
        return self._request("POST", "/machine/services/stop", json=body)

    def machine_services_start(self, service: str) -> Any:
        """Start a system service

        Commands a service to start. The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must NOT be `none`.
        - The service must be present in the list of `allowed_services`.
        - Moonraker must have the necessary permissions to manage services.

        Args:
            service: The name of the service to start.

        JSON-RPC method: machine.services.start
        """
        body: dict[str, Any] = {}
        body["service"] = service
        return self._request("POST", "/machine/services/start", json=body)

    def machine_procstats(self) -> Any:
        """Get process statistics

        Requests system usage information.  This includes CPU usage, network usage,
        etc.

        JSON-RPC method: machine.proc_stats
        """
        return self._request("GET", "/machine/proc_stats")

    def machine_sudo_info(self, check_access: bool = False) -> Any:
        """Get Sudo Info

        Retrieves sudo information status.  Optionally checks if Moonraker has
        permission to run commands as root.

        Args:
            check_access: When `true` Moonraker will attempt to run a sudo command in a effort to check if (optional)

        JSON-RPC method: machine.sudo.info
        """
        params: dict[str, Any] = {}
        if check_access is not None:
            params["check_access"] = check_access
        return self._request("GET", "/machine/sudo/info", params=params)

    def machine_sudo_password(self, password: str) -> Any:
        """Set sudo password

        Sets the sudo password currently used by Moonraker.  The password
        is not persistent across Moonraker restarts.  If Moonraker has one or
        more pending sudo requests they will be processed.
        
        **Note:** This request will return an error if the supplied password is
        incorrect or if any pending sudo requests fail.

        Args:
            password: The linux user password necessary to grant Moonraker sudo permission.

        JSON-RPC method: machine.sudo.password
        """
        body: dict[str, Any] = {}
        body["password"] = password
        return self._request("POST", "/machine/sudo/password", json=body)

    def machine_peripherals_usb(self) -> Any:
        """List USB Devices

        Returns a list of all USB devices currently detected on the system.

        JSON-RPC method: machine.peripherals.usb
        """
        return self._request("GET", "/machine/peripherals/usb")

    def machine_peripherals_serial(self) -> Any:
        """List Serial Devices

        Returns a list of all serial devices detected on the system.  These may be USB
        CDC-ACM devices or hardware UARTs.

        JSON-RPC method: machine.peripherals.serial
        """
        return self._request("GET", "/machine/peripherals/serial")

    def machine_peripherals_video(self) -> Any:
        """List Video Capture Devices

        Retrieves a list of V4L2 video capture devices on the system.  If
        the python3-libcamera system package is installed this request will
        also return libcamera devices.

        JSON-RPC method: machine.peripherals.video
        """
        return self._request("GET", "/machine/peripherals/video")

    def machine_peripherals_canbus(self, interface: str = 'can0') -> Any:
        """Query Unassigned Canbus UUIDs

        Queries the provided canbus interface for unassigned Klipper or Katapult
        node IDs.
        
        !!! Warning
            It is recommended that frontends provide users with an explanation
            of how UUID queries work and the potential pitfalls when querying
            a bus with multiple unassigned nodes.  An "unassigned" node is a
            CAN node that has not been activated by Katapult or Klipper.  If
            either Klipper or Katapult has connected to the node, it will be
            assigned a Node ID and therefore will no longer respond to queries.
            A device reset is required to remove the assignment.
        
            When multiple unassigned nodes are on the network, each responds to
            the query at roughly the same time.  This results in arbitration
            errors.  Nodes will retry the send until the response reports success.
            However, nodes track the count of arbitration errors, and once a
            specific threshold is reached they will go into a "bus off" state. A
            device reset is required to reset the counter and recover from "bus off".
        
            For this reason, it is recommended that users only issue a query when
            a single unassigned node is on the network.  If a user does wish to
            query multiple unassigned nodes it is vital that they reset all nodes
            on the network before running Klipper.

        Args:
            interface: The cansocket interface to query. (optional)

        JSON-RPC method: machine.peripherals.canbus
        """
        params: dict[str, Any] = {}
        if interface is not None:
            params["interface"] = interface
        return self._request("GET", "/machine/peripherals/canbus", params=params)


class AsyncMachineMixin:
    """Asynchronous machine API methods."""

    async def machine_systeminfo(self) -> Any:
        """Get System Info

        JSON-RPC method: machine.system_info
        """
        return await self._request("GET", "/machine/system_info")

    async def machine_shutdown(self) -> Any:
        """Shutdown the Operating System

        Commands the Operating System to shutdown.  The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must be `systemd_cli` or `systemd_dbus`.
        - Moonraker must have permission to shutdown the host.
        - Moonraker must not be running inside a container.

        JSON-RPC method: machine.shutdown
        """
        return await self._request("POST", "/machine/shutdown")

    async def machine_reboot(self) -> Any:
        """Reboot the Operating System

        Commands the Operating System to shutdown.  The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must be `systemd_cli` or `systemd_dbus`.
        - Moonraker must have permission to reboot the host.
        - Moonraker must not be running inside a container.

        JSON-RPC method: machine.reboot
        """
        return await self._request("POST", "/machine/reboot")

    async def machine_services_restart(self, service: str) -> Any:
        """Restart a system service

        Commands a service to restart. The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must NOT be `none`.
        - The service must be present in the list of `allowed_services`.
        - Moonraker must have the necessary permissions to manage services.

        Args:
            service: The name of the service to restart.

        JSON-RPC method: machine.services.restart
        """
        body: dict[str, Any] = {}
        body["service"] = service
        return await self._request("POST", "/machine/services/restart", json=body)

    async def machine_services_stop(self, service: str) -> Any:
        """Stop a system service

        Commands a service to stop. The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must NOT be `none`.
        - The service must be present in the list of `allowed_services`.
        - Moonraker must have the necessary permissions to manage services.

        Args:
            service: The name of the service to stop.

        JSON-RPC method: machine.services.stop
        """
        body: dict[str, Any] = {}
        body["service"] = service
        return await self._request("POST", "/machine/services/stop", json=body)

    async def machine_services_start(self, service: str) -> Any:
        """Start a system service

        Commands a service to start. The following pre-requisites must be
        met to successfully perform this action:
        
        - The `provider` must NOT be `none`.
        - The service must be present in the list of `allowed_services`.
        - Moonraker must have the necessary permissions to manage services.

        Args:
            service: The name of the service to start.

        JSON-RPC method: machine.services.start
        """
        body: dict[str, Any] = {}
        body["service"] = service
        return await self._request("POST", "/machine/services/start", json=body)

    async def machine_procstats(self) -> Any:
        """Get process statistics

        Requests system usage information.  This includes CPU usage, network usage,
        etc.

        JSON-RPC method: machine.proc_stats
        """
        return await self._request("GET", "/machine/proc_stats")

    async def machine_sudo_info(self, check_access: bool = False) -> Any:
        """Get Sudo Info

        Retrieves sudo information status.  Optionally checks if Moonraker has
        permission to run commands as root.

        Args:
            check_access: When `true` Moonraker will attempt to run a sudo command in a effort to check if (optional)

        JSON-RPC method: machine.sudo.info
        """
        params: dict[str, Any] = {}
        if check_access is not None:
            params["check_access"] = check_access
        return await self._request("GET", "/machine/sudo/info", params=params)

    async def machine_sudo_password(self, password: str) -> Any:
        """Set sudo password

        Sets the sudo password currently used by Moonraker.  The password
        is not persistent across Moonraker restarts.  If Moonraker has one or
        more pending sudo requests they will be processed.
        
        **Note:** This request will return an error if the supplied password is
        incorrect or if any pending sudo requests fail.

        Args:
            password: The linux user password necessary to grant Moonraker sudo permission.

        JSON-RPC method: machine.sudo.password
        """
        body: dict[str, Any] = {}
        body["password"] = password
        return await self._request("POST", "/machine/sudo/password", json=body)

    async def machine_peripherals_usb(self) -> Any:
        """List USB Devices

        Returns a list of all USB devices currently detected on the system.

        JSON-RPC method: machine.peripherals.usb
        """
        return await self._request("GET", "/machine/peripherals/usb")

    async def machine_peripherals_serial(self) -> Any:
        """List Serial Devices

        Returns a list of all serial devices detected on the system.  These may be USB
        CDC-ACM devices or hardware UARTs.

        JSON-RPC method: machine.peripherals.serial
        """
        return await self._request("GET", "/machine/peripherals/serial")

    async def machine_peripherals_video(self) -> Any:
        """List Video Capture Devices

        Retrieves a list of V4L2 video capture devices on the system.  If
        the python3-libcamera system package is installed this request will
        also return libcamera devices.

        JSON-RPC method: machine.peripherals.video
        """
        return await self._request("GET", "/machine/peripherals/video")

    async def machine_peripherals_canbus(self, interface: str = 'can0') -> Any:
        """Query Unassigned Canbus UUIDs

        Queries the provided canbus interface for unassigned Klipper or Katapult
        node IDs.
        
        !!! Warning
            It is recommended that frontends provide users with an explanation
            of how UUID queries work and the potential pitfalls when querying
            a bus with multiple unassigned nodes.  An "unassigned" node is a
            CAN node that has not been activated by Katapult or Klipper.  If
            either Klipper or Katapult has connected to the node, it will be
            assigned a Node ID and therefore will no longer respond to queries.
            A device reset is required to remove the assignment.
        
            When multiple unassigned nodes are on the network, each responds to
            the query at roughly the same time.  This results in arbitration
            errors.  Nodes will retry the send until the response reports success.
            However, nodes track the count of arbitration errors, and once a
            specific threshold is reached they will go into a "bus off" state. A
            device reset is required to reset the counter and recover from "bus off".
        
            For this reason, it is recommended that users only issue a query when
            a single unassigned node is on the network.  If a user does wish to
            query multiple unassigned nodes it is vital that they reset all nodes
            on the network before running Klipper.

        Args:
            interface: The cansocket interface to query. (optional)

        JSON-RPC method: machine.peripherals.canbus
        """
        params: dict[str, Any] = {}
        if interface is not None:
            params["interface"] = interface
        return await self._request("GET", "/machine/peripherals/canbus", params=params)
