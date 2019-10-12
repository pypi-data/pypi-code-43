"""
    >>> from chaospy.polynomial import npoly
    >>> poly = npoly({(0,): [[1., 2.], [3., 4.]], (1,): [[4., 5.], [6., 7.]]})
    >>> print(poly)
    [[1.0+4.0q0 2.0+5.0q0]
     [3.0+6.0q0 4.0+7.0q0]]
    >>> print(poly**0)
    [[1.0 1.0]
     [1.0 1.0]]
    >>> print(poly**1)
    [[1.0+4.0q0 2.0+5.0q0]
     [3.0+6.0q0 4.0+7.0q0]]
    >>> print(poly**2)
    [[1.0+8.0q0+16.0q0^2 4.0+20.0q0+25.0q0^2]
     [9.0+36.0q0+36.0q0^2 16.0+56.0q0+49.0q0^2]]
    >>> print(poly**3)
    [[1.0+12.0q0+48.0q0^2+64.0q0^3 8.0+60.0q0+150.0q0^2+125.0q0^3]
     [27.0+162.0q0+324.0q0^2+216.0q0^3 64.0+336.0q0+588.0q0^2+343.0q0^3]]
"""
import numpy

from .multiply import poly_mul


def poly_pow(poly, exponent):
    assert exponent >= 0, "only positive integers allowed"
    out = poly.from_attributes([(0,)], [numpy.ones(poly.shape, dtype=poly._dtype)])
    for _ in range(exponent):
        out = poly_mul(out, poly)
    return out
