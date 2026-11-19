import asyncio
import time
import unittest
from unittest.mock import AsyncMock, patch

import robot.state as state
from robot.watchdog import watchdog_loop


class WatchdogTests(unittest.IsolatedAsyncioTestCase):
    async def test_connected_client_does_not_trigger_stop(self):
        self.addCleanup(setattr, state, "active_client", state.active_client)
        self.addCleanup(setattr, state, "last_command_time", state.last_command_time)
        state.active_client = object()
        state.last_command_time = time.monotonic()

        with patch(
            "robot.watchdog.stop_robot", new_callable=AsyncMock
        ) as stop_robot, patch(
            "robot.watchdog.asyncio.sleep",
            new_callable=AsyncMock,
            side_effect=asyncio.CancelledError,
        ):
            await watchdog_loop(None)

        stop_robot.assert_not_awaited()
