from abc import abstractmethod
from .baseinterpolator1d import BaseInterpolator1D
import numpy as np
from typing import Union


class InterpolantInterpolator1D(BaseInterpolator1D):
    """Abstract class for "interpolant" interpolator objects not requiring
    any pre-filtering. Cannot be instantiated
    """
    def __init__(
            self,
            data_axis: np.ndarray,
            support: int,
            boundary: str,
            dtype
    ):

        # Call super constructor
        super(InterpolantInterpolator1D, self).__init__(
            data_axis=data_axis,
            support=support,
            boundary=boundary,
            dtype=dtype
        )

    # Abstract methods
    @staticmethod
    @abstractmethod
    def _func(x: Union[float, np.ndarray]):
        pass

    # Methods
    def _prefilter(self, data: np.ndarray) -> np.ndarray:
        return data.copy()
