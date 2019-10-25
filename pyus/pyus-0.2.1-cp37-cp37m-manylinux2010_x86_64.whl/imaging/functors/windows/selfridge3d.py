import numpy as np
from .basewindow import BaseWindow
from pyus.utils.types import Real, _assert_real_number
from pyus.core.cython.imaging.functors.windows import _Selfridge3D


class Selfridge3D(BaseWindow):

    def __init__(
            self,
            element_width: Real,
            element_height: Real,
            wavelength: Real,
            dtype=None
    ):

        # Call super constructor
        super(Selfridge3D, self).__init__(dtype=dtype)

        # Check arguments
        _assert_real_number(element_width)
        _assert_real_number(element_height)
        _assert_real_number(wavelength)

        # Assign properties
        self._element_width = element_width
        self._element_height = element_height
        self._wavelength = wavelength

        # Attach backend functor
        self._functor = _Selfridge3D(wavelength, element_width, element_height)

    # Properties
    @property
    def element_width(self):
        return self._element_width

    @property
    def element_height(self):
        return self._element_height

    @property
    def wavelength(self):
        return self._wavelength

    # Methods
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:

        # Get dtype
        dtype = self._dtype

        # Direction cosines (need to account for singularity)
        eps = np.spacing(0, dtype=dtype)
        diff = im_pos - el_pos
        dist = np.linalg.norm(diff, axis=0) + eps
        cos_a = diff[0] / dist
        cos_b = diff[1] / dist
        cos_c = (diff[2] + eps) / dist

        # Compute factor
        factor = np.sinc(self._element_width / self._wavelength * cos_a)
        factor *= np.sinc(self._element_height / self._wavelength * cos_b)
        factor *= cos_c  # TODO: cos_c ony when considering soft baffle

        return factor
