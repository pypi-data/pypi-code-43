import math


def round_down(x):
    return math.floor(x)


def bound(value, lower_bound=None, upper_bound=None):
    if upper_bound is not None and lower_bound is not None:
        if upper_bound < lower_bound:
            raise ValueError("Upper bound must be greater than lower bound")

    if upper_bound:
        value = min(value, upper_bound)
    if lower_bound:
        value = max(value, lower_bound)

    return value


def is_int(x):
    try:
        return int(x) == x
    except (ValueError, TypeError):
        return False