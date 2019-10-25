import json
from json import JSONEncoder


class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, object):
            return o.__dict__
        else:
            return json.JSONEncoder.default(self, o)


def check_locals(**kwargs):
    ret_dict = {}
    for item in kwargs:
        if kwargs[item] and not item == "self":
            if isinstance(kwargs[item], list):
                kwargs[item] = MyEncoder().encode(kwargs[item])
            ret_dict[item] = kwargs[item]
    return ret_dict
