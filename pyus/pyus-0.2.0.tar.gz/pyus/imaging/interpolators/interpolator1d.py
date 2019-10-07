import numpy as np

from pyus.utils.types import _assert_str
from .baseinterpolator1d import BaseInterpolator1D
from .bspline0interpolator1d import Bspline0Interpolator1D
from .bspline1interpolator1d import Bspline1Interpolator1D
from .bspline2interpolator1d import Bspline2Interpolator1D
from .nearestinterpolator1d import NearestInterpolator1D
from .linearinterpolator1d import LinearInterpolator1D
from .keysinterpolator1d import KeysInterpolator1D
from .bspline3interpolator1d import Bspline3Interpolator1D
from .omoms3interpolator import Omoms3Interpolator1D
from .bspline4interpolatior1d import Bspline4Interpolator1D
from .bspline5interpolator1d import Bspline5Interpolator1D

# Supported interpolators
# TODO(@dperdios): use of namedtuple instead? or dataclass? or enum?
interpolator_map = {
    'nearest': NearestInterpolator1D,
    'linear': LinearInterpolator1D,
    'keys': KeysInterpolator1D,
    'bspline0': Bspline0Interpolator1D,
    'bspline1': Bspline1Interpolator1D,
    'bspline2': Bspline2Interpolator1D,
    'bspline3': Bspline3Interpolator1D,
    'bspline4': Bspline4Interpolator1D,
    'bspline5': Bspline5Interpolator1D,
    'omoms3': Omoms3Interpolator1D,
}

class Interpolator1D:

    def __new__(
            cls, data_axis: np.ndarray, method: str, boundary: str, dtype=None
    ) -> BaseInterpolator1D:
        """Factory-like for interpolator objects
        """
        # Note: since __new__ does not return an instance of Interpolator1D
        #   class, __init__ is not called
        # TODO(@dperdios): this seems be a bad practice, but provides a nice
        #   API...

        # Instantiate interpolator object
        instance = create_interpolator1d(
            data_axis=data_axis, method=method, boundary=boundary, dtype=dtype
        )

        return instance


def create_interpolator1d(
        data_axis: np.ndarray, method: str, boundary: str, dtype=None
) -> BaseInterpolator1D:
    """Factory method for interpolator 1D objects"""

    # Check arguments
    _assert_str(method)
    method = method.lower()

    # Check supported interpolators
    if method not in interpolator_map:
        valid_str = ["'{:s}'".format(m) for m in interpolator_map.keys()]
        raise NotImplementedError(
            "Unsupported interpolation method '{:s}'. "
            "Supported methods: {:s}".format(method, ", ".join(valid_str))
        )

    # Instantiate corresponding interpolator object
    interp_cls = interpolator_map[method]
    instance = interp_cls(data_axis=data_axis, boundary=boundary, dtype=dtype)

    return instance
