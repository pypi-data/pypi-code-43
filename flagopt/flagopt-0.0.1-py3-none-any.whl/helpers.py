

__all__ = ()


def wrap(ends, value):

    (open, *junk, close) = ends

    return open + value + close
