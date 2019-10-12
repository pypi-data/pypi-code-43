"""Polynomial base class Polynomial."""
from __future__ import division
import string

import numpy

from .align import align_polynomials
from .array_function import ARRAY_FUNCTIONS
from . import operator

FORWARD_DICT = dict(enumerate(numpy.array(list(string.printable), dtype="S1")))
FORWARD_MAP = numpy.vectorize(FORWARD_DICT.get)
INVERSE_DICT = {value: key for key, value in FORWARD_DICT.items()}
INVERSE_MAP = numpy.vectorize(INVERSE_DICT.get)


def npoly(poly_like, dtype=None):
    """
    Polynomial representation in variable dimensions.

    Examples:
        >>> print(npoly({(1,): 1}))
        q0
        >>> x, y = variable(2)
        >>> print(x**2 + x*y + 2)
        2+q0q1+q0^2
        >>> poly = -3*x + x**2 + y
        >>> print(poly.coefficients)
        [1, -3, 1]
        >>> print(poly.exponents)
        [[0 1]
         [1 0]
         [2 0]]
        >>> print(npoly([x*y, x, y]))
        [q0q1 q0 q1]

        # >>> print(poly([1, 2, 3], [1, 2, 3]))
        # [-1  0  3]
    """
    if poly_like is None:
        poly = Polynomial(keys=[(0,)], shape=())
        poly["0"] = 0

    elif isinstance(poly_like, dict):
        exponents, coefficients = zip(*list(poly_like.items()))
        exponents, coefficients = clean_attributes(exponents, coefficients)
        poly = npoly_from_attributes(exponents, coefficients, dtype)

    elif isinstance(poly_like, Polynomial):
        poly = poly_like.copy()

    elif isinstance(poly_like, (int, float, numpy.ndarray, numpy.generic)):
        poly = npoly_from_attributes([(0,)], [poly_like])

    else:
        poly = compose_polynomial_array(poly_like)

    return poly


def npoly_from_attributes(exponents, coefficients, dtype=None):
    dtype = coefficients.dtype if dtype is None else dtype
    poly = Polynomial(
        keys=exponents, shape=coefficients.shape[1:], dtype=dtype)
    for key, values in zip(poly._keys, coefficients):
        poly[key] = values
    return poly


def clean_attributes(exponents, coefficients):
    exponents = numpy.asarray(exponents, dtype=int)
    coefficients = numpy.asarray(coefficients)
    assert len(exponents.shape) == 2, exponents
    assert len(exponents) == len(coefficients)

    # remove dead space
    empty = numpy.all(coefficients.reshape(len(coefficients), -1) == 0, -1)
    if numpy.all(empty):
        exponents = numpy.zeros((1, exponents.shape[-1]), dtype=int)
        coefficients = numpy.zeros(1, dtype=coefficients.dtype)
    else:
        exponents = exponents[~empty]
        coefficients = coefficients[~empty]

    assert len(numpy.unique(exponents, axis=0)) == exponents.shape[0]

    exponents.setflags(write=False)
    coefficients.setflags(write=False)
    return exponents, coefficients


class Polynomial(numpy.ndarray):
    """
    Polynomial representation in variable dimensions.

    Examples:
        >>> poly = Polynomial(keys=[(0,), (1,)], shape=(3,))
        >>> print(poly._keys)
        ['0' '1']
        >>> print(poly.exponents)
        [[0]
         [1]]
        >>> print(poly.shape)
        (3,)
        >>> poly["0"] = 1, 2, 3
        >>> poly["1"] = 4, 5, 6
        >>> print(numpy.array(list(poly.coefficients)))
        [[1 2 3]
         [4 5 6]]
        >>> print(poly)
        [1+4q0 2+5q0 3+6q0]
        >>> print(poly[0])
        1+4q0
    """

    __array_priority__ = 16

    def __new__(cls, keys=[(0,)], shape=(), dtype=None, buffer=None, offset=0,
                strides=None, order=None, info=None):

        keys = numpy.array(keys, dtype=int)
        dtype_ = "S%d" % keys.shape[1]
        keys = FORWARD_MAP(keys).flatten()
        keys = numpy.array(keys.view(dtype_), dtype="U")

        dtype = int if dtype is None else dtype
        dtype_ = numpy.dtype([(key, dtype) for key in keys])


        obj = super(Polynomial, cls).__new__(
            cls, shape, dtype_, buffer, offset, strides, order)
        obj._dtype = dtype
        obj._keys = keys
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._keys = getattr(obj, "_keys", None)
        self._dtype = getattr(obj, "_dtype", None)

    def __array_ufunc__(self, ufunc, method, poly, **kwargs):
        coefficients = numpy.array(poly.coefficients)
        if "axis" in kwargs:
            axis = kwargs["axis"]
            if axis is None:
                coefficients = coefficients.reshape(len(coefficients), -1)
                axis = 1
            else:
                axis = axis+1 if axis >= 0 else len(coefficients.shape)+axis
            kwargs["axis"] = axis

        coefficients = super(Polynomial, self).__array_ufunc__(
            ufunc, method, coefficients, **kwargs)
        return npoly_from_attributes(poly.exponents, coefficients)

    def __array_function__(self, func, types, args, kwargs):
        if func not in ARRAY_FUNCTIONS:
            return super(Polynomial, self).__array_function__(
                func, types, args, kwargs)
        if not all(issubclass(type_, Polynomial) for type_ in types):
            return NotImplemented
        return ARRAY_FUNCTIONS[func](func, *args, **kwargs)

    @property
    def exponents(self):
        keys = numpy.array(self._keys, dtype="S")
        keys = keys.view("S1").reshape(len(keys), -1)
        return INVERSE_MAP(keys)

    @property
    def coefficients(self):
        out = numpy.empty((len(self._keys),) + self.shape, dtype=self._dtype)
        for idx, key in enumerate(self._keys):
            out[idx] = numpy.ndarray.__getitem__(self, key)
        return list(out)

    @staticmethod
    def from_attributes(exponents, coefficients):
        return npoly_from_attributes(
            numpy.asarray(exponents, dtype=int), numpy.asarray(coefficients))

    def todict(self):
        """
        Cast polynomial to dict where keys are exponents and values are
        coefficients.
        """
        return {tuple(exponent): coefficient
                for exponent, coefficient in zip(
                    self.exponents, self.coefficients)}

    def __abs__(self):
        """Absolute value"""
        return npoly_from_attributes(
            self.exponents, numpy.abs(self.coefficients))

    def __add__(self, other):
        """Left addition"""
        self, other = align_polynomials(self, other)
        return operator.poly_add(self, other)

    def __call__(self, *args):
        """Evaluate polynomial"""
        return operator.poly_call(self, *args)

    def __getitem__(self, index):
        return operator.poly_getitem(self, index)

    def __div__(self, other):
        """Left division"""
        return operator.poly_mul(self, numpy.asarray(other)**-1)

    def __eq__(self, other):
        """Left equality"""
        self, other = align_polynomials(self, other)
        return operator.poly_eq(self, other)

    def __floordiv__(self, other):
        """Left floor division"""
        poly = operator.poly_mul(self, numpy.asfarray(other)**-1)
        return npoly_from_attributes(
            poly.exponents, numpy.floor(poly.coefficients).astype(int))

    def __getitem__(self, index):
        """Get item."""
        return operator.poly_getitem(self, index)

    def __iter__(self):
        coefficients = numpy.array(list(self.coefficients))
        return iter(npoly_from_attributes(self.exponents, coefficients[:, idx])
                    for idx in range(len(self)))

    def __len__(self):
        return self.shape[0]

    def __mul__(self, other):
        """Left multiplication"""
        return operator.poly_mul(*align_polynomials(self, other))

    def __ne__(self, other):
        """Not equal"""
        self, other = align_polynomials(self, other)
        return ~operator.poly_eq(self, other)

    def __neg__(self):
        """Negative"""
        return npoly_from_attributes(
            self.exponents, -numpy.array(self.coefficients))

    def __pos__(self):
        """Positive"""
        return self.copy()

    def __pow__(self, other):
        """Left power"""
        other = numpy.asarray(other)
        assert numpy.all(other == numpy.asarray(other, dtype=int))
        assert other.size == 1
        return operator.poly_pow(self, other)

    def __radd__(self, other):
        """Right addition"""
        return operator.poly_add(*align_polynomials(other, self))

    def __repr__(self):
        """
        Examples:
            >>> npoly({(0,): 4, (2,): 6})
            4+6*q0**2
            >>> npoly({(0,): [1., 0., 3.], (1,): [0., -5., -1.]})
            npoly([1.0, -5.0*q0, 3.0-1.0*q0])
            >>> npoly({
            ...     (0, 0,): [[[1., 2.], [3., 4.]]],
            ...     (0, 4,): [[[4., 5.], [6., 7.]]]})
            npoly([[[1.0+4.0*q1**4, 2.0+5.0*q1**4],
                    [3.0+6.0*q1**4, 4.0+7.0*q1**4]]])
        """
        array = operator.construct_str_array(self, sep="*", power="**")
        if isinstance(array, str):
            return array
        prefix = "npoly("
        suffix = ")"
        return prefix + numpy.array2string(
            numpy.array(array),
            formatter={"all": str},
            separator=", ",
            prefix=prefix,
            suffix=suffix,
        ) + suffix

    def __rmul__(self, other):
        """Right multiplication"""
        return operator.poly_mul(*align_polynomials(other, self))

    def __rsub___(self):
        """Right subtraction"""
        self, other = align_polynomials(self, other)
        return operator.poly_add(other, -self)

    def __str__(self):
        """
        Examples:
            >>> print(npoly({(0,): 4, (2,): 6}))
            4+6q0^2
            >>> print(npoly({(0,): [1., 0., 3.], (1,): [0., -5., -1.]}))
            [1.0 -5.0q0 3.0-1.0q0]
            >>> print(npoly({
            ...     (0,): [[[1., 2.], [3., 4.]]],
            ...     (1,): [[[4., 5.], [6., 7.]]]}))
            [[[1.0+4.0q0 2.0+5.0q0]
              [3.0+6.0q0 4.0+7.0q0]]]
        """
        array = numpy.array(operator.construct_str_array(self))
        return numpy.array2string(
            array,
            formatter={"all": str},
            separator=" ",
        )

    def __sub__(self, other):
        """Left subtraction"""
        self, other = align_polynomials(self, other)
        return operator.poly_add(self, -other)

    def __truediv__(self, other):
        """Left true division"""
        return operator.poly_mul(self, numpy.asfarray(other)**-1)


def variable(dimensions=1, dtype="i8"):
    """
    Simple constructor to create single variables to create polynomials.

    Args:
        dimensions (int):
            Number of dimensions in the array.
        dtype:

    Returns:
        (Poly):
            Polynomial array with unit components in each dimension.

    Examples:
        >>> print(variable())
        q0
        >>> print(variable(3))
        [q0 q1 q2]
    """
    keys = numpy.eye(dimensions, dtype=dtype)
    values = numpy.eye(dimensions, dtype=dtype)
    if dimensions == 1:
        values = values[0]
    return npoly_from_attributes(keys, values)


def compose_polynomial_array(arrays):
    arrays = numpy.array(arrays, dtype=object)
    shape = arrays.shape
    arrays = arrays.flatten().tolist()

    dtypes = []
    keys = {(0,)}
    for array in arrays:
        if isinstance(array, Polynomial):
            dtypes.append(array._dtype)
            keys = keys.union([tuple(key) for key in array.exponents.tolist()])
        elif isinstance(array, (numpy.generic, numpy.ndarray)):
            dtypes.append(array.dtype)
        else:
            dtypes.append(type(array))

    dtype = numpy.find_common_type(dtypes, [])
    length = max([len(key) for key in keys])

    collection = {}
    for idx, array in enumerate(arrays):
        if isinstance(array, Polynomial):
            for key, value in zip(array.exponents, array.coefficients):
                key = tuple(key)+(0,)*(length-len(key))
                if key not in collection:
                    collection[key] = numpy.zeros(len(arrays), dtype=dtype)
                collection[key][idx] = value
        else:
            key = (0,)*length
            if key not in collection:
                collection[key] = numpy.zeros(len(arrays), dtype=dtype)
            collection[key][idx] = array

    exponents = sorted(collection)
    coefficients = numpy.array([collection[key] for key in exponents])
    coefficients = coefficients.reshape(-1, *shape)

    return npoly_from_attributes(exponents, coefficients)


def zeros(keys, shape, dtype=None):
    poly = Polynomial(keys=keys, shape=shape, dtype=dtype)
    for key in poly._keys:
        poly[key] = 0
    return poly
