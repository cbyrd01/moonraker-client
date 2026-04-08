# System Administration

## System Information

```python
info = client.machine_systeminfo()
sys_info = info["system_info"]
print(f"CPU: {sys_info['cpu_info']}")
print(f"Distribution: {sys_info['distribution']}")

# Process statistics
stats = client.machine_procstats()
print(f"CPU temp: {stats['cpu_temp']}C")
print(f"Uptime: {stats['system_uptime']}s")
print(f"Memory: {stats['system_memory']}")

# System health helper
from moonraker_client.helpers import get_system_health
health = get_system_health(client)
```

## Service Management

```python
client.machine_services_restart(service="klipper")
client.machine_services_stop(service="klipper")
client.machine_services_start(service="klipper")
```

## Power Devices

```python
# List devices
devices = client.power_devices_list()

# Turn on/off
client.power_on(printer=None)
client.power_off(printer=None)

# Get status
status = client.power_device_status("printer")
```

## Update Manager

```python
# Check update status
status = client.machine_update_status()
for name, info in status.get("version_info", {}).items():
    print(f"{name}: {info}")

# Refresh update info
client.machine_update_refresh()
```

## Peripherals

```python
usb = client.machine_peripherals_usb()
serial = client.machine_peripherals_serial()
video = client.machine_peripherals_video()
canbus = client.machine_peripherals_canbus()
```

## Machine Control

```python
client.machine_shutdown()  # Shutdown the OS
client.machine_reboot()    # Reboot the OS
```
