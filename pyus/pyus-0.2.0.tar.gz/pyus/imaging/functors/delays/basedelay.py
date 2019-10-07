from abc import abstractmethod
import numpy as np

from pyus.imaging.functors.basefunctor import BaseFunctor
from pyus.utils.types import Real, _assert_real_number


class BaseDelay(BaseFunctor):
    """Base class for two-way delay laws"""
    def __init__(self, mean_sound_speed: Real, offset: Real, dtype):

        # Call super constructor
        super(BaseDelay, self).__init__(dtype=dtype)

        # Check inputs
        _assert_real_number(mean_sound_speed)
        _assert_real_number(offset)

        # Assign properties
        self._mean_sound_speed = mean_sound_speed
        self._offset = offset

    # Properties
    @property
    def mean_sound_speed(self):
        return self._mean_sound_speed

    @property
    def offset(self):
        return self._offset

    # Abstract Methods
    @abstractmethod
    def _call_no_offset(
            self, im_pos: np.ndarray, el_pos: np.ndarray
    ) -> np.ndarray:
        pass

    # Methods
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:

        t_tot = self._call_no_offset(im_pos=im_pos, el_pos=el_pos)

        return t_tot + self._offset
