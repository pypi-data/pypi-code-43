import importlib

from coderadio.log import logger


def load_plugin(path_to_plugin):
    try:
        plug = importlib.import_module(path_to_plugin)
        return plug
    except ImportError as exc:
        logger.debug(exc)


class Station:
    plug = None

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
        return f"{self.id:<6} | {self.state} {self.name[0:30]:<30} | tags: {self.tags}\n"

    def plugin_name(self):
        return f"plug_{self.id}"

    def path_to_plugin(self):
        path = "coderadio.plugins." + self.plugin_name()
        return load_plugin(path)

    def show_info(self):
        # msg = f"\n{self.id} | > {self.name}\n\n{self.url}\n"
        msg = f"\n{self.id} | {self.state} {self.name}\n\nWebsite: {self.homepage}\n"
        return msg

    def __repr__(self):
        return f"Station(name: {self.name})"


class StationList:
    def __init__(self, data):
        self._data = [Station(**obj) for obj in data]
        self._content = "".join(line.printable() for line in self.data)

    @property
    def content(self):
        return self._content

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, other):
        self._data = [Station(**obj) for obj in other]
        self._content = "".join(line.printable() for line in self._data)

    def get_station(self, index):
        return self.data[index]
