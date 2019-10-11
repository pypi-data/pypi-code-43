from time import time
from sys import version_info, executable


def get_timestamp():
    return time()


def get_python_version():
    return version_info


def get_python_interpreter():
    return executable


def pop_by_name(items, name):
    """pop list item by its value"""
    if name in items:
        items.pop(name)
    return name


def swap(items, a, b):
    """swap between list/dict items values"""
    items[a], items[b] = items[b], items[a]
    return items
