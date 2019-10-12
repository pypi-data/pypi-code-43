"""
Polynomial addition::

    >>> from chaospy.polynomial import npoly
    >>> poly = npoly({(0, 0): [1., 2.], (0, 1): [3., 4.], (1, 0): [5., 6.]})
    >>> print(poly)
    [1.0+3.0q1+5.0q0 2.0+4.0q1+6.0q0]
    >>> print(poly+poly[0])
    [2.0+6.0q1+10.0q0 3.0+7.0q1+11.0q0]
    >>> print(poly+poly)
    [2.0+6.0q1+10.0q0 4.0+8.0q1+12.0q0]
    >>> print(poly+4)
    [5.0+3.0q1+5.0q0 6.0+4.0q1+6.0q0]
"""


def poly_add(poly1, poly2):
    collection = poly1.todict()
    for exponent, coefficient in poly2.todict().items():
        collection[exponent] = collection.get(exponent, False) + coefficient
    exponents = sorted(collection)
    coefficients = [collection[exponent] for exponent in exponents]

    return poly1.from_attributes(exponents, coefficients)
