import _thread
import time

from src import pid
from src import servo
from src import ms5837

class DepthController():
    def __init__(self, sensor: ms5837.Sensor, output_controller: servo.Servo) -> None:
        self.sensor = sensor
        self.target = 0.0

        self.pid = pid.PIDController(0.0)
        self.output = output_controller

        self.thread_handle = _thread.start_new_thread(self._thread_method, ())

    def tick(self, dt: float):
        self.pid.target = self.target
        
        depth = self.sensor.depth()
        modulation = self.pid.compute_modulation(depth, dt)
        speed = self.output.get_speed() * modulation * dt
        self.output.set_speed(speed)

    
    def _thread_method(self):
        dt = 0.0
        while True:
            start = time.ticks_ms()
            self.tick(dt)
            dt = time.ticks_diff(time.ticks_ms(), start)