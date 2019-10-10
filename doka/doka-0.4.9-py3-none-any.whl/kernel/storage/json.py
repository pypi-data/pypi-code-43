import json
from doka.config import doka_config
from doka.kernel.definition.entities import ProjectEntity


class JsonStorage:
    _data = None
    _filename = None

    def read(self):
        if self._data is None:
            try:
                with open(self._filename, 'rt') as f:
                    self._data = json.load(f)
            except:
                return None
        return self._data

    def write(self, data: dict, filename=None):
        try:
            filename = filename or self._filename
            with open(filename, 'wt') as f:
                json.dump(data, f, indent=2)
            self._data = data
            return True
        except Exception as e:
            return False


class ProjectStorage(JsonStorage):
    _filename = doka_config.STORAGE_DIR.joinpath("projects.json")


class UnitStorage(JsonStorage):
    def __init__(self, project: ProjectEntity):
        self._filename = project.metadir.joinpath("units.json")


class StackStorage(JsonStorage):
    def __init__(self, project: ProjectEntity):
        self._filename = project.metadir.joinpath("stacks.json")
