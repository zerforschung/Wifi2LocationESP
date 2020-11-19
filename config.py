from micropython import const

EPOCH_OFFSET = const(946681200)  # seconds between 1970 and 2000

WIFI_CONNECT_TIMEOUT = const(15)  # seconds

AP_NAME = "Your Mother's iPhone"
AP_PASS = "password123"


SSID_EXCLUDE_PREFIX = [
    "AndroidAP",
    AP_NAME,  # we don't want my personal hotspot at every location :D
]
SSID_EXCLUDE_SUFFIX = [
    "_nomap",
    "iPhone",
]
SSID_EXCLUDE_REGEX = [
    ".*[M|m]obile[ |\-|_]?[H|h]otspot.*",
    ".*[M|m]obile[ |\-|_]?[W|w][I|i][ |\-]?[F|f][I|i].*",
    ".*[M|m][I|i][\-]?[F|f][I|i].*",
    ".*Samsung.*",
    ".*BlackBerry.*",
]
