import difflib
import functools

from . import abstract


__all__ = ('specific', 'generic', 'rank', 'lead', 'pick')


def single(value, argument):

    """
    Return the best matcher ratio of the two arguments.
    """

    matcher = difflib.SequenceMatcher(a = argument, b = value)

    ratio = matcher.ratio()

    return ratio


key = str.lower


def specific(values, argument, single = single, key = key):

    """
    Return (value, score) pairs for values against the argument.
    """

    rank = single

    return abstract.specific(rank, values, argument, key = key)


def multiple(attributes, argument, specific = specific, key = key):

    """
    Return the highest best score against the argument.
    """

    assets = specific(attributes, argument, key = key)

    (junk, ratios) = zip(*assets)

    ratio = max(ratios)

    return ratio


def generic(fetch, values, argument, multiple = multiple, key = key):

    """
    Return (value, score) pairs for value's attributes against argument.
    """

    rank = functools.partial(multiple, key = key)

    return abstract.generic(rank, fetch, values, argument)


def differentiate(pair):

    """
    Overglorified sorting key.
    """

    (value, score) = pair

    return score


def rank(pairs, key = differentiate, reverse = False):

    """
    Use on results similar from the exposed functions.
    """

    return sorted(pairs, key = key, reverse = not reverse)


def lead(pairs, rank = rank):

    """
    Return the highest scored pair.
    """

    (leader, *lowers) = rank(pairs)

    (value, score) = leader

    return value


def pick(values, argument, fetch = None, lead = lead, key = key):

    """
    Return the best value matching the argument.
    If fetch is used, attribute-based search is commences.
    """

    if key:

        argument = key(argument)

    args = (generic, fetch) if fetch else (specific,)

    pairs = functools.partial(*args)(values, argument, key = key)

    value = lead(pairs)

    return value
