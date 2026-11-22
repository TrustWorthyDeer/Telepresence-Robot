# Robot Safety & Watchdog Settings
COMMAND_TIMEOUT_MS = 500  # Stop robot if no command/heartbeat received within 500ms
MAX_CONTROL_AGE_MS = 500  # Reject control frames queued for longer than the watchdog timeout
WATCHDOG_INTERVAL = 0.1   # Watchdog loop check frequency in seconds (100ms)

# Motors Min & Max Threshold to overcome friction
PWM_MIN = 70
PWM_MAX = 255

# H-Bridge Pin Assignment
D0 = 18
D1 = 19
D2 = 12
D3 = 13