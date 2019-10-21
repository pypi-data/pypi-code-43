from urwid import AttrMap, Button, Columns

from pacurses.constants.palette_names import PaletteNames
from pacurses.gui.widgets.sink_progress_bar import SinkProgressBar

FIXED_BUTTON_WIDTH = 5
DIVIDER_WIDTH = 2


class VolumeSlider(Columns):
    def __init__(self, sink, redraw, width=20):
        self.sink = sink
        self.redraw = redraw
        self.width = width
        self.focused = False

        button_lower = Button("-", self.adjust_volume, -5)
        bar = self.build_bar(False)
        button_higher = Button("+", self.adjust_volume, +5)

        super(VolumeSlider, self).__init__(
            [
                (
                    "fixed",
                    FIXED_BUTTON_WIDTH,
                    AttrMap(
                        button_lower, None, focus_map=PaletteNames.REVERSED
                    ),
                ),
                bar,
                (
                    "fixed",
                    FIXED_BUTTON_WIDTH,
                    AttrMap(
                        button_higher, None, focus_map=PaletteNames.REVERSED
                    ),
                ),
            ],
            dividechars=DIVIDER_WIDTH,
        )

    def build_bar(self, focused):
        normal = (
            PaletteNames.PROGRESS_BAR_NORMAL_FOCUSED
            if focused
            else PaletteNames.PROGRESS_BAR_NORMAL
        )

        complete = (
            PaletteNames.PROGRESS_BAR_COMPLETE_FOCUSED
            if focused
            else PaletteNames.PROGRESS_BAR_COMPLETE
        )

        slider_width = self.width - 2 * FIXED_BUTTON_WIDTH - 2 * DIVIDER_WIDTH

        return SinkProgressBar(
            normal, complete, sink=self.sink, width=slider_width
        )

    def adjust_volume(self, _, value):
        self.sink.volume = self.sink.volume + value
        self.redraw()

    def set_focus(self, value=True):
        self.widget_list[1] = self.build_bar(value)

    def keypress(self, size, key):
        key = super(VolumeSlider, self).keypress(size, key)

        if key == "right" and self.focus_position < 2:
            self.focus_position = 2

        if key == "left" and self.focus_position > 0:
            self.focus_position = 0

        if key == "h":
            self.adjust_volume(None, -5)

        if key == "l":
            self.adjust_volume(None, +5)

        else:
            return key
