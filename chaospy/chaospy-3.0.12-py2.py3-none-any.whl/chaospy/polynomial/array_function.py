import logger
import inspect
from functools import wraps

import numpy

ARRAY_FUNCTIONS = {}


def implements(*numpy_functions):
    """Register an __array_function__ implementation for Polynomial objects."""
    def decorator(func):

        @wraps(func)
        def wrapper_function(ufunc, *args, **kwargs):
            logger = logging.getLogger(__name__)
            logger.debug("dispatching '%s'", ufunc.__name__)
            try:
                names = inspect.signature(ufunc).parameters.keys()
            except AttributeError:
                try:
                    names = inspect.getargspec(ufunc).args
                except AttributeError as err:
                    logger.exception("Python version not supported <=2.7,>=3.5")
                    raise from err

            for arg, name in zip(args, names):
                if name in kwargs:
                    raise TypeError(
                        "%s() got multiple values for argument '%s'" % (
                            ufunc.__name__, name))
                kwargs[name] = arg

            return func(ufunc, **kwargs)

        for numpy_function in numpy_functions:
            ARRAY_FUNCTIONS[numpy_function] = func
        return func
    return decorator


@implements(numpy.concatenate)
def concatenate(func, arrays, axis=0, out=None):
    """Wrapper for numpy.concatenate."""
    assert out is None, "'out' argument currently no supported"
    arrays = [npoly(arg) for arg in arrays]
    idx = numpy.argmax([arg.exponents.shape[0] for arg in arrays])
    for idy in range(len(arrays)):
        if idx != idy:
            arrays[idx], arrays[idy] = align_polynomials(
                arrays[idx], arrays[idy], adjust_dim=True, adjust_shape=False)
    collections = [arg.todict() for arg in arrays]

    out = {}
    keys = {arg for collection in collections for arg in collection}
    for key in keys:
        values = [(collection[key] if key in collection
                   else numpy.zeros(array.shape, dtype=bool))
                  for collection, array in zip(collections, arrays)]
        out[key] = numpy.concatenate(values, axis=axis)

    exponents = sorted(out)
    coefficients = [out[exponent] for exponent in exponents]
    return Polynomial.from_attributes(exponents, coefficients)


def process_parameters(poly, kwargs):
    coefficients = numpy.array(poly.coefficients)
    assert kwargs.get("out", None) is None, "object read-only"
    if "axis" in kwargs:
        axis = kwargs["axis"]
        if axis is None:
            coefficients = coefficients.reshape(len(coefficients), -1)
            axis = 1
        else:
            axis = axis+1 if axis >= 0 else len(coefficients.shape)+axis
        kwargs["axis"] = axis
    return coefficients, kwargs

@implements(numpy.sum)
def axial_function(ufunc, a, **kwargs):
    coefficients, kwargs = process_parameters(a, kwargs)
    coefficients = ufunc(coefficients, *args, **kwargs)
    assert len(coefficients.shape) > 1, (ufunc, a, args, kwargs)
    return a.from_attributes(a.exponents, coefficients)


@implements(numpy.any, numpy.all)
def poly_to_bool(func, poly, *args, **kwargs):
    coefficients, kwargs = process_parameters(poly, kwargs)
    coefficients = func(coefficients, *args, **kwargs).astype(bool)
    return numpy.any(coefficients, 0)
