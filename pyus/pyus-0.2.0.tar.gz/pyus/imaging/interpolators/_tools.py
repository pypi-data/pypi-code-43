import numpy as np


def _instantiate_backend_functor(cls, data_axis: np.ndarray):
    """Instantiate backend functor

    Note: based on pyus.core.cython.imaging.interpolator.interpolator.pyx
    """
    functor = cls(
        data_axis[0], data_axis[-1], data_axis.size,
        1 / (data_axis[1] - data_axis[0])
    )
    return functor
