"""Generating config files.

Very often we need to generate a few files of yaml, or json, or ini
encoded data.

.. code-block:: python

    from p10s import cfg

    setup = cfg.JSONContext("config.json")
    setup += {"VAR": "VALUE"}

    c.variable.name = 'default-value'

"""
import configparser
import json
from collections.abc import Mapping, Sequence
from copy import deepcopy

from p10s.base import BaseContext
from p10s.loads import ruamel
from p10s.utils import merge_dicts


class ConfigContext(BaseContext):
    def __init__(self, *args, data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data if data is not None else {}

    def add(self, data):
        self.data = merge_dicts(self.data, data)
        return self

    def __iadd__(self, data):
        return self.add(data)

    def __add__(self, data):
        return deepcopy(self).add(data)


class INIContext(ConfigContext):
    """Context for ini files.

    Does not support the full nested sections allowed by configparser,
    one level deep only, and values must be scalars.

    """

    output_file_extension = ".ini"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configparser = configparser.ConfigParser()

    def add(self, data):
        for key, value in data.items():
            self.configparser[key] = value
        return self

    def render_to_stream(self, stream):
        self.configparser.write(stream)


class YAMLContext(ConfigContext):
    """Context for yaml files."""

    output_file_extension = ".yaml"

    def render_to_stream(self, stream):
        ruamel.dump_all([self.data], stream)


class JSONContext(ConfigContext):
    """Context for json files."""

    output_file_extension = ".json"

    def render_to_stream(self, steam):
        json.dump(self.data, steam, indent=4, sort_keys=True)


class UnknownDataTypeError(ValueError):
    pass


class DataAccessMismatch(ValueError):
    pass


class InvalidKeyType(ValueError):
    pass


class AutoData:
    def __init__(self):
        self._data = {}
        self._type = None

    def data(self):
        if self._type is None:
            return {}
        elif self._type == Mapping:
            d = {}
            for key, value in self._data.items():
                if isinstance(value, AutoData):
                    d[key] = value.data()
                else:
                    d[key] = value
            return d
        elif self._type == Sequence:
            d = []
            for i in range(1 + max(self._data.keys())):
                if i in self._data:
                    v = self._data[i]
                    if isinstance(v, AutoData):
                        v = v.data()
                else:
                    v = None
                d.append(v)
            return d
        else:
            raise UnknownDataTypeError(
                "Sorry, self._data is a %s, which we can't handle."
                % self._data.__class__
            )

    def _assert_for_key(self, key):
        if isinstance(key, str):
            if self._type is None:
                self._type = Mapping
            if self._type == Sequence:
                raise DataAccessMismatch(
                    "_data (%s) was a sequence but is now being accessed as a dict (%s)."
                    % (self._data, key)
                )
        elif isinstance(key, int):
            if self._type is None:
                self._type = Sequence
            if self._type == Mapping:
                raise DataAccessMismatch(
                    "_data was set to a dict (%s) but is now being accessed as an array (%s)."
                )
        else:
            raise InvalidKeyType(
                "Sorry, AutoData keys must be strings or ints, not %s (%s)"
                % (key, key.__class__)
            )

    def __getitem__(self, key):
        self._assert_for_key(key)

        if key in self._data:
            return self._data[key]
        else:
            return self.__setitem__(key, AutoData())

    def __getattr__(self, name):
        # NOTE _data and _type are actually on the object's __dict__
        # so this method isn't called for those properties. This means
        # it's important to always set them before attempting to read
        # them. 20190919:mb
        return self[name]

    def __setattr__(self, name, value):
        if name in ["_data", "_type"]:
            return object.__setattr__(self, name, value)
        else:
            self[name] = value
            return value

    def __setitem__(self, key, value):
        self._assert_for_key(key)
        self._data[key] = value
        return value
