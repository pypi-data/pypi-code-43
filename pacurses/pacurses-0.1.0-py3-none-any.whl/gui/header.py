from urwid import Divider, Pile, Text

from pacurses.constants.palette_names import PaletteNames


class Header(Pile):
    def __init__(self):
        self._text = Text("", align="center")
        divider = Divider()

        super(Header, self).__init__([divider, self._text, divider])

    @property
    def text(self):
        return self._text.get_text()

    @text.setter
    def text(self, text):
        self._text.set_text((PaletteNames.UNDERLINE, text))
