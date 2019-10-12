import pathlib
import typing as t

import appdirs
import attr

from .. import core
from .. import schemas


@attr.dataclass(frozen=True)
class AppFile:
    encoder: core.Encoder
    _filename: t.Optional[str] = None
    app_name: t.Optional[str] = None
    _path: t.Optional[pathlib.Path] = attr.ib(
        default=None, converter=attr.converters.optional(pathlib.Path)
    )
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset({"app_name"}))
    metadata_key: str = "appfile"
    allow_missing_file: bool = False

    @property
    def path(self):
        if self._path is not None:
            return pathlib.Path(self._path)
        if self.app_name is None:
            raise TypeError(self.app_name)
        return pathlib.Path(appdirs.user_config_dir(self.app_name)) / self._filename

    def prep(self, cls):
        try:
            return self.encoder.loads(self.path.read_text())
        except FileNotFoundError:
            if self.allow_missing_file:
                return {}
            raise

    def build(self, cls):
        schema = schemas.class_schema(cls)()
        return schema.load(self.prep(cls))

    def set(self, **kw):
        return attr.evolve(self, **kw)
