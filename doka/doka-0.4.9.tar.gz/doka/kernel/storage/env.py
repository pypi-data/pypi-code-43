from doka.kernel.definition.entities import ProjectEntity, UnitEntity
from doka.config import doka_config


class EnvStorage:
    _filename = None

    def read(self) -> dict:
        result = {}
        with open(self._filename, 'rt') as f:
            for line in f:
                line = line.strip()
                if len(line) > 0 and '=' in line:
                    key, value = line.split("=")
                    key = key.strip()
                    value = value.strip()
                    result[key] = value
        return result or None

    def save(self, data: dict):
        with open(self._filename, 'wt') as f:
            for key, value in data.items():
                f.write("{}={}\n".format(key, value))
        return True


class StacksEnvStorage(EnvStorage):
    def __init__(self, unit: UnitEntity):
        self._filename = doka_config.STORAGE_DIR.joinpath(
            *["projects", unit.project_name, "stacks", ".{}.env".format(unit.name)]
        )


class ProjectEnvStorage(EnvStorage):
    def __init__(self, project: ProjectEntity):
        self._filename = project.metadir.joinpath(*["environments", ".env.{}".format(project.env)])


class UnitEnvStorage(EnvStorage):
    def __init__(self, unit: UnitEntity):
        self._filename = unit.codedir.joinpath(".env.example")
