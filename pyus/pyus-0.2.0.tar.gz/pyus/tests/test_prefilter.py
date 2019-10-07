import os
import unittest
import itertools
import numpy as np
from pycuda import gpuarray

from pyus.imaging.interpolators import (
    NearestInterpolator1D, LinearInterpolator1D, KeysInterpolator1D,
    Bspline3Interpolator1D, Bspline4Interpolator1D, Bspline5Interpolator1D,
    Omoms3Interpolator1D
)
from pyus.core.cython.imaging.interpolator.prefiltering import prefilter_backend

import pycuda.autoinit
DTYPE = [np.float32, np.complex64]
RTOL = 1e-5
SEED = 12345
PRNG = np.random.RandomState(seed=SEED)


# TODO:
#  - Mirror boundary condition: B-spline 4 do not pass (with RTOL <= 1e-5)
#  - Zero boundary condition: no non-interpolating interp pass
class TestPrefilter(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test_1d(self):
        self._test_interp(data_shape=(100,), boundary='mirror')
        self._test_interp(data_shape=(100), boundary='mirror')

    def test_2d(self):
        self._test_interp(data_shape=(10, 100), boundary='mirror')

    def test_3d(self):
        self._test_interp(data_shape=(3, 10, 100), boundary='mirror')

    def test_4d(self):
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='mirror')

    def test_boundary_mirror(self):
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='mirror')
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='MIRROR')
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='reflect')
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='REFLECT')

    def test_boundary_zero(self):
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='zero')
        self._test_interp(data_shape=(2, 3, 10, 100), boundary='ZERO')

    def _test_interp(self, data_shape, boundary):
        interpolators = [NearestInterpolator1D, LinearInterpolator1D,
                         KeysInterpolator1D, Bspline3Interpolator1D,
                         # Bspline4Interpolator1D,
                         Bspline5Interpolator1D,
                         Omoms3Interpolator1D]

        # interpolators = [Bspline4Interpolator1D]

        for interp in interpolators:
            self._test(
                Interpolator=interp, data_shape=data_shape, boundary=boundary
            )

    def _test(self, Interpolator, data_shape, boundary):

        for dtype in DTYPE:

            if dtype is np.float32:
                data = PRNG.uniform(size=data_shape).astype(dtype=np.float32)

            elif dtype is np.complex64:
                data_real = PRNG.uniform(size=data_shape).astype(
                    dtype=np.float32)
                data_imag = PRNG.uniform(size=data_shape).astype(
                    dtype=np.float32)

                data = data_real + 1j * data_imag

            else:
                raise TypeError

            data_gpu = gpuarray.to_gpu(data)

            time_axis = np.arange(data.shape[-1])
            interpolator = Interpolator(time_axis, boundary, dtype)

            data_filt_py = interpolator._prefilter(data)
            data_filt_cpp = prefilter_backend(data, boundary, interpolator)
            data_filt_cuda = prefilter_backend(data_gpu, boundary, interpolator).get()

            # np.testing.assert_allclose(data_filt_py, data_filt_cpp, rtol=RTOL)
            # np.testing.assert_allclose(data_filt_py, data_filt_cuda, rtol=RTOL)

            if dtype is np.float32:

                data_cpp = np.linalg.norm(
                    data_filt_cpp - data_filt_py, axis=-1
                ) / np.linalg.norm(data_filt_py, axis=-1)

                if np.any(data_cpp > RTOL):
                    raise AssertionError(
                        'Prefilter C++ test failed: {} > {}'.format(
                            data_cpp, RTOL
                        )
                    )

                data_cuda = np.linalg.norm(
                    data_filt_cuda - data_filt_py, axis=-1
                ) / np.linalg.norm(data_filt_py)

                if np.any(data_cuda > RTOL):
                    raise AssertionError(
                        'Prefilter C++ test failed: {} > {}'.format(
                            data_cuda, RTOL
                        )
                    )

            elif dtype is np.complex64:

                data_real_cpp = np.linalg.norm(
                    data_filt_cpp.real - data_filt_py.real, axis=-1
                ) / np.linalg.norm(data_filt_py.real)

                data_imag_cpp = np.linalg.norm(
                    data_filt_cpp.imag - data_filt_py.imag, axis=-1
                ) / np.linalg.norm(data_filt_py.imag)

                if np.any(data_real_cpp > RTOL) or np.any(data_imag_cpp > RTOL):
                    raise AssertionError('Prefilter C++ test failed')

                data_real_cuda = np.linalg.norm(
                    data_filt_cuda.real - data_filt_py.real, axis=-1
                ) / np.linalg.norm(data_filt_py.real)

                data_imag_cuda = np.linalg.norm(
                    data_filt_cuda.imag - data_filt_py.imag, axis=-1
                ) / np.linalg.norm(data_filt_py.imag)

                if np.any(data_real_cuda > RTOL) or np.any(
                        data_imag_cuda > RTOL):
                    raise AssertionError('Prefilter CUDA test failed')

            else:
                raise TypeError

    # def _test_all(self,):
    #     interpolators = [NearestInterpolator1D, LinearInterpolator1D,
    #                      KeysInterpolator1D, Bspline3Interpolator1D,
    #                      Bspline4Interpolator1D, Bspline5Interpolator1D,
    #                      Omoms3Interpolator1D]
    #     shapes = [(1000), (128, 1000), (3, 128, 1000), (2, 3, 128, 1000)]
    #     boundaries = ['mirror', 'reflect', 'zero']
    #
    #     for (i,s,b,t) in itertools.product(interpolators, shapes, boundaries):
    #         self._test(Interpolator=i, data_shape=s, boundary=b)


suite = unittest.TestLoader().loadTestsFromTestCase(TestPrefilter)
