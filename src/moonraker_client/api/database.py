"""API endpoints for Database operations.

Auto-generated from OpenAPI spec. Hand-tune as needed.
"""

from __future__ import annotations

from typing import Any


class DatabaseMixin:
    """Synchronous database API methods."""

    def server_database_list(self) -> Any:
        """List Database Info

        Lists all namespaces with read and/or write access.  Also lists database
        backup files.

        JSON-RPC method: server.database.list
        """
        return self._request("GET", "/server/database/list")

    def server_database_item(self, namespace: str, key: str | None = None) -> Any:
        """Get Database Item

        Retrieves an item from a specified namespace. The `key` argument may be
        omitted, in which case an object representing the entire namespace will
        be returned in the `value` field.  If the `key` is provided and does not
        exist in the database an error will be returned.

        Args:
            namespace: The namespace of the item to retrieve.
            key: The key indicating the field or fields within the namespace to retrieve.  May be (optional)

        JSON-RPC method: server.database.get_item
        """
        params: dict[str, Any] = {}
        params["namespace"] = namespace
        if key is not None:
            params["key"] = key
        return self._request("GET", "/server/database/item", params=params)

    def server_database_compact(self) -> Any:
        """Compact Database

        Compacts and defragments the the sqlite database using the `VACUUM` command.
        This endpoint cannot be requested when Klipper is printing.

        JSON-RPC method: server.database.compact
        """
        return self._request("POST", "/server/database/compact")

    def server_database_backup(self, filename: str = 'sqldb-backup-{timespec}.db') -> Any:
        """Backup Database

        Creates a backup of the current database.  The backup will be
        created in the `<data_path>/backup/database/<filename>`.
        
        This API cannot be requested when Klipper is printing.
        
        **Note:** The `{timespec}` of the default `filename` is in the following format:
        
        `<year><month><day>-<hour><minute><second>`

        Args:
            filename: The file name of the saved backup file. (optional)

        JSON-RPC method: server.database.post_backup
        """
        body: dict[str, Any] = {}
        if filename is not None:
            body["filename"] = filename
        return self._request("POST", "/server/database/backup", json=body)

    def server_database_restore(self, filename: str) -> Any:
        """Restore Database

        Restores a previously backed up sqlite database file. The backup
        must be located at `<data_path>/backup/database/<filename>`. The
        `<filename>` must be a valid filename reported in by the
        [database list](#list-database-info) API.
        
        This API cannot be requested when Klipper is printing.
        
        **Note:** Moonraker will restart immediately after this request is processed.

        Args:
            filename: The name of the backup file to restore. Must be a valid filename reported by the

        JSON-RPC method: server.database.restore
        """
        body: dict[str, Any] = {}
        body["filename"] = filename
        return self._request("POST", "/server/database/restore", json=body)

    def debug_database_list(self) -> Any:
        """List Database Info (debug)

        Debug version of the [List Database Info](#list-database-info) endpoint.
        Returns all namespaces, including those exclusively reserved for Moonraker.
        In addition all registered SQL tables are reported.

        JSON-RPC method: debug.database.list
        """
        return self._request("GET", "/debug/database/list")

    def debug_database_item(self) -> Any:
        """Add Database Item (debug)

        Debug version of the [Add Database Item](#add-database-item) endpoint.
        Keys within protected and forbidden namespaces may be inserted.
        
        **Note:** Modifying protected namespaces outside of Moonraker can result in
        broken functionality and is not supported for production environments.
        Issues opened with reports/queries related to this endpoint will be
        redirected to this documentation and closed.

        JSON-RPC method: debug.database.post_item
        """
        return self._request("POST", "/debug/database/item")

    def debug_database_table(self, table: str) -> Any:
        """Get Database Table

        Requests all the contents of a specified table.

        Args:
            table: The name of the table to request.

        JSON-RPC method: debug.database.table
        """
        params: dict[str, Any] = {}
        params["table"] = table
        return self._request("GET", "/debug/database/table", params=params)


class AsyncDatabaseMixin:
    """Asynchronous database API methods."""

    async def server_database_list(self) -> Any:
        """List Database Info

        Lists all namespaces with read and/or write access.  Also lists database
        backup files.

        JSON-RPC method: server.database.list
        """
        return await self._request("GET", "/server/database/list")

    async def server_database_item(self, namespace: str, key: str | None = None) -> Any:
        """Get Database Item

        Retrieves an item from a specified namespace. The `key` argument may be
        omitted, in which case an object representing the entire namespace will
        be returned in the `value` field.  If the `key` is provided and does not
        exist in the database an error will be returned.

        Args:
            namespace: The namespace of the item to retrieve.
            key: The key indicating the field or fields within the namespace to retrieve.  May be (optional)

        JSON-RPC method: server.database.get_item
        """
        params: dict[str, Any] = {}
        params["namespace"] = namespace
        if key is not None:
            params["key"] = key
        return await self._request("GET", "/server/database/item", params=params)

    async def server_database_compact(self) -> Any:
        """Compact Database

        Compacts and defragments the the sqlite database using the `VACUUM` command.
        This endpoint cannot be requested when Klipper is printing.

        JSON-RPC method: server.database.compact
        """
        return await self._request("POST", "/server/database/compact")

    async def server_database_backup(self, filename: str = 'sqldb-backup-{timespec}.db') -> Any:
        """Backup Database

        Creates a backup of the current database.  The backup will be
        created in the `<data_path>/backup/database/<filename>`.
        
        This API cannot be requested when Klipper is printing.
        
        **Note:** The `{timespec}` of the default `filename` is in the following format:
        
        `<year><month><day>-<hour><minute><second>`

        Args:
            filename: The file name of the saved backup file. (optional)

        JSON-RPC method: server.database.post_backup
        """
        body: dict[str, Any] = {}
        if filename is not None:
            body["filename"] = filename
        return await self._request("POST", "/server/database/backup", json=body)

    async def server_database_restore(self, filename: str) -> Any:
        """Restore Database

        Restores a previously backed up sqlite database file. The backup
        must be located at `<data_path>/backup/database/<filename>`. The
        `<filename>` must be a valid filename reported in by the
        [database list](#list-database-info) API.
        
        This API cannot be requested when Klipper is printing.
        
        **Note:** Moonraker will restart immediately after this request is processed.

        Args:
            filename: The name of the backup file to restore. Must be a valid filename reported by the

        JSON-RPC method: server.database.restore
        """
        body: dict[str, Any] = {}
        body["filename"] = filename
        return await self._request("POST", "/server/database/restore", json=body)

    async def debug_database_list(self) -> Any:
        """List Database Info (debug)

        Debug version of the [List Database Info](#list-database-info) endpoint.
        Returns all namespaces, including those exclusively reserved for Moonraker.
        In addition all registered SQL tables are reported.

        JSON-RPC method: debug.database.list
        """
        return await self._request("GET", "/debug/database/list")

    async def debug_database_item(self) -> Any:
        """Add Database Item (debug)

        Debug version of the [Add Database Item](#add-database-item) endpoint.
        Keys within protected and forbidden namespaces may be inserted.
        
        **Note:** Modifying protected namespaces outside of Moonraker can result in
        broken functionality and is not supported for production environments.
        Issues opened with reports/queries related to this endpoint will be
        redirected to this documentation and closed.

        JSON-RPC method: debug.database.post_item
        """
        return await self._request("POST", "/debug/database/item")

    async def debug_database_table(self, table: str) -> Any:
        """Get Database Table

        Requests all the contents of a specified table.

        Args:
            table: The name of the table to request.

        JSON-RPC method: debug.database.table
        """
        params: dict[str, Any] = {}
        params["table"] = table
        return await self._request("GET", "/debug/database/table", params=params)
