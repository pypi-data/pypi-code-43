from contextlib import contextmanager

_output = list()


def _reset_output():
    _output.clear()


def get_output() -> list:
    """
    Retrieve the current output
    """
    return _output


@contextmanager
def new_output() -> list:
    """
    Create a new output for the duration of a with-block
    """
    try:
        yield get_output()
    finally:
        _reset_output()
