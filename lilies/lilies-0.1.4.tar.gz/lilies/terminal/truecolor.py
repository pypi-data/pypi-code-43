from __future__ import print_function
from builtins import int, super

from ..style import Color, Style
from ..style.colors import hsl_to_rgb
from .exceptions import UnsupportedColorException
from .ansi8 import Ansi8Terminal
from .attr_mixin import AnsiAttributesMixin
from . import ansicodes


class TrueColorTerminal(Ansi8Terminal, AnsiAttributesMixin):
    """
    An ANSI-sequence based truecolor terminal
    """

    def __init__(self):
        super().__init__()
        self.supported_attrs = ["bold", "dim", "underline", "blink"]

    def configure_style(self, style):
        def issupported(style):
            return style in self.supported_attrs

        attrs = [attr for attr in style.attrs if issupported(attr)]
        return Style(style.fg, style.bg, attrs)

    def assert_compatible_color(self, color):
        if color == Color():
            return
        for val in color.rgb:
            if not isinstance(val, int):
                msg = "color must have integer rgb values: rgb{clr}".format(
                    clr=color.rgb
                )
                raise UnsupportedColorException(msg)

    def _build_fg_codes(self, fg_color):
        if fg_color is None:
            return []
        if fg_color == Color():
            return [ansicodes.NOCOLOR]
        (r, g, b) = fg_color.rgb
        formatted = "38;2;{r};{g};{b}".format(r=r, g=g, b=b)
        return [formatted]

    def _build_bg_codes(self, bg_color):
        if bg_color is None:
            return []
        if bg_color == Color():
            return [ansicodes.fg_to_bg(ansicodes.NOCOLOR)]
        (r, g, b) = bg_color.rgb
        formatted = "48;2;{r};{g};{b}".format(r=r, g=g, b=b)
        return [formatted]

    def test(self):
        def _color_cell(h, s, l):
            r, g, b = hsl_to_rgb(h, s, l)
            return "\033[48;2;{r};{g};{b}m ".format(r=r, g=g, b=b)

        width = 75
        height = 24
        rows = ["~Lilies~", "Terminal test: ANSI True Color", ""]
        rows.append("Colors sample:")
        for y in range(height):
            lightness = float(height - y) / float(height) * 100
            row = []
            for x in range(width):
                hue = float(x) / float(width) * 360
                row.append(_color_cell(hue, 100, lightness))
            rows.append("".join(row) + "\033[0m")
        rows.append("")
        rows.append("Grayscale sample:")
        rows.append(
            "".join(
                [
                    _color_cell(0, 0, float(x) / float(width) * 50)
                    for x in range(width)
                ]
            )
            + "\033[0m"
        )
        rows.append(
            "".join(
                [
                    _color_cell(0, 0, 100 - float(x) / float(width) * 50)
                    for x in range(width)
                ]
            )
            + "\033[0m"
        )
        rows.append("")
        print("\n".join(rows))
        self.test_attributes()
