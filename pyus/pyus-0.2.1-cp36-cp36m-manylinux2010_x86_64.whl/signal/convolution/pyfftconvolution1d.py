import numpy as np
import pyfftw
import multiprocessing
from typing import Tuple

from .baseconvolution1d import BaseConvolution1D


class PyFFTConvolution1D(BaseConvolution1D):

    def __init__(
            self,
            in1_shape: Tuple[int, ...],
            in2_shape: Tuple[int, ...],
            mode: str = 'full',
            axis: int = -1,
            dtype=None,
    ):
        # Call super constructor
        super(PyFFTConvolution1D, self).__init__(
            in1_shape=in1_shape,
            in2_shape=in2_shape,
            mode=mode,
            axis=axis,
            dtype=dtype
        )

        # Full convolution length (required for each `mode`)
        full_conv_len = in1_shape[axis] + in2_shape[axis] - 1

        # Fast FFT length
        fft_len = pyfftw.next_fast_len(full_conv_len)

        # FFTW interface
        #   Define FFTW plans
        # planner_effort = 'FFTW_ESTIMATE'  # default pyfftw
        planner_effort = 'FFTW_MEASURE'  # slower to plan (default fftw)
        # planner_effort = 'FFTW_PATIENT'  # REALLY slower
        threads = None  # default
        # threads = multiprocessing.cpu_count()  # can speed up things
        # TODO(@dperdios):
        #   - empty_aligned doesn't "alloc" the memory (before first call)
        #   - output_array also allocated (internally) with empty_aligned
        #   - could try to allocate output and use FFTW core object
        # _in1_tmp = pyfftw.empty_aligned(in1_shape, dtype=dtype)
        # _in2_tmp = pyfftw.empty_aligned(in2_shape, dtype=dtype)
        _in1_tmp = pyfftw.zeros_aligned(in1_shape, dtype=dtype)
        _in2_tmp = pyfftw.zeros_aligned(in2_shape, dtype=dtype)
        rfft_in1 = pyfftw.builders.rfft(
            _in1_tmp, n=fft_len, axis=axis, planner_effort=planner_effort,
            threads=threads
        )
        rfft_in2 = pyfftw.builders.rfft(
            _in2_tmp, n=fft_len, axis=axis, planner_effort=planner_effort,
            threads=threads
        )

        #   Mimic broadcasting (for the point-wise multiplication)
        _fft_dtype = rfft_in1.output_array.dtype
        _spo_shape = np.broadcast(
            rfft_in1.output_array, rfft_in2.output_array
        ).shape

        # _spo_tmp = pyfftw.empty_aligned(_spo_shape, dtype=dtype)
        _spo_tmp = pyfftw.zeros_aligned(_spo_shape, dtype=_fft_dtype)
        self._spo_fft = _spo_tmp
        irfft_spo = pyfftw.builders.irfft(
            _spo_tmp, n=fft_len, axis=axis, planner_effort=planner_effort,
            threads=threads
        )

        #   Store plans in properties
        self._fft_len = fft_len
        self._rfft_in1 = rfft_in1
        self._rfft_in2 = rfft_in2
        self._irfft_spo = irfft_spo

        # Compute final slicing w.r.t. output shape and FFT padding
        fft_pad = fft_len - full_conv_len
        out_shape = self.output_shape
        ifft_out_shape_arr = np.asarray(irfft_spo.output_shape)
        out_shape_arr = np.asarray(out_shape)
        # start_inds = (ifft_out_shape_arr - out_shape_arr - fft_pad) // 2
        start_inds = ifft_out_shape_arr - out_shape_arr
        start_inds[axis] -= fft_pad  # remove FFT pad
        start_inds[axis] = start_inds[axis] // 2  # center
        end_inds = start_inds + out_shape_arr
        _out_slice = tuple([slice(s, e) for s, e in zip(start_inds, end_inds)])
        self._out_slice = _out_slice

    # Methods
    def _convolve(
            self,
            in1: np.ndarray,
            in2: np.ndarray,
            out: np.ndarray,
    ):
        # Real FFT
        sp1_fft = self._rfft_in1(in1)
        sp2_fft = self._rfft_in2(in2)

        # Point-wise multiplication (broadcasting)
        # spo_fft = sp1_fft * sp2_fft
        # out_fftw = self._irfft_spo(spo_fft)
        spo_fft = self._irfft_spo.input_array  # ptr
        np.multiply(sp1_fft, sp2_fft, out=spo_fft)  # avoid interm. alloc.

        # Inverse Real FFT
        # # out_fftw = self._irfft_spo.output_array
        # # self._irfft_spo(input_array=spo_fft, output_array=out_fftw)
        out_fftw = self._irfft_spo(input_array=spo_fft)

        # Slicing w.r.t. convolution method
        out[:] = out_fftw[self._out_slice]  # copy result in output
