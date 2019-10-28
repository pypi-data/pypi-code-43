# Created: 10/12/2019
# Author:  Emiliano Jordan,
# Project: settings
from collections import defaultdict


class Sejings:

    def __new__(cls, value=None, old_class=...):
        return super().__new__(object_class_mapping[type(value)])

    def __init__(self, value=None, old_class=...):
        super().__setattr__('_val', value)

        if old_class is ...:
            return

        generator = ((key, val)
                     for key, val
                     in old_class.__dict__.items()
                     if key != '_val')

        for key, val in generator:
            super().__setattr__(key, val)

    def __call__(self, value=...):

        if value is ...:
            return self._val

        super().__setattr__('_val', value)

    def __getattr__(self, item):
        # print('Hit __getattr__', item, getattr(self(), item), callable(getattr(self(), item)))
        setattr(self, item, Sejings())
        return super().__getattribute__(item)

    def __setattr__(self, key, value):

        if key == '_val':
            super().__setattr__(key, value)
            return

        if isinstance(value, Sejings):
            super().__setattr__(key, value)
            return

        try:
            stale = super().__getattribute__(key)
        except AttributeError:
            super().__setattr__(key, Sejings(value))
            return

        stale_type = object_class_mapping[type(stale())]
        value_type = object_class_mapping[type(value)]

        if stale_type is value_type:
            stale(value)
            return

        super().__setattr__(key, Sejings(value, stale))


class SejingsNumber(Sejings):
    def __add__(self, other):
        return self() + other

    def __iadd__(self, other):
        self(self() + other)

    def __radd__(self, other):
        return self() + other

    def __sub__(self, other):
        return self() - other

    def __isub__(self, other):
        self(self() - other)

    def __rsub__(self, other):
        return other - self()

    def __mul__(self, other):
        return self() * other

    def __imul__(self, other):
        self(self() * other)

    def __rmul__(self, other):
        return self() * other

    def __truediv__(self, other):
        return self() / other

    def __itruediv__(self, other):
        self(self() / other)

    def __rtruediv__(self, other):
        return other / self()

    def __pow__(self, power, modulo=None):
        return pow(self(), power, modulo)

    def __ipow__(self, other):
        self(self() ** other)

    def __rpow__(self, other):
        return other ** self()

    def __neg__(self):
        return -self()

    def __pos__(self):
        return +self()

    def __abs__(self):
        return abs(self())

    def __invert__(self):
        return ~self()

    def __int__(self):
        return int(self._va)


object_class_mapping = defaultdict(lambda: Sejings)
object_class_mapping[int] = SejingsNumber
object_class_mapping[float] = SejingsNumber

sejings = Sejings()
