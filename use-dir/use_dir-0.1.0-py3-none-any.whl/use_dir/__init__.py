__version__ = '0.1.0'

from contextlib import contextmanager
import os

@contextmanager
def use_dir(path):
    owd = os.getcwd()
    os.chdir(path)

    try:
        yield
    finally:
        os.chdir(owd)
