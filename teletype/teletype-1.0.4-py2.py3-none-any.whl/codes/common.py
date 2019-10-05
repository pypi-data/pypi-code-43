# coding=utf-8

CHARS_ASCII = {
    "arrow": ">",
    "block": "#",
    "left-edge": "|",
    "right-edge": "|",
    "selected": "*",
    "unselected": ".",
}

COLOURS = {
    "blue": "\x1b[34m",
    "cyan": "\x1b[36m",
    "green": "\x1b[32m",
    "grey": "\x1b[30m",
    "magenta": "\x1b[35m",
    "red": "\x1b[31m",
    "white": "\x1b[37m",
    "yellow": "\x1b[33m",
}

CURSOR = {
    "bol": "\x1b[1K",
    "clear": "\x1b[3J\x1b[H\x1b[2J",
    "down": "\x1b[B",
    "eol": "\x1b[K",
    "hide": "\x1b[?25l",
    "left": "\x08",
    "right": "\x1b[C",
    "show": "\x1b[?12l\x1b[?25h",
    "up": "\x1b[A",
}

ESCAPE_SEQUENCES = {
    "\x1b",
    "\x1b[",
    "\x1b[1",
    "\x1b[15",
    "\x1b[16",
    "\x1b[17",
    "\x1b[18",
    "\x1b[19",
    "\x1b[2",
    "\x1b[20",
    "\x1b[21",
    "\x1b[22",
    "\x1b[23",
    "\x1b[24",
    "\x1b[3",
    "\x1b[5",
    "\x1b[6",
    "\x1b\x1b",
    "\x1b\x1b[",
    "\x1b\x1b[2",
    "\x1b\x1b[3",
    "\x1bO",
}

HIGHLIGHTS = {
    "on-blue": "\x1b[44m",
    "on-cyan": "\x1b[46m",
    "on-green": "\x1b[42m",
    "on-grey": "\x1b[40m",
    "on-magenta": "\x1b[45m",
    "on-red": "\x1b[41m",
    "on-white": "\x1b[47m",
    "on-yellow": "\x1b[43m",
}

KEYS = {
    "lf": "\r",
    "cr": "\n",
    "space": " ",
    "backspace": "\x08",
    "ctrl-a": "\x01",
    "ctrl-b": "\x02",
    "ctrl-c": "\x03",
    "ctrl-d": "\x04",
    "ctrl-e": "\x05",
    "ctrl-f": "\x06",
    "ctrl-z": "\x1a",
    "down": "\x1b[B",
    "left": "\x1b[D",
    "right": "\x1b[C",
    "up": "\x1b[A",
    "f1": "\x1bOP",
    "f2": "\x1bOQ",
    "f3": "\x1bOR",
    "f4": "\x1bOS",
    "f5": "\x1bO15~",
    "f6": "\x1bO17~",
    "f7": "\x1bO18~",
    "f8": "\x1bO19~",
    "f9": "\x1bO20~",
    "f10": "\x1bO21~",
    "f11": "\x1bO23~",
    "f12": "\x1bO24~",
    "delete": "\x1b[7f",
    "end": "\x1b[F",
    "escape": "\x1b",
    "home": "\x1b[H",
    "insert": "\x1b[2~",
    "page-down": "\x1b[6~",
    "page-up": "\x1b[5~",
    "super": "\x1b[3~",
}

KEYS_FLIPPED = {v: k for k, v in KEYS.items()}

MODES = {
    "blink": "\x1b[5m",
    "bold": "\x1b[1m",
    "concealed": "\x1b[8m",
    "dark": "\x1b[2m",
    "italic": "\x1b[3m",
    "reversed": "\x1b[7m",
    "strikeout": "\x1b[9m",
    "underline": "\x1b[4m",
    "reset": "\x1b[0m",
}
