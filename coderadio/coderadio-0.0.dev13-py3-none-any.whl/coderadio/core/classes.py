from pyradios import RadioBrowser


class Station:
    plug = None

    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def printable(self):
        return f"{self.id:<6} | > {self.name[0:30]:<30} | tags: {self.tags}\n"

    def plugin_name(self):
        return f"plug_{self.id}"

    def show_info(self):
        # msg = f"\n{self.id} | > {self.name}\n\n{self.url}\n"
        msg = f"\n{self.id} | > {self.name}\n\nWebsite: {self.homepage}\n"
        return msg

    def info(self):
        return self.id, self.name, self.url

    def __repr__(self):
        return f"{self.name}"


class Radios:
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

    def get_obj(self, index):
        return self.data[index]


radio_browser = RadioBrowser()

radios = Radios(radio_browser.stations_bytag("bbc"))
