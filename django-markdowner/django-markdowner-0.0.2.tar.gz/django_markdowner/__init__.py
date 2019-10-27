# -*- coding: utf-8 -*-
VERSION = (0, 0, 2)


def get_version(version: tuple) -> str:
    """
    Gets the version of the package based on a :class:`tuple` and returns a :class:`str`.
    This method is based on ``django-extensions`` get_version method.
    """

    if not isinstance(version[-1], int):
        str_version = '.'.join(list(map(str, version[:-1]))) + '_{}'.format(version[-1])
        return str_version

    str_version = '.'.join(list(map(str, version)))
    return str_version


__version__ = get_version(VERSION)
