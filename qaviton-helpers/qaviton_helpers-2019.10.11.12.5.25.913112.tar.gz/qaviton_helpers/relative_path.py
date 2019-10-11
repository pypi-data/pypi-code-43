import os


def path(__file__):
    """Returns abs path relative to this file and not cwd
        example:
            from qaviton_helpers import path
            path(__file__)('../../path/to/file.txt')
    """
    return lambda p: os.path.abspath(os.path.join(os.path.dirname(__file__), p))
