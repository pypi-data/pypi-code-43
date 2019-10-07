import warnings

warn_msg = (
    'pyus.imaging.window module deprecated. '
    'Please use pyus.imaging.windows instead'
)
# TODO(@dperdios): DeprecationWarning not thrown in modules?
# warnings.warn(warn_msg, DeprecationWarning)
warnings.warn(warn_msg)

from pyus.imaging.windows import *
# from pyus.imaging.windows import BaseWindow
# from pyus.imaging.windows import StandardWindow
# from pyus.imaging.windows import IdentityWindow
# from pyus.imaging.windows import Boxcar
# from pyus.imaging.windows import Hamming
# from pyus.imaging.windows import Hanning
# from pyus.imaging.windows import Selfridge2D
# from pyus.imaging.windows import Selfridge3D
# from pyus.imaging.windows import Tukey
