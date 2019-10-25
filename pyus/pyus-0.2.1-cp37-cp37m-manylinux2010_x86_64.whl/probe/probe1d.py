import numpy as np
from typing import Optional

from .baseprobe import BaseProbe
from pyus.utils.types import Real


class Probe1D(BaseProbe):
    def __init__(
            self,
            name: str,
            pitch: Real,
            center_frequency: Real,
            element_number: int,
            element_width: Real,
            element_height: Real,
            elevation_focus: Optional[Real] = None,
            bandwidth: Optional[Real] = None,
            # TODO: should probably have an impulse_response object
            # -> it could be a measured or a synthetic one
            # -> synthetic with or without KLM
    ):

        # Element positions
        width = (element_number - 1) * pitch
        x_pos = np.linspace(
            start=-width / 2, stop=width / 2, num=element_number
        )
        y_pos = np.zeros_like(x_pos)
        z_pos = np.zeros_like(x_pos)
        element_positions = np.stack((x_pos, y_pos, z_pos), axis=1)
        # element_positions = np.stack((x_pos, y_pos, z_pos))

        # Super constructor
        super(Probe1D, self).__init__(
            name=name,
            center_frequency=center_frequency,
            element_positions=element_positions,
            element_width=element_width,
            element_height=element_height,
            bandwidth=bandwidth
        )

        # Specific properties
        # self._type = 'Linear'  # TODO: shouldn't it be a BaseProbe property?
        self._pitch = pitch
        self._width = width
        self._elevation_focus = elevation_focus

    # Properties
    @property
    def pitch(self):  # TODO: shouldn't it be a BaseProbe property?
        return self._pitch

    @property
    def kerf(self):
        return self.pitch - self.element_width

    @property
    def elevation_focus(self):
        return self._elevation_focus

    @property
    def width(self):  # TODO: only valid if non-convex array
        return self._width

    @property
    def height(self):  # TODO: only valid if element height provided
        return self.element_height
