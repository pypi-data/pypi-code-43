from pacurses.pulse_audio.sink import Sink


class Input(Sink):
    def __init__(self, index):
        super(Input, self).__init__(index, "sink-input")

    @property
    def name(self):
        application = self.get_info("application.name = ", '"')
        media = self.get_info("media.name =", '"')
        return f"{application}: {media}"

    @property
    def mapped_output_index(self):
        return self.get_info("sink: ", " ")
