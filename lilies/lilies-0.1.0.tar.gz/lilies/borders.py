# -*- coding: utf-8 -*-
from __future__ import unicode_literals


NONE = 0
THIN = 1


# These key characters are sorted to help
# the API take any input sequence.
# t = top
# b = bottom
# l = left
# r = right
MAGIC_MAP = {
    "lr": (0, 0, 1, 1),
    "bt": (1, 1, 0, 0),
    "lt": (1, 0, 1, 0),
    "rt": (1, 0, 0, 1),
    "bl": (0, 1, 1, 0),
    "br": (0, 1, 0, 1),
    "blt": (1, 1, 1, 0),
    "brt": (1, 1, 0, 1),
    "lrt": (1, 0, 1, 1),
    "blr": (0, 1, 1, 1),
    "blrt": (1, 1, 1, 1),
}


BOUNDS_MAP = {
    (0, 0, 0, 0): " ",
    (1, 1, 0, 0): "│",
    (0, 0, 1, 1): "─",
    (1, 0, 1, 0): "┘",
    (1, 0, 0, 1): "└",
    (0, 1, 1, 0): "┐",
    (0, 1, 0, 1): "┌",
    (1, 1, 1, 0): "┤",
    (1, 1, 0, 1): "├",
    (1, 0, 1, 1): "┴",
    (0, 1, 1, 1): "┬",
    (1, 1, 1, 1): "┼",
}

STYLE_MAP = {"thin": THIN}


def _getbounds(vectors, style_int):
    vector_key = "".join(sorted(vectors))
    bounds = MAGIC_MAP[vector_key]
    return tuple(map(lambda b: b * style_int, bounds))


def _frombounds(bounds):
    return BOUNDS_MAP[bounds]


def border_char(vectors, style="thin"):
    style_int = STYLE_MAP[style]
    return _frombounds(_getbounds(vectors, style_int))
