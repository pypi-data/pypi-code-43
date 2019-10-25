from typing import Optional
from abc import ABCMeta, abstractmethod
import numpy as np
from pyus.utils.types import Real, _assert_3d_point_stack


class BaseProbe(metaclass=ABCMeta):
    def __init__(
            self,
            name: str,
            center_frequency: Real,
            element_positions: np.ndarray,
            element_width: Real,
            element_height: Real,
            bandwidth: Optional[Real] = None
    ):

        # Name
        if not isinstance(name, str):
            raise TypeError('Must be a string')
        self._name = name

        # Center frequency
        self._center_frequency = center_frequency

        # Element positions and number
        if not isinstance(element_positions, np.ndarray):
            raise TypeError('Must be a NumPy array')
        _assert_3d_point_stack(element_positions)
        self._element_positions = element_positions
        element_number = element_positions.shape[0]
        self._element_number = element_number

        # Element properties
        self._element_width = element_width
        self._element_height = element_height
        self._bandwidth = bandwidth

    # Properties
    @property
    def name(self):
        return self._name

    @property
    def center_frequency(self):
        return self._center_frequency

    @property
    def element_number(self):
        return self._element_number

    @property
    def element_width(self):
        return self._element_width

    @property
    def element_height(self):
        return self._element_height

    @property
    def bandwidth(self):
        return self._bandwidth

    @property
    def element_positions(self):
        return self._element_positions.copy()

    @property
    @abstractmethod
    def width(self) -> Real: pass

    @property
    @abstractmethod
    def height(self) -> Real: pass
