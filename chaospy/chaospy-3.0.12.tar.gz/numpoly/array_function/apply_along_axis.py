"""Apply a function to 1-D slices along the given axis."""
from functools import wraps
import numpy
import numpoly

from .common import implements


@implements(numpy.apply_along_axis)
def apply_along_axis(func1d, axis, arr, *args, **kwargs):
    """
    Apply a function to 1-D slices along the given axis.

    Execute `func1d(a, *args)` where `func1d` operates on 1-D arrays and `a` is
    a 1-D slice of `arr` along `axis`.

    This is equivalent to (but faster than) the following use of `ndindex` and
    `s_`, which sets each of ``ii``, ``jj``, and ``kk`` to a tuple of indices::

        Ni, Nk = a.shape[:axis], a.shape[axis+1:]
        for ii in ndindex(Ni):
            for kk in ndindex(Nk):
                f = func1d(arr[ii + s_[:,] + kk])
                Nj = f.shape
                for jj in ndindex(Nj):
                    out[ii + jj + kk] = f[jj]

    Equivalently, eliminating the inner loop, this can be expressed as::

        Ni, Nk = a.shape[:axis], a.shape[axis+1:]
        for ii in ndindex(Ni):
            for kk in ndindex(Nk):
                out[ii + s_[...,] + kk] = func1d(arr[ii + s_[:,] + kk])

    Args:
        func1d (Callable[[numpoly.ndpoly], Any]):
            This function should accept 1-D arrays. It is applied to 1-D slices
            of `arr` along the specified axis.
        axis (int):
            Axis along which `arr` is sliced.
        arr (numpoly.ndpoly):
            Input array.
        args:
            Additional arguments to `func1d`.
        kwargs:
            Additional named arguments to `func1d`.

    Returns:
        out (numpoly.ndpoly):
            The output array. The shape of `out` is identical to the shape of
            `arr`, except along the `axis` dimension. This axis is removed, and
            replaced with new dimensions equal to the shape of the return value
            of `func1d`. So if `func1d` returns a scalar `out` will have one
            fewer dimensions than `arr`.

    Examples:
        >>> x, y = numpoly.symbols("x y")
        >>> b = numpoly.polynomial([[1, 2, x], [4, y, 6], [x+y, 8, 9]])
        >>> numpoly.apply_along_axis(numpoly.mean, -1, b)
        polynomial([2, 5, 8])

    """
    @wraps(func1d)
    def wrapper_func(array):
        keys = numpy.asarray(array.dtype.names, dtype="U")
        exponents = keys.flatten().view(numpy.uint32)-48
        exponents = exponents.reshape(len(keys), -1)

        poly = numpoly.ndpoly.from_attributes(
            exponents=exponents,
            coefficients=[array[key] for key in array.dtype.names],
            indeterminants=arr.indeterminants,
            dtype=arr.dtype,
            clean=False,
        )
        out = func1d(poly)
        if isinstance(out, numpoly.ndpoly):
            out = numpoly.align_exponents(out, arr)
            out = numpoly.align_indeterminants(out, arr)
            out = out.values
        return out

    arr = numpoly.aspolynomial(arr)
    out = numpy.apply_along_axis(
        wrapper_func, axis=axis, arr=arr.values)

    keys = numpy.asarray(out.dtype.names, dtype="U")
    exponents = keys.flatten().view(numpy.uint32)-48
    exponents = exponents.reshape(len(keys), -1)

    out = numpoly.ndpoly.from_attributes(
        exponents=exponents,
        coefficients=[out[key] for key in out.dtype.names],
        indeterminants=arr.indeterminants,
        dtype=arr.dtype,
        clean=True,
    )
    return out
