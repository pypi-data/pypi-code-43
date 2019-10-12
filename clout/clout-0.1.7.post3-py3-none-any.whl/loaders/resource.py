import pathlib
import types
import typing as t

import appdirs
import attr
import importlib_resources

from .. import core
from .. import schemas


@attr.dataclass(frozen=True)
class Resource:
    encoder: core.Encoder
    package: types.ModuleType
    filename: str
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset({"package"}))
    metadata_key: str = "resource"
    allow_missing_file: bool = False

    def prep(self, cls):
        try:
            text = importlib_resources.read_text(self.package, self.filename)
        except FileNotFoundError:
            if self.allow_missing_file:
                return {}
            raise
        return self.encoder.loads(text)

    def build(self, cls):
        schema = schemas.class_schema(cls)()
        return schema.load(self.prep(cls))

    def set(self, **kw):
        return attr.evolve(self, **kw)
