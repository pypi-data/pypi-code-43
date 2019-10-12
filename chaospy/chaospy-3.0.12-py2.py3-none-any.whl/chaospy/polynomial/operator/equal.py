"""
Polynomial equality::

    >>> from chaospy.polynomial import npoly
    >>> poly = npoly({(0,): [[1., 2.], [3., 4.]], (1,): [[4., 5.], [6., 7.]]})
    >>> print(poly)
    [[1.0+4.0q0 2.0+5.0q0]
     [3.0+6.0q0 4.0+7.0q0]]
    >>> print(poly == poly)
    [[ True  True]
     [ True  True]]
    >>> print(poly == poly[0])
    [[ True  True]
     [False False]]
    >>> print(poly == poly[1, 1])
    [[False False]
     [False  True]]
"""
import numpy


def poly_eq(poly1, poly2):
    out = numpy.ones(poly1.shape, dtype=bool)
    collection = poly1.todict()
    for exponent, coefficient in poly2.todict().items():
        if exponent in collection:
            out &= collection.pop(exponent) == coefficient
        else:
            out &= coefficient == 0
    for _, coefficient in collection.items():
        out &= coefficient == 0
    return out
