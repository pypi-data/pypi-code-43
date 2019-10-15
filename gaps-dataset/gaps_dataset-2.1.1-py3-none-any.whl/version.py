# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function


_VERSION_MAJOR = 2
_VERSION_MINOR = 1
_VERSION_MICRO = 1
_VERSION_SUFFIX = ""


def _get_version(with_suffix=False):    # pragma no cover
    """Private function to determine version"""
    if with_suffix:
        return (_VERSION_MAJOR,
                _VERSION_MINOR,
                _VERSION_MICRO,
                _VERSION_SUFFIX)
    else:
        return (_VERSION_MAJOR, _VERSION_MINOR, _VERSION_MICRO)


__version__ = '{}.{}.{}'.format(*_get_version(with_suffix=False))
