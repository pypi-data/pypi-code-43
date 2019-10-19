import functools
from collections.abc import Iterable

def chain(initial, *transforms):
    return functools.reduce(
        lambda prev_result, next_transform: next_transform(prev_result),
        transforms,
        initial
    )

def _wrap(fn):
    def wrapper(item):
        if isinstance(item, tuple):
            return fn(*item)
        else:
            return fn(item)
    return wrapper

_built_in_map = map
def map(transform):
    return functools.partial(_built_in_map, _wrap(transform))

def reduce(transform, initial = None):
    def wrapper(acc, value):
        if isinstance(value, tuple):
            return transform(acc, *value)
        else:
            return transform(acc, value)

    if initial is None:
        return lambda iterable: functools.reduce(wrapper, iterable)
    else:
        return lambda iterable: functools.reduce(wrapper, iterable, initial)

_built_in_filter = filter
def filter(condition):
    return functools.partial(_built_in_filter, _wrap(condition))

def sort(key = None, reverse = False):
    return lambda iterable: sorted(iterable, key=key, reverse=reverse)

def tap(fn):
    """Intended for debugging purposes, usually with `print`"""
    def tapper(value):
        if isinstance(value, Iterable) and not isinstance(value, str):
            value = list(value)
        fn(value)
        return value

    return tapper

def tap_each(fn):
    """Intended for debugging purposes, usually with `print`"""
    def each_tapper(value):
        _wrap(fn)(value)
        return value

    def tapper(iterable):
        if isinstance(iterable, str):
            return each_tapper(iterable)
        else:
            return _built_in_map(each_tapper, iterable)

    return tapper
