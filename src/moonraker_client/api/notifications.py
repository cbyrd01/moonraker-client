"""WebSocket notification constants and subscription helpers.

Moonraker broadcasts 26 notification types over WebSocket connections.
This module provides constants for all notification method names.
"""

from __future__ import annotations

# Klipper state notifications
NOTIFY_KLIPPY_READY = "notify_klippy_ready"
NOTIFY_KLIPPY_SHUTDOWN = "notify_klippy_shutdown"
NOTIFY_KLIPPY_DISCONNECTED = "notify_klippy_disconnected"

# Print and GCode notifications
NOTIFY_GCODE_RESPONSE = "notify_gcode_response"
NOTIFY_STATUS_UPDATE = "notify_status_update"

# File notifications
NOTIFY_FILELIST_CHANGED = "notify_filelist_changed"

# Update notifications
NOTIFY_UPDATE_RESPONSE = "notify_update_response"
NOTIFY_UPDATE_REFRESHED = "notify_update_refreshed"

# System notifications
NOTIFY_PROC_STAT_UPDATE = "notify_proc_stat_update"
NOTIFY_CPU_THROTTLED = "notify_cpu_throttled"
NOTIFY_SERVICE_STATE_CHANGED = "notify_service_state_changed"
NOTIFY_SUDO_ALERT = "notify_sudo_alert"

# History notifications
NOTIFY_HISTORY_CHANGED = "notify_history_changed"

# User notifications
NOTIFY_USER_CREATED = "notify_user_created"
NOTIFY_USER_DELETED = "notify_user_deleted"
NOTIFY_USER_LOGGED_OUT = "notify_user_logged_out"

# Job queue notifications
NOTIFY_JOB_QUEUE_CHANGED = "notify_job_queue_changed"

# Button notifications
NOTIFY_BUTTON_EVENT = "notify_button_event"

# Announcement notifications
NOTIFY_ANNOUNCEMENT_UPDATE = "notify_announcement_update"
NOTIFY_ANNOUNCEMENT_DISMISSED = "notify_announcement_dismissed"
NOTIFY_ANNOUNCEMENT_WAKE = "notify_announcement_wake"

# Webcam notifications
NOTIFY_WEBCAMS_CHANGED = "notify_webcams_changed"

# Sensor notifications
NOTIFY_SENSOR_UPDATE = "notify_sensor_update"

# Spoolman notifications
NOTIFY_ACTIVE_SPOOL_SET = "notify_active_spool_set"
NOTIFY_SPOOLMAN_STATUS_CHANGED = "notify_spoolman_status_changed"

# Agent notifications
NOTIFY_AGENT_EVENT = "notify_agent_event"

ALL_NOTIFICATIONS = [
    NOTIFY_KLIPPY_READY,
    NOTIFY_KLIPPY_SHUTDOWN,
    NOTIFY_KLIPPY_DISCONNECTED,
    NOTIFY_GCODE_RESPONSE,
    NOTIFY_STATUS_UPDATE,
    NOTIFY_FILELIST_CHANGED,
    NOTIFY_UPDATE_RESPONSE,
    NOTIFY_UPDATE_REFRESHED,
    NOTIFY_PROC_STAT_UPDATE,
    NOTIFY_CPU_THROTTLED,
    NOTIFY_SERVICE_STATE_CHANGED,
    NOTIFY_SUDO_ALERT,
    NOTIFY_HISTORY_CHANGED,
    NOTIFY_USER_CREATED,
    NOTIFY_USER_DELETED,
    NOTIFY_USER_LOGGED_OUT,
    NOTIFY_JOB_QUEUE_CHANGED,
    NOTIFY_BUTTON_EVENT,
    NOTIFY_ANNOUNCEMENT_UPDATE,
    NOTIFY_ANNOUNCEMENT_DISMISSED,
    NOTIFY_ANNOUNCEMENT_WAKE,
    NOTIFY_WEBCAMS_CHANGED,
    NOTIFY_SENSOR_UPDATE,
    NOTIFY_ACTIVE_SPOOL_SET,
    NOTIFY_SPOOLMAN_STATUS_CHANGED,
    NOTIFY_AGENT_EVENT,
]
