import asyncio
import unittest
from unittest.mock import AsyncMock, Mock, patch

import robot.state as state
from app import motor_control_loop


class MotorControlTests(unittest.IsolatedAsyncioTestCase):
    async def test_reverses_throttle_but_preserves_steering(self):
        original_throttle = state.robot_state["throttle"]
        original_steering = state.robot_state["steering"]
        self.addCleanup(state.robot_state.__setitem__, "throttle", original_throttle)
        self.addCleanup(state.robot_state.__setitem__, "steering", original_steering)
        state.robot_state["throttle"] = 0.6
        state.robot_state["steering"] = -0.3
        motor_driver = Mock()

        with patch(
            "app.asyncio.sleep",
            new_callable=AsyncMock,
            side_effect=asyncio.CancelledError,
        ):
            await motor_control_loop({"motor_driver": motor_driver})

        motor_driver.set_motors.assert_called_once_with(
            throttle=-0.6,
            steering=-0.3,
        )
