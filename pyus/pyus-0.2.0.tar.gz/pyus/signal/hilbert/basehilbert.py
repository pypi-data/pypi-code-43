from abc import ABCMeta, abstractmethod
import numpy as np
from typing import Tuple


class BaseHilbert(metaclass=ABCMeta):

    def __init__(self, data_shape: Tuple[int, ...], axis: int, dtype):

        # Check inputs
        dtype = np.dtype(dtype)
        # TODO(@dperdios): add checks on data_shape and axis (as for convols)
        if axis != -1:
            raise NotImplementedError()

        # Get output dtype w.r.t. input dtype
        out_dtype = np.result_type(dtype, 1j)

        # Assign properties
        self._dtype = dtype
        self._data_shape = data_shape
        self._axis = axis
        self._out_dtype = out_dtype

    # Properties
    @property
    def dtype(self):
        return self._dtype

    # Abstract methods
    @abstractmethod
    def _call(self, x: np.ndarray) -> np.ndarray:
        pass

    # Methods
    def __call__(self, x: np.ndarray) -> np.ndarray:

        # Check input shape
        if x.shape != self._data_shape:
            raise ValueError('Invalid shape')

        return self._call(x=x)
