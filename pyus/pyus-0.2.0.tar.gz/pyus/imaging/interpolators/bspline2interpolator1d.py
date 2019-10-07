import numpy as np
from typing import Union
import warnings

from .splineinterpolator1d import SplineInterpolator1D
from ._tools import _instantiate_backend_functor
# from pyus.core.cython.imaging.interpolator import _Bspline2


class Bspline2Interpolator1D(SplineInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support and poles
        support = 3
        poles = [2 * np.sqrt(2) - 3]

        # Call super constructor
        super(Bspline2Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            poles=poles,
            boundary=boundary,
            dtype=dtype
        )

        warnings.warn('Backend functor not implemented')
        # self._functor = _instantiate_backend_functor(_Bspline2, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # Case 3/2 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 3/2 (i.e. 1/2 <= |x| < 3/2)
        func = np.where(
            np.logical_and(x_abs >= 1 / 2, x_abs < 3 / 2),
            # 1 / 8 * (3 - 2 * x_abs) * (3 - 2 * x_abs),
            9 / 8 - (3 * x_abs) / 2 + x_abs * x_abs / 2,
            func
        )

        # Case |x| < 1/2 (i.e. 0 <= |x| < 1/2)
        func = np.where(x_abs < 1 / 2, 3 / 4 - x_abs * x_abs, func)

        return func
