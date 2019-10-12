import pathlib
import typing as t

import attr

from .. import core
from .. import schemas


@attr.dataclass(frozen=True)
class Raw:
    data = dict
    inherits: t.FrozenSet[str] = attr.ib(default=frozenset({}))
    metadata_key: str = "raw"
    allow_missing_file: bool = False

    def prep(self, cls):
        return self.data

    def build(self, cls):
        schema = schemas.class_schema(cls)()
        return schema.load(self.prep(cls))

    def set(self, **kw):
        return attr.evolve(self, **kw)
