import numpy as np
from typing import Union

from .interpolantinterpolator1d import InterpolantInterpolator1D
from ._tools import _instantiate_backend_functor
from pyus.core.cython.imaging.interpolator import _Nearest


class NearestInterpolator1D(InterpolantInterpolator1D):

    def __init__(self, data_axis: np.ndarray, boundary: str, dtype=None):

        # Support
        support = 1

        # Call super constructor
        super(NearestInterpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

        # Attach backend functor
        self._functor = _instantiate_backend_functor(_Nearest, data_axis)

    # Methods
    @staticmethod
    def _func(x: Union[float, np.ndarray]):
        x = np.asarray(x)
        # -1/2 >= x <= 1/2  # TODO: or -1/2 >= x < 1/2? see Thevenaz
        func = np.zeros(shape=x.shape, dtype=x.dtype)
        func = np.where(
            np.logical_and(x >= -1 / 2, x <= 1 / 2),
            1.,
            func
        )

        return func
