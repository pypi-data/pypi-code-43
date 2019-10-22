from functools import partial as _partial


def partial(*args, **kwargs):
    """
    sanic now requires function handlers to have a __name__,
    so we wrap functools.partial to also assign a __name__,
    which functools.partial objects don't have
    """
    p = _partial(*args, **kwargs)
    p.__name__ = args[0].__name__
    return p
