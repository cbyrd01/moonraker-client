# Printer Control

## Printer Information

```python
info = client.printer_info()
# Returns: state, state_message, hostname, software_version, etc.
```

## Print Management

### Start a Print

```python
# Direct start
client.print_start("my_model.gcode")

# With file validation (helper)
from moonraker_client.helpers import start_print
start_print(client, "my_model.gcode")  # Raises FileNotFoundError if missing

# Upload and print
from moonraker_client.helpers import upload_and_print
upload_and_print(client, "/path/to/local/file.gcode")
```

### Pause, Resume, Cancel

```python
client.print_pause()
client.print_resume()
client.print_cancel()
```

## GCode Commands

```python
# Single command
client.gcode_script("G28")  # Home all axes

# Multiple commands
client.gcode_script("G28\nG1 X100 Y100 F3000")

# Temperature commands via helpers
from moonraker_client.helpers import set_hotend_temp, set_bed_temp
set_hotend_temp(client, 210.0)       # M104 S210 T0
set_hotend_temp(client, 200.0, tool=1)  # M104 S200 T1
set_bed_temp(client, 60.0)           # M140 S60
```

## Printer Objects

Query Klipper's internal state:

```python
# List available objects
objects = client.printer_objects_list()

# Query specific objects
result = client.printer_objects_query({
    "toolhead": ["position", "homed_axes", "status"],
    "extruder": ["temperature", "target", "power"],
    "heater_bed": None,  # None = all attributes
})
status = result["status"]
position = status["toolhead"]["position"]  # [x, y, z, e]
```

## Emergency Stop

```python
client.emergency_stop()  # Immediate halt - requires restart to recover
```

## Restart

```python
client.printer_restart()    # Soft restart (reloads config, MCUs stay up)
client.firmware_restart()   # Full restart (resets MCUs too)

# Helper: restart and wait for ready state
from moonraker_client.helpers import restart_firmware
success = restart_firmware(client, timeout=30.0)
```

## Endstops

```python
endstops = client.query_endstops()
# Returns: {"x": "open", "y": "TRIGGERED", "z": "open"}
```
