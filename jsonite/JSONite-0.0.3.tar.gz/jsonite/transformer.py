from collections.abc import Iterable
from json import dumps, JSONEncoder


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
        try:
            if not isinstance(val, Iterable) or isinstance(val, (str, dict)):
                raise TypeError()

            try:
                # try to unpack an Orator model
                val = [v.__dict__['_attributes'] for v in val]
            except:
                # unpack other iterable
                val = [v for v in val]
        except TypeError:
            pass

        return self.declaration.format(key, self.encoder.encode(val))

