from urwid import CheckBox, SimpleFocusListWalker

from pacurses.constants.menu_names import MenuNames
from pacurses.constants.sink_types import SinkTypes
from pacurses.gui.abbreviation import abbreviate_sink
from pacurses.gui.menus.menu import Menu
from pacurses.pulse_audio.information import Information

CHECKBOX_WIDTH = 4


class MuteMenu(Menu):
    def __init__(self, width, state, redraw, sink_type=SinkTypes.OUTPUT):
        info = Information()
        length = width - CHECKBOX_WIDTH - 2
        checkboxes = []
        index_positions = {}

        sink_list = (
            info.output_list
            if sink_type == SinkTypes.OUTPUT
            else info.input_list
        )

        for position, sink in enumerate(sink_list):
            name = abbreviate_sink(sink, sink_type, length)
            checkbox = CheckBox(
                name,
                state=sink.muted,
                on_state_change=self.mute_sink,
                user_data=sink,
            )

            checkboxes.append(checkbox)
            index_positions[sink.index] = position

        walker = SimpleFocusListWalker(checkboxes)

        super(MuteMenu, self).__init__(
            walker, width, state, redraw, index_positions, sink_type
        )

    @property
    def name(self):
        return MenuNames.MUTE

    @property
    def header_text(self):
        return f"(Un)Check an {self.sink_type.name.lower()} to (un)mute:"

    def mute_sink(self, _, value, sink):
        sink.muted = value
        self.redraw_self()
