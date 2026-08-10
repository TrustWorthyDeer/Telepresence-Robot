import json
import time
from aiohttp import web
import robot.state as state
from robot.state import clients, robot_state

async def broadcast_state():
    """Broadcasts current robot state to all connected control clients."""
    dead = set()
    state_json = json.dumps(robot_state)
    
    for client in list(clients):
        try:
            await client.send_str(state_json)
        except Exception:
            dead.add(client)

    for client in dead:
        clients.discard(client)


async def control_websocket_handler(request):
    """aiohttp WebSocket handler for robot controls and heartbeat telemetry."""

    if len(clients) >= 1:
        print("[WS Control] Connection rejected: Another client is already connected.")
        return web.HTTPForbidden(reason="Robot is already in use by another client.")

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("[WS Control] Browser joystick connected")
    clients.add(ws)
    
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

                await broadcast_state()

            elif msg.type == web.WSMsgType.ERROR:
                print(f"[WS Control] Error: {ws.exception()}")

    finally:
        clients.discard(ws)
        print("[WS Control] Browser joystick disconnected")
        
        # Trigger immediate emergency stop when client disconnects
        from robot.watchdog import stop_robot
        await stop_robot()

    return ws