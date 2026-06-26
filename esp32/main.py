import network
import math
import time

from src import consts
from src import ms5837
from src import servo
from src import udp
from src import depth

class Profiler():
    def __init__(self) -> None:
        # setup network ap
        self.ap = network.WLAN(network.WLAN.IF_AP)
        self.ap.config(essid=consts.NETWORK_NAME)
        self.ap.active(True)

        # sensor
        self.sensor = ms5837.Sensor()

        # servo
        self.servo = servo.Servo(consts.BUOYANCY_SERVO_PIN, consts.FEEDBACK_PIN)
        
        # networker
        self.networker = udp.FloatNetworker()

        # depth controller
        self.depth_controller = depth.DepthController(self.sensor, self.servo)

        # stuff
        self.keep_open = True
        self.profiles = 0
        self.ready_to_transmit = False

        # readings
        self.last_readings: list[tuple[float, float, float]] = [] # time, depth, temperature

    def run(self):
        print("started!")
        while self.keep_open:
            addr, id, data = self.networker.handle_packet()

            if id == udp.START_PROFILE:         self.start_profile(addr)
            if id == udp.STATION_ASKS_FOR_DATA: self.send_data(addr)


    def start_profile(self, addr: udp.Address):
        self.profiles += 1
        print(f"starting profile #{self.profiles}..")
        self.ready_to_transmit = False
        
        # clear data from last reading
        self.last_readings = []

        # descend down about 2.5 meters and hold for 30 seconds
        self.depth_controller.target = 2.5
        time.sleep(30)
        

        # ascend to about 40cm and hold for 30 seconds
        self.depth_controller.target = 0.4
        time.sleep(30)

        # descend again
        self.depth_controller.target = 2.5
        time.sleep(30)

        # ascend again
        self.depth_controller.target = 0.4
        time.sleep(30)

        # surface
        self.depth_controller.target = 0.0

        # send data
        self.networker.send(addr, udp.FloatNetworker.build_packet(udp.ACK))
        self.ready_to_transmit = True
        print("profile complete")

    def send_data(self, addr: udp.Address):
        if self.ready_to_transmit:
            print("sending payload..")
            self.networker.send(addr, udp.FloatNetworker.build_packet(udp.DATA_PAYLOAD, 
                                                                      udp.FloatNetworker.gathered_data(
                                                                          profile=self.profiles,
                                                                          avg_temperature=self.average_temperature(),
                                                                          data_points=self.extract_graphable_data()
                                                                          )
                                                                    ))
            print("data transmitted")

    def get_macs(self) -> list[str]:
        return [':'.join('%02x' % b for b in sta[0]) for sta in self.ap.status('stations')]
    
    def get_ip(self) -> str:
        return self.ap.ipconfig('addr4')[0]
    
    def average_temperature(self) -> float:
        reduced = 0
        n = 0
        for datum in self.last_readings:
            reduced += datum[2]
            n += 1
        return reduced / n
    
    def extract_graphable_data(self) -> list[tuple[float, float]]:
        data = []
        for datum in self.last_readings:
            data.append((datum[0], datum[1]))
        return data


if __name__ == "__main__":
    network.hostname(consts.NETWORK_HOSTNAME)

    print(consts.IMPROVISE_ASCII_ART_STRING)
    print()
    profiler = Profiler()
    print("ip: " + profiler.get_ip())
    profiler.run()
