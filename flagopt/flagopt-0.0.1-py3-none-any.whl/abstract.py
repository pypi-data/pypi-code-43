import re
import itertools

from . import helpers


__all__ = ()


def parse(escape, values, keys):

    match = lambda key: re.finditer(key, values)

    generate = map(match, keys)

    matches = itertools.chain.from_iterable(generate)

    drag = lambda match: match.start()

    matches = sorted(matches, key = drag)

    for match in matches:

        span = match.span()

        (start, end) = span

        defeat = lambda other: (
            not match is other
            and start <= other.start() < end
            and other.end() > end
        )

        if any(map(defeat, matches)):

            continue

        key = match.re.pattern

        back = start - len(escape)

        against = values[back:start]

        valid = not against == escape

        yield (valid, key, span)


def snip(combine, clean, explicit, store, value):

    pairs = combine(value)

    for (index, pair) in enumerate(pairs):

        (key, value) = pair

        if not key:

            if not value or explicit:

                continue

            key = next(iter(store))

        value = clean(value)

        item = store[key]

        if not isinstance(item, str):

            value = snip(combine, clean, explicit, item, value)

        yield (key, value)


def draw(clause, variable, figure):

    for (key, value) in figure.items():

        yield key

        if isinstance(value, dict):

            ends = clause

            value = draw(value)

        else:

            ends = variable

        value = helpers.wrap(ends, value)

        yield value
