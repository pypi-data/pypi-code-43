import numpy as np
from .basewindow import BaseWindow
from pyus.utils.types import Real, _assert_real_number
from pyus.core.cython.imaging.functors.windows import _Selfridge2D


class Selfridge2D(BaseWindow):

    def __init__(self, element_width: Real, wavelength: Real, dtype=None):

        # Call super constructor
        super(Selfridge2D, self).__init__(dtype=dtype)

        # Check arguments
        _assert_real_number(element_width)
        _assert_real_number(wavelength)

        # Assign properties
        self._element_width = element_width
        self._wavelength = wavelength

        # Attach backend functor
        self._functor = _Selfridge2D(wavelength, element_width)

    # Properties
    @property
    def element_width(self):
        return self._element_width

    @property
    def wavelength(self):
        return self._wavelength

    # Methods
    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:

        # Get dtype
        dtype = self._dtype

        # Extract coordinates
        x_im = im_pos[0]
        z_im = im_pos[2]
        x_td = el_pos[0]

        # Direction cosines (need to account for singularity)
        #   - cos: z_im / dist
        #   - sin: (x_im - x_td) / dist
        #   - when dist -> 0 we use the `eps` around 0
        #   - when dist -> 0 and z_im -> 0 we need to add `eps` for both
        eps = np.spacing(0, dtype=dtype)
        dist = np.sqrt((x_im - x_td) ** 2 + z_im ** 2) + eps
        # factor = (z_im + eps) / dist * np.sinc(
        #     self.element_width / self.wavelength * (x_im - x_td) / dist
        # )
        cos_a = (x_im - x_td) / dist
        cos_c = (z_im + eps) / dist

        # Compute factor
        factor = np.sinc(self._element_width / self._wavelength * cos_a)
        factor *= cos_c  # TODO: cos_c ony when considering soft baffle

        return factor
