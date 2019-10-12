"""
Polynomial multiplication::

    >>> from chaospy.polynomial import npoly
    >>> poly = npoly({(0,): [[1., 2.], [3., 4.]], (1,): [[4., 5.], [6., 7.]]})
    >>> print(poly)
    [[1.0+4.0q0 2.0+5.0q0]
     [3.0+6.0q0 4.0+7.0q0]]
    >>> print(poly*4)
    [[4.0+16.0q0 8.0+20.0q0]
     [12.0+24.0q0 16.0+28.0q0]]
    >>> print(poly*poly[0])
    [[1.0+8.0q0+16.0q0^2 4.0+20.0q0+25.0q0^2]
     [3.0+18.0q0+24.0q0^2 8.0+34.0q0+35.0q0^2]]
    >>> print(poly*poly[0, 0])
    [[1.0+8.0q0+16.0q0^2 2.0+13.0q0+20.0q0^2]
     [3.0+18.0q0+24.0q0^2 4.0+23.0q0+28.0q0^2]]
"""
import numpy


def poly_mul(poly1, poly2):
    exponents = (numpy.tile(poly1.exponents, (len(poly2.exponents), 1))+
                 numpy.repeat(poly2.exponents, len(poly1.exponents), 0))

    shape = (len(poly2.coefficients),)+(1,)*len(poly2.shape)
    coefficients = (numpy.tile(poly1.coefficients, shape)*
                    numpy.repeat(poly2.coefficients,
                                    len(poly1.coefficients), 0))

    collection = {}
    for exponent, coefficient in zip(exponents.tolist(), coefficients):
        exponent = tuple(exponent)
        collection[exponent] = collection.get(exponent, False) + coefficient

    exponents = sorted(collection)
    coefficients = [collection[exponent] for exponent in exponents]

    return poly1.from_attributes(exponents, coefficients)
