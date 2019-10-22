import json
from pathlib import Path

class Database():
    def __init__(self, path=None):
        self._dict = {}
        if(path):
            self.path = path
        else:
            self.path = str(Path.home()) + "/db.ynit"
        self.read()

    def read(self):
        try:
            with open(self.path, "r") as f:
                self._dict = json.load(f)
        except(FileNotFoundError):
            with open(self.path, "w+") as f:
                f.write("{}")

    def write(self):
        with open(self.path, "w+") as f:
            f.write(json.dumps(self._dict))

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value
        self.write()
