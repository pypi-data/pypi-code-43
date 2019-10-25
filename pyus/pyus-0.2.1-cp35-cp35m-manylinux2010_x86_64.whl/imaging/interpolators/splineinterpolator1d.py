from abc import abstractmethod
from .baseinterpolator1d import BaseInterpolator1D
import numpy as np
from typing import Sequence, Union

from pyus.utils.types import get_compat_real_dtype
from ._core import _data_to_coeffs


class SplineInterpolator1D(BaseInterpolator1D):
    """Abstract class for spline interpolator objects requiringpre-filtering.
    """

    def __init__(
            self, data_axis: np.ndarray,
            support: int,
            poles: Sequence[float],
            boundary: str,
            dtype
    ):

        # Call super constructor
        super(SplineInterpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

        # Assign properties
        # TODO: check iterable of floats
        self._poles = np.asarray(poles, dtype=self._real_dtype)

    # Properties
    @property
    def poles(self) -> np.ndarray:
        return self._poles.copy()

    # Abstract methods
    @staticmethod
    @abstractmethod
    def _func(x: Union[float, np.ndarray]):
        pass

    # Methods
    def _prefilter(self, data: np.ndarray) -> np.ndarray:
        # In-place filtering (on copied data)
        data_flt = data.copy()
        _data_to_coeffs(
            data=data_flt, poles=self._poles, boundary=self._boundary, tol=0
        )
        return data_flt
