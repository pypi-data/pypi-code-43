__all__ = ["zeros_like", "ones_like"]

import xarray as xr


def zeros_like(array, dtype=None):
    """Make a dataarray filled with zeros keeping shape of an input."""
    return xr.zeros_like(array, dtype)


def ones_like(array, dtype=None):
    """Make a dataarray filled with ones keeping shape of an input."""
    return xr.ones_like(array, dtype)
