import logging
import os

logger = logging.getLogger(__name__)


def getAttr(o, name, default=None):
    if o is None:
        return default
    return o[name] if name in o else default


def setAttr(o, name, value):
    o[name] = value
    return o


def delAttr(o, name):
    if name in o:
        del o[name]
        return True
    else:
        return False


def isEmptyDict(dictionary):
    for element in dictionary:
        if element:
            return True
        return False


def delete_drive_leter(path):
    path = path.replace(os.path.sep, os.path.altsep)
    if path.find(':') != -1:
        path = (path.split(':')[1]).replace(os.path.sep, os.path.altsep)
        path = ''.join(path)

    if path.startswith(os.altsep):
        return path[1:]
    return path


def get_drive_leter(path):
    path = path.replace(os.path.sep, os.path.altsep)
    if path.find(':') != -1:
        return f"{(path.split(':')[0])}:"
    return None


def replace_alt_set(path):
    return path.replace(os.altsep, os.sep).replace(f'{os.sep}{os.sep}', os.sep)


def del_last_not_digit(str):
    res = ''
    flag = False
    for ch in reversed(str):
        if flag or ch.isdigit():
            res += ch
            flag = True

    return res[::-1]


def str_to_bool(s):
    if s in ['True', 'true']:
        return True
    elif s in ['False', 'false']:
        return False
    else:
        raise ValueError(f'{s} is not a good boolean string')

def bool_to_jsBool(value):
    if value == True:
        return "true"
    return "false"
