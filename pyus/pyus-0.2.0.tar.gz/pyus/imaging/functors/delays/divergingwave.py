import numpy as np
from .basedelay import BaseDelay
from pyus.utils.types import Real
from pyus.core.cython.imaging.functors.delays import _DivergingWave2D


class DivergingWave(BaseDelay):
    """Generic diverging-wave round-trip time of flight

    Notes:
        origin of time at source position
        offset in seconds
    """
    def __init__(
            self,
            source: np.ndarray,
            mean_sound_speed: Real,
            offset: Real = 0,
            dtype=None
    ):
        super(DivergingWave, self).__init__(
            mean_sound_speed=mean_sound_speed, offset=offset, dtype=dtype
        )

        # Check inputs not directly forwarded to abstract class
        # TODO(@dperdios): proper check with pyus.utils
        if source.ndim != 1 and source.size != 3:
            raise ValueError('Must be a (3,) array')

        source = source.astype(dtype=dtype)
        _, _, z = source
        if z > 0:
            raise NotImplementedError()

        # Assign properties
        self._source = source[:, np.newaxis]
        self._functor = _DivergingWave2D(mean_sound_speed, source, offset)

    # Properties
    @property
    def source(self):
        return self._source.copy()

    # Methods
    def _call_no_offset(
            self, im_pos: np.ndarray, el_pos: np.ndarray
    ) -> np.ndarray:
        # Transmit distance(s)
        # TODO(@dperdios): should we split between transmit and receive to
        #   to avoid a loop in DAS since transmit is indep of el_pos?
        r_tx = np.linalg.norm(im_pos - self._source, axis=0)

        # Receive distance(s)
        r_rx = np.linalg.norm(im_pos - el_pos, axis=0)

        # Round-trip time-of-flight
        t_tot = (r_tx + r_rx) / self._mean_sound_speed

        return t_tot
