import asyncio
import time
import robot.state as state
from config import COMMAND_TIMEOUT_MS, WATCHDOG_INTERVAL
from robot.state import active_client, robot_state

async def stop_robot():
    # Safety action: zero out movement controls if connection drops.
    changed = False

    if robot_state["throttle"] != 0:
        robot_state["throttle"] = 0.0
        changed = True

    if robot_state["steering"] != 0:
        robot_state["steering"] = 0.0
        changed = True

    if changed:
        print("[WATCHDOG] Safety Timeout: STOP ROBOT")
        from robot.websocket import send_active_state
        await send_active_state()

        # Hardware UART / GPIO commands will go here later


async def watchdog_loop(app):
    # Background async task checking for heartbeats every WATCHDOG_INTERVAL seconds.
    try:
        while True:
            time_since_last_cmd = (time.monotonic() - state.last_command_time) * 1000

            # Stop robot if no browser is connected or timeout exceeded
            if active_client == None:
                await stop_robot()
            elif time_since_last_cmd > COMMAND_TIMEOUT_MS:
                await stop_robot()

            await asyncio.sleep(WATCHDOG_INTERVAL)
    except asyncio.CancelledError:
        pass  # Graceful exit on server shutdown