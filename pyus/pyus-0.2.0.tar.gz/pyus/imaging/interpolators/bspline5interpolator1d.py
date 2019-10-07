import numpy as np
from typing import Union

from .splineinterpolator1d import SplineInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Bspline5


class Bspline5Interpolator1D(SplineInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support and poles
        support = 6
        poles = [
            np.sqrt(135 / 2 - np.sqrt(17745 / 4)) + np.sqrt(105 / 4) - 13 / 2,
            np.sqrt(135 / 2 + np.sqrt(17745 / 4)) - np.sqrt(105 / 4) - 13 / 2
        ]

        # Call super constructor
        super(Bspline5Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            poles=poles,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        self._functor = _instantiate_backend_functor(_Bspline5, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # Case 3 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 3 (i.e. 2 <= |x| < 3)
        func = np.where(
            np.logical_and(x_abs >= 2, x_abs < 3),
            1 / 120 * (243 + x_abs * (-405 + x_abs * (
                    270 + x_abs * (-90 + x_abs * (15 - x_abs))))),
            func
        )

        # Case |x| < 2 (i.e. 1 <= |x| < 2)
        func = np.where(
            np.logical_and(x_abs >= 1, x_abs < 2),
            1 / 120 * (51 + x_abs * (75 + x_abs * (
                    -210 + x_abs * (150 + x_abs * (-45 + x_abs * 5))))),
            func
        )

        # Case |x| < 1 (i.e. 0 <= |x| < 1)
        func = np.where(
            x_abs < 1,
            1 / 60 * (33 + x_abs * x_abs * (
                    -30 + x_abs * x_abs * (15 - 5 * x_abs))),
            func
        )

        return func
