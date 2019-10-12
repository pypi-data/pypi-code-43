
import numpy
import numpoly

from .common import implements


@implements(numpy.apply_over_axes)
def apply_over_axes(func, a, axes):
    """
    Examples:
        >>> array = numpy.arange(24).reshape(2,3,4)
        >>> numpoly.apply_over_axes(numpy.sum, array, [0, 2])
        polynomial([[[60],
                     [92],
                     [124]]])
        >>> x, y = numpoly.symbols("x y")
        >>> poly = numpoly.polynomial([[[1], [x+1], [y**2]]])
        >>> numpoly.apply_over_axes(numpy.prod, poly, [1, 2])

    """
    def wrapper_func(array, axis):
        keys = numpy.asarray(array.dtype.names, dtype="U")
        exponents = keys.flatten().view(numpy.uint32)-48
        exponents = exponents.reshape(len(keys), -1)

        poly = numpoly.ndpoly.from_attributes(
            exponents=exponents,
            coefficients=[array[key] for key in array.dtype.names],
            indeterminants=a.indeterminants,
            dtype=a.dtype,
            clean=False,
        )
        out = func(poly, axis=axis)
        out = numpy.asarray(out)
        return out

    a = numpoly.aspolynomial(a)
    out = numpy.apply_over_axes(wrapper_func, numpy.asarray(a), axes)

    keys = numpy.asarray(out.dtype.names, dtype="U")
    exponents = keys.flatten().view(numpy.uint32)-48
    exponents = exponents.reshape(len(keys), -1)

    out = numpoly.ndpoly.from_attributes(
        exponents=exponents,
        coefficients=[out[key] for key in out.dtype.names],
        indeterminants=a.indeterminants,
        dtype=a.dtype,
        clean=True,
    )
    return out
