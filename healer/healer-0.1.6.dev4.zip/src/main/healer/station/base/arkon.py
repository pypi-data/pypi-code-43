"""
"""

from __future__ import annotations


class WireDict:

    def __str__(self):
        return f"{self.__class__.__name__}({self.into_wire()})"

    def __eq__(self, that):
        if isinstance(that, self.__class__):
            return self.__dict__ == that.__dict__
        else:
            return False

    def into_wire(self) -> str:
        return f"{self.__dict__}"

    @classmethod
    def from_wire(cls, wire:str) -> object:
        bean = cls()
        bean.__dict__ = eval(wire)
        return bean


class DataBean(WireDict):
    one:str = None
    two:str = None
    count:float = None

    def __init__(self, one:str=None, two:str=None, count:float=0):
        self.one = one
        self.two = two
        self.count = count
