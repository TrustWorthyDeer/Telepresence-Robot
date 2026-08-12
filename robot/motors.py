import time
from gpiozero import PWMOutputDevice


class DirectPiMotorDriver:
    def __init__(self, in1=18, in2=19, in3=12, in4=13, min_pwm=70, max_pwm=255):
        # Initialize PWM outputs at 1kHz
        self.left_in1 = PWMOutputDevice(in1, frequency=1000)
        self.left_in2 = PWMOutputDevice(in2, frequency=1000)
        self.right_in3 = PWMOutputDevice(in3, frequency=1000)
        self.right_in4 = PWMOutputDevice(in4, frequency=1000)

        # Minimum PWM required to overcome motor/chassis static friction
        self.min_pwm = min_pwm
        self.max_pwm = max_pwm

    def set_motors(self, throttle: float, steering: float):
        
        # throttle: [-1.0 to 1.0]
        # steering: [-1.0 to 1.0]

        # Differential drive (skid steer) calculations
        left_speed = throttle + steering
        right_speed = throttle - steering

        # Normalize speeds within [-1.0, 1.0]
        max_val = max(abs(left_speed), abs(right_speed))
        if max_val > 1.0:
            left_speed /= max_val
            right_speed /= max_val

        # LEFT MOTOR FIX: IN2 is Forward, IN1 is Reverse
        self._drive_side(self.left_in2, self.left_in1, left_speed)
        
        # RIGHT MOTOR FIX: IN3 is Forward, IN4 is Reverse
        self._drive_side(self.right_in3, self.right_in4, right_speed)

    def _drive_side(self, pwm_fwd, pwm_rev, speed: float):
        speed = max(-1.0, min(1.0, speed))  # Clamp between -1.0 and 1.0
        abs_speed = abs(speed)

        if abs_speed > 0.001:  # Non-zero speed input
            # Map [0.0 ... 1.0] to [min_pwm ... max_pwm] and convert to gpiozero duty cycle [0.0 ... 1.0]
            pwm_value = (self.min_pwm + abs_speed * (self.max_pwm - self.min_pwm)) / 255.0

            if speed > 0:  # Forward
                pwm_fwd.value = pwm_value
                pwm_rev.value = 0.0
            else:          # Reverse
                pwm_fwd.value = 0.0
                pwm_rev.value = pwm_value
        else:  # Stop
            pwm_fwd.value = 0.0
            pwm_rev.value = 0.0

    def stop(self):
        self.left_in1.value = 0.0
        self.left_in2.value = 0.0
        self.right_in3.value = 0.0
        self.right_in4.value = 0.0

    def close(self):
        self.stop()
        self.left_in1.close()
        self.left_in2.close()
        self.right_in3.close()
        self.right_in4.close()