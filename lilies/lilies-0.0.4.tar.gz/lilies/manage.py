from __future__ import print_function
import atexit
from .compiler import teardown


def lilies_init():
    atexit.register(teardown)
