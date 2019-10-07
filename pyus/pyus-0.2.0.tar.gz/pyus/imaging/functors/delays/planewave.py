import numpy as np
from .basedelay import BaseDelay
from typing import Tuple
from pyus.utils.types import Real
from pyus.core.cython.imaging.functors.delays import _PlaneWave3D, _PlaneWave2D
from pyus.utils.types import _assert_real_number


class BasePlaneWave(BaseDelay):
    """Base class for plane-wave delay laws
    """
    def __init__(
            self,
            angles: Tuple[Real, Real],
            mean_sound_speed: Real,
            offset: Real,
            dtype,
            functor,
    ):
        # Call super constructor
        super(BasePlaneWave, self).__init__(
            mean_sound_speed=mean_sound_speed, offset=offset, dtype=dtype
        )

        # Check inputs not directly forwarded to abstract class
        angle_x, angle_y = angles
        _assert_real_number(angle_x)
        _assert_real_number(angle_y)

        # Assign properties
        self._angle_x = angle_x
        self._angle_y = angle_y
        _dir = [
            np.sin(angle_x) * np.cos(angle_y),
            np.cos(angle_x) * np.sin(angle_y),
            np.cos(angle_x) * np.cos(angle_y)
        ]
        #   Expand dimension to (3, 1) for proper broadcasting
        direction = np.array(_dir, dtype=self._dtype)[:, np.newaxis]
        self._direction = direction

        # Attach backend functor
        self._functor = functor

    @property
    def direction(self):
        return self._direction.copy()

    # Methods
    def _call_no_offset(
            self, im_pos: np.ndarray, el_pos: np.ndarray
    ) -> np.ndarray:
        # Transmit distance(s)
        # TODO(@dperdios): should we split between transmit and receive to
        #   to avoid a loop in DAS since transmit is indep of el_pos?
        r_tx = (im_pos * self._direction).sum(axis=0)

        # Receive distance(s)
        r_rx = np.linalg.norm(im_pos - el_pos, axis=0)

        # Round-trip time-of-flight
        t_tot = (r_tx + r_rx) / self._mean_sound_speed

        return t_tot


class PlaneWave3D(BasePlaneWave):
    """3D plane-wave round-trip time of flight

    Notes:
        origin of time when wavefront crosses the transducer center (0, 0, 0)
        offset in seconds
    """
    def __init__(
            self,
            angles: Tuple[Real, Real],
            mean_sound_speed: Real,
            offset: Real = 0,
            dtype=None
    ):

        # Check inputs (for functor instantiation)
        angle_x, angle_y = angles
        _assert_real_number(angle_x)
        _assert_real_number(angle_y)
        self._angles = angles

        # Functor
        functor = _PlaneWave3D(mean_sound_speed, angle_x, angle_y, offset)

        # Call super constructor
        super(PlaneWave3D, self).__init__(
            angles=angles,
            mean_sound_speed=mean_sound_speed,
            offset=offset,
            dtype=dtype,
            functor=functor
        )

    # Properties
    @property
    def angles(self):
        return self._angles


class PlaneWave2D(BasePlaneWave):
    """2D plane-wave round-trip time of flight

    Notes:
        origin of time when wavefront crosses the transducer center (0, 0, 0)
        offset in seconds
    """
    def __init__(
            self,
            angle: Real,
            mean_sound_speed: Real,
            offset: Real = 0,
            dtype=None
    ):

        # Check inputs (for functor instantiation)
        _assert_real_number(angle)
        self._angle = angle

        # Functor
        functor = _PlaneWave2D(mean_sound_speed, angle, offset)

        # Angles
        angles = angle, 0

        # Call super constructor
        super(PlaneWave2D, self).__init__(
            angles=angles,
            mean_sound_speed=mean_sound_speed,
            offset=offset,
            dtype=dtype,
            functor=functor
        )

    # Properties
    @property
    def angle(self):
        return self._angle

    # Methods
    # def _call_no_offset(
    #         self, im_pos: np.ndarray, el_pos: np.ndarray
    # ) -> np.ndarray:
    #     # Transmit distance(s)
    #     r_tx = (im_pos * self._direction).sum(axis=0)
    #
    #     # Receive distance(s)
    #     x_im, _, z_im = im_pos
    #     x_td, _, _ = el_pos
    #     r_rx = np.sqrt((x_im - x_td) ** 2 + z_im ** 2)
    #
    #     # Round-trip time-of-flight
    #     t_tot = (r_tx + r_rx) / self._mean_sound_speed
    #
    #     return t_tot
