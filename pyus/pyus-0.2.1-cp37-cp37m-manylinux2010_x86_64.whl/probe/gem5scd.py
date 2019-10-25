from .probe1d import Probe1D


class GEM5ScD(Probe1D):  # TODO: make Probe15D
    def __init__(self):

        name = 'GE M5Sc-D'
        center_frequency = 2.8e6
        pitch = 270e-6
        # TODO: the actual transducer element array is 80 X 3 for a total of 240 active
        element_number = 80
        element_width = 230e-6  # width from GE data sheet; kerf is 0.04 mm
        element_height = 13e-3
        low, high = 1.7e6, 4.2e6  # According to Verasonics (computeTrans)
        bandwidth = 0.9
        # bandwidth = 2 * (high - low) / (high + low)
        elevation_focus = 77e-3

        super(GEM5ScD, self).__init__(
            name=name,
            pitch=pitch,
            center_frequency=center_frequency,
            element_number=element_number,
            element_width=element_width,
            element_height=element_height,
            elevation_focus=elevation_focus,
            bandwidth=bandwidth,
        )
