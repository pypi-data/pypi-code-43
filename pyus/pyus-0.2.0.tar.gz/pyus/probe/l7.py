from .probe1d import Probe1D


class L7Probe(Probe1D):
    def __init__(self):

        name = 'L7-4'  # ATL L7-4
        pitch = 298e-6  # TBC
        center_frequency = 1540 / pitch  # TBC
        element_number = 128
        element_width = 0.283e-3
        element_height = 7e-3
        low, high = 4e6, 7e6  # According to the ATL L7-4 specifications
        # low, high = 3.75e6, 6.5e6  # Seems more accurante than specs?
        # bandwidth = 2 * (high - low) / (high + low)
        bandwidth = 0.60  # TBC (seems to be the best by hand on the PSF)
        elevation_focus = 25e-3

        super(L7Probe, self).__init__(
            name=name,
            pitch=pitch,
            center_frequency=center_frequency,
            element_number=element_number,
            element_width=element_width,
            element_height=element_height,
            elevation_focus=elevation_focus,
            bandwidth=bandwidth,
        )
