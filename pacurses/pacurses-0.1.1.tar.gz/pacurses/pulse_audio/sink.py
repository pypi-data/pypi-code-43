from pacurses.pulse_audio.external import call_pacmd


class Sink:
    def __init__(self, index, type):
        self.index = index
        self.type = type

        self.step = 65536 / 100
        self.base = int(self.get_info("^\\s\\+volume: ", column=3))

    @property
    def name(self):
        raise NotImplementedError()

    @property
    def volume(self):
        return int(self.base / self.step)

    @volume.setter
    def volume(self, value):
        new_base = int(value * self.step)
        call_pacmd(f"set-{self.type}-volume {self.index} {new_base}")

    @property
    def muted(self):
        return self.get_info("muted", ": ") == "yes"

    @muted.setter
    def muted(self, value):
        call_pacmd(f"set-{self.type}-mute {self.index} {value}")

    @property
    def default(self):
        raise NotImplementedError()

    @default.setter
    def default(self, value):
        raise NotImplementedError()

    def get_info(self, filter, split=" ", column=2):
        command = f"list-{self.type}s"
        command += f"| grep -A 38 'index: {self.index}'"
        command += f"| grep '{filter}'"
        command += f"| awk -F '{split}' " + "'{print $" + str(column) + "}'"

        information = call_pacmd(command)

        return information.splitlines()[0] if information else information
