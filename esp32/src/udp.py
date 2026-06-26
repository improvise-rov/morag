import socket
import random
import struct
from src import consts

class Address():
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

    def tupl(self) -> tuple[str, int]:
        return (self.ip, self.port)
    
    @staticmethod
    def of(tuple: tuple[str, int]) -> Address:
        return Address(tuple[0], tuple[1])

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

class FloatNetworker():
    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # use UDP
        self.server.bind(('', consts.PORT))
        self.server.settimeout(1)
    
    def send(self, addr: Address, packet: bytes):
        self.server.sendto(packet, addr.tupl())

    def handle_packet(self) -> tuple[Address, int, bytes]:
        try:
            data, addr = self.server.recvfrom(consts.PACKET_SIZE)

            id, = struct.unpack_from(HEADER_FORMAT, data)

            return Address.of(addr), id, data[struct.calcsize(HEADER_FORMAT):]
        except OSError: # micropython raises OSError instead of TimeoutError
            return Address("", 0), 0, bytes()

    @staticmethod
    def build_packet(id: int, data: bytes = bytes()) -> bytes:

        if len(data) > consts.PACKET_SIZE - struct.calcsize(HEADER_FORMAT):
            raise OverflowError(f"too much data! max is {consts.PACKET_SIZE - struct.calcsize(HEADER_FORMAT)}, this is {len(data)}")

        packet = [0x0 for i in range(consts.PACKET_SIZE)]
        header = struct.pack(HEADER_FORMAT, id)

        packet[0:len(header)] = list(header)

        packet[len(header):consts.PACKET_SIZE] = list(data)

        while len(packet) < consts.PACKET_SIZE:
            packet.append(0x0)

        return bytes(packet)
    
    @staticmethod
    def random_data(profile: int = 0, points: int = 64) -> bytes:
        data: bytes = bytes()

        # other data
        temperature = random.randrange(-20, 20)
        data += struct.pack(OTHER_DATA_FORMAT, profile, temperature)

        # points
        data += struct.pack(">i", points) # pack number of points
        for i in range(points):
            data += struct.pack(POINT_FORMAT, i, random.randrange(-100, 0))


        return data
    
    @staticmethod
    def gathered_data(profile: int = 0, avg_temperature: float = 0.0, data_points: list[tuple[float, float]] = []) -> bytes:
        data: bytes = bytes()

        # other data
        data += struct.pack(OTHER_DATA_FORMAT, profile, avg_temperature)

        # points
        data += struct.pack(">i", len(data_points)) # pack number of points
        for datum in data_points: # time, depth
            data += struct.pack(POINT_FORMAT, datum[0], datum[1])


        return data