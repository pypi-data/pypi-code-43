"""
Polynomial get item::

    >>> from chaospy.polynomial import npoly
    >>> poly = npoly({(0,): [[1., 2.], [3., 4.]], (1,): [[4., 5.], [6., 7.]]})
    >>> print(poly)
    [[1.0+4.0q0 2.0+5.0q0]
     [3.0+6.0q0 4.0+7.0q0]]
    >>> print(poly[0])
    [1.0+4.0q0 2.0+5.0q0]
    >>> print(poly[:, 1])
    [2.0+5.0q0 4.0+7.0q0]
"""
import numpy


def poly_getitem(poly, index):
    if isinstance(index, tuple):
        index = (slice(None),) + index
    else:
        index = (slice(None), index)
    out = poly.from_attributes(
        poly.exponents, numpy.array(poly.coefficients)[index])
    return out
