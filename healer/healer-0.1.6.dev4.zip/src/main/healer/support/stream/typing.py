from __future__ import annotations

import collections
import weakref


class OrderedSet(collections.MutableSet):

    def __init__(self, values=()):
        self._od = collections.OrderedDict().fromkeys(values)

    def __len__(self):
        return len(self._od)

    def __iter__(self):
        return iter(self._od)

    def __contains__(self, value):
        return value in self._od

    def add(self, value):
        self._od[value] = None

    def discard(self, value):
        self._od.pop(value, None)


class OrderedWeakrefSet(weakref.WeakSet):

    def __init__(self, entry_set=()):
        super().__init__()
        self.data = OrderedSet()
        for entry in entry_set:
            self.add(entry)
