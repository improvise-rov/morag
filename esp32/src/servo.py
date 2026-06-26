from machine import Pin, PWM
from src import consts

class Servo():

    def __init__(self, pin: int, feedback_pin: int) -> None:
        self.pwm = PWM(Pin(pin), consts.PWM_FREQUENCY)
        self.feedback = PWM(Pin(feedback_pin), consts.PWM_FREQUENCY)
        self._speed = 0

    def set_speed(self, speed: float):
        if speed >= -1.0 and speed <= 1.0:
            self._speed = speed
            self.pwm.duty_u16(Servo.rotation_to_duty(self._speed)) 
    
    def get_speed(self) -> float:
        return self._speed
    
    def get_feedback(self) -> float:
        if consts.FEEDBACK:
            return 0 # do.. something... here
        return -1.0

    @staticmethod
    def rotation_to_duty(speed: float):
        assert speed >= -1.0 and speed <= 1.0

        pulse = _map(
            -1.0, 0.0, 1.0,
            speed,
            consts.SERVO_MINIMUM_US, 
            consts.SERVO_NEUTRAL_US, 
            consts.SERVO_MAXIMUM_US
        )
        period = 1_000_000 / consts.PWM_FREQUENCY

        return int((pulse / period) * 0xFFFF)
    

def _map(low: float, zero: float, high: float, map: float, target_low: float, target_zero: float, target_high: float) -> float:
    
    if map == zero:
        return target_zero
    
    delta = (map - low) / (high - low)
    value = target_low + delta * (target_high - target_low)

    return _clamp(target_low, target_high, value)


def _clamp(low: float, high: float, v: float) -> float:
    if v > high:
        return high
    elif v < low:
        return low
    else:
        return v