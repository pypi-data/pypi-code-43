# -*- coding: utf-8 -*-
from os import path
import json
import yaml
import importlib.util

def write_json(filename, data):
    """Saves data to a json file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, sort_keys=False, indent=4, ensure_ascii=False)

    return True

def read_json(filename):
    """Reads data from a json file."""
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data

def write_yaml(filename, data):
    """Saves data to a yaml file."""
    with open(filename, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, sort_keys=False, default_flow_style=False)

    return True

def read_yaml(filename):
    """Reads data from a yaml file."""

    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.load(file, Loader=yaml.FullLoader)

    return data

def load_class(filepath, classname, relative=False):
    """Loads dynamically a class given its path.

    Path can be absolute (default) or relative (mostly for drummer packages).
    """

    if relative:
        modname = filepath.replace('/', '.')
        mod = __import__(modname, fromlist=[classname])

    else:
        _, filename = path.split(filepath)
        modname = filename[:-3]
        spec = importlib.util.spec_from_file_location(modname, filepath)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    return getattr(mod, classname)
