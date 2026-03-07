from http.server import BaseHTTPRequestHandler, HTTPServer
import threading as t
import json
import time
import random as r
import ms5837 as bar02
from common import host, port

"""
What certain extreme (negative) depth values mean for reference:

-inf -> Sensor could not initialise

In the event of a failed read, the last known depth will be passed again. This ensures accuracy is not impacted too much.
"""


data = {
    "name": "ImpROVise",
    "number": 0,
    "time": "",
    "depth": 0
}

failedToInit = False
sensor = bar02.MS5837_02BA(bus=1) # bar02 sensor
lastKnownDepth = 0
startTime = 0

DEPTH_OFFSET = 0.3
INF = float("inf") # this produces infinity

## webserver management

def UpdateData() -> None:
    data["depth"] = FetchDepth()
    data["time"] = startTime - time.time()

def DoGet() -> str:
    UpdateData()
    return json.dumps(data)


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(f"{DoGet()}", "utf-8"))


## Thread Management

def DoServer() -> None:
    ws = HTTPServer((host, port), Server)
    
    print(f"< Started Server (http://{host}:{port}/) >")
    
    try:
        ws.serve_forever()
    except KeyboardInterrupt:
        pass
    
    ws.server_close()
    print("< Stopped >")


## depth meter stuff - bar02 sensor

def InitialiseSensor() -> None:
    if (not sensor.init()):
        failedToInit = True
        print("Sensor could not initialise (something has gone terribly wrong); values of -inf will be passed as depth")
    else:
        ## initialise sensor references, scales and stuff
        sensor.setFluidDensity(bar02.DENSITY_FRESHWATER) # the rov will ALWAYS be in freshwater

def FetchDepth() -> int:
    if (failedToInit):
        return -INF
    else:
        if (sensor.read()):
            depth = (sensor.depth() + DEPTH_OFFSET) * -1
            lastKnownDepth = depth
            return depth
        else:
            print("Failed to read sensor! Returning last known depth.")
            return lastKnownDepth
    pass

##


## main

if __name__ == "__main__":
    # Set Start Time
    startTime = time.time()

    # Initialise Sensor
    InitialiseSensor()
    
    # Execute Server
    DoServer()
    
