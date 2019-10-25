import numpy as np
from .standardwindow import StandardWindow
from pyus.utils.types import Real
from pyus.core.cython.imaging.functors.windows import _Hanning


class Hanning(StandardWindow):

    def __init__(self, f_number: Real, dtype=None):

        # Call super constructor
        super(Hanning, self).__init__(f_number=f_number, dtype=dtype)

        # Attach backend functor
        self._functor = _Hanning(f_number)

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
        # @flomz: more elegant than `aperture + eps` since the `eps` is only
        # required when `aperture` is zero. However, not sure this can be
        # easily done on GPU implementations...
        # Also, the situation where `aperture` is zero cannot "really" happen
        # physically

        # Compute window
        factor = np.zeros(shape=z_im.shape, dtype=dtype)
        #   distance < aperture / 2
        factor = np.where(
            distance < aperture / 2,
            0.5 * (1 + np.cos(2 * np.pi * distance / aperture)),
            factor
        )

        return factor
