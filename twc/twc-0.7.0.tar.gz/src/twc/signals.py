# Copyright (C) 2019 Michał Góral.
#
# This file is part of TWC
#
# TWC is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TWC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with TWC. If not, see <http://www.gnu.org/licenses/>.

import weakref
import inspect


class StrongRefDead(Exception):
    pass


class signal:
    def __init__(self, name):
        self._observers = []
        self._observer_names = {}
        self._name = name

    def connect(self, slot, **kwargs):
        '''Connects a given object as signal's slot (observer). Object must be
        callable. It will receive emitted arguments and keywords and
        additionally, keywords passed to connect(). This is usually sufficent to
        not use lambdas and partials for callables which need some additional
        data. Keep in mind that slot's additional data should be at the end of
        signal's signature.

        Note that internally slot and keywords are stored as weakrefs. This
        means that slot is automatically disconnected when it's deleted.
        Keywords which are deleted are simply not used when slot is called.'''
        ref = _weak_partial(slot, **kwargs)

        if ref not in self._observers:
            self._observers.append(ref)

    def disconnect(self, slot):
        try:
            self._observers.remove(slot)
        except ValueError:
            pass

    def emit(self, *args, **kwargs):
        missing = []

        for i, ref in enumerate(self._observers):
            try:
                ref(*args, **kwargs)
            except StrongRefDead:
                missing.append(i)

        for i in reversed(missing):
            del self._observers[i]

    def clear(self):
        self._observers.clear()


class _weak_partial:
    def __init__(self, obj, **kwargs):
        self._ref = self._make(obj)
        self._kwargs_weak = weakref.WeakValueDictionary()
        self._kwargs_strong = {}

        for k in kwargs:
            try:
                self._kwargs_weak[k] = kwargs[k]
            except TypeError:
                self._kwargs_strong[k] = kwargs[k]

    def __call__(self, *args, **kwargs):
        obj = self._ref()
        if not obj:
            raise StrongRefDead()
        obj(*args, **kwargs, **self._kwargs_weak, **self._kwargs_strong)

    def _make(self, obj):
        if inspect.ismethod(obj):
            return weakref.WeakMethod(obj)
        return weakref.ref(obj)

    def __eq__(self, other):
        if isinstance(other, _weak_partial):
            return self._ref == other._ref  # pylint: disable=protected-access
        return self._ref() == other
