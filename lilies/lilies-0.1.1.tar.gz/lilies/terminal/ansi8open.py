from builtins import super

from ..style import Style
from .ansi8 import Ansi8Terminal
from .attr_mixin import AnsiAttributesMixin


class Ansi8OpenTerminal(Ansi8Terminal, AnsiAttributesMixin):
    def __init__(self):
        super().__init__()
        self.supported_attrs = ["bold", "dim", "underline"]

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
