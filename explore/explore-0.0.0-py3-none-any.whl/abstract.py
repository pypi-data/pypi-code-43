

__all__ = ()


def specific(rank, values, argument, key = None):

    """
    Yield (value, score) pairs from values against the argument, according to
    rank, after transformation by key if used.
    """

    for value in values:

        check = key(value) if key else value

        score = rank(check, argument)

        yield (value, score)


def generic(rank, fetch, values, argument):

    """
    Yield (value, score) pairs from values' attributes against the argument,
    according to rank.
    """

    for value in values:

        generate = fetch(value)

        attributes = tuple(generate)

        if not attributes:

            continue

        score = rank(attributes, argument)

        yield (value, score)
