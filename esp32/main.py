import network
import math

from src import consts
from src import ms5837
from src import servo
from src import udp

class Profiler():
    def __init__(self) -> None:
        # setup network ap
        self.ap = network.WLAN(network.WLAN.IF_AP)
        self.ap.config(essid=consts.NETWORK_NAME)
        self.ap.active(True)

        # sensor
        #sensor = ms5837.Sensor()

        # servo
        self.buoyancy = servo.Servo(consts.BUOYANCY_SERVO_PIN)
        
        # networker
        self.networker = udp.FloatNetworker()

        # stuff
        self.keep_open = True
        self.profiles = 0
        self.ready_to_transmit = False

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
        self.networker.send(addr, udp.FloatNetworker.build_packet(udp.ACK))
        self.ready_to_transmit = True
        print("profile complete")

    def send_data(self, addr: udp.Address):
        if self.ready_to_transmit:
            print("sending payload..")
            self.networker.send(addr, udp.FloatNetworker.build_packet(udp.DATA_PAYLOAD, udp.FloatNetworker.random_data(profile=self.profiles)))
            print("data transmitted")

    def get_macs(self) -> list[str]:
        return [':'.join('%02x' % b for b in sta[0]) for sta in self.ap.status('stations')]
    
    def get_ip(self) -> str:
        return self.ap.ipconfig('addr4')[0]


if __name__ == "__main__":
    network.hostname(consts.NETWORK_HOSTNAME)

    print(consts.IMPROVISE_ASCII_ART_STRING)
    print()
    profiler = Profiler()
    print("ip: " + profiler.get_ip())
    profiler.run()
