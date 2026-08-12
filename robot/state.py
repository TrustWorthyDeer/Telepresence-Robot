import time

active_client = None

robot_state = {
    "type": "state",
    "throttle": 0.0,
    "steering": 0.0,
    "headlights": False,
    "floodlights": False
}

last_command_time = time.monotonic()