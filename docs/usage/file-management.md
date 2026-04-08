# File Management

## Listing Files

```python
# List all gcode files
files = client.files_list(root="gcodes")
for f in files:
    print(f"{f['path']} ({f['size']} bytes)")

# List config files
configs = client.files_list(root="config")

# Sorted listing via helper
from moonraker_client.helpers import list_gcode_files
files = list_gcode_files(client, sort_by="modified")  # Most recent first
```

## Directory Operations

```python
# Get directory contents (non-recursive)
result = client.files_directory(path="gcodes")
print(f"Files: {len(result['files'])}, Dirs: {len(result['dirs'])}")

# With metadata
result = client.files_directory(path="gcodes", extended=True)

# Create directory
client.files_create_directory("gcodes/my_folder")

# Delete directory
client.files_delete_directory("gcodes/my_folder")
client.files_delete_directory("gcodes/my_folder", force=True)  # Non-empty
```

## Uploading Files

```python
# Upload from file path
result = client.files_upload("/path/to/model.gcode")

# Upload to subdirectory
result = client.files_upload("/path/to/model.gcode", path="my_folder")

# Upload and start printing
result = client.files_upload("/path/to/model.gcode", start_print=True)

# Upload with checksum verification
result = client.files_upload(
    "/path/to/model.gcode",
    checksum="sha256hexdigest..."
)
```

## Downloading Files

```python
content = client.files_download("gcodes", "model.gcode")
```

## File Metadata

```python
meta = client.files_metadata("model.gcode")
print(f"Slicer: {meta.get('slicer')}")
print(f"Estimated time: {meta.get('estimated_time')}s")
print(f"Filament: {meta.get('filament_total')}mm")

# Force re-scan metadata
client.files_metascan("model.gcode")

# Get thumbnails
thumbs = client.files_thumbnails("model.gcode")
```

## Move, Copy, Delete

```python
client.files_move("gcodes/old_name.gcode", "gcodes/new_name.gcode")
client.files_copy("gcodes/original.gcode", "gcodes/backup.gcode")
client.files_delete("gcodes", "unwanted.gcode")
```

## Creating Archives

```python
result = client.files_zip(
    items=["gcodes/file1.gcode", "gcodes/file2.gcode"],
    dest="gcodes/archive.zip",
)
```

## Log Files

```python
klippy_log = client.files_klippy_log()
moonraker_log = client.files_moonraker_log()
```
