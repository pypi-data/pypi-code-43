import warnings

warn_msg = (
    'pyus.imaging.delay module deprecated. '
    'Please use pyus.imaging.delays instead'
)
# TODO(@dperdios): DeprecationWarning not thrown in modules?
# warnings.warn(warn_msg, DeprecationWarning)
warnings.warn(warn_msg)

from pyus.imaging.delays import *
from pyus.imaging.delays import BaseDelay
from pyus.imaging.delays import PlaneWave2D, PlaneWave3D
from pyus.imaging.delays import DivergingWave2D, DivergingWave3D
