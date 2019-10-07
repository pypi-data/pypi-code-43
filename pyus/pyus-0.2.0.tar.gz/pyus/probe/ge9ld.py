from .probe1d import Probe1D


class GE9LD(Probe1D):
    def __init__(self):

        name = 'GE 9-LD'
        pitch = 230e-6
        center_frequency = 5.3e6  # better than λ-pitch
        element_number = 192
        element_width = 0.9 * pitch  # Verasonics' guess (computeTrans.m)
        element_height = 6e-3
        bandwidth = 0.75
        elevation_focus = 28e-3  # Verasonics' website (not computeTrans.m)

        super(GE9LD, self).__init__(
            name=name,
            pitch=pitch,
            center_frequency=center_frequency,
            element_number=element_number,
            element_width=element_width,
            element_height=element_height,
            elevation_focus=elevation_focus,
            bandwidth=bandwidth,
        )
