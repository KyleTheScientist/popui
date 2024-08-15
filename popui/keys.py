BACKSPACE = 8
TAB = 9
ENTER = 13
SHIFT = 16
CONTROL = 17
ALT = 18
CAPSLOCK = 20
ESCAPE = 27
SPACE = 32
PAGEUP = 33
PAGEDOWN = 34
END = 35
HOME = 36
LEFT = 37
UP = 38
RIGHT = 39
DOWN = 40
DELETE = 46
GRAVE = 192

KEY_CODES = {}
KEY_NAMES = {
    BACKSPACE : "backspace",
    TAB : "tab",
    ENTER : "enter",
    SHIFT : "shift",
    CONTROL : "control",
    ALT : "alt",
    CAPSLOCK : "capslock",
    ESCAPE : "escape",
    SPACE : "space",
    PAGEUP : "pageup",
    PAGEDOWN : "pagedown",
    END : "end",
    HOME : "home",
    LEFT : "left",
    UP : "up",
    RIGHT : "right",
    DOWN : "down",
    DELETE : "delete",
    GRAVE: "`",
}


for i in range(10):
    KEY_NAMES[48 + i] = str(i)

for i in range(26):
    KEY_NAMES[65 + i] = chr(65 + i).lower()


for i in range(10):
    KEY_NAMES[97 + i] = 'numpad' + str(i)

for i in range(12):
    KEY_NAMES[112 + i] = 'f' + str(i + 1)

for key, name in KEY_NAMES.items():
    KEY_CODES[name] = key


def key_code(name):
    return KEY_CODES[name.lower()]

def key_name(code):
    return KEY_NAMES[code]
