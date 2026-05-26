from enum import Enum

class MenuState(Enum):
    MAIN = 0
    AIRPORT = 1
    PLANE = 2

SAVE_FILE_NAME = "save"
REFRESH_PLANE_MARKET_PRICE = 1
ALERT_CODE = '►'
END_CODE = '¶'
OPTION_MENU_CODE = '‼'
CONSOLE_C = 120
CONSOLE_R = 30
MAP_C = 80
MAP_R = 28

Plane_Serial = 65 #ascii char A

class ColorModes(Enum):
    default = 0

class Pallette():
    def __init__(self):
        self.airportcolor   = Color.WHITE
        self.highlightcolor = Color.YELLOW
        self.planecolor_c   = Color.CYAN
        self.planecolor_b   = Color.RED
        self.planecolor_a   = Color.MAGENTA
        self.pathcolor      = Color.BLUE
        self.mapcolor       = Color.GREEN
        self.bordercolor    = Color.GREEN
        self.titlecolor     = Color.GREEN
        self.menucolor      = Color.GREEN
        self.optioncolor_bg = Color.BG_GREEN
        self.optioncolor    = Color.YELLOW
        self.alertcolor     = Color.RED
        self.cloudcolor     = Color.WHITE
        self.cloudinfo      = Color.CYAN

class PlaneState(Enum):
    need_dest = 0
    ready = 1
    taking_off = 2
    fly = 3

class Page(Enum):
    default = 0
    planes = 1
    airports = 2
    store = 3
    market = 4
    about = 5
    construct = 6
    commands = 7
    stats = 8

class Color:
    BLACK   = "\u001b[30m"
    RED     = "\u001b[31m"
    GREEN   = "\u001b[32m"
    YELLOW  = "\u001b[33m"
    BLUE    = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN    = "\u001b[36m"
    WHITE   = "\u001b[37m"
    END     = "\u001b[0m"
    BG_BLACK = "\u001b[40m"
    BG_RED   = "\u001b[41m"
    BG_GREEN = "\u001b[42m"
    BG_ORANGE = "\u001b[43m"
    BG_BLUE = "\u001b[44m"
    BG_PURPLE = "\u001b[45m"
    BG_CYAN = "\u001b[46m"
    BG_LIGHTGRAY = "\u001b[47m"

class ALOOKUP:
    lookup = {
            "JFK" : ["New York", [10,19]],
            "LAX" : ["Los Angeles", [11,7]],
            "DUB" : ["Dublin", [7,32]],
            "PEK" : ["Beijing", [12,64]],
            "YUL" : ["Montreal", [8,19]],
            "HNL" : ["Honolulu", [12,2]], 
            "ANC" : ["Anchorage", [6,3]],
            "GOH" : ["Nuuk", [4,26]],
            "MAD" : ["Madrid", [10,34]], 
            "CDG" : ["Paris", [9,36]],
            "LGW" : ["London", [7,34]],
            "ATH" : ["Athens", [10,41]],
            "LED" : ["St. Petersburg", [7,42]], 
            "MEX" : ["Mexico City", [13,14]],
            "GIG" : ["Rio de Janeiro", [17,24]],
            "EZE" : ["Buenos Aires", [21,21]],
            "LIM" : ["Lima", [17,15]],
            "CAI" : ["Cairo", [13,43]],
            "DXB" : ["Dubai", [13,48]]
            }

AirportLookup = {
    "JFK" : ["New York", [10,19]],
    "LAX" : ["Los Angeles", [11,7]],
    "DUB" : ["Dublin", [7,32]],
    "PEK" : ["Beijing", [12,64]],
    "YUL" : ["Montreal", [8,19]],
    "HNL" : ["Honolulu", [12,2]], 
    "ANC" : ["Anchorage", [6,3]],
    "GOH" : ["Nuuk", [4,26]],
    "MAD" : ["Madrid", [10,34]], 
    "CDG" : ["Paris", [9,36]],
    "LGW" : ["London", [7,34]],
    "ATH" : ["Athens", [10,41]],
    "LED" : ["St. Petersburg", [7,42]], 
    "MEX" : ["Mexico City", [13,14]],
    "GIG" : ["Rio de Janeiro", [17,24]],
    "EZE" : ["Buenos Aires", [21,21]],
    "LIM" : ["Lima", [17,15]],
    "CAI" : ["Cairo", [13,43]],
    "DXB" : ["Dubai", [13,48]]
}
