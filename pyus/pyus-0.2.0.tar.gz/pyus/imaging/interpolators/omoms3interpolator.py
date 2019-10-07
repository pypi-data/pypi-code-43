import numpy as np
from typing import Union

from .splineinterpolator1d import SplineInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Omoms3


class Omoms3Interpolator1D(SplineInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support and poles
        support = 4
        poles = [1/8 * (-13 + np.sqrt(105))]

        # Call super constructor
        super(Omoms3Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            poles=poles,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        self._functor = _instantiate_backend_functor(_Omoms3, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)
        x_abs_2 = x_abs * x_abs
        x_abs_3 = x_abs_2 * x_abs

        # Case 2 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 2 (i.e. 1 <= |x| < 2)
        func = np.where(
            np.logical_and(x_abs >= 1, x_abs < 2),
            - 1 / 6 * x_abs_3 + x_abs_2 - 85 / 42 * x_abs + 29 / 21,
            func
        )

        # Case |x| < 1 (i.e. 0 <= |x| < 1)
        func = np.where(
            x_abs < 1,
            1 / 2 * x_abs_3 - x_abs_2 + 1 / 14 * x_abs + 13 / 21,
            func
        )

        return func
