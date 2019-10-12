import numpy


def align_polynomials(
        poly1,
        poly2,
        adjust_dim=True,
        adjust_shape=True,
):
    from .baseclass import Polynomial
    if not isinstance(poly1, Polynomial):
        poly1 = Polynomial.from_attributes([(0,)], [poly1])
    if not isinstance(poly2, Polynomial):
        poly2 = Polynomial.from_attributes([(0,)], [poly2])

    if adjust_dim:
        dim1 = poly1.exponents.shape[1]
        dim2 = poly2.exponents.shape[1]
        if dim1 < dim2:
            poly2, poly1 = align_polynomials(
                poly2, poly1, adjust_dim=True, adjust_shape=False)

        elif dim1 > dim2:
            exponents = numpy.hstack([
                poly2.exponents,
                numpy.zeros((len(poly2.exponents), dim1-dim2), dtype=int),
            ])
            poly2 = Polynomial.from_attributes(exponents, poly2.coefficients)
            assert dim1 == poly2.exponents.shape[1]

    if adjust_shape:
        shapedelta = len(poly2.shape)-len(poly1.shape)
        if shapedelta < 0:
            poly2, poly1 = align_polynomials(
                poly2, poly1, adjust_dim=False, adjust_shape=True)

        elif shapedelta > 0:
            coefficients = numpy.array(poly1.coefficients)[
                (slice(None),)+(numpy.newaxis,)*shapedelta]
            common = (numpy.ones(coefficients.shape[1:], dtype=bool)|
                      numpy.ones(poly2.shape, dtype=bool))
            poly1 = Polynomial.from_attributes(
                poly1.exponents, coefficients*common)
            poly2 = Polynomial.from_attributes(
                poly2.exponents, numpy.array(poly2.coefficients)*common)
        assert poly1.shape == poly2.shape

    return poly1, poly2
