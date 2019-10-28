import sys
from importlib import import_module
from dataclasses import MISSING
from typing import Sequence, Union

from . import dataclass, field
from rx.operators import map as rxmap


def getter(*path, obj=MISSING):
    def _getter(obj=obj):
        assert obj is not MISSING
        for attr in path:
            obj = getattr(obj, attr)
        return obj
    return _getter


def setter(*path, obj=MISSING):
    assert len(path)
    def _setter(obj=obj, value=MISSING):
        assert obj is not MISSING
        for attr in path[:-1]:
            obj = getattr(attr)
        return setattr(obj, path[-1], value)
    return _setter

def deleter(*path, obj=MISSING):
    assert len(path)
    def _deleter(obj=obj, value=MISSING):
        assert obj is not MISSING
        for attr in path[:-1]:
            obj = getattr(attr)
        return delattr(obj, path[-1])
    return _deleter

@dataclass
class path:
    module: str = field(default=None)
    attribute: Sequence[str] = field(default=None, evolves=rxmap(lambda attr: attr.split('.') if isinstance(attr, str) else attr))
    package: Union[None, str] = field(default=None)
    importable: bool = field(default=True)


    def get_module(self):
        if not self.importable or self.module in sys.modules:
            module = sys.modules[self.module]
        else:
            module = import_module(self.module, package=self.package)
        return module

    def get(self):
        return getter(*self.attribute)(self.get_module())

    def set(self, value):
        assert self.attribute, f'No attribute path supplied for {self}. Will not assign value to module'
        return setter(*self.attribute)(self.get_module(), value)

    def delete(self):
        assert self.attribute, f'No attribute path supplied for {self}. Unable to delete module object'
        return deleter(*self.attribute)(self.get_module())

    @property
    def name(self):
        return f'{self.module}:{".".join(self.attribute)}'

    @classmethod
    def fromstring(cls, path: str):
        splitter = ':' if ':' in path else '.'
        return  cls(*path.rsplit(splitter, 1))
