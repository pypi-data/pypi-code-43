from contextlib import contextmanager

from rtm.main.exceptions import UninitializedError

_digits = None


def get_digits():
    if _digits is None:
        raise UninitializedError("_digits wasn't initialized")
    else:
        return _digits


@contextmanager
def set_digits():
    global _digits
    _digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    yield
    _digits = None
