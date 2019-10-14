from builtins import super

from .ansi8 import Ansi8Terminal
from .attr_mixin import AnsiAttributesMixin
from . import ansicodes
from .exceptions import UnsupportedColorException
from ..style import Color, Style
from ..style.palette import (
    ORDERED_ANSI_16_COLOR_PALETTE,
    ANSI_16_COLOR_PALETTE,
)

# ANSI 256 color uses 5 color intensities plus "none" for each of R, G, B.
# This identifies the standard "color space" for colored text, not including
# an additional grayscale band.
COLOR_MAGNITUDES = [95, 135, 175, 215, 255]
COLOR_INTENSITY_MAP = {
    0: 0,
    COLOR_MAGNITUDES[0]: 1,
    COLOR_MAGNITUDES[1]: 2,
    COLOR_MAGNITUDES[2]: 3,
    COLOR_MAGNITUDES[3]: 4,
    COLOR_MAGNITUDES[4]: 5,
}


# Does not include white or black, which are special cases.
# This tops out at 238, then the next magnitude full white.
GRAY_MAGNITUDES = range(8, 240, 10)
WHITE = Color(rgb=(255, 255, 255))


class Ansi256Terminal(AnsiAttributesMixin, Ansi8Terminal):
    """
    A 256-color ansi terminal
    """

    def __init__(self):
        super().__init__()
        self.supported_attrs = ["bold", "dim", "italic", "underline", "blink"]

    def configure_style(self, style):
        """
        Configure the style for this terminal
        """
        if style.fg.isreset():
            fg = Color()
        else:
            if style.fg in ANSI_16_COLOR_PALETTE:
                fg = style.fg
            else:
                fg = self._rgb_to_color(*style.fg.rgb)
        if style.bg.isreset():
            bg = Color()
        else:
            if style.bg in ANSI_16_COLOR_PALETTE:
                bg = style.bg
            else:
                bg = self._rgb_to_color(*style.bg.rgb)

        def issupported(style):
            return style in self.supported_attrs

        attrs = filter(issupported, style.attrs)
        attrs = [attr for attr in attrs]
        return Style(fg, bg, attrs)

    def assert_compatible_color(self, color):
        if color == Color():
            return
        (r, g, b) = color.rgb

        # The 256 color space also has the "legacy"
        # original 16 ansi colors. These don't really
        # fit in the other 240 color 'cube'
        if color in ANSI_16_COLOR_PALETTE:
            return

        if r == g and g == b:
            if r in GRAY_MAGNITUDES:
                return
            msg = "color unsupported in this terminal: rgb{clr}".format(
                clr=color.rgb
            )
            raise UnsupportedColorException(msg)

        for color_part in color.rgb:
            if color_part == 0 or color_part in COLOR_MAGNITUDES:
                continue
            msg = "color unsupported in this terminal: rgb{clr}".format(
                clr=color.rgb
            )
            raise UnsupportedColorException(msg)

    def _build_fg_codes(self, fg_color):
        if fg_color is None:
            return []
        if fg_color == Color():
            return [ansicodes.NOCOLOR]
        ansi = self._ansi256_code(fg_color)
        formatted = "38;5;{ansi}".format(ansi=ansi)
        return [formatted]

    def _build_bg_codes(self, bg_color):
        if bg_color is None:
            return []
        if bg_color == Color():
            return [ansicodes.fg_to_bg(ansicodes.NOCOLOR)]
        ansi = self._ansi256_code(bg_color)
        formatted = "48;5;{ansi}".format(ansi=ansi)
        return [formatted]

    def _16color_code(self, color):
        return ORDERED_ANSI_16_COLOR_PALETTE.index(color)

    def _ansi256_code(self, color):
        if color in ANSI_16_COLOR_PALETTE:
            if color == WHITE:
                return 231
            return self._16color_code(color)

        (r, g, b) = color.rgb

        # grayscale
        #
        # We are ignoring the color-cube grays, since they aren't super
        # useful and special casing would be weird.
        if r == g and g == b:
            intensity_ratio = (r - 8) / 247.0
            # 24 different grayscale colors
            return int(round(intensity_ratio * 24)) + 232

        # colors!
        # break back out into a 0-5 intensity
        # then overlay that result over the color cube
        try:
            r_component = COLOR_INTENSITY_MAP[r]
            g_component = COLOR_INTENSITY_MAP[g]
            b_component = COLOR_INTENSITY_MAP[b]
        except KeyError:
            msg = "unexpected color for ANSI256: rgb({r}, {g}, {b})".format(
                r=r, g=g, b=b
            )
            raise UnsupportedColorException(msg)

        return 36 * r_component + 6 * g_component + b_component + 16

    def _rgb_to_color(self, r, g, b):
        if r == g and g == b:
            # Full white/black aren't in the "graybyte" list
            if r > 246:
                return Color(rgb=(255, 255, 255))
            if r < 5:
                return Color(rgb=(0, 0, 0))
            new_c = self._round_graybyte(r)
            return Color(rgb=(new_c, new_c, new_c))
        # Instead of doing a "dumb round" which assumes that the colors are
        # evenly spaced, do a smarter round based on actual outcomes:
        new_r = self._round_colorbyte(r)
        new_g = self._round_colorbyte(g)
        new_b = self._round_colorbyte(b)
        return Color(rgb=(new_r, new_g, new_b))

    def _round_colorbyte(self, colorbyte):
        # This is kind of arbitrary, but we want to split the color space
        # between 0 and 95 a bit unevenly to try to get slightly more
        # true colors out.
        if colorbyte < 32:
            return 0
        return min(COLOR_MAGNITUDES, key=lambda mag: abs(mag - colorbyte))

    def _round_graybyte(self, graybyte):
        return min(GRAY_MAGNITUDES, key=lambda mag: abs(mag - graybyte))

    def test(self):
        def _get_swatch(indices):
            colors = []
            for i in indices:
                colors.append("\033[48;5;{i}m    ".format(i=i))
            colors.append("\033[0m")
            return "".join(colors)

        lines = ["~Lilies~", "Terminal test: ANSI 256 Colors", ""]

        lines.append("Standard 16 Colors:")
        lines.append("    {sw}".format(sw=_get_swatch(range(8))))
        lines.append("    {sw}".format(sw=_get_swatch(range(8, 16))))
        lines.append("")

        lines.append("Color cube:")
        for i_1, i_2 in zip(
            range(16, 200, 36 * 2), range(16 + 36, 200, 36 * 2)
        ):
            for j in range(6):
                start1 = i_1 + j * 6
                start2 = i_2 + j * 6
                swatch1 = _get_swatch(range(start1, start1 + 6))
                swatch2 = _get_swatch(range(start2, start2 + 6))
                lines.append("    ".join(["", swatch1, swatch2]))
            lines.append("")

        lines.append("Grays:")
        swatch1 = _get_swatch(range(232, 232 + 6))
        swatch2 = _get_swatch(range(232 + 12, 232 + 12 + 6))
        lines.append("    ".join(["", swatch1, swatch2]))
        swatch1 = _get_swatch(range(238, 238 + 6))
        swatch2 = _get_swatch(range(238 + 12, 256))
        lines.append("    ".join(["", swatch1, swatch2]))
        lines.append("")

        print("\n".join(lines))
        self.test_attributes()

        print("\n")
