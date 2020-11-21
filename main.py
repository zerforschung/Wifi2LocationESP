import gc
import machine
import network
import ntptime
import ubinascii
import ure
import usocket
import utime

from machine import Pin

import config


def now() -> int:
    return utime.time() + config.EPOCH_OFFSET


def syslog(categorie: str, message: str):
    print("-- [{}] -- {}".format(categorie, message))


def syncTime():
    try:
        ntptime.settime()
        syslog("Time", "Synced via NTP.")
    except Exception as e:
        syslog("Time", "Error getting NTP: {}".format(e))


def removeIgnoredSSIDs(nets):
    new_nets = []

    compiled_regex = []
    for regex in config.SSID_EXCLUDE_REGEX:
        compiled_regex.append(ure.compile(regex))

    for net in nets:
        ssid, mac, channel, rssi, authmode, hidden = net
        isIgnored = False

        if hidden:
            continue

        for prefix in config.SSID_EXCLUDE_PREFIX:
            if ssid.startswith(prefix):
                isIgnored = True
                break

        if isIgnored:
            continue

        for suffix in config.SSID_EXCLUDE_SUFFIX:
            if ssid.endswith(suffix):
                isIgnored = True
                break

        if isIgnored:
            continue

        for r in compiled_regex:
            if r.match(ssid):
                isIgnored = True
                break

        if isIgnored:
            continue

        new_nets.append(net)

    return new_nets


def connectWLAN(name: str, passphrase: str) -> bool:
    syslog("Wifi", "Connecting...")
    wlan.connect(name, passphrase)
    connect_delay_counter = 0
    while not wlan.isconnected():
        if connect_delay_counter > 100 * config.WIFI_CONNECT_TIMEOUT:
            syslog("Wifi", "Timeout.")
            return False
        connect_delay_counter = connect_delay_counter + 1
        utime.sleep_ms(10)
    syslog("Wifi", "Connected.")
    return True


def formatMAC(mac: str) -> str:
    mac = ubinascii.hexlify(mac).decode().upper()
    return (
        mac[0:2]
        + ":"
        + mac[2:4]
        + ":"
        + mac[4:6]
        + ":"
        + mac[6:8]
        + ":"
        + mac[8:10]
        + ":"
        + mac[10:12]
    )


def writeWifisList(filename, nets):
    for net in nets:
        ssid, mac, channel, rssi, authmode, hidden = net
        filename.write(
            "'{}','{}','{}','{}','{}','{}', '{}'\n".format(
                now(),
                ssid.decode(),
                formatMAC(mac),
                channel,
                rssi,
                authmode,
                hidden,
            )
        )
        filename.flush()


def flashLED():
    led.off()  # for some reason off and on are flipped on board "Tinchen"
    utime.sleep_ms(50)
    led.on()  # for some reason off and on are flipped on board "Tinchen"
    utime.sleep_ms(50)


syslog("Machine", "Wifi2LocationESP - {}".format(config.AP_NAME))

led = Pin(2, Pin.OUT)
led.on()  # for some reason off and on are flipped on board "Tinchen"

syslog("Wifi", "Starting Wifi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
try:
    nets = wlan.scan()
except Exception:
    nets = []

connected = connectWLAN(config.AP_NAME, config.AP_PASS)
if not connected:
    for _ in range(0, 10):
        flashLED()
    syslog("Machine", "Going into deep sleep for basically ever...")
    machine.deepsleep(1000 * 60 * 60 * 24)  # closest thing to "shutdown"

syncTime()
gc.collect()

syslog("Server", "Starting listener...")
s = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
s.bind(("", 80))
s.listen(0)

while True:
    conn, addr = s.accept()
    syslog("Server", "Accepted connection from {}".format(addr))
    request = conn.recv(1024).decode()
    get = request.split("\r\n")[0]  # only GET line
    path = get.split(" ")[1]  # only path
    filename = path.split("/")[-1]  # only last element

    if filename == "favicon.ico":
        conn.send("HTTP/1.1 404 Not Found\n")
        conn.send("Connection: close\n\n")
        conn.close()
        utime.sleep_ms(100)
        continue

    if filename == "":
        filename = "scan-{}".format(now())
    filename += ".csv"

    conn.send("HTTP/1.1 200 OK\n")
    conn.send("Content-Type: text/html\n")
    conn.send("Connection: close\n\n")
    conn.send(
        """
        <html>
            <head>
                <title>Wifi2LocationESP</title>
            </head>
            <body>
                <p>Starting new scan, saving to file: <strong>{}</strong></p>
                <p>To stop scanning, just turn off power when LED is off.</p>
            </body>
        </html>""".format(
            filename
        )
    )
    syslog("Server", "Closing connection...")
    conn.close()
    utime.sleep_ms(250)
    syslog("Wifi", "Disconnecting...")
    wlan.disconnect()
    gc.collect()

    syslog("Scan", "Starting new scan, saving to file: {}".format(filename))
    csv = open(filename, "a")
    while True:
        led.off()  # for some reason off and on are flipped on board "Tinchen"
        try:
            nets = wlan.scan()
        except Exception:
            nets = []
        nets = removeIgnoredSSIDs(nets)
        writeWifisList(csv, nets)
        gc.collect()

        led.on()  # for some reason off and on are flipped on board "Tinchen"
        utime.sleep(3)
