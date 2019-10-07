from abc import ABCMeta, abstractmethod
import numpy as np
from typing import Union

from pyus.utils.types import (
    _assert_1d_array, get_compat_real_dtype, _assert_str
)


class BaseInterpolator1D(metaclass=ABCMeta):
    """Base abstract class for 1D interpolator objects"""
    def __init__(
            self, data_axis: np.ndarray, support: int, boundary: str, dtype
    ):

        # Data type
        dtype = np.dtype(dtype)
        self._dtype = dtype

        # Indexes data type
        self._real_dtype = get_compat_real_dtype(dtype=dtype)
        # TODO(@dperdios): deduce it from `dtype` for consistent accuracy?
        int_dtype = np.dtype(np.int32)
        self._int_dtype = int_dtype

        # Data axis
        if not isinstance(data_axis, np.ndarray):
            raise TypeError('Must be a NumPy array')
        _assert_1d_array(data_axis)
        # TODO(@dperdios): check regular ascending array + extract fs
        # TODO(@dperdios): check data_axis dtype?
        # TODO(@dperdios): issue with length=1
        self._data_len = data_axis.size
        self._data_lim = (data_axis[0], data_axis[-1])
        self._sampling_frequency = 1 / (data_axis[1] - data_axis[0])

        # Boundary condition
        _assert_str(boundary)
        boundary = boundary.lower()
        valid_boundary = ('mirror', 'reflect', 'zero')
        if boundary not in valid_boundary:
            raise NotImplementedError('Unsupported boundary condition')
        self._boundary = boundary.lower()

        # Support and order
        # TODO(@dperdios): assert integer
        self._support = support

        # Indexes
        idx_offset = 0.5 if support & 1 else 0.0  # offset for odd supports
        idx_span = np.arange(support, dtype=int_dtype) - (support - 1) // 2
        self._idx_offset = idx_offset
        self._idx_span = idx_span

        self._functor = None

    # Properties
    @property
    def dtype(self):
        return self._dtype

    @property
    def support(self):
        return self._support

    @property
    def boundary(self):
        return self._boundary

    @property
    def pad_left(self):
        return (self._support - 1) // 2

    @property
    def pad_right(self):
        return self._support // 2

    # Abstract methods
    @abstractmethod
    def _prefilter(self, data: np.ndarray) -> np.ndarray:
        pass

    @staticmethod
    @abstractmethod
    def _func(x: Union[float, np.ndarray]):
        pass

    # Methods
    def prefilter(self, data: np.ndarray) -> np.ndarray:
        # Batch pre-filtering along last axis, data: (..., N)
        return self._prefilter(data=data)

    def interpolate(
            self, data: np.ndarray, eval_axis: np.ndarray
    ) -> np.ndarray:

        # Input checks
        _assert_1d_array(data)
        _assert_1d_array(eval_axis)

        # Get properties
        dtype = self._real_dtype
        sampling_frequency = self._sampling_frequency
        x_min, x_max = self._data_lim
        data_len = self._data_len

        # Indexes
        #   Compute rational indexes
        rat_indexes = (eval_axis - x_min) * sampling_frequency
        #   Compute corresponding integer indexes (including support)
        indexes = self._indexes(ind=rat_indexes)

        # Interpolation weights
        weights = self._func(np.subtract(indexes, rat_indexes, dtype=dtype))

        # Out of bounds
        valid = np.logical_and(eval_axis >= x_min, eval_axis <= x_max)

        # Boundary conditions
        # TODO(@dperdios): function to apply boundary condition?
        bc_l = np.logical_and(valid, indexes < 0)
        bc_r = np.logical_and(valid, indexes >= data_len)  # TODO: >= or >?
        if self._boundary in ['mirror', 'reflect']:
            len_2 = 2 * data_len - 2
            # idx_new = np.mod(idx, len_2)
            # idx = np.where(idx_new >= data_len, len_2 - idx_new, idx_new)
            # TODO(@dperdios): infinite signal required in our case?
            indexes = np.where(bc_l, - indexes - len_2 * (-indexes // len_2), indexes)
            indexes = np.where(bc_r, len_2 - indexes, indexes)
        elif self._boundary == 'zero':
            indexes = np.where(bc_l, 0, indexes)  # dumb index
            indexes = np.where(bc_r, 0, indexes)  # dumb index
            # valid = np.logical_or(valid, np.logical_or(left_bc, right_bc))
            weights[bc_l] = 0
            weights[bc_r] = 0
        else:
            raise NotImplementedError('Unknown boundary condition')

        indexes *= valid  # remove out-of-bounds indexes (dumb value)
        weights *= valid  # remove out-of-bounds factors (dumb value)

        # Interpolation by summation
        data_interp = (data[indexes] * weights).sum(axis=0)

        return data_interp

    def _indexes(self, ind: Union[float, np.ndarray]) -> np.ndarray:

        # Extract property
        dtype = self._int_dtype

        # idx_fl = ind.astype(copy=True, dtype=dtype)
        # idx_fl = np.floor(ind)
        idx_fl = np.floor(ind + self._idx_offset).astype(dtype=dtype)

        # TODO(@dperdios): check fastest axis for computations
        # First axis
        idx = np.array([s + idx_fl for s in self._idx_span], dtype=dtype)
        # _ns = tuple([self.support] + idx_fl.ndim * [1])
        # idx = idx_fl + self._idx_span.reshape(_ns)
        # # Last axis
        # idx = idx_fl[..., np.newaxis] + self._idx_span
        return idx

    def func(self, x: Union[float, np.ndarray]) -> np.ndarray:
        return self._func(x=x)

    # Methods
    # TODO(@dperdios): assertion methods as static? or in "module"?
    def _assert_data_compat(self, data: np.ndarray):
        # Assert if data length compatibility w.r.t. object construction
        data_len = data.shape[-1]
        interp_len = self._data_len
        if not interp_len == data_len:
            raise ValueError(
                'Incompatible data length: current length={}, '
                'expected length={}'.format(interp_len, data_len)
            )

    def _assert_axis_lim_compat(self, data_axis: np.ndarray):
        # Assert data axis compatibility w.r.t. object construction
        data_lim = (data_axis[0], data_axis[-1])
        expected_lim = self._data_lim
        if not data_lim == expected_lim:
            raise ValueError(
                'Incompatible data limits: current limits={}, '
                'expected limits={}'.format(data_lim, expected_lim)
            )
