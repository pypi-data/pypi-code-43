from urwid import RadioButton, SimpleFocusListWalker

from pacurses.constants.menu_names import MenuNames
from pacurses.constants.sink_types import SinkTypes
from pacurses.gui.abbreviation import abbreviate_sink
from pacurses.gui.menus.menu import Menu
from pacurses.pulse_audio.information import Information

RADIO_BUTTON_WIDTH = 4


class DefaultMenu(Menu):
    def __init__(self, width, state, redraw, sink_type=SinkTypes.OUTPUT):
        info = Information()
        length = width - RADIO_BUTTON_WIDTH - 2
        radio_buttons = []
        group = []

        sink_list = (
            info.output_list
            if sink_type == SinkTypes.OUTPUT
            else info.input_list
        )

        for sink in sink_list:
            name = abbreviate_sink(sink, sink_type, length)
            radio_button = RadioButton(
                group,
                name,
                state=sink.default,
                on_state_change=self.set_default_sink,
                user_data=sink,
            )

            radio_buttons.append(radio_button)

        walker = SimpleFocusListWalker(radio_buttons)

        super(DefaultMenu, self).__init__(
            walker, width, state, redraw, sink_type
        )

    @property
    def name(self):
        return MenuNames.DEFAULT

    @property
    def header_text(self):
        return f"Select the default {self.sink_type.name.lower()}:"

    def set_default_sink(self, _, value, sink):
        sink.default = value
        self.redraw_self()
