from abc import abstractmethod
import numpy as np

from pyus.imaging.functors.basefunctor import BaseFunctor


class BaseWindow(BaseFunctor):
    """Base class for window functors"""

    def __init__(self, dtype):

        # Call super constructor
        super(BaseWindow, self).__init__(dtype=dtype)

    # Abstract methods
    @abstractmethod
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:
        pass
