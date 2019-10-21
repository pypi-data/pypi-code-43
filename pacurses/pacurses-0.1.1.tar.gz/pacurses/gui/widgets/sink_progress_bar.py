from urwid import ProgressBar

from pacurses.gui.abbreviation import abbreviate_sink
from pacurses.pulse_audio.utils import get_sink_type


class SinkProgressBar(ProgressBar):
    def __init__(self, normal, complete, sink, width=20):
        self.sink = sink
        self.width = width

        maximum_volume = (int(sink.volume / 100) + 1) * 100
        super(SinkProgressBar, self).__init__(
            normal, complete, sink.volume, maximum_volume
        )

    def get_text(self):
        sink_type = get_sink_type(self.sink)
        return abbreviate_sink(self.sink, sink_type, self.width, stretch=True)
