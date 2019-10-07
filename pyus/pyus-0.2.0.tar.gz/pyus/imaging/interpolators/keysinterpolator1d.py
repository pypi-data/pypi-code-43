import numpy as np
from typing import Union

from .interpolantinterpolator1d import InterpolantInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Keys


class KeysInterpolator1D(InterpolantInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support
        support = 4

        # Call super constructor
        super(KeysInterpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        self._functor = _instantiate_backend_functor(_Keys, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)
        x_abs_2 = x_abs * x_abs
        x_abs_3 = x_abs_2 * x_abs
        a = -0.5  # best interpolation order (i.e. 3) achievable with a = -1/2

        # Case 2 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 2 (i.e. 1 <= |x| < 2)
        func = np.where(
            # x_abs < 2,
            np.logical_and(x_abs >= 1, x_abs < 2),
            a * x_abs_3 - 5 * a * x_abs_2 + 8 * a * x_abs - 4 * a,
            func
        )

        # Case |x| < 1 (i.e. 0 <= |x| < 1)
        func = np.where(
            x_abs < 1,
            (a + 2) * x_abs_3 - (a + 3) * x_abs_2 + 1,
            func
        )

        return func
