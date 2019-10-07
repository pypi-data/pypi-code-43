from abc import ABCMeta, abstractmethod
import numpy as np
from typing import List, Tuple

from pyus.probe.baseprobe import BaseProbe
from pyus.imaging.interpolators.baseinterpolator1d import BaseInterpolator1D
from pyus.imaging.delays import BaseDelay
from pyus.imaging.windows import BaseWindow
from pyus.utils.types import (
    _assert_1d_array, _is_elem_identical, get_compat_real_dtype
)


class BaseDelayAndSumRF(metaclass=ABCMeta):
    """Abstract class for DelayAndSumRF objects"""
    def __init__(
            self,
            probe: BaseProbe,
            time_axis: np.ndarray,
            image_axes: Tuple[np.ndarray, np.ndarray, np.ndarray],
            dtype=None
    ):

        # Data type
        # TODO(@dperdios): check dtype
        dtype = np.dtype(dtype)  # make sure it is a valid dtype
        dtype_str_list = ['f4', 'f8', 'c8', 'c16']
        dtype_list = [np.dtype(t) for t in dtype_str_list]
        if dtype in dtype_list:
            self._dtype = dtype
        else:
            raise ValueError('Unsupported dtype')
        #   Corresponding real data type (in case of complex data)
        real_dtype = get_compat_real_dtype(dtype=dtype)

        # Time axis
        _assert_1d_array(time_axis)
        time_axis = time_axis.astype(dtype=real_dtype)
        self._time_axis = time_axis
        sample_number = time_axis.size
        self._sample_number = sample_number

        # Probe
        if not isinstance(probe, BaseProbe):
            raise TypeError('Must be a `BaseProbe`')
        element_positions = probe.element_positions.astype(dtype=real_dtype)
        element_number = probe.element_number
        self._element_number = element_number
        self._element_positions = element_positions

        # Data shape
        self._event_shape = (element_number, sample_number)

        # Image shape and axes
        image_axes = tuple(ax.astype(dtype=real_dtype) for ax in image_axes)
        self._image_axes = image_axes
        image_shape = tuple(ax.size for ax in image_axes)
        self._image_shape = image_shape

    # Properties
    @property
    def dtype(self):
        return self._dtype

    @property
    def element_positions(self):
        return self._element_positions.copy()

    @property
    def image_axes(self):
        return tuple([ax.copy() for ax in self._image_axes])

    @property
    def image_shape(self):
        return self._image_shape

    @property
    def event_shape(self):
        return self._event_shape

    # Abstract methods
    @abstractmethod
    def _reconstruct(
            self,
            data: np.ndarray,
            interpolator: BaseInterpolator1D,
            delays: List[BaseDelay],
            apodization: BaseWindow,
    ) -> np.ndarray:
        pass

    # Methods
    def reconstruct(
            self,
            data: np.ndarray,
            interpolator: BaseInterpolator1D,
            delays: List[BaseDelay],
            apodization: BaseWindow,
    ):

        # Checks on inputs
        #   Interpolator
        if not isinstance(interpolator, BaseInterpolator1D):
            raise TypeError('Must be a `BaseInterpolator1D`')
        interpolator._assert_data_compat(data=data)
        interpolator._assert_axis_lim_compat(data_axis=self._time_axis)
        #   Delays
        _delay_types = [type(d) for d in delays]
        if not (_is_elem_identical(_delay_types)
                and isinstance(delays[0], BaseDelay)):
            raise TypeError('Must be a list of `BaseDelay`')
        #   Event number
        inp_data_shape = data.shape
        if inp_data_shape[1] != len(delays):
            raise ValueError('Delay list and data dimension mismatch')
        #   Data shape
        if data.ndim != 4:
            raise TypeError('Invalid data shape: must be a 4D NumPy array')
        event_number = len(delays)
        frame_number = inp_data_shape[0]
        if inp_data_shape[-2:] != self._event_shape:
            exp_data_shape = (frame_number, event_number, *self._event_shape)
            raise ValueError(
                'Invalid data shape: current shape={}, '
                'expected shape={}'.format(inp_data_shape, exp_data_shape)
            )

        # Launch forward operator
        beamformed_data = self._reconstruct(
            data=data,
            interpolator=interpolator,
            delays=delays,
            apodization=apodization
        )

        return beamformed_data
