"""
Test script to simulate the float.

Since we dont have the ESP32s at time of writing, this stands as a test for the poolside code.
This is also a template for the networking micropython that needs to be written on them.
"""

import socket
import struct
import random

# packet identifiers
NONE: int = 0
START_PROFILE: int = 1
STATION_ASKS_FOR_DATA: int = 2
DATA_PAYLOAD: int = 3
ACK: int = 4

# format specifier
HEADER_FORMAT: str = '>H' # packet id
POINT_FORMAT: str = '>ff' # time, depth
OTHER_DATA_FORMAT: str = ">if" # profile no., temperature

# network
IP: str = "127.0.0.1"
PORT: int = 8090
PACKET_SIZE: int = 1024

type _addr = tuple[str, int]

class FloatNetworker():
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # use UDP
        self.server.bind(('', PORT))
        self.server.settimeout(1)
    
    def send(self, addr: _addr, packet: bytes):
        self.server.sendto(packet, addr)

    def handle_packet(self) -> tuple[_addr, int, bytes]:
        try:
            data, addr = self.server.recvfrom(PACKET_SIZE)

            id, = struct.unpack_from(HEADER_FORMAT, data)

            return addr, id, data[struct.calcsize(HEADER_FORMAT):]
        except TimeoutError:
            return ("", 0), 0, bytes()

    @staticmethod
    def build_packet(id: int, data: bytes = bytes()) -> bytes:

        if len(data) > PACKET_SIZE - struct.calcsize(HEADER_FORMAT):
            raise OverflowError(f"too much data! max is {PACKET_SIZE - struct.calcsize(HEADER_FORMAT)}, this is {len(data)}")

        packet = [0x0 for i in range(PACKET_SIZE)]
        header = struct.pack(HEADER_FORMAT, id)

        packet[0:len(header)] = header

        packet[len(header):PACKET_SIZE] = data

        while len(packet) < 1024:
            packet += [0x0]

        return bytes(packet)
    
    @staticmethod
    def random_data(profile: int = 0, points: int = 64) -> bytes:
        data: bytes = bytes()

        # other data
        temperature = random.randrange(-20, 20)
        data += struct.pack(OTHER_DATA_FORMAT, profile, temperature)

        # points
        data += struct.pack(">i", points)
        for i in range(points):
            data += struct.pack(POINT_FORMAT, i, random.randrange(-100, 0))


        return data



class Profiler():
    def __init__(self) -> None:
        self.networker = FloatNetworker()
        self.keep_open = True
        self.profiles = 0
        self.ready_to_transmit = False

    def run(self):
        print("started!")
        while self.keep_open:
            addr, id, data = self.networker.handle_packet()

            if id == START_PROFILE:         self.start_profile(addr)
            if id == STATION_ASKS_FOR_DATA: self.send_data(addr)


    def start_profile(self, addr: _addr):
        self.profiles += 1
        print(f"starting profile #{self.profiles}..")
        self.ready_to_transmit = False
        self.networker.send(addr, FloatNetworker.build_packet(ACK))
        self.ready_to_transmit = True
        print("profile complete")

    def send_data(self, addr: _addr):
        if self.ready_to_transmit:
            print("sending payload..")
            self.networker.send(addr, FloatNetworker.build_packet(DATA_PAYLOAD, FloatNetworker.random_data(profile=self.profiles)))
            print("data transmitted")

if __name__ == "__main__":
    profiler = Profiler()
    profiler.run()

    
    