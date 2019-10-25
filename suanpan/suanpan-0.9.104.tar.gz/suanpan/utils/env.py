# coding=utf-8
from __future__ import absolute_import, print_function

import os

environ = os.environ


def get(key, default=None, required=False, type=str):
    if key not in environ:
        if required:
            raise Exception("No such env: {}".format(key))
        return default
    value = environ[key]
    try:
        return type(value)
    except Exception:
        raise Exception(
            "EnvTypeErr: ({}) {} except {}".format(key, value, getTypeName(type))
        )


def getTypeName(type):
    name = getattr(type, "name", None) or getattr(type, "__name__", None)
    if not name:
        raise Exception("Unknown env type: {}".format(type))
    return name


def update(*args, **kwargs):
    return environ.update(*args, **kwargs)


str = str
int = int
float = float


def bool(value):
    return value in ("true", "True")
