import numpy as np
from .standardwindow import StandardWindow
from pyus.utils.types import Real
from pyus.core.cython.imaging.functors.windows import _Boxcar


class Boxcar(StandardWindow):

    def __init__(self, f_number: Real, dtype=None):

        # Call super constructor
        super(Boxcar, self).__init__(f_number=f_number, dtype=dtype)

        # Attach backend functor
        self._functor = _Boxcar(f_number)

    def _call(self, im_pos: np.ndarray, el_pos: np.ndarray) -> np.ndarray:

        # Get dtype
        dtype = self._dtype

        # Extract coordinates
        x_im = im_pos[0]
        z_im = im_pos[2]
        x_td = el_pos[0]

        # Compute lateral relative distance and aperture w.r.t. depth
        distance = np.abs(x_im - x_td)
        aperture = z_im / self._f_number

        # Spacing (due to the distance / aperture)
        #   Note: here the spacing around zero cannot be used as easily as in
        #   the Selfridge2D case.
        eps = np.spacing(1, dtype=dtype)
        aperture[aperture == 0] = eps

        factor = np.zeros(shape=z_im.shape, dtype=dtype)
        factor = np.where(
            distance < aperture / 2,
            np.ones(shape=factor.shape, dtype=dtype),
            factor
        )

        return factor
