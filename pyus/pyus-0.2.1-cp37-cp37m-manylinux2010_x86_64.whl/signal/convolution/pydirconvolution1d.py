import numpy as np
from typing import Tuple

from pyus.signal.convolution._utils import (
    _flatten_array_as_2d, _broadcast_to_out_shape
)
from .baseconvolution1d import BaseConvolution1D


class PyDIRConvolution1D(BaseConvolution1D):

    def __init__(
            self,
            in1_shape: Tuple[int, ...],
            in2_shape: Tuple[int, ...],
            mode: str = 'full',
            axis: int = -1,
            dtype=None,
    ):
        # Call super constructor
        super(PyDIRConvolution1D, self).__init__(
            in1_shape=in1_shape,
            in2_shape=in2_shape,
            mode=mode,
            axis=axis,
            dtype=dtype
        )

    # Methods
    def _convolve(
            self,
            in1: np.ndarray,
            in2: np.ndarray,
            out: np.ndarray,
    ) -> np.ndarray:

        # Note: input checks have been carried in base class

        # Extract properties
        mode = self.mode
        axis = self.axis

        # TODO(@dperdios): allocate arrays in a "BaseDIRConv" class

        # Broadcast arrays (no copies)
        #   Note: similar to tiling
        in1_bc = _broadcast_to_out_shape(in1, out, axis=axis)
        in2_bc = _broadcast_to_out_shape(in2, out, axis=axis)

        # Construct 2D flattened views
        #   Note: may result in copies
        #   Note: may not be C-contiguous
        out_2d_view = _flatten_array_as_2d(out, axis=axis)
        in1_2d_view = _flatten_array_as_2d(in1_bc, axis=axis)
        in2_2d_view = _flatten_array_as_2d(in2_bc, axis=axis)

        # Perform convolution
        for sig1, sig2, res in zip(in1_2d_view, in2_2d_view, out_2d_view):
            res[:] = np.convolve(sig1, sig2, mode=mode)

        return out
