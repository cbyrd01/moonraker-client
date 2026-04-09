# Temperature Management

## Reading Temperatures

### Via Helper Function

```python
from moonraker_client.helpers import get_temperatures

temps = get_temperatures(client)
for name, reading in temps.items():
    print(f"{name}: {reading.current:.1f}C -> {reading.target:.1f}C (power: {reading.power:.0%})")
```

### Via Object Query

```python
result = client.printer_objects_query({
    "extruder": ["temperature", "target", "power"],
    "heater_bed": ["temperature", "target", "power"],
})
extruder = result["status"]["extruder"]
print(f"Hotend: {extruder['temperature']}C")
```

### Temperature History

```python
# Get cached temperature data
store = client.server_temperaturestore()
# Returns time-series data for all heaters
```

## Setting Temperatures

These helpers use Klipper's native `SET_HEATER_TEMPERATURE` command, which
is more reliable than G-code `M104`/`M140` for Klipper-based printers.

```python
from moonraker_client.helpers import set_hotend_temp, set_bed_temp

set_hotend_temp(client, 210.0)       # PLA
set_hotend_temp(client, 250.0)       # PETG
set_bed_temp(client, 60.0)           # PLA
set_bed_temp(client, 80.0)           # PETG

# Multi-extruder: specify tool index
set_hotend_temp(client, 210.0, tool=1)  # Second extruder

# Cool down
set_hotend_temp(client, 0)
set_bed_temp(client, 0)
```

## Waiting for Temperature

```python
from moonraker_client.helpers import wait_for_temps

# Wait up to 5 minutes for temps to reach targets within 2C
reached = wait_for_temps(
    client,
    targets={"extruder": 210.0, "heater_bed": 60.0},
    tolerance=2.0,
    timeout=300.0,
)
if reached:
    print("Temperatures reached!")
else:
    print("Timed out waiting for temperatures")
```
