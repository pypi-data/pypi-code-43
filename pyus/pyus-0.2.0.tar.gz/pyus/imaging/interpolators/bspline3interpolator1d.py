import numpy as np
from typing import Union

from .splineinterpolator1d import SplineInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Bspline3


class Bspline3Interpolator1D(SplineInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support and poles
        support = 4
        poles = [np.sqrt(3) - 2]

        # Call super constructor
        super(Bspline3Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            poles=poles,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        self._functor = _instantiate_backend_functor(_Bspline3, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # Case 2 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 2 (i.e. 1 <= |x| < 2)
        func = np.where(
            np.logical_and(x_abs >= 1, x_abs < 2),
            1 / 6 * (2 - x_abs) * (2 - x_abs) * (2 - x_abs),
            func
        )

        # Case |x| < 1 (i.e. 0 <= |x| < 1)
        func = np.where(
            x_abs < 1,
            2 / 3 - 1 / 2 * x_abs * x_abs * (2 - x_abs),
            func
        )

        return func
