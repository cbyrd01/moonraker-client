"""File Manager API endpoint mixins.

Covers /server/files/* endpoints for file listing, upload, download,
metadata, and directory management.
Generated from OpenAPI spec and hand-tuned.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, BinaryIO


class FilesMixin:
    """Synchronous file manager API methods."""

    def files_list(self, root: str = "gcodes") -> list[dict[str, Any]]:
        """List available files in a root directory.

        Args:
            root: Root directory to list. Defaults to "gcodes".

        JSON-RPC method: server.files.list
        """
        return self._request("GET", "/server/files/list", params={"root": root})  # type: ignore[attr-defined]

    def files_roots(self) -> list[dict[str, Any]]:
        """List registered root directories.

        JSON-RPC method: server.files.roots
        """
        return self._request("GET", "/server/files/roots")  # type: ignore[attr-defined]

    def files_metadata(self, filename: str) -> dict[str, Any]:
        """Get GCode metadata for a file.

        Args:
            filename: Path to the gcode file, relative to the gcodes root.

        JSON-RPC method: server.files.metadata
        """
        return self._request("GET", "/server/files/metadata", params={"filename": filename})  # type: ignore[attr-defined]

    def files_metascan(self, filename: str) -> dict[str, Any]:
        """Initiate a metadata scan for a file.

        Forces a re-scan if the file has already been scanned.

        Args:
            filename: Path to the gcode file, relative to the gcodes root.

        JSON-RPC method: server.files.metascan
        """
        return self._request("POST", "/server/files/metascan", json={"filename": filename})  # type: ignore[attr-defined]

    def files_thumbnails(self, filename: str) -> list[dict[str, Any]]:
        """Get thumbnail details for a gcode file.

        Args:
            filename: Path to the gcode file, relative to the gcodes root.

        JSON-RPC method: server.files.thumbnails
        """
        return self._request("GET", "/server/files/thumbnails", params={"filename": filename})  # type: ignore[attr-defined]

    def files_directory(
        self, path: str = "gcodes", extended: bool = False
    ) -> dict[str, Any]:
        """Get directory information.

        Returns files and subdirectories at the given path (non-recursive).

        Args:
            path: Directory path. First part must be a registered root.
            extended: Include metadata for gcode files.

        JSON-RPC method: server.files.get_directory
        """
        params: dict[str, Any] = {"path": path}
        if extended:
            params["extended"] = extended
        return self._request("GET", "/server/files/directory", params=params)  # type: ignore[attr-defined]

    def files_create_directory(self, path: str) -> dict[str, Any]:
        """Create a directory.

        Args:
            path: Directory path to create. Must start with a root.

        JSON-RPC method: server.files.post_directory
        """
        return self._request("POST", "/server/files/directory", json={"path": path})  # type: ignore[attr-defined]

    def files_delete_directory(self, path: str, force: bool = False) -> dict[str, Any]:
        """Delete a directory.

        Args:
            path: Directory path to delete. Must start with a root.
            force: Force deletion of non-empty directories.

        JSON-RPC method: server.files.delete_directory
        """
        params: dict[str, Any] = {"path": path}
        if force:
            params["force"] = force
        return self._request("DELETE", "/server/files/directory", params=params)  # type: ignore[attr-defined]

    def files_move(self, source: str, dest: str) -> dict[str, Any]:
        """Move a file or directory.

        Args:
            source: Source path (must start with a root).
            dest: Destination path (must start with a root).

        JSON-RPC method: server.files.move
        """
        return self._request("POST", "/server/files/move", json={"source": source, "dest": dest})  # type: ignore[attr-defined]

    def files_copy(self, source: str, dest: str) -> dict[str, Any]:
        """Copy a file or directory.

        Args:
            source: Source path (must start with a root).
            dest: Destination path (must start with a root).

        JSON-RPC method: server.files.copy
        """
        return self._request("POST", "/server/files/copy", json={"source": source, "dest": dest})  # type: ignore[attr-defined]

    def files_zip(
        self,
        items: list[str],
        dest: str | None = None,
        store_only: bool = False,
    ) -> dict[str, Any]:
        """Create a ZIP archive.

        Args:
            items: Paths to include in the archive.
            dest: Destination archive path. Must start with a root.
            store_only: If True, don't compress the contents.

        JSON-RPC method: server.files.zip
        """
        body: dict[str, Any] = {"items": items}
        if dest is not None:
            body["dest"] = dest
        if store_only:
            body["store_only"] = store_only
        return self._request("POST", "/server/files/zip", json=body)  # type: ignore[attr-defined]

    def files_download(self, root: str, filename: str) -> Any:
        """Download a file.

        Args:
            root: Root directory (e.g. "gcodes", "config").
            filename: Path to file relative to root.
        """
        return self._request("GET", f"/server/files/{root}/{filename}")  # type: ignore[attr-defined]

    def files_delete(self, root: str, filename: str) -> dict[str, Any]:
        """Delete a file.

        Args:
            root: Root directory.
            filename: Path to file relative to root.

        JSON-RPC method: server.files.delete_file
        """
        return self._request("DELETE", f"/server/files/{root}/{filename}")  # type: ignore[attr-defined]

    def files_upload(
        self,
        file: str | Path | BinaryIO,
        root: str = "gcodes",
        path: str | None = None,
        checksum: str | None = None,
        start_print: bool = False,
    ) -> dict[str, Any]:
        """Upload a file.

        Args:
            file: File path (str/Path) or file-like object to upload.
            root: Root to upload to ("gcodes" or "config").
            path: Subdirectory within root to save to.
            checksum: Optional SHA256 hex digest for verification.
            start_print: If True, start printing after upload (gcodes only).
        """
        data: dict[str, str] = {"root": root}
        if path is not None:
            data["path"] = path
        if checksum is not None:
            data["checksum"] = checksum
        if start_print:
            data["print"] = "true"

        if isinstance(file, (str, Path)):
            file_path = Path(file)
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                return self._request("POST", "/server/files/upload", data=data, files=files)  # type: ignore[attr-defined]
        else:
            name = getattr(file, "name", "upload")
            if isinstance(name, (str, Path)):
                name = Path(name).name
            files = {"file": (name, file, "application/octet-stream")}
            return self._request("POST", "/server/files/upload", data=data, files=files)  # type: ignore[attr-defined]

    def files_klippy_log(self) -> Any:
        """Download klippy.log."""
        return self._request("GET", "/server/files/klippy.log")  # type: ignore[attr-defined]

    def files_moonraker_log(self) -> Any:
        """Download moonraker.log."""
        return self._request("GET", "/server/files/moonraker.log")  # type: ignore[attr-defined]


class AsyncFilesMixin:
    """Asynchronous file manager API methods."""

    async def files_list(self, root: str = "gcodes") -> list[dict[str, Any]]:
        """List available files in a root directory.

        JSON-RPC method: server.files.list
        """
        return await self._request("GET", "/server/files/list", params={"root": root})  # type: ignore[attr-defined]

    async def files_roots(self) -> list[dict[str, Any]]:
        """List registered root directories.

        JSON-RPC method: server.files.roots
        """
        return await self._request("GET", "/server/files/roots")  # type: ignore[attr-defined]

    async def files_metadata(self, filename: str) -> dict[str, Any]:
        """Get GCode metadata for a file.

        Args:
            filename: Path to the gcode file, relative to the gcodes root.

        JSON-RPC method: server.files.metadata
        """
        return await self._request("GET", "/server/files/metadata", params={"filename": filename})  # type: ignore[attr-defined]

    async def files_metascan(self, filename: str) -> dict[str, Any]:
        """Initiate a metadata scan for a file.

        Args:
            filename: Path to the gcode file, relative to the gcodes root.

        JSON-RPC method: server.files.metascan
        """
        return await self._request("POST", "/server/files/metascan", json={"filename": filename})  # type: ignore[attr-defined]

    async def files_thumbnails(self, filename: str) -> list[dict[str, Any]]:
        """Get thumbnail details for a gcode file.

        Args:
            filename: Path to the gcode file, relative to the gcodes root.

        JSON-RPC method: server.files.thumbnails
        """
        return await self._request("GET", "/server/files/thumbnails", params={"filename": filename})  # type: ignore[attr-defined]

    async def files_directory(
        self, path: str = "gcodes", extended: bool = False
    ) -> dict[str, Any]:
        """Get directory information.

        Args:
            path: Directory path.
            extended: Include metadata for gcode files.

        JSON-RPC method: server.files.get_directory
        """
        params: dict[str, Any] = {"path": path}
        if extended:
            params["extended"] = extended
        return await self._request("GET", "/server/files/directory", params=params)  # type: ignore[attr-defined]

    async def files_create_directory(self, path: str) -> dict[str, Any]:
        """Create a directory.

        Args:
            path: Directory path to create.

        JSON-RPC method: server.files.post_directory
        """
        return await self._request("POST", "/server/files/directory", json={"path": path})  # type: ignore[attr-defined]

    async def files_delete_directory(self, path: str, force: bool = False) -> dict[str, Any]:
        """Delete a directory.

        Args:
            path: Directory path to delete.
            force: Force deletion of non-empty directories.

        JSON-RPC method: server.files.delete_directory
        """
        params: dict[str, Any] = {"path": path}
        if force:
            params["force"] = force
        return await self._request("DELETE", "/server/files/directory", params=params)  # type: ignore[attr-defined]

    async def files_move(self, source: str, dest: str) -> dict[str, Any]:
        """Move a file or directory.

        Args:
            source: Source path.
            dest: Destination path.

        JSON-RPC method: server.files.move
        """
        return await self._request("POST", "/server/files/move", json={"source": source, "dest": dest})  # type: ignore[attr-defined]

    async def files_copy(self, source: str, dest: str) -> dict[str, Any]:
        """Copy a file or directory.

        Args:
            source: Source path.
            dest: Destination path.

        JSON-RPC method: server.files.copy
        """
        return await self._request("POST", "/server/files/copy", json={"source": source, "dest": dest})  # type: ignore[attr-defined]

    async def files_zip(
        self,
        items: list[str],
        dest: str | None = None,
        store_only: bool = False,
    ) -> dict[str, Any]:
        """Create a ZIP archive.

        Args:
            items: Paths to include.
            dest: Destination archive path.
            store_only: Don't compress.

        JSON-RPC method: server.files.zip
        """
        body: dict[str, Any] = {"items": items}
        if dest is not None:
            body["dest"] = dest
        if store_only:
            body["store_only"] = store_only
        return await self._request("POST", "/server/files/zip", json=body)  # type: ignore[attr-defined]

    async def files_download(self, root: str, filename: str) -> Any:
        """Download a file.

        Args:
            root: Root directory.
            filename: Path to file relative to root.
        """
        return await self._request("GET", f"/server/files/{root}/{filename}")  # type: ignore[attr-defined]

    async def files_delete(self, root: str, filename: str) -> dict[str, Any]:
        """Delete a file.

        Args:
            root: Root directory.
            filename: Path to file relative to root.

        JSON-RPC method: server.files.delete_file
        """
        return await self._request("DELETE", f"/server/files/{root}/{filename}")  # type: ignore[attr-defined]

    async def files_upload(
        self,
        file: str | Path | BinaryIO,
        root: str = "gcodes",
        path: str | None = None,
        checksum: str | None = None,
        start_print: bool = False,
    ) -> dict[str, Any]:
        """Upload a file.

        Args:
            file: File path or file-like object to upload.
            root: Root to upload to.
            path: Subdirectory within root.
            checksum: Optional SHA256 hex digest.
            start_print: Start printing after upload.
        """
        data: dict[str, str] = {"root": root}
        if path is not None:
            data["path"] = path
        if checksum is not None:
            data["checksum"] = checksum
        if start_print:
            data["print"] = "true"

        if isinstance(file, (str, Path)):
            file_path = Path(file)
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                return await self._request("POST", "/server/files/upload", data=data, files=files)  # type: ignore[attr-defined]
        else:
            name = getattr(file, "name", "upload")
            if isinstance(name, (str, Path)):
                name = Path(name).name
            files = {"file": (name, file, "application/octet-stream")}
            return await self._request("POST", "/server/files/upload", data=data, files=files)  # type: ignore[attr-defined]

    async def files_klippy_log(self) -> Any:
        """Download klippy.log."""
        return await self._request("GET", "/server/files/klippy.log")  # type: ignore[attr-defined]

    async def files_moonraker_log(self) -> Any:
        """Download moonraker.log."""
        return await self._request("GET", "/server/files/moonraker.log")  # type: ignore[attr-defined]
