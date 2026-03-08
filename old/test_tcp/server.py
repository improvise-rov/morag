import threading as t
import json
import time
import random as r
import ms5837 as bar02
from common import tcp_ip, tcp_port
import socket as s
import RPi.GPIO as pin

"""
What certain extreme (negative) depth values mean for reference:

-inf -> Sensor could not initialise

In the event of a failed read, the last known depth will be passed again. This ensures accuracy is not impacted too much.
"""

## RPI PINS
PIN_Up = 17
PIN_Down = 27
##


data = {
    "name": "ImpROVise",
    "number": 0,
    "time": "",
    "depth": 0,
    "temp": 0,
    "pressure": 0
}

failedToInit = False
sensor = bar02.MS5837_02BA(bus=1) # bar02 sensor
lastKnownDepth = 0
lastKnownTemp = 0
lastKnownPressure = 0
startTime = 0

DEPTH_OFFSET = 0.3
TEMP_OFFSET = -33
PRESSURE_OFFSET = 1900
INF = float("inf") # this produces infinity

## webserver management

def test_values() -> dict:
    return {'name': 'TEST', 'number': "EX23", 'time': time.time() - startTime, 'depth': r.randint(0, 10), 'pressure': r.randint(0, 10), 'temp': 13}

def UpdateData() -> None:
    global data

    data["depth"] = FetchDepth()
    data["time"] = time.time() - startTime
    data["temp"] = FetchTemp()
    data["pressure"] = FetchPressure()

    data = test_values()

def DoGet() -> str:
    UpdateData()
    return json.dumps(data)

def test(o):
    print(o)
    return o

class SocketHandle(t.Thread):
    

    def __init__(self):
        t.Thread.__init__(self)
        self.conn = None
    
    def SetConnection(self, conn: s.socket):
        self.conn = conn
    
    def run(self):
        pin.setmode(pin.BCM)
        pin.setup(PIN_Up, pin.OUT)
        pin.setup(PIN_Down, pin.OUT)

        while True:
            data = ""
            try:
                # receive
                data = self.conn.recv(1024)
            except:
                print("bad packet! crashing and burning..")
                break
            if (len(data) == 0):
                break
            self.do_packet(data)

    def conn_close(self):
        print("cleanup")
        pin.cleanup()
        if (not self.conn == None):
            self.conn.close()
            print("connection closed.")

    def do_packet(self, data):
        TERMINATOR = '\0' # ill be back

        id = data[0] # get leading character as ascii, acts as an id
        if (id == 0): # get data
            d = DoGet()
            self.conn.sendall(bytes(d + TERMINATOR, "utf-8"))
        elif (id == 1): # send up to arduino
            pin.output(PIN_Up, pin.HIGH)
            print("going up, sire?")
            time.sleep(.1)
            pin.output(PIN_Up, pin.LOW)
        elif (id == 2): # send down to arduino
            pin.output(PIN_Down, pin.HIGH)
            print("yro'ue going down!1!11!!!")
            time.sleep(.1)
            pin.output(PIN_Down, pin.LOW)
        else:
            print(f"unknown packet ({id}?), ignoring")

## Thread Management

def DoServer() -> None:
    serverSock = s.socket(s.AF_INET, s.SOCK_STREAM)
    serverSock.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)

    try:
        serverSock.bind((tcp_ip, tcp_port))
    except:
        print("couldnt bind server socket")
        exit()
    serverSock.listen(10)

    print(f"< Started Server ({tcp_ip}:{tcp_port}/) >")

    h = SocketHandle()

    while True:
        try:
            conn, addr = serverSock.accept()
            print(f"connection: {addr[0]}")

            h.SetConnection(conn)
            h.setDaemon(True)

            h.start()
        except KeyboardInterrupt:
            break
    h.conn_close()

    print("< Stopped >")
    exit()


## depth meter stuff - bar02 sensor

def InitialiseSensor() -> None:
    if (not sensor.init()):
        failedToInit = True
        print("Sensor could not initialise (something has gone terribly wrong); values of -inf will be passed as depth")
    else:
        ## initialise sensor references, scales and stuff
        sensor.setFluidDensity(bar02.DENSITY_FRESHWATER) # the rov will ALWAYS be in freshwater

def FetchDepth() -> float:
    global lastKnownDepth
    if (failedToInit):
        return -INF
    else:
        if (sensor.read()):
            depth = (sensor.depth() + DEPTH_OFFSET) * 1
            lastKnownDepth = depth
            return depth
        else:
            print("Failed to read sensor! Returning last known depth.")
            return lastKnownDepth

def FetchTemp()-> float:
    global lastKnownTemp
    if (failedToInit):
        return -INF
    else:
        if (sensor.read()):
            temp = (sensor.temperature() + TEMP_OFFSET) * -1
            lastKnownTemp = temp
            return temp
        else:
            print("Failed to read Sensor Temperature! Returning last known temp.")
            return lastKnownTemp

def FetchPressure() -> float:
    global lastKnowPressure
    if (failedToInit):
        return -INF
    else:
        if (sensor.read()):
            pressure = (sensor.pressure(bar02.UNITS_Pa) + PRESSURE_OFFSET) * 1 # get pressure in pascals
            lastKnown = pressure
            return pressure
        else:
            print("Failed to read Sensor Pressure! Returning last known pressure.")
            return lastKnownPressure

## main

if __name__ == "__main__":
    # Set Start Time
    startTime = time.time()

    # Initialise Sensor and Pinouts
    InitialiseSensor()
    
    # Execute Server
    DoServer()
    
