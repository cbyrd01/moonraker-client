"""API endpoints for Integrations operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class IntegrationsMixin:
    """Synchronous integrations API methods."""

    def server_notifiers_list(self) -> Any:
        """List Notifiers

        JSON-RPC method: server.notifiers.list
        """
        return self._request("GET", "/server/notifiers/list")

    def debug_notifiers_test(self, name: str) -> Any:
        """Test a notifier (debug)

        Forces a registered notifier to push a notification.

        **Note:** This endpoint is only available when Moonraker's debug
        features are enabled and should not be implemented
        in production code

        Args:
            name: The name of the notifier to test.

        JSON-RPC method: debug.notifiers.test
        """
        body: dict[str, Any] = {}
        body["name"] = name
        return self._request("POST", "/debug/notifiers/test", json=body)

    def server_spoolman_status(self) -> Any:
        """Get Spoolman Status

        Returns the current status of the spoolman module.

        JSON-RPC method: server.spoolman.status
        """
        return self._request("GET", "/server/spoolman/status")

    def server_spoolman_spoolid(self) -> Any:
        """Get active spool

        Retrieve the ID of the spool to which Moonraker reports usage for Spoolman.

        JSON-RPC method: server.spoolman.get_spool_id
        """
        return self._request("GET", "/server/spoolman/spool_id")

    def server_spoolman_proxy(
        self,
        request_method: str,
        path: str,
        use_v2_response: bool = False,
        query: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        """Proxy

        Proxy an API request to the Spoolman Server.

        See Spoolman's [OpenAPI Description](https://donkie.github.io/Spoolman/) for
        detailed information about it's API.

        **Note:** The version 2 response has been added to eliminate ambiguity between
        Spoolman errors and Moonraker errors.  With version 1 a frontend
        is not able to reliably to determine if the error is sourced from
        Spoolman or Moonraker.  Version 2 responses will return success
        unless Moonraker is the source of the error.

        The version 2 response is currently opt-in to avoid breaking
        existing implementations, however in the future it will be
        required, at which point the version 1 response will be removed.
        The version 1 response is now deprecated.

        **Note:** Version 1 responses are proxied directly.  See Spoolman's API
        documentation for response specifications.  Errors are also
        proxied directly.

        Args:
            use_v2_response: When set to `true` the request will return a version 2 response. (optional)
            request_method: The HTTP request method of the API call to proxy.
            path: The path section of the API endpoint to proxy.  It must include the version, ie:
            query: An optional query string component of the URL to proxy.  A `null` value will omi (optional)
            body: An optional body containing request parameters for the API call.  This should be (optional)

        JSON-RPC method: server.spoolman.proxy
        """
        body: dict[str, Any] = {}
        if use_v2_response is not None:
            body["use_v2_response"] = use_v2_response
        body["request_method"] = request_method
        body["path"] = path
        if query is not None:
            body["query"] = query
        if body is not None:
            body["body"] = body
        return self._request("POST", "/server/spoolman/proxy", json=body)

    def server_analysis_status(self) -> Any:
        """Get Analysis Status

        JSON-RPC method: server.analysis.status
        """
        return self._request("GET", "/server/analysis/status")

    def server_analysis_estimate(
        self, filename: str, estimator_config: str = "**CONFIG_DEFAULT**"
    ) -> Any:
        """Perform a time analysis

        Args:
            filename: The path to the gcode file to perform a time estimate on.  This should be a path
            estimator_config: The path to a Klipper Estimator config file, relative to the `config` root folde (optional)

        JSON-RPC method: server.analysis.estimate
        """
        body: dict[str, Any] = {}
        body["filename"] = filename
        if estimator_config is not None:
            body["estimator_config"] = estimator_config
        return self._request("POST", "/server/analysis/estimate", json=body)

    def server_analysis_process(
        self, filename: str, estimator_config: str = "**CONFIG_DEFAULT**", force: bool = False
    ) -> Any:
        """Post process a file

        Klipper Estimator will perform a time analysis and use the results to
        modify the time estimates in the file.  If M73 (progress) commands are
        present they will also be modified.

        **Note:** If the `file_manager` has `inotify` enabled the post-process will trigger a
        `create_file` event, which will in turn trigger metadata extraction.

        Args:
            filename: The path to the gcode file to post-process. This should be a path relative to th
            estimator_config: The path to a Klipper Estimator config file, relative to the `config` root folde (optional)
            force: By default the request will not perform a new post-process if the file was alrea (optional)

        JSON-RPC method: server.analysis.process
        """
        body: dict[str, Any] = {}
        body["filename"] = filename
        if estimator_config is not None:
            body["estimator_config"] = estimator_config
        if force is not None:
            body["force"] = force
        return self._request("POST", "/server/analysis/process", json=body)

    def server_analysis_dumpconfig(self, dest_config: str | None = None) -> Any:
        """Dump the current configuration

        Create a Klipper Estimator configuration file using Klippy's
        current settings.

        **Note:** Klippy must be connected and in the `ready` state to run
        this request.

        **Note:** The default configuration for Klipper Estimator is stored in the same
        folder as the binary.

        ```
        <data_path>/tools/klipper_estimator/default_estimator_cfg.json
        ```

        Args:
            dest_config: The name of the destination config file for the dump. This should be a path rela (optional)

        JSON-RPC method: server.analysis.dump_config
        """
        body: dict[str, Any] = {}
        if dest_config is not None:
            body["dest_config"] = dest_config
        return self._request("POST", "/server/analysis/dump_config", json=body)

    def api_version(self) -> Any:
        """Version information"""
        return self._request("GET", "/api/version")

    def api_server(self) -> Any:
        """Server status"""
        return self._request("GET", "/api/server")

    def api_login(self) -> Any:
        """Login verification & User information"""
        return self._request("GET", "/api/login")

    def api_settings(self) -> Any:
        """Get settings"""
        return self._request("GET", "/api/settings")

    def api_files_local(self) -> Any:
        """OctoPrint File Upload"""
        return self._request("POST", "/api/files/local")

    def api_job(self) -> Any:
        """Get Job status"""
        return self._request("GET", "/api/job")

    def api_printer(self) -> Any:
        """Get Printer status"""
        return self._request("GET", "/api/printer")

    def api_printer_command(self) -> Any:
        """Send GCode command"""
        return self._request("POST", "/api/printer/command")

    def api_printerprofiles(self) -> Any:
        """List Printer profiles"""
        return self._request("GET", "/api/printerprofiles")

    def machine_td1_data(self) -> Any:
        """Get TD-1 Data

        Returns TD-1 data for all devices that are connected.

        **Note:** All TD-1 data fields return null after successful power on until first filament
        is scanned.

        JSON-RPC method: machine.td1.data
        """
        return self._request("GET", "/machine/td1/data")

    def machine_td1_reboot(self, serial: str = "REQUIRED") -> Any:
        """Reset TD-1

        Gives ability to reboot TD-1 device remotely if an error exists when first powering on device.

        Example: User has filament inserted before power on TD-1 device, the following error occurs if
        this happens.

        Args:
            serial: The TD-1 serial to reboot (optional)

        JSON-RPC method: machine.td1.reboot
        """
        body: dict[str, Any] = {}
        if serial is not None:
            body["serial"] = serial
        return self._request("POST", "/machine/td1/reboot", json=body)


class AsyncIntegrationsMixin:
    """Asynchronous integrations API methods."""

    async def server_notifiers_list(self) -> Any:
        """List Notifiers

        JSON-RPC method: server.notifiers.list
        """
        return await self._request("GET", "/server/notifiers/list")

    async def debug_notifiers_test(self, name: str) -> Any:
        """Test a notifier (debug)

        Forces a registered notifier to push a notification.

        **Note:** This endpoint is only available when Moonraker's debug
        features are enabled and should not be implemented
        in production code

        Args:
            name: The name of the notifier to test.

        JSON-RPC method: debug.notifiers.test
        """
        body: dict[str, Any] = {}
        body["name"] = name
        return await self._request("POST", "/debug/notifiers/test", json=body)

    async def server_spoolman_status(self) -> Any:
        """Get Spoolman Status

        Returns the current status of the spoolman module.

        JSON-RPC method: server.spoolman.status
        """
        return await self._request("GET", "/server/spoolman/status")

    async def server_spoolman_spoolid(self) -> Any:
        """Get active spool

        Retrieve the ID of the spool to which Moonraker reports usage for Spoolman.

        JSON-RPC method: server.spoolman.get_spool_id
        """
        return await self._request("GET", "/server/spoolman/spool_id")

    async def server_spoolman_proxy(
        self,
        request_method: str,
        path: str,
        use_v2_response: bool = False,
        query: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> Any:
        """Proxy

        Proxy an API request to the Spoolman Server.

        See Spoolman's [OpenAPI Description](https://donkie.github.io/Spoolman/) for
        detailed information about it's API.

        **Note:** The version 2 response has been added to eliminate ambiguity between
        Spoolman errors and Moonraker errors.  With version 1 a frontend
        is not able to reliably to determine if the error is sourced from
        Spoolman or Moonraker.  Version 2 responses will return success
        unless Moonraker is the source of the error.

        The version 2 response is currently opt-in to avoid breaking
        existing implementations, however in the future it will be
        required, at which point the version 1 response will be removed.
        The version 1 response is now deprecated.

        **Note:** Version 1 responses are proxied directly.  See Spoolman's API
        documentation for response specifications.  Errors are also
        proxied directly.

        Args:
            use_v2_response: When set to `true` the request will return a version 2 response. (optional)
            request_method: The HTTP request method of the API call to proxy.
            path: The path section of the API endpoint to proxy.  It must include the version, ie:
            query: An optional query string component of the URL to proxy.  A `null` value will omi (optional)
            body: An optional body containing request parameters for the API call.  This should be (optional)

        JSON-RPC method: server.spoolman.proxy
        """
        body: dict[str, Any] = {}
        if use_v2_response is not None:
            body["use_v2_response"] = use_v2_response
        body["request_method"] = request_method
        body["path"] = path
        if query is not None:
            body["query"] = query
        if body is not None:
            body["body"] = body
        return await self._request("POST", "/server/spoolman/proxy", json=body)

    async def server_analysis_status(self) -> Any:
        """Get Analysis Status

        JSON-RPC method: server.analysis.status
        """
        return await self._request("GET", "/server/analysis/status")

    async def server_analysis_estimate(
        self, filename: str, estimator_config: str = "**CONFIG_DEFAULT**"
    ) -> Any:
        """Perform a time analysis

        Args:
            filename: The path to the gcode file to perform a time estimate on.  This should be a path
            estimator_config: The path to a Klipper Estimator config file, relative to the `config` root folde (optional)

        JSON-RPC method: server.analysis.estimate
        """
        body: dict[str, Any] = {}
        body["filename"] = filename
        if estimator_config is not None:
            body["estimator_config"] = estimator_config
        return await self._request("POST", "/server/analysis/estimate", json=body)

    async def server_analysis_process(
        self, filename: str, estimator_config: str = "**CONFIG_DEFAULT**", force: bool = False
    ) -> Any:
        """Post process a file

        Klipper Estimator will perform a time analysis and use the results to
        modify the time estimates in the file.  If M73 (progress) commands are
        present they will also be modified.

        **Note:** If the `file_manager` has `inotify` enabled the post-process will trigger a
        `create_file` event, which will in turn trigger metadata extraction.

        Args:
            filename: The path to the gcode file to post-process. This should be a path relative to th
            estimator_config: The path to a Klipper Estimator config file, relative to the `config` root folde (optional)
            force: By default the request will not perform a new post-process if the file was alrea (optional)

        JSON-RPC method: server.analysis.process
        """
        body: dict[str, Any] = {}
        body["filename"] = filename
        if estimator_config is not None:
            body["estimator_config"] = estimator_config
        if force is not None:
            body["force"] = force
        return await self._request("POST", "/server/analysis/process", json=body)

    async def server_analysis_dumpconfig(self, dest_config: str | None = None) -> Any:
        """Dump the current configuration

        Create a Klipper Estimator configuration file using Klippy's
        current settings.

        **Note:** Klippy must be connected and in the `ready` state to run
        this request.

        **Note:** The default configuration for Klipper Estimator is stored in the same
        folder as the binary.

        ```
        <data_path>/tools/klipper_estimator/default_estimator_cfg.json
        ```

        Args:
            dest_config: The name of the destination config file for the dump. This should be a path rela (optional)

        JSON-RPC method: server.analysis.dump_config
        """
        body: dict[str, Any] = {}
        if dest_config is not None:
            body["dest_config"] = dest_config
        return await self._request("POST", "/server/analysis/dump_config", json=body)

    async def api_version(self) -> Any:
        """Version information"""
        return await self._request("GET", "/api/version")

    async def api_server(self) -> Any:
        """Server status"""
        return await self._request("GET", "/api/server")

    async def api_login(self) -> Any:
        """Login verification & User information"""
        return await self._request("GET", "/api/login")

    async def api_settings(self) -> Any:
        """Get settings"""
        return await self._request("GET", "/api/settings")

    async def api_files_local(self) -> Any:
        """OctoPrint File Upload"""
        return await self._request("POST", "/api/files/local")

    async def api_job(self) -> Any:
        """Get Job status"""
        return await self._request("GET", "/api/job")

    async def api_printer(self) -> Any:
        """Get Printer status"""
        return await self._request("GET", "/api/printer")

    async def api_printer_command(self) -> Any:
        """Send GCode command"""
        return await self._request("POST", "/api/printer/command")

    async def api_printerprofiles(self) -> Any:
        """List Printer profiles"""
        return await self._request("GET", "/api/printerprofiles")

    async def machine_td1_data(self) -> Any:
        """Get TD-1 Data

        Returns TD-1 data for all devices that are connected.

        **Note:** All TD-1 data fields return null after successful power on until first filament
        is scanned.

        JSON-RPC method: machine.td1.data
        """
        return await self._request("GET", "/machine/td1/data")

    async def machine_td1_reboot(self, serial: str = "REQUIRED") -> Any:
        """Reset TD-1

        Gives ability to reboot TD-1 device remotely if an error exists when first powering on device.

        Example: User has filament inserted before power on TD-1 device, the following error occurs if
        this happens.

        Args:
            serial: The TD-1 serial to reboot (optional)

        JSON-RPC method: machine.td1.reboot
        """
        body: dict[str, Any] = {}
        if serial is not None:
            body["serial"] = serial
        return await self._request("POST", "/machine/td1/reboot", json=body)
