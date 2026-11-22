import os
import subprocess
import asyncio
from aiohttp import web

import robot.state as state
from robot.webrtc import websocket_handler as audio_ws_handler
from robot.websocket import control_websocket_handler
from robot.watchdog import watchdog_loop
from robot.motors import DirectPiMotorDriver
# from robot.audio import cleanup_audio

from config import *


async def index(request):
    # Serves the frontend HTML interface.
    return web.FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))


async def start_mediamtx(app):
    # Starts MediaMTX as a subprocess when the web server starts.
    print("Starting MediaMTX subprocess...")
    
    # Get the directory where app.py is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mediamtx_path = os.path.join(base_dir, "mediamtx")
    
    try:
        # Popen runs the process in the background without blocking Python.
        # cwd ensures MediaMTX finds its mediamtx.yml config file.
        app["mediamtx_process"] = subprocess.Popen([mediamtx_path], cwd=base_dir)
        print("MediaMTX started successfully.")
    except FileNotFoundError:
        print(f"Error: Could not find MediaMTX binary at {mediamtx_path}")


async def motor_control_loop(app):
    # Background task: Reads the central state every 50ms (20Hz) 
    # and applies it to the motor driver.
    motor_driver = app["motor_driver"]
    try:
        while True:
            try:
                # 1. Read the latest state updated by WebSockets or Watchdog
                throttle = state.robot_state.get("throttle", 0.0)
                steering = state.robot_state.get("steering", 0.0)
                
                # The rear-facing camera reverses forward and reverse.
                motor_driver.set_motors(throttle=-throttle, steering=steering)
            except Exception as e:
                print(f"[Motor Error] Failed to update motor PWM: {e}")
            
            # 3. Yield control back to the event loop (20Hz refresh rate)
            await asyncio.sleep(0.05) 
    except asyncio.CancelledError:
        pass # Graceful exit on server shutdown


async def start_background_tasks(app):
    # Starts Watchdog task in background.
    app["watchdog_task"] = asyncio.create_task(watchdog_loop(app))
    app["motor_task"] = asyncio.create_task(motor_control_loop(app))


async def cleanup_background_tasks(app):
    # Stop background loops before releasing the hardware they use.
    tasks = [
        app[task_name]
        for task_name in ("watchdog_task", "motor_task")
        if task_name in app
    ]
    for task in tasks:
        if not task.done():
            task.cancel()

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, BaseException) and not isinstance(
            result, asyncio.CancelledError
        ):
            raise result


async def on_shutdown(app):
    # Frees hardware resources when the server stops.
    if state.active_client is not None and not state.active_client.closed:
        await state.active_client.close(
            code=web.WSCloseCode.GOING_AWAY,
            message=b"Server shutting down",
        )
    await cleanup_background_tasks(app)

    # Stop Motors safely
    print("Shutting down hardware resources...")
    print("Stopping Motors...")
    app["motor_driver"].close()

    # Terminate MediaMTX
    mtx_process = app.get("mediamtx_process")
    if mtx_process and mtx_process.poll() is None:
        print("Stopping MediaMTX...")
        mtx_process.terminate()
        mtx_process.wait()  # Wait for the process to exit cleanly
        
    # Terminate PyAudio
    # print("Stopping Audio...")
    # cleanup_audio()

    print("Shutdown complete.")


def main():
    app = web.Application()

    app["motor_driver"] = DirectPiMotorDriver(in1=D0, in2=D1, in3=D2, in4=D3, min_pwm=PWM_MIN, max_pwm=PWM_MAX)
    
    # Register the startup and teardown functions
    app.on_startup.append(start_mediamtx)
    app.on_startup.append(start_background_tasks)
    app.on_shutdown.append(on_shutdown)

    # Setup web routes
    app.router.add_get("/", index)
    app.router.add_get("/ws", audio_ws_handler)
    app.router.add_get("/ws/control", control_websocket_handler)

    # Mounts the static directory containing css/ and js/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    app.router.add_static("/static/", path=static_dir, name="static")

    print("Modular Telepresence Server running on http://0.0.0.0:8080")
    web.run_app(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()