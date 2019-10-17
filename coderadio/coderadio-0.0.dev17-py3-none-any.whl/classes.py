import importlib

from coderadio.log import logger


def load_plugin(path_to_plugin):
    try:
        plug = importlib.import_module(path_to_plugin)
        return plug
    except ImportError as exc:
        logger.exception("Import Error: ")


class Station:
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._state = " "

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, s):
        self._state = s

    def printable(self):
        return "{:<6} | {} {:<30} | tags: {}\n".format(
            self.id, self.state, self.name[0:30], self.tags
        )

    def plugin_name(self):
        return "plug_{}".format(self.id)

    def path_to_plugin(self):
        path = "coderadio.plugins." + self.plugin_name()
        return load_plugin(path)

    def show_info(self):
        msg = "\n{} | {} {}\n\nWebsite: {}\n".format(
            self.id, self.state, self.name, self.homepage
        )
        return msg

    def plugin(self):
        # TODO
        pass

    def __repr__(self):
        return "Station(name: {})".format(self.name)


class StationList:
    def __init__(self, data):
        self._data = [Station(**obj) for obj in data]
        self._content = "".join(line.printable() for line in self.data)

    @property
    def content(self):
        return self._content.rstrip()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, other):
        self._data = [Station(**obj) for obj in other]
        self._content = "".join(line.printable() for line in self._data)

    def get_station(self, index):
        return self.data[index]
