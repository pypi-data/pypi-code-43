import numpy as np
from typing import Union
import warnings

from .interpolantinterpolator1d import InterpolantInterpolator1D
from ._tools import _instantiate_backend_functor
# from pyus.core.cython.imaging.interpolator import _Bspline1


class Bspline1Interpolator1D(InterpolantInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support (and poles)
        # TODO(@dperdios): Daughter of SplineInterp + overriding of prefilter?
        support = 2
        poles = [1]  # -> interpolant interpolator

        # Call super constructor
        super(Bspline1Interpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        warnings.warn('Backend functor not implemented')
        # self._functor = _instantiate_backend_functor(_Bspline1, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        # Pre-computations
        x = np.asarray(x)
        x_abs = np.abs(x)

        # Case 1 <= |x|
        func = np.zeros(shape=x.shape, dtype=x.dtype)

        # Case |x| < 1 (i.e. 0 <= |x| < 1)
        func = np.where(x_abs < 1, 1 - x_abs, func)

        return func
