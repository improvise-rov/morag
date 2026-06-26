class PIDController():
    def __init__(self, target: float,
                 kp: float = 1.0, ki: float = 0.1, kd: float = 0.05) -> None:
        self.target = target

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self._previous_error = 0.0
        self._derivative = 0.0
        self._integral = 0.0

    def compute_modulation(self, process_variable: float, dt: float) -> float:
        if dt == 0.0:
            return process_variable
        
        error = self.target - process_variable

        self._integral += error * dt
        self._derivative = (error - self._previous_error) / dt

        v = (self.kp * error) + (self.ki * self._integral) + (self.kd * self._derivative)
        
        self._previous_error = error

        return v