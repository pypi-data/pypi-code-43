import json
from datetime import date, datetime, timedelta


def treat_non_serializable(x):
    """tries to convert a supplied item into something that is json serializable"""
    if isinstance(x, (datetime, date)):
        return x.isoformat()
    elif isinstance(x, timedelta):
        return str(x)
    elif isinstance(x, dict):
        make_dict_values_json_serializable(x)
        return x
    elif isinstance(x, list):
        for i, l in enumerate(x):
            try:
                _ = json.dumps(l)
            except TypeError:
                x[i] = treat_non_serializable(l)
        return x
    else:
        return str(x)


def make_list_items_json_serializable(l: list):
    """tries to convert items in a supplied list into something that is json serializable"""
    for count, value in enumerate(l):
        if type(value) is dict:
            make_dict_values_json_serializable(l[count])
        else:
            try:
                _ = json.dumps(value)
            except TypeError:
                l[count] = treat_non_serializable(value)


def make_dict_values_json_serializable(d: dict):
    """tries to convert the values of a dict into something that is json serializable if it is not;
    works recursively for nested dicts, i.e. if value is also a dict"""
    for key in d.keys():  # can't loop at items() as value will then be a copy, not a reference to orig obj
        if type(d[key]) is dict:
            make_dict_values_json_serializable(d[key])
        else:
            try:
                _ = json.dumps(d[key])
            except TypeError:
                d[key] = treat_non_serializable(d[key])
