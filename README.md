# Wifi2LocationESP

A [MicroPython](https://micropython.org/)-based firmware to collect MAC addresses of access points at specific locations, so you can generate your personal wifi location database.

You need some kind of mobile access point (iPhone/Android, [VoCore](https://vocore.io/), 4G router, etc.) to start a scan and an active internet uplink to get the current time via NTP (it will work without NTP but won't include correct timestamps).

This has been tested with ESP8266 board `Tinchen` made by [@ubahnverleih](https://github.com/ubahnverleih), but it should work with any ESP8266 or ESP32 board, maybe even other MCUs. Please try and submit PRs ;-)

## How do I use it?

### preparing

1. flash your ESP with [MicroPython](https://micropython.org/)
2. edit config.py to your needs
    * set `AP_NAME`/`AP_PASS` to the SSID and password of your hotspot
    * if your hotspot is slow to connect, increase the `WIFI_CONNECT_TIMEOUT`
3. copy main.py and config.py to your ESP for example with [rshell](https://github.com/dhylands/rshell)

### on the road

1. enable your hotspot
2. power on the ESP
3. connect your phone or notebook to the hotspot
4. figure out the IP address of your ESP
    * with a router: there is probably a webinterface which lists all connected devices and their IP addresses
    * with an iOS or Android Device: use [HE Network Tools](https://networktools.he.net/), under `ARP/NDP`
    * with a notebook:
        * query your ARP table (Google: `show arp table $yourOperatingSystem`)
        * scan the network with nmap: `nmap -sP ip.of.your.notebook/24`
5. open `http://ip.of.your.esp/SomeNameForYourScan` in a browser/with curl/etc. - instructions how to stop are shown
6. the ESP will wake up every 3 seconds, scan for wifis and save them in a file - Caution: this will require a lot of power!

### back home

1. copy the files from your ESP, for example with [rshell](https://github.com/dhylands/rshell)
