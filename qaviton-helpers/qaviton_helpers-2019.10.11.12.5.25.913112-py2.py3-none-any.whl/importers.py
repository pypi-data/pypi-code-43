from sys import path as paths
from os import sep
from os.path import basename, isdir, exists, dirname
from os.path import isdir
from importlib.util import spec_from_file_location, module_from_spec


def make_importable(path):
    parent = dirname(path)
    if parent not in paths:
        paths.append(parent)


def import_path(path):
    make_importable(path)
    if isdir(path): path += sep + '__init__.py'
    name = basename(path)
    spec = spec_from_file_location(name, path)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
