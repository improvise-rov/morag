# main.py
import network
 
ssid = "esp-ap"
security = 2
key = "password"

# setup network
ap = network.WLAN(network.WLAN.IF_AP)
ap.config(ssid=ssid, security=security, key=key)
ap.active(True)

while True:
    for sta in ap.status('stations'):
        mac = ':'.join('%02x' % b for b in sta[0]) # format the bytes into a mac address
        print('Connected MAC:', mac)