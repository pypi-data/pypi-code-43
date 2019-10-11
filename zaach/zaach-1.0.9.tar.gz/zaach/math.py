from functools import reduce
from operator import mul


def prod(iterable):
    """ Returns the product of the iterable. """
    return reduce(mul, iterable)
