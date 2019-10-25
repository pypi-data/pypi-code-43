import numpy as np
from typing import Union

from .interpolantinterpolator1d import InterpolantInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Linear


class LinearInterpolator1D(InterpolantInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support
        support = 2

        # Call super constructor
        super(LinearInterpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

        self._functor = _instantiate_backend_functor(_Linear, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # Case |x| >= 1
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 1
        func = np.where(
            x_abs < 1,
            1 - x_abs,
            func
        )

        return func
