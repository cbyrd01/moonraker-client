"""API endpoints for Updates operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class UpdatesMixin:
    """Synchronous updates API methods."""

    def machine_update_status(self, refresh: bool = False) -> Any:
        """Get update status

        Args:
            refresh: *DEPRECATED*.  When `true` an attempt will be made to refresh all updaters. The  (optional)

        JSON-RPC method: machine.update.status
        """
        params: dict[str, Any] = {}
        if refresh is not None:
            params["refresh"] = refresh
        return self._request("GET", "/machine/update/status", params=params)

    def machine_update_refresh(self, name: str | None = None) -> Any:
        """Refresh update status

        Refreshes the internal update state for the requested software.
        
        **Note:** This endpoint will raise 503 error under the following conditions:
        
          - An update is in progress
          - A print is in progress
          - The update manager hasn't completed initialization
        
        **Note:** Applications should use care when calling this method as a refresh
        is CPU intensive and may be time consuming.  Moonraker can be
        configured to refresh state periodically, thus it is recommended
        that applications avoid their own procedural implementations.
        Instead it is best to call this API only when a user requests a
        refresh.

        Args:
            name: The name of the software to refresh. If omitted all registered software will be  (optional)

        JSON-RPC method: machine.update.refresh
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return self._request("POST", "/machine/update/refresh", json=body)

    def machine_update_upgrade(self, name: str | None = None) -> Any:
        """Perform an Upgrade

        *Added in API Version 1.5.0*
        
        Upgrade to the most recent release of the requested software.
        If an update is requested while a print is in progress then this
        request will return an error.

        Args:
            name: The name of the software to upgrade. If omitted all registered software updates  (optional)

        JSON-RPC method: machine.update.upgrade
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return self._request("POST", "/machine/update/upgrade", json=body)

    def machine_update_recover(self, name: str, hard: bool = False) -> Any:
        """Recover a corrupt repo

        On occasion a git command may fail resulting in a repo in a
        dirty or invalid state.  This endpoint may be used to attempt
        to recover a git repo that is dirty, broken, or corrupt.

        Args:
            name: The name of the software to recover.
            hard: Determines the [mode](#git-repo-recovery-mode-desc) used to perform the recovery (optional)

        JSON-RPC method: machine.update.recover
        """
        body: dict[str, Any] = {}
        body["name"] = name
        if hard is not None:
            body["hard"] = hard
        return self._request("POST", "/machine/update/recover", json=body)

    def machine_update_rollback(self) -> Any:
        """Rollback to the previous version
        """
        return self._request("POST", "/machine/update/rollback")

    def machine_update_full(self) -> Any:
        """Perform a full update

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Attempts to update all registered software.  Updates are performed in the
        following order:
        
        - `system` if enabled
        - All optional software configured in `moonraker.conf`.
        - Klipper
        - Moonraker

        JSON-RPC method: machine.update.full
        """
        return self._request("POST", "/machine/update/full")

    def machine_update_moonraker(self) -> Any:
        """Update Moonraker

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Upgrades to the latest version of Moonraker and restarts
        the service. If an update is requested while a print is in progress then
        this request will return an error.

        JSON-RPC method: machine.update.moonraker
        """
        return self._request("POST", "/machine/update/moonraker")

    def machine_update_klipper(self) -> Any:
        """Update Klipper

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Upgrades to the latest version of Klipper and restarts
        the service. If an update is requested while a print is in progress
        then this request will return an error.

        JSON-RPC method: machine.update.klipper
        """
        return self._request("POST", "/machine/update/klipper")

    def machine_update_client(self, name: str | None = None) -> Any:
        """Update Client

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Update to the most recent release of the requested software.
        If an update is requested while a print is in progress then this
        request will return an error.

        Args:
            name: The name of the software to upgrade. If omitted all registered software updates  (optional)

        JSON-RPC method: machine.update.client
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return self._request("POST", "/machine/update/client", json=body)

    def machine_update_system(self) -> Any:
        """Update System Packages

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Upgrades system packages.  If an update is requested while a print is
        in progress then this request will return an error.

        JSON-RPC method: machine.update.system
        """
        return self._request("POST", "/machine/update/system")


class AsyncUpdatesMixin:
    """Asynchronous updates API methods."""

    async def machine_update_status(self, refresh: bool = False) -> Any:
        """Get update status

        Args:
            refresh: *DEPRECATED*.  When `true` an attempt will be made to refresh all updaters. The  (optional)

        JSON-RPC method: machine.update.status
        """
        params: dict[str, Any] = {}
        if refresh is not None:
            params["refresh"] = refresh
        return await self._request("GET", "/machine/update/status", params=params)

    async def machine_update_refresh(self, name: str | None = None) -> Any:
        """Refresh update status

        Refreshes the internal update state for the requested software.
        
        **Note:** This endpoint will raise 503 error under the following conditions:
        
          - An update is in progress
          - A print is in progress
          - The update manager hasn't completed initialization
        
        **Note:** Applications should use care when calling this method as a refresh
        is CPU intensive and may be time consuming.  Moonraker can be
        configured to refresh state periodically, thus it is recommended
        that applications avoid their own procedural implementations.
        Instead it is best to call this API only when a user requests a
        refresh.

        Args:
            name: The name of the software to refresh. If omitted all registered software will be  (optional)

        JSON-RPC method: machine.update.refresh
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return await self._request("POST", "/machine/update/refresh", json=body)

    async def machine_update_upgrade(self, name: str | None = None) -> Any:
        """Perform an Upgrade

        *Added in API Version 1.5.0*
        
        Upgrade to the most recent release of the requested software.
        If an update is requested while a print is in progress then this
        request will return an error.

        Args:
            name: The name of the software to upgrade. If omitted all registered software updates  (optional)

        JSON-RPC method: machine.update.upgrade
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return await self._request("POST", "/machine/update/upgrade", json=body)

    async def machine_update_recover(self, name: str, hard: bool = False) -> Any:
        """Recover a corrupt repo

        On occasion a git command may fail resulting in a repo in a
        dirty or invalid state.  This endpoint may be used to attempt
        to recover a git repo that is dirty, broken, or corrupt.

        Args:
            name: The name of the software to recover.
            hard: Determines the [mode](#git-repo-recovery-mode-desc) used to perform the recovery (optional)

        JSON-RPC method: machine.update.recover
        """
        body: dict[str, Any] = {}
        body["name"] = name
        if hard is not None:
            body["hard"] = hard
        return await self._request("POST", "/machine/update/recover", json=body)

    async def machine_update_rollback(self) -> Any:
        """Rollback to the previous version
        """
        return await self._request("POST", "/machine/update/rollback")

    async def machine_update_full(self) -> Any:
        """Perform a full update

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Attempts to update all registered software.  Updates are performed in the
        following order:
        
        - `system` if enabled
        - All optional software configured in `moonraker.conf`.
        - Klipper
        - Moonraker

        JSON-RPC method: machine.update.full
        """
        return await self._request("POST", "/machine/update/full")

    async def machine_update_moonraker(self) -> Any:
        """Update Moonraker

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Upgrades to the latest version of Moonraker and restarts
        the service. If an update is requested while a print is in progress then
        this request will return an error.

        JSON-RPC method: machine.update.moonraker
        """
        return await self._request("POST", "/machine/update/moonraker")

    async def machine_update_klipper(self) -> Any:
        """Update Klipper

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Upgrades to the latest version of Klipper and restarts
        the service. If an update is requested while a print is in progress
        then this request will return an error.

        JSON-RPC method: machine.update.klipper
        """
        return await self._request("POST", "/machine/update/klipper")

    async def machine_update_client(self, name: str | None = None) -> Any:
        """Update Client

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Update to the most recent release of the requested software.
        If an update is requested while a print is in progress then this
        request will return an error.

        Args:
            name: The name of the software to upgrade. If omitted all registered software updates  (optional)

        JSON-RPC method: machine.update.client
        """
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        return await self._request("POST", "/machine/update/client", json=body)

    async def machine_update_system(self) -> Any:
        """Update System Packages

        *Deprecated in API Version 1.5.0, superseded by the*
        *[Upgrade](#perform-an-upgrade) endpoint.*
        
        Upgrades system packages.  If an update is requested while a print is
        in progress then this request will return an error.

        JSON-RPC method: machine.update.system
        """
        return await self._request("POST", "/machine/update/system")
