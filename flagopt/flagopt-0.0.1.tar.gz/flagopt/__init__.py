import multidict

from .general import *

from . import helpers


__all__ = (*general.__all__, 'snip', 'draw', 'trace')


def snip(flags, value, parse = parse, strip = strip):

    """
    Get recursive multidict representation of arguments based on the flags.
    """

    keys = flags.keys()

    store = multidict.MultiDict()

    for (key, value) in parse(value, *keys):

        value = strip(value)

        if key is None:

            if not value:

                continue

            key = next(iter(keys))

        item = flags[key]

        if isinstance(item, dict):

            value = snip(item, value, parse, strip)

        store.add(key, value)

    return store


empty = ' '


clause = '()'


variable = '[]'


def draw(flags, empty = empty, clause = clause, variable = variable):

    """
    Draw description on how this flags expects.
    """

    store = []

    for (key, value) in flags.items():

        store.append(key)

        if isinstance(value, dict):

            ends = clause

            value = draw(value)

        else:

            ends = variable

        value = helpers.wrap(ends, value)

        store.append(value)

    return empty.join(store)


ignore = '{}' + empty


def trace(values, ignore = ignore, clause = clause, variable = variable):

    """
    Get flags from the string; used from drawing and snipping.
    """

    flags = {}

    buffer = ''

    level = 0

    upper = True

    for value in values:

        if upper:

            if value in ignore:

                continue

            if value == clause[0]:

                try:

                    if not level:

                        key = buffer

                        buffer = ''

                        continue

                finally:

                    level += 1

            if value == clause[1]:

                level -= 1

                if not level:

                    value = trace(buffer, ignore, clause, variable)

                    buffer = ''

                    flags[key] = value

                    continue

        if not level:

            if value == variable[0]:

                key = buffer

                buffer = ''

                upper = False

                continue

            if value == variable[1]:

                value = buffer

                buffer = ''

                flags[key] = value

                upper = True

                continue

        buffer += value

    return flags
