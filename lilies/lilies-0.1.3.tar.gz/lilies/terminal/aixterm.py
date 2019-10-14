from builtins import super

from ..style import Color, Style
from . import ansi16, ansicodes


AIX_COLOR_CODES = {
    ansi16.DARKGRAY: [ansicodes.DARKGRAY],
    ansi16.RED: [ansicodes.BRIGHTRED],
    ansi16.LIME: [ansicodes.BRIGHTGREEN],
    ansi16.YELLOW: [ansicodes.BRIGHTYELLOW],
    ansi16.BLUE: [ansicodes.BRIGHTBLUE],
    ansi16.MAGENTA: [ansicodes.MAGENTA],
    ansi16.CYAN: [ansicodes.BRIGHTCYAN],
    ansi16.WHITE: [ansicodes.WHITE],
}


class AixTerminal(ansi16.Ansi16Terminal):
    def __init__(self):
        super().__init__()
        self.fg_colormap.update(AIX_COLOR_CODES)
        for key in AIX_COLOR_CODES:
            fgcodes = AIX_COLOR_CODES[key]
            bgcodes = [ansicodes.fg_to_bg(code) for code in fgcodes]
            self.bg_colormap[key] = bgcodes

    def configure_style(self, style):
        if style.fg.isreset():
            fg = Color()
        else:
            fg = self._hsl_to_16color(*style.fg.hsl)
        if style.bg.isreset():
            bg = Color()
        else:
            bg = self._hsl_to_16color(*style.bg.hsl)

        def issupported(style):
            return style in self.supported_attrs

        attrs = filter(issupported, style.attrs)
        return Style(fg, bg, attrs)

    def assert_compatible_stylediff(self, style_diff):
        if style_diff.fg is not None:
            self.assert_compatible_color(style_diff.fg)
        if style_diff.bg is not None:
            self.assert_compatible_color(style_diff.bg)
        self.assert_compatible_attrs(style_diff.attrs.keys())

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

        text_rows = ["~Lilies~", "Terminal test: ANSI 8 Colors, Extended", ""]
        text_rows.append("Color table:")
        color_rows = map(lambda rowlist: "".join(rowlist), swatches)

        print("\n".join(text_rows + list(color_rows)))
        self.test_attributes()
        print("\n")
