import json
import os
import sys

from attrdict import AttrDict


def in_venv(dirname):
    if "/venv/" in dirname:
        return True, "/venv"
    elif "/env/" in dirname:
        return True, "/env"
    elif "/virtualenv/" in dirname:
        return True, "/virtualenv"
    else:
        return False, ""


def exists_and_is_file(path):
    return os.path.exists(path) and os.path.isfile(path)


def get_strings_json(string_path=None):
    string_paths = [
        ["app", "strings.json"],
        ["strings.json"],
        ["resources", "strings.json"],
        ["strings", "strings.json"],
    ]
    STRING_FILE = None
    if string_path is None:
        ROOT_DIR = os.path.dirname(sys.modules["__main__"].__file__)
        is_virtual, splitter = in_venv(ROOT_DIR)
        if is_virtual:
            ROOT_DIR = ROOT_DIR.split(splitter)[0]
        for sp in string_paths:
            STRING_FILE = os.path.join(ROOT_DIR, *sp)
            if exists_and_is_file(STRING_FILE):
                break
    else:
        STRING_FILE = string_path

    if STRING_FILE is None:
        raise FileNotFoundError("Could not find strings.json file")

    with open(STRING_FILE, "r") as f:
        return AttrDict(json.load(f))
