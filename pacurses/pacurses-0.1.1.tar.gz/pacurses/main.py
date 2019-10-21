from urwid import (
    Divider,
    ExitMainLoop,
    Frame,
    LineBox,
    MainLoop,
    Overlay,
    Padding,
    SolidFill,
)

from pacurses.constants.button_names import ButtonNames
from pacurses.constants.menu_names import MenuNames
from pacurses.constants.palette_names import PaletteNames
from pacurses.constants.state_keys import StateKeys
from pacurses.gui.footer import Footer
from pacurses.gui.header import Header
from pacurses.gui.menus.menu import Menu, MenuState
from pacurses.gui.menus.utils import get_menu
from pacurses.gui.palette import palette

PADDING_WIDTH = 2
UPDATE_CYCLE_PERIODE = 2


class App:
    def __init__(self, dimensions):
        self._dimenstions = dimensions
        self.states = {}
        self.last_menu_name = None

        self.header = Header()
        self.menu = Divider()
        self.footer = Divider()
        self.frame = Frame(self.menu, header=self.header, footer=self.footer)

        self.switch_menu(MenuNames.MAIN)

    @property
    def width(self):
        return self._dimenstions[0]

    @property
    def height(self):
        return self._dimenstions[1]

    @property
    def inner_width(self):
        return self.width - 2 * PADDING_WIDTH - 2

    def switch_menu(self, menu_name, sink_type=None):
        menu_name = (
            self.last_menu_name
            if isinstance(self.menu, Menu)
            and self.menu.name == MenuNames.HELP
            and self.last_menu_name
            else menu_name
        )

        self.last_menu_name = (
            self.menu.name if menu_name == MenuNames.HELP else None
        )

        if menu_name not in MenuNames:
            raise ValueError("Unkown menu '{0}'!".format(menu_name))

        if isinstance(self.menu, Menu):
            self.states[self.menu.name] = self.menu.current_state

        state = (
            self.states[menu_name]
            if menu_name in self.states
            else MenuState({StateKeys.FOCUS_POSITION: 0})
        )

        if StateKeys.SINK_TYPE in state and sink_type:
            del state[StateKeys.SINK_TYPE]

        self.menu = get_menu(menu_name)(
            self.inner_width, state, self.switch_menu, sink_type=sink_type
        )
        self.header.text = self.menu.header_text
        self.frame.body = self.menu

        self.frame.focus_position = "body"
        self.update_footer()

    def update_footer(self):
        button_list = [ButtonNames.CLOSE]
        button_list.extend(
            [ButtonNames.BACK] if self.menu.name != MenuNames.MAIN else []
        )
        button_list.extend(
            [ButtonNames.HELP] if self.menu.name != MenuNames.HELP else []
        )

        button_list.extend([ButtonNames.CLOSE])
        self.footer = Footer(self.inner_width, button_list, self.switch_menu)
        self.frame.footer = self.footer

    def global_input(self, key):
        if key == "q":
            if self.menu.name == MenuNames.MAIN:
                self.header.text = (
                    PaletteNames.WARNING,
                    "Press 'Q' to close the application!",
                )

            else:
                self.switch_menu(MenuNames.MAIN)

        if key == "Q":
            raise ExitMainLoop()

        if key == "H":
            self.switch_menu(MenuNames.HELP)

        if key == "tab":
            if self.frame.focus_position == "body":
                self.frame.focus_position = "footer"

            else:
                last_index = len(self.footer.button_list.cells) - 1
                position = self.footer.button_list.focus_position

                if position == last_index:
                    self.frame.focus_position = "body"
                    self.footer.button_list.focus_position = 0

                else:
                    self.footer.button_list.focus_position = position + 1

    def update_cycle(self, loop=None, user_data=None):
        self.switch_menu(self.menu.name, self.menu.sink_type)
        loop.set_alarm_in(UPDATE_CYCLE_PERIODE, self.update_cycle)

    def start(self):
        padding = Padding(
            self.frame,
            left=PADDING_WIDTH,
            right=PADDING_WIDTH,
            width=self.inner_width,
            min_width=self.inner_width,
        )

        box = LineBox(padding, title="pacurses")

        overlay = Overlay(
            box,
            SolidFill(" "),
            align="center",
            width=self.width,
            valign="middle",
            height=self.height,
        )

        loop = MainLoop(
            overlay, palette=palette, unhandled_input=self.global_input
        )
        self.update_cycle(loop)
        loop.run()


def main():
    App((48, 30)).start()
