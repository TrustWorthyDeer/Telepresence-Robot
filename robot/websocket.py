import json
import time
from aiohttp import web
import robot.state as state
from robot.state import active_client, robot_state

async def send_active_state():
    # Sends current state to the single active connected client.
    global active_client
    if active_client and not active_client.closed:
        try:
            await active_client.send_str(json.dumps(robot_state))
        except Exception:
            active_client = None


async def control_websocket_handler(request):
    # aiohttp WebSocket handler for robot controls and heartbeat telemetry.

     # Single-client enforcement lock
    global active_client
    if active_client is not None and not active_client.closed:
        print("[WS Control] Connection rejected: Robot is already controlled by an active client.")
        return web.HTTPForbidden(reason="Robot is already in use by another client.")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    active_client = ws
    print("[WS Control] Browser joystick connected")
    
    # Update command timestamp upon connection
    state.last_command_time = time.monotonic()
    
    # Send current state to newly connected client
    await ws.send_str(json.dumps(robot_state))

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                
                # Reset Watchdog timer
                state.last_command_time = time.monotonic()

                # Update control state
                robot_state["throttle"] = float(data.get("throttle", 0.0))
                robot_state["steering"] = float(data.get("steering", 0.0))
                robot_state["headlights"] = bool(data.get("headlights", False))
                robot_state["floodlights"] = bool(data.get("floodlights", False))

                # Debug output to Pi terminal
                print(
                    f"[TX/RX] Thr: {robot_state['throttle']:.2f} | "
                    f"Str: {robot_state['steering']:.2f} | "
                    f"H-Lights: {robot_state['headlights']} | "
                    f"F-Lights: {robot_state['floodlights']}"
                )

                await send_active_state()

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[WS Control] Error: {ws.exception()}")

    finally:
        if active_client == ws:
            active_client = None
        
        print("[WS Control] Browser joystick disconnected")
        
        # Trigger immediate emergency stop when client disconnects
        from robot.watchdog import stop_robot
        await stop_robot()

    return ws

