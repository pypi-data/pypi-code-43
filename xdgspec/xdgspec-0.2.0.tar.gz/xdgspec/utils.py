# system modules

# internal modules

# external modules


def unique(iterable):
    """
    Generator yielding only unique elements

    Args:
        iterable (iterable): iterable of :any:`hash`-able objects
    """
    seen = set()
    for x in iterable:
        if x in seen:
            continue
        else:
            seen.add(x)
            yield x
