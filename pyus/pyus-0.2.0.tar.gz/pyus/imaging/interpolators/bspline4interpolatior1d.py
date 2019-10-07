import numpy as np
from typing import Union

from .splineinterpolator1d import SplineInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Bspline4


class Bspline4Interpolator1D(SplineInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support and poles
        support = 5
        poles = [
            np.sqrt(664 - np.sqrt(438976)) + np.sqrt(304) - 19,
            np.sqrt(664 + np.sqrt(438976)) - np.sqrt(304) - 19
        ]

        # Call super constructor
        super(Bspline4Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            poles=poles,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        self._functor = _instantiate_backend_functor(_Bspline4, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # Case 5/2 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 5/2 (i.e. 3/2 <= |x| < 5/2)
        func = np.where(
            np.logical_and(x_abs >= 3 / 2, x_abs < 5 / 2),
            1 / 384 * (625 + x_abs * (
                    -1000 + x_abs * (600 + x_abs * (-160 + 16 * x_abs)))),
            func
        )

        # Case |x| < 3/2 (i.e. 1/2 <= |x| < 3/2)
        func = np.where(
            np.logical_and(x_abs >= 1 / 2, x_abs < 3 / 2),
            1 / 96 * (55 + x_abs * (
                    20 + x_abs * (-120 + x_abs * (80 - 16 * x_abs)))),
            func
        )

        # Case |x| < 1/2 (i.e. 0 <= |x| < 1/2)
        func = np.where(
            x_abs < 1 / 2,
            1 / 192 * (115 + x_abs * x_abs * (-120 + 48 * x_abs * x_abs)),
            func
        )

        return func
