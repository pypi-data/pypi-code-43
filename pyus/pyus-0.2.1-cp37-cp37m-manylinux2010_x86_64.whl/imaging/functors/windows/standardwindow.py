import numpy as np
from abc import abstractmethod
from .basewindow import BaseWindow
from pyus.utils.types import Real


class StandardWindow(BaseWindow):
    """Abstract class for standard ultrasound windows"""
    def __init__(self, f_number: Real, dtype):

        # Call super constructor
        super(StandardWindow, self).__init__(dtype=dtype)

        # TODO(@dperdios): add check
        self._f_number = f_number

    # Properties
    @property
    def f_number(self):
        return self._f_number

    # @f_number.setter
    # def f_number(self, value: Real):
    #     self._f_number = value
    # TODO: do we really want a setter for this property?

    # Methods
    @abstractmethod
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:
        pass
