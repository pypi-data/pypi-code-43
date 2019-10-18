
from collections import Iterable
from inspect import isclass
from json import dumps, JSONEncoder

from orator import Model


class Encoder(JSONEncoder):
    """ JSON encoder for class instances.

    Orator models will encode their attributes only
    Any others will encode all fields int their __dict__ attribute
    """

    def default(self, obj):
        try:
            return obj['_attributes']
        except:
            pass
        return obj.__dict__


class Transformer:
    """Transforms Python variables to Javascript."""

    declaration = '.{} = {};'

    def __init__(self):
        self.declaration = '"{}": {},'
        self.encoder = Encoder()

    def convert(self, key, val):
        if isinstance(val, Iterable) and not isinstance(val, (str, dict)):
            val = list(val)

        return self.declaration.format(key, self.encoder.encode(val))

