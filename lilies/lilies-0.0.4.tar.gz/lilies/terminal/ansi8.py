from .nocolor import NoColorTerminal
from . import ansicodes
from .exceptions import UnsupportedColorException
from ..style import Color, Style
from ..style.palette import get_color

BLACK = get_color("black")
RED = get_color("maroon")
GREEN = get_color("green")
YELLOW = get_color("olive")
BLUE = get_color("navy")
PURPLE = get_color("purple")
CYAN = get_color("teal")
GRAY = get_color("silver")


class Ansi8Terminal(NoColorTerminal):
    """
    An 8-color ansi terminal
    """

    def __init__(self):
        self.supported_colors = [
            Color(),
            BLACK,
            RED,
            GREEN,
            YELLOW,
            BLUE,
            PURPLE,
            CYAN,
            GRAY,
        ]
        self.supported_attrs = []
        self.fg_colormap = {
            None: [],
            Color(): [ansicodes.NOCOLOR],
            BLACK: [ansicodes.BLACK],
            RED: [ansicodes.RED],
            GREEN: [ansicodes.GREEN],
            YELLOW: [ansicodes.YELLOW],
            BLUE: [ansicodes.BLUE],
            PURPLE: [ansicodes.MAGENTA],
            CYAN: [ansicodes.CYAN],
            GRAY: [ansicodes.LIGHTGRAY],
        }
        self.bg_colormap = {}
        for key in self.fg_colormap:
            val = self.fg_colormap[key]
            bgcodes = map(ansicodes.fg_to_bg, val)
            self.bg_colormap[key] = bgcodes

    def configure_style(self, style):
        """
        Configure the style for this terminal
        """
        if style.fg.isreset():
            fg = Color()
        else:
            fg = self._hsl_to_8color(*style.fg.hsl)
        if style.bg.isreset():
            bg = Color()
        else:
            bg = self._hsl_to_8color(*style.bg.hsl)

        def issupported(style):
            return style in self.supported_attrs

        attrs = filter(issupported, style.attrs)
        return Style(fg, bg, attrs)

    def _build_fg_codes(self, fg_color):
        ansi = self.fg_colormap.get(fg_color)
        if ansi is None:
            raise UnsupportedColorException()
        return ansi

    def _build_bg_codes(self, bg_color):
        return map(ansicodes.fg_to_bg, self._build_fg_codes(bg_color))

    def _build_attr_codes(self, attrs):
        return []

    def _hsl_to_8color(self, h, s, l):
        # grayscale, low saturation
        if s < 10:
            return BLACK if l < 20 else GRAY

        # higher saturation, go by hue
        if h < 30 or h > 345:
            return RED
        if h < 65:
            return YELLOW
        if h < 145:
            return GREEN
        if h < 215:
            return CYAN
        if h < 260:
            return BLUE
        return PURPLE

    def _build_reset_sequence(self):
        return [ansicodes.esc(0)]

    def test(self):
        # remove the first "No color" color
        colors = self.supported_colors[1:]
        swatches = [
            ["" for x in range(len(colors))] for y in range(len(colors))
        ]

        for i in range(len(colors)):
            for j in range(len(colors)):
                style = Style(fg=colors[i], bg=colors[j])
                diff = style.diff(Style())
                reset_diff = Style().diff(style)
                color = self.encode_sequence(diff)
                reset = self.encode_sequence(reset_diff)
                swatches[i][j] = "{clr} A {reset}".format(
                    clr=color, reset=reset
                )

        text_rows = ["~Lilies~", "Terminal test: ANSI 8 Colors", ""]
        text_rows.append("Color table:")
        color_rows = map(lambda rowlist: "".join(rowlist), swatches)

        print("\n".join(text_rows + list(color_rows)))
