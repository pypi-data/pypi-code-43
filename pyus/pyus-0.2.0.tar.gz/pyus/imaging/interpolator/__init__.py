import warnings

warn_msg = (
    'pyus.imaging.interpolator module deprecated. '
    'Please use pyus.imaging.interpolators instead'
)
# TODO(@dperdios): DeprecationWarning not thrown in modules?
# warnings.warn(warn_msg, DeprecationWarning)
warnings.warn(warn_msg)

from pyus.imaging.interpolators.baseinterpolator1d import BaseInterpolator1D
from pyus.imaging.interpolators.bspline0interpolator1d import Bspline0Interpolator1D
from pyus.imaging.interpolators.bspline1interpolator1d import Bspline1Interpolator1D
from pyus.imaging.interpolators.bspline2interpolator1d import Bspline2Interpolator1D
from pyus.imaging.interpolators.nearestinterpolator1d import NearestInterpolator1D
from pyus.imaging.interpolators.linearinterpolator1d import LinearInterpolator1D
from pyus.imaging.interpolators.keysinterpolator1d import KeysInterpolator1D
from pyus.imaging.interpolators.bspline3interpolator1d import Bspline3Interpolator1D
from pyus.imaging.interpolators.omoms3interpolator import Omoms3Interpolator1D
from pyus.imaging.interpolators.bspline4interpolatior1d import Bspline4Interpolator1D
from pyus.imaging.interpolators.bspline5interpolator1d import Bspline5Interpolator1D
