import asyncio
import unittest
from unittest.mock import Mock

import robot.state as state
from app import on_shutdown


class ShutdownTests(unittest.IsolatedAsyncioTestCase):
    async def test_background_tasks_stop_before_motor_driver_closes(self):
        events = []
        original_client = state.active_client
        self.addCleanup(setattr, state, "active_client", original_client)
        state.active_client = None

        async def background_task():
            try:
                await asyncio.Event().wait()
            finally:
                events.append("task-stopped")

        app = {
            "watchdog_task": asyncio.create_task(background_task()),
            "motor_task": asyncio.create_task(background_task()),
            "motor_driver": Mock(),
        }
        app["motor_driver"].close.side_effect = lambda: events.append(
            "motor-driver-closed"
        )
        await asyncio.sleep(0)

        await on_shutdown(app)

        self.assertEqual(events.count("task-stopped"), 2)
        self.assertEqual(events[-1], "motor-driver-closed")
