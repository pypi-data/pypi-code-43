"""Extends interpreter search path to import the modules which are stored
above Jupyter's server root folder.

This singleton module is a thin wrapper on top of sys.path variable. It helps
to reduce the boilerplate required to properly setup paths when working within
notebook.
"""
import sys
import os
from os.path import dirname


_old = sys.path.copy()


def add(folder, *folders):
    """Extends interpreter's search path with additional folders.

    If a folder already exists in the sys.path, it is ignored.
    """
    folders = [folder] + list(folders)
    for path in folders:
        path = str(path)
        if path in sys.path:
            continue
        sys.path.insert(0, str(path))


def add_parent_folder():
    add(dirname(os.getcwd()))


def add_grandparent_folder():
    add(dirname(dirname(os.getcwd())))


def restore():
    """Restores the sys.path variable to the original state."""
    sys.path = _old.copy()


def pprint():
    """Prints current sys.path in a convenient format."""
    print('sys.path:')
    for i, path in enumerate(sorted(sys.path), 1):
        print(f'\t({i}) {path}')
