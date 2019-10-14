from builtins import super

from .ansi8open import Ansi8OpenTerminal
from .exceptions import UnsupportedColorException
from . import ansicodes
from ..style.palette import get_color

# darks
BLACK = get_color("black")
MAROON = get_color("maroon")
GREEN = get_color("green")
OLIVE = get_color("olive")
NAVY = get_color("navy")
PURPLE = get_color("purple")
TEAL = get_color("teal")
GRAY = get_color("silver")

# lights
DARKGRAY = get_color("grey")
RED = get_color("red")
LIME = get_color("lime")
YELLOW = get_color("yellow")
BLUE = get_color("blue")
MAGENTA = get_color("fuchsia")
CYAN = get_color("aqua")
WHITE = get_color("white")

DARK_TO_LIGHT = {
    BLACK: DARKGRAY,
    MAROON: RED,
    GREEN: LIME,
    OLIVE: YELLOW,
    NAVY: BLUE,
    PURPLE: MAGENTA,
    TEAL: CYAN,
    GRAY: WHITE,
}


class Ansi16Terminal(Ansi8OpenTerminal):
    def __init__(self):
        super().__init__()
        # new bright colors
        self.supported_colors += [
            DARKGRAY,
            RED,
            LIME,
            YELLOW,
            BLUE,
            MAGENTA,
            CYAN,
            WHITE,
        ]
        self.fg_colormap.update(
            {
                DARKGRAY: [ansicodes.BLACK, ansicodes.BOLD],
                RED: [ansicodes.RED, ansicodes.BOLD],
                LIME: [ansicodes.GREEN, ansicodes.BOLD],
                YELLOW: [ansicodes.YELLOW, ansicodes.BOLD],
                BLUE: [ansicodes.BLUE, ansicodes.BOLD],
                MAGENTA: [ansicodes.MAGENTA, ansicodes.BOLD],
                CYAN: [ansicodes.CYAN, ansicodes.BOLD],
                WHITE: [ansicodes.WHITE, ansicodes.BOLD],
            }
        )
        self.supported_attrs = ["italic", "dim", "underline", "blink"]

    def configure_style(self, style):
        configured = super().configure_style(style)
        if style.fg.isreset():
            return configured
        configured.fg = self._hsl_to_16color(*style.fg.hsl)
        return configured

    def assert_compatible_stylediff(self, style_diff):
        super().assert_compatible_stylediff(style_diff)
        if style_diff.bg is not None:
            self.assert_compatible_bgcolor(style_diff.bg)

    def assert_compatible_bgcolor(self, color):
        # check if it's in the DARK colors
        # light backgrounds aren't supported.
        if color not in DARK_TO_LIGHT:
            raise UnsupportedColorException("Unsupported background color")

    def _hsl_to_16color(self, h, s, l):
        color = super()._hsl_to_8color(h, s, l)
        # For grayscale, we want to optimize for a different lightness
        if color.hsl[1] == 0:
            if l < 25:
                return BLACK
            elif l < 65:
                return DARKGRAY
            elif l < 85:
                return GRAY
            else:
                return WHITE
        if l > 35:
            return DARK_TO_LIGHT[color]
        return color
