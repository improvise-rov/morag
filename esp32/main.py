# main.py
import network
 
ssid = "esp-ap"
security = 2
key = "password"

# setup network
ap = network.WLAN(network.WLAN.IF_AP)
ap.config(essid=ssid, security=security, key=key)
ap.active(True)

while True:
    pass