import json

from kamzik3 import units


class JsonKamzikEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, units.Quantity):
            return {"pint-unit-quantity": o.to_tuple()}
        return o


def JsonPintHook(dct):
    if 'pint-unit-quantity' in dct:
        return units.Quantity.from_tuple(dct['pint-unit-quantity'])
    return dct