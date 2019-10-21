import json
from datetime import datetime as dt

from kcuforms.errors import FieldError


def date_type(dt_str, fmt='%Y%m%d'):
    return dt.strptime(dt_str, fmt)


def list_type(lst_obj):
    try:
        if isinstance(lst_obj, (list, tuple)):
            ret = lst_obj
        elif isinstance(lst_obj, dict):
            ret = [lst_obj]
        else:
            ret = json.loads(lst_obj)
        return ret
    except Exception as ex:
        raise FieldError(u'Val: {}, Reason: {}, Type: list'.format(lst_obj, ex))


def dict_type(dict_obj):
    try:
        if isinstance(dict_obj, dict):
            ret = dict_obj
        else:
            try:
                ret = json.loads(dict_obj)
            except JSONDecodeError as ex:
                if 'Expecting property name enclosed in double quotes' in ex.msg:
                    ret = ast.literal_eval(dict_obj)
                else:
                    raise ex
        return ret
    except Exception as ex:
        raise FieldError(u'Val: {}, Reason: {}, Type: list'.format(dict_obj, ex))


def many_type(range_string):
    if isinstance(range_string, (tuple, list)):
        return range_string
    else:
        return range_string.split(',')
