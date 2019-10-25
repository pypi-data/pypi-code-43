import numpy as np
from .basewindow import BaseWindow
from pyus.core.cython.imaging.functors.windows import _IdentityWindow


class IdentityWindow(BaseWindow):
    """Identity window function"""
    def __init__(self, dtype=None):

        # Call super constructor
        super(IdentityWindow, self).__init__(dtype=dtype)

        # Attach backend functor
        self._functor = _IdentityWindow()

    # Methods
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:
        # TODO(@dperdios): Make sure it is broadcasted properly
        # return 0 * (im_pos + el_pos) + 1
        return 1.
