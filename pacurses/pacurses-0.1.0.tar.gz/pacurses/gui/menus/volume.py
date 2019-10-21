from urwid import SimpleFocusListWalker

from pacurses.constants.menu_names import MenuNames
from pacurses.constants.sink_types import SinkTypes
from pacurses.gui.menus.menu import FOCUS_POSITION_INTERNAL, Menu
from pacurses.gui.widgets.volume_slider import VolumeSlider
from pacurses.pulse_audio.information import Information


class VolumeMenu(Menu):
    def __init__(self, width, state, redraw, sink_type=SinkTypes.OUTPUT):
        info = Information()
        sliders = []
        index_positions = {}

        sink_list = (
            info.output_list
            if sink_type == SinkTypes.OUTPUT
            else info.input_list
        )

        for position, sink in enumerate(sink_list):
            slider = VolumeSlider(sink, self.redraw_self, width=width)
            sliders.append(slider)
            index_positions[sink.index] = position

        walker = SimpleFocusListWalker(sliders)

        super(VolumeMenu, self).__init__(
            walker, width, state, redraw, index_positions, sink_type
        )

        self.internal_focus = 0

    @property
    def name(self):
        return MenuNames.VOLUME

    @property
    def header_text(self):
        return f"Adjust {self.sink_type.name.lower()} volumes:"

    @property
    def current_state(self):
        state = super(VolumeMenu, self).current_state
        state[FOCUS_POSITION_INTERNAL] = [
            bar.focus_position for bar in self.body
        ]

        return state

    def load_state(self, state):
        super(VolumeMenu, self).load_state(state)

        try:
            self.body[self.focus_position].set_focus(True)
            #  self.internal_focus = self.focus_position

        except IndexError:
            pass

        if FOCUS_POSITION_INTERNAL in state:
            for index, position in enumerate(state[FOCUS_POSITION_INTERNAL]):
                try:
                    self.body[index].focus_position = position

                except IndexError:
                    pass

    def set_sink_volume(self, sink, value):
        sink.volume = value

    def keypress(self, size, key):
        key = super(VolumeMenu, self).keypress(size, key)

        if key and (key in ("j", "k", "down", "up") or key.isdigit()):
            self.body[self.internal_focus].set_focus(False)
            self.body[self.focus_position].set_focus(True)
            self.internal_focus = self.focus_position

        else:
            return key
