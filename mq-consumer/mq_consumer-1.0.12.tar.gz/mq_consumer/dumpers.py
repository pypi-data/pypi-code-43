import json
import pickle

from .encoders import DateTimeDecimalJSONEncoder


__dumpers_dict = {}


def register(content_type):
    def wrap_decor(dump_function):
        __dumpers_dict[content_type] = dump_function
        return dump_function
    return wrap_decor


@register('text/plain')
def pickle_dumper(data):
    return pickle.dumps(data)


@register('application/json')
def json_dumper(data):
    return json.dumps(data, cls=DateTimeDecimalJSONEncoder)


def get_dumper(content_type):
    return __dumpers_dict.get(content_type)
