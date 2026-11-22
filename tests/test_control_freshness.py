import unittest

from robot.websocket import is_fresh_control_command


class ControlFreshnessTests(unittest.TestCase):
    def test_accepts_commands_within_timeout_window(self):
        self.assertTrue(is_fresh_control_command(10.0, 10.49))

    def test_rejects_commands_older_than_timeout_window(self):
        self.assertFalse(is_fresh_control_command(10.0, 10.501))

    def test_rejects_invalid_future_timestamp(self):
        self.assertFalse(is_fresh_control_command(20.0, 10.0))
