import os
import subprocess
import asyncio
from aiohttp import web
# from robot.audio import cleanup_audio

from robot.webrtc import websocket_handler as audio_ws_handler
from robot.websocket import control_websocket_handler
from robot.watchdog import watchdog_loop

async def index(request):
    """Serves the frontend HTML interface."""
    return web.FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))

async def start_mediamtx(app):
    """Starts MediaMTX as a subprocess when the web server starts."""
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

async def start_background_tasks(app):
    """Starts Watchdog task in background."""
    app["watchdog_task"] = asyncio.create_task(watchdog_loop(app))

async def cleanup_background_tasks(app):
    """Cancels Watchdog task and MediaMTX on shutdown."""
    app["watchdog_task"].cancel()
    await app["watchdog_task"]

async def on_shutdown(app):
    """Frees hardware resources when the server stops."""
    print("Shutting down hardware resources...")
    # 1. Terminate MediaMTX
    mtx_process = app.get("mediamtx_process")
    if mtx_process and mtx_process.poll() is None:
        print("Stopping MediaMTX...")
        mtx_process.terminate()
        mtx_process.wait()  # Wait for the process to exit cleanly
        
    # 2. Terminate PyAudio
    print("Stopping Audio...")
    # cleanup_audio()
    print("Shutdown complete.")

def main():
    app = web.Application()
    
    # Register the startup and teardown functions
    app.on_startup.append(start_mediamtx)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
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