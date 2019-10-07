from .probe1d import Probe1D


class L11Probe(Probe1D):
    def __init__(self):

        name = 'L11-4v'
        pitch = 300e-6
        center_frequency = 1540 / pitch
        element_number = 128
        element_width = 0.27e-3
        element_height = 5e-3
        bandwidth = 0.67
        elevation_focus = 20e-3

        super(L11Probe, self).__init__(
            name=name,
            pitch=pitch,
            center_frequency=center_frequency,
            element_number=element_number,
            element_width=element_width,
            element_height=element_height,
            elevation_focus=elevation_focus,
            bandwidth=bandwidth,
        )
