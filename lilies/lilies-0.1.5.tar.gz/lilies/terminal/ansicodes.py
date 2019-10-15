from __future__ import unicode_literals

# Leading control character
CSI = "\033["

FULLRESET = 0
BOLD = BRIGHT = 1
DIM = 2
ITALIC = 3
UNDERLINE = 4
BLINK = 5

# Unsupported
################
# RAPIDBLINK = 6
# REVERSE = 7
# CONCEAL = 8

STRIKE = 9

# Unsupported
################
# PRIMARY_FONT = 10
# ALTFONT1 = 11
# ALTFONT2 = 12
# ALTFONT3 = 13
# ALTFONT4 = 14
# ALTFONT5 = 15
# ALTFONT6 = 16
# ALTFONT7 = 17
# ALTFONT8 = 18
# ALTFONT9 = 19
# FRAKTUR = 20
# DOUBLEUNDERLINE = 21

NOBOLDDIM = 22
NOITALIC = 23
NOUNDERLINE = 24
NOBLINK = 25

# Unsupported
################
# 26 is missing?
# NOREVERSE = 27
# NOCONCEAL = 28

NOSTRIKE = 29

# COLORS!
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
LIGHTGRAY = 37

NOCOLOR = 39


# 16-color extended,
# Only kind of supported
DARKGRAY = 90
BRIGHTRED = 91
BRIGHTGREEN = 92
BRIGHTYELLOW = 93
BRIGHTBLUE = 94
BRIGHTMAGENTA = 95
BRIGHTCYAN = 96
WHITE = 97


ATTR_ON_CODES = {
    "bold": BOLD,
    "dim": DIM,
    "italic": ITALIC,
    "underline": UNDERLINE,
    "blink": BLINK,
}


ATTR_OFF_CODES = {
    "bold": NOBOLDDIM,
    "dim": NOBOLDDIM,
    "italic": NOITALIC,
    "underline": NOUNDERLINE,
    "blink": NOBLINK,
}


def fg_to_bg(ansi):
    if ansi is None:
        return None
    return ansi + 10


def esc(code):
    if code is None:
        return ""
    return "{csi}{code}m".format(csi=CSI, code=code)
