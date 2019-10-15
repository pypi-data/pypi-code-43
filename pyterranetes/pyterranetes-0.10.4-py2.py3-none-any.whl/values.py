import os
from collections.abc import MutableMapping
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path

from p10s.loads import load_file
from p10s.utils import merge_dicts


class Values(MutableMapping):
    """Class for storing p10s value mappings.

Can be used as a dict. Has classmethods, such as
:py:meth:`p10s.values.Values.from_files` for loading values from
various sources.

The assumption is that Values won't be created directly, though that's
certainly possible, but that they're be created from external
source. If, for example, we want to have our values stored in a yaml
on disk, and allow over riding form the env, we would this:

.. code-block:: python

    VALUES = Values.from_files(".") + Values.from_environ(".")


    """

    def __init__(self, values=None):
        if values is not None:
            self.values = values
        else:
            self.values = {}

    @classmethod
    def from_files(cls, basedir):
        """Builds a Values object from a hierarchically organzied collections
of yaml files.

All the files named ``values.yaml`` in basedir and up the file system
(up until the file system's root) will be collected and parsed and
merged. The merging is top down, so values specifed in files closer to
basedir will over ride values specified in a higher up values file.
        """
        basedir = Path(basedir)
        if not basedir.exists():
            raise FileNotFoundError("basedir %s does not exist" % basedir)
        here = basedir

        values_files = []

        if basedir.is_file():
            basedir = basedir.parent()

        while True:
            if (here / "values.yaml").exists():
                values_files.insert(0, here / "values.yaml")
            if here == here.parent:
                break
            else:
                here = here.parent

        values = {}
        for file in values_files:
            merge_dicts(values, load_file(file))

        return cls(values)

    @classmethod
    def from_environ(cls):
        """Builds a Values object from the current OS environment."""
        # NOTE we may be able to just pass in os.enviro directly,
        # without creating a dict, but i'm not sure what other magic
        # is on that and this feels safer. 20181220:mb
        return cls(dict(os.environ))

    def __add__(self, other):
        """Returns a new values containg the merge of ``other`` into this
        object (key/value pairs in ``other`` replace equally named
        pairs in ``self``)"""
        new = self.copy()
        return new.__iadd__(other)

    def __iadd__(self, other):
        """Modifies ``self`` by merging in the values of ``other``"""
        self.values = merge_dicts(self.values, other)
        return self

    def copy(self):
        return Values(values=deepcopy(self.values))

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __keytransform__(self, key):
        return key

    def set_value(self, key, value):
        self.values[key] = value

    def get_value(self, key, default=None):
        return self.values.get(key, default)


global VALUES
VALUES = Values()


def use_values(values):
    global VALUES
    VALUES = values


@contextmanager
def values(*args, **kwargs):
    """context manager, runs the body with the given key=value pairs
bound.

``*args`` is a list of dicts, whose final values will be computed as
by :func:``merge_dicts <p10s.utils.merge_dicts>`. ``*kwargs`` are
tweated as a single dict of key=value pairs, and take precedence over
anything in ``*args``.

    """
    global VALUES
    old = VALUES
    new = old.copy()

    for dict in args:
        new += Values(values=dict)
    new += Values(values=kwargs)

    VALUES = new
    yield
    VALUES = old


def value(key, default=None):
    """Returns the value of the key named ``key``."""
    global VALUES
    return VALUES.get_value(key, default)


def set_value(key, value):
    """Sets the value with the key ``key`` to ``value``."""
    global VALUES
    VALUES.set_value(key, value)
    return value
