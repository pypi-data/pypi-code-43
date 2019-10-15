from functools import wraps
from types import FunctionType
import xarray as xr
import sdarray as sd


def to_method(func):
    """Decorator that converts a function to an accessor method."""

    @wraps(func)
    def wrapped(self, *args, **kwargs):
        return func(self.accessed, *args, **kwargs)

    return wrapped


def add_methods(module):
    """Class decorator that adds functions in a module to an accessor."""

    def decorator(cls):
        for name, func in vars(module).items():
            if isinstance(func, FunctionType):
                setattr(cls, name, to_method(func))

        return cls

    return decorator


@xr.register_dataarray_accessor(sd.ACCESSOR)
@add_methods(sd.arrayfunc)
class SDArrayAccessor:
    """DataArray accessor for an SD dataarray."""

    def __init__(self, accessed):
        """Initialize an accessor."""
        self.accessed = accessed
