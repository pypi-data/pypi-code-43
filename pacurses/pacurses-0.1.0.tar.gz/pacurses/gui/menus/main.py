from urwid import AttrMap, Button, SimpleFocusListWalker

from pacurses.constants.menu_names import MenuNames
from pacurses.constants.palette_names import PaletteNames
from pacurses.constants.sink_types import SinkTypes
from pacurses.gui.abbreviation import abbreviate_text
from pacurses.gui.menus.menu import Menu

BUTTON_DECORATION_WIDTH = 2 * 2


class MainMenu(Menu):
    def __init__(self, width, state, redraw, sink_type=None):
        self.redraw = redraw
        self.max_label_width = width - BUTTON_DECORATION_WIDTH

        buttons = []
        buttons.append(
            self.create_menu_button(
                f"Adjust {SinkTypes.OUTPUT.name.lower()}s volumes",
                MenuNames.VOLUME,
                SinkTypes.OUTPUT,
            )
        )

        buttons.append(
            self.create_menu_button(
                f"Adjust {SinkTypes.INPUT.name.lower()}s volumes",
                MenuNames.VOLUME,
                SinkTypes.INPUT,
            )
        )

        buttons.append(
            self.create_menu_button(
                f"Mute {SinkTypes.OUTPUT.name.lower()}s",
                MenuNames.MUTE,
                SinkTypes.OUTPUT,
            )
        )

        buttons.append(
            self.create_menu_button(
                f"Mute {SinkTypes.INPUT.name.lower()}s",
                MenuNames.MUTE,
                SinkTypes.INPUT,
            )
        )

        buttons.append(
            self.create_menu_button(
                f"Set default {SinkTypes.OUTPUT.name.lower()}s",
                MenuNames.DEFAULT,
                SinkTypes.OUTPUT,
            )
        )

        walker = SimpleFocusListWalker(buttons)

        super(MainMenu, self).__init__(walker, width, state, redraw)

    @property
    def name(self):
        return MenuNames.MAIN

    @property
    def header_text(self):
        return "Select:"

    def create_menu_button(self, label, menu_name, sink_type):
        label = abbreviate_text(label, self.max_label_width)
        button = Button(label, self.redraw_wrapper, (menu_name, sink_type))
        decorated_button = AttrMap(
            button, None, focus_map=PaletteNames.REVERSED
        )
        return decorated_button
