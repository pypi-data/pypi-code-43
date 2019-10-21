from pacurses.pulse_audio.external import call_pacmd
from pacurses.pulse_audio.sink import Sink


class Output(Sink):
    def __init__(self, index):
        super(Output, self).__init__(index, "sink")

    @property
    def name(self):
        return self.get_info("alsa.card_name = ", '"')

    @property
    def default(self):
        return self.get_info("index: ", " ", 1) == "*"

    @default.setter
    def default(self, value):
        if value:
            call_pacmd(f"set-default-sink {self.index}")
