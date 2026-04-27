from machine import Pin, PWM
from src import consts

class Servo():
    def __init__(self, pin: int) -> None:
        self.pwm = PWM(Pin(pin), consts.PWM_FREQUENCY)
        self._ang = 0

    def set_angle(self, angle: int):
        if angle >= 0 and angle <= 180:
            self._ang = angle
            self.pwm.duty_u16(Servo.ang_to_duty_ns(self._ang)) 
    
    def get_angle(self) -> int:
        return self._ang

    @staticmethod
    def ang_to_duty_ns(angle: int):
        assert angle >= 0 and angle <= 180

        pulse = _map(
            0, 90, 180,
            angle,
            consts.SERVO_MINIMUM_DUTY, 
            consts.SERVO_NEUTRAL_DUTY, 
            consts.SERVO_MAXIMUM_DUTY
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