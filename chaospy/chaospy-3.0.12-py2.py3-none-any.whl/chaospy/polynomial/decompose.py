import numpy


def decompose(poly):
    """
    Example:
        >>> from chaospy.polynomial import npoly
        >>> poly = npoly({(0, 1): [[1, 2], [3, 4]], (1, 0): [[4, 5], [6, 7]]})
        >>> print(poly)
        [[q1+4q0 2q1+5q0]
         [3q1+6q0 4q1+7q0]]

        # >>> print(decompose(poly))
        # [[[1q1 2q1]
        #   [3q1 4q1]]
        # <BLANKLINE>
        #  [[4q0 5q0]
        #   [6q0 7q0]]]
        # >>> print(decompose(decompose(poly)))
        # [[[[1q1 2q1]
        #    [3q1 4q1]]
        # <BLANKLINE>
        #   [[4q0 5q0]
        #    [6q0 7q0]]]]
    """
    counts = numpy.sum(poly.coefficients != 0, 0)
    if not numpy.any(counts > 1):
        return poly[numpy.newaxis]
    coefficients = numpy.zeros(
        (len(poly.coefficients),)*2+poly.shape, dtype=poly._dtype)
    coefficients[numpy.diag_indices(len(coefficients))] = numpy.array(
        poly.coefficients)
    return poly.from_attributes(poly.exponents, coefficients)
