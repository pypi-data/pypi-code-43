from urwid import ListBox

from pacurses.constants.menu_names import MenuNames
from pacurses.constants.state_keys import StateKeys

FOCUS_POSITION = "focus_position"
FOCUS_POSITION_INTERNAL = "focus_position_internal"


class Menu(ListBox):
    def __init__(
        self, body, width, state, redraw, index_positions={}, sink_type=None
    ):
        self.width = width
        self.redraw = redraw
        self.index_positions = index_positions
        self.sink_type = sink_type
        self.last_digit = ""

        super(Menu, self).__init__(body)

        self.load_state(state)

    @property
    def name(self):
        return MenuNames.MAIN

    @property
    def header_text(self):
        return ""

    @property
    def current_state(self):
        position = 0

        try:
            position = self.focus_position

        except IndexError:
            pass

        state = MenuState({StateKeys.FOCUS_POSITION: position})

        if self.sink_type:
            state[StateKeys.SINK_TYPE] = self.sink_type

        return state

    def load_state(self, state):
        if not isinstance(state, MenuState):
            raise ValueError(
                "Unknown state object type {0}. Can only load {1}!".format(
                    type(state).__name__, MenuState.__name__
                )
            )

        try:
            self.set_focus(state[StateKeys.FOCUS_POSITION])

        except IndexError:
            pass

        if StateKeys.SINK_TYPE in state:
            self.sink_type = state[StateKeys.SINK_TYPE]

    def goto_index_position(self, index):
        if index in self.index_positions:
            try:
                self.focus_position = self.index_positions[index]

            except IndexError:
                pass

    def redraw_wrapper(self, _, data):
        menu_name, sink_type = data
        self.redraw(menu_name, sink_type)

    def redraw_self(self):
        self.redraw(self.name, self.sink_type)

    def keypress(self, size, key):
        copy = key if key in ("down", "up") else None
        key = super(Menu, self).keypress(size, key)
        key = copy if copy else key

        if key and key in "jk":
            step = 1 if key == "j" else -1

            try:
                self.focus_position = self.focus_position + step

            except IndexError:
                pass

        if key and key.isdigit():
            self.goto_index_position(key)
            self.goto_index_position(self.last_digit + key)
            self.last_digit = key

        return key


class MenuState(dict):
    def __init__(self, values={}):
        if StateKeys.FOCUS_POSITION not in values:
            raise Exception(
                "Menu state requires at least the {0} value!".format(
                    StateKeys.FOCUS_POSITION
                )
            )

        super(MenuState, self).__init__(values)
