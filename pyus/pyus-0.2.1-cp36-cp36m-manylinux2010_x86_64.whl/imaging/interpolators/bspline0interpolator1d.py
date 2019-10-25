import numpy as np
from typing import Union
import warnings

from .interpolantinterpolator1d import InterpolantInterpolator1D
from ._tools import _instantiate_backend_functor
# from pyus.core.cython.imaging.interpolator import _Bspline1


class Bspline0Interpolator1D(InterpolantInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        support = 1
        poles = [1]  # -> interpolant interpolator

        super(Bspline0Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

        warnings.warn('Backend functor not implemented')
        # self._functor = _instantiate_backend_functor(_Bspline1, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # TODO(@dperdios): check exact def. (Thevenaz et al.)
        # # Case 1/2 <= |x|
        # func = np.zeros(shape=x.shape, dtype=x.dtype)
        #
        # # Case |x| == 1/2
        # func = np.where(x_abs == 1 / 2, 1 / 2, func)
        #
        # # Case |x| < 1/2 (i.e. 0 <= |x| < 1/2)
        # func = np.where(x_abs < 1 / 2, 1, func)

        # Case 1/2 < |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| <= 1/2 (i.e. 0 <= |x| <= 1/2)
        func = np.where(x_abs <= 1 / 2, 1, func)

        return func
