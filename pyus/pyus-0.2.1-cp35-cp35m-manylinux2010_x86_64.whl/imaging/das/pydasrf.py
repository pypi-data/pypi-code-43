import numpy as np
from typing import List, Tuple

from .basedasrf import BaseDelayAndSumRF
from pyus.probe.baseprobe import BaseProbe
from pyus.imaging.interpolators.baseinterpolator1d import BaseInterpolator1D
from pyus.imaging.delays import BaseDelay
from pyus.imaging.windows import BaseWindow


class PyDelayAndSumRF(BaseDelayAndSumRF):
    def __init__(
            self,
            probe: BaseProbe,
            time_axis: np.ndarray,
            image_axes: Tuple[np.ndarray, np.ndarray, np.ndarray],
            dtype=None,
    ):

        # Call super constructor
        super(PyDelayAndSumRF, self).__init__(
            probe=probe, time_axis=time_axis, image_axes=image_axes,
            dtype=dtype
        )

        # Extract properties
        image_shape = self._image_shape
        image_axes = self._image_axes

        # Image grid
        im_mg = np.array(np.meshgrid(*image_axes, indexing='ij'))
        im_pos = im_mg.reshape((3, np.prod(image_shape)))
        self._image_positions = im_pos

    @property
    def image_positions(self):
        return self._image_positions.copy()

    # Methods
    def _reconstruct(
            self,
            data: np.ndarray,
            interpolator: BaseInterpolator1D,
            delays: List[BaseDelay],
            apodization: BaseWindow,
    ) -> np.ndarray:

        # Note: input checks have been carried in base class

        # Extract object properties
        element_positions = self._element_positions
        image_shape = self._image_shape
        im_pos = self._image_positions

        # Pre-allocate output
        frame_number = data.shape[0]
        images = np.zeros((frame_number, *image_shape), dtype=self.dtype)

        # Pre-filter data for generalized interpolation
        data_flt = interpolator.prefilter(data=data)

        # Beamforming loops
        for frame, image in zip(data_flt, images):
            im_v = image.ravel()
            for event, delay in zip(frame, delays):
                for el_pos, data_td in zip(element_positions, event):

                    # Round-trip time-of-flight
                    t_tot = delay(im_pos=im_pos, el_pos=el_pos[:, np.newaxis])

                    # Apodization
                    factor = apodization(
                        im_pos=im_pos, el_pos=el_pos[:, np.newaxis]
                    )

                    # Data interpolation
                    interp_value = interpolator.interpolate(
                        data=data_td, eval_axis=t_tot
                    )

                    # Summation
                    im_v += factor * interp_value

        return images
