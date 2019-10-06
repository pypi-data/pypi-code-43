from __future__ import annotations

import functools
import inspect

from copy import copy
from dataclasses import dataclass, field
from typing import Tuple, Callable, Optional

from mnectar.util.signal import BoundSignal
from mnectar.config import Setting
from mnectar.util import classproperty


class Actionable:
    app = None

    @property
    def actionables(self):
        # Look up actions via the class (not instance) to avoid infinite recursion
        return {
            key: getattr(self, key)
            for key, unbound in inspect.getmembers(
                type(self), lambda _: isinstance(_, Action)
            )
        }

    def __init__(self, *arg, app=None, **kw):
        self.app = self.app or app
        super().__init__(*arg, **kw)

        if self.app:
            if not hasattr(self.app, '_actionable_instances'):
                self.app._actionable_instances = []
            self.app._actionable_instances.append(self)


@dataclass
class Action:
    # fmt: off
    menu:             str
    group:            str                   = ""
    name:             str                   = ""
    shortcut_default: str                   = ""
    checkable:        bool                  = False
    exclusive:        bool                  = False
    setting:          Optional[Setting]     = None
    signal:           Optional[BoundSignal] = None
    args:             Tuple                 = field(default_factory = tuple)
    _instance:        Actionable            = field(default = None, init = False)
    _name:            str                   = field(default = "",   init = False)
    _triggered_cb:    Callable              = field(default = None, init = False)
    _shortcut_cb:     Callable              = field(default = None, init = False)
    # fmt: on

    shortcut_overrides = Setting()

    def __post_init__(self):
        self._instance = None

        if self.setting and self.signal:
            raise ValueError("An action cannot specify both a setting and a signal!")

    def __set_name__(self, owner, name):
        self._name = name

    @property
    def _shortcut_key(self):
        return (self.menu, self.group, self.name)

    @property
    def shortcut(self):
        if self.shortcut_overrides is None:
            self.shortcut_overrides = {}

        if self._shortcut_key in self.shortcut_overrides:
            return self.shortcut_overrides[self._shortcut_key]
        else:
            return self.shortcut_default

    @shortcut.setter
    def shortcut(self, value):
        if self.shortcut_overrides is None:
            self.shortcut_overrides = {}

        if value == self.shortcut_default:
            del self.shortcut
        else:
            self.shortcut_overrides[self._shortcut_key] = value
            if callable(self._shortcut_cb):
                self._shortcut_cb(value)

    @shortcut.deleter
    def shortcut(self):
        if self._shortcut_key in self.shortcut_overrides:
            del self.shortcut_overrides[self._shortcut_key]
            if callable(self._shortcut_cb):
                self._shortcut_cb(self.shortcut_default)

    def set_shortcut_change_callback(self, cb = None):
        self._shortcut_cb = cb

    def bind(self, instance, owner):
        bound = copy(self)
        bound._instance = instance
        bound.app = getattr(instance, 'app', None)
        if bound.signal:
            bound.signal = bound.signal.bind(instance, owner)
        if bound.setting and type(bound.is_checked()) == bool:
            bound.checkable = True
        if self._triggered_cb:
            bound._triggered_cb = functools.partial(self._triggered_cb, instance)
        return bound

    def get_setting(self):
        """
        Return the value of the setting object.
        """
        return self.setting.__get__(self._instance, type(self._instance))

    def set_setting(self, value):
        """
        Set the value of the setting.
        """
        self.setting.__set__(self._instance, value)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        elif self._name in instance.__dict__:
            return instance.__dict__[self._name]
        else:
            bound = self.bind(instance, owner)

            instance.__dict__[self._name] = bound
            return bound

    def __set__(self, instance, value):
        raise ValueError(f"Read-Only Descriptor: {self._name}")

    def is_checked(self):
        if self.setting and self.args:
            return (self.setting.__get__(self._instance, type(self._instance)),) == self.args
        elif self.setting and not self.args:
            return self.setting.__get__(self._instance, type(self._instance))

    def triggered(self, function):
        """
        Decorator used to set a callback when the action is triggered
        """
        self._triggered_cb = function
        return function

    def on_triggered(self, checked=False):
        if self.signal:
            if self.args:
                self.signal.emit(*self.args)
            elif self.checkable:
                self.signal.emit(checked)
            else:
                self.signal.emit()
        elif self.setting:
            if self.args:
                self.set_setting(*self.args)
            else:
                self.set_setting(checked)

        if self._triggered_cb:
            if self.args:
                self._triggered_cb(*self.args)
            elif self.checkable:
                self._triggered_cb(checked)
            else:
                self._triggered_cb()
