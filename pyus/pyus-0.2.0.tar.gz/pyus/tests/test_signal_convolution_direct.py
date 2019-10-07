"""
Test suite for the signal module of the pyus package.
"""
import unittest
import warnings

import numpy as np
from pycuda import gpuarray

from pyus.signal import convolution
from pyus.signal.convolution import SUPPORTED_MODES

import pycuda.autoinit
DTYPE, RTOL = [np.float32, np.complex64], 1e-6
SEED = 123
PRNG = np.random.RandomState(seed=SEED)

class TestConvolution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cls_convol_host = convolution.CppDIRConvolution1D
        cls._cls_convol_device = convolution.CudaDIRConvolution1D
        cls._cls_convol_py_dir = convolution.PyDIRConvolution1D

    @classmethod
    def tearDownClass(cls):
        pass

    def test_shape_1d_1d(self):
        self._test_shape(in1_shape=(22,), in2_shape=(13,))

    def test_shape_1d_1d_2(self):
        self._test_shape(in1_shape=(222,), in2_shape=(133,))

    def test_shape_1d_2d(self):
        self._test_shape(in1_shape=(1, 13), in2_shape=(3, 9))

    def test_shape_2d_1d(self):
        self._test_shape(in1_shape=(3, 9), in2_shape=(1, 13))

    def test_shape_2d_2d(self):
        self._test_shape(in1_shape=(3, 19), in2_shape=(3, 13))

    def test_shape_3d_3d(self):
        self._test_shape(in1_shape=(3, 6, 8), in2_shape=(3, 6, 16))

    def test_shape_4d_4d(self):
        self._test_shape(in1_shape=(3, 6, 8, 21), in2_shape=(3, 6, 8, 11))

    def test_broadcasting_1d_2d(self):
        self._test_shape(in1_shape=(27,), in2_shape=(6, 33))

    def test_broadcasting_2d_1d(self):
        self._test_shape(in1_shape=(3, 27), in2_shape=(33,))

    def test_broadcasting_2d_2d(self):
        # TODO: isn't this one the same as test_shape_1d_2d?
        self._test_shape(in1_shape=(1, 27), in2_shape=(6, 33))

    # def test_broadcasting_3d_3d(self):
    #     # TODO: do we really want this to be supported?
    #     self._test_shape(in1_shape=(11, 1, 27), in2_shape=(11, 6, 33))
    #
    # def test_broadcasting_4d_4d(self):
    #     # TODO: do we really want this to be supported?
    #     self._test_shape(in1_shape=(1, 11, 1, 27), in2_shape=(5, 11, 6, 33))

    def test_mode_full(self):
        self._test_mode(mode='full')
        self._test_mode(mode='FULL')

    def test_mode_same(self):
        self._test_mode(mode='same')
        self._test_mode(mode='SAME')

    def test_mode_valid(self):
        self._test_mode(mode='valid')
        self._test_mode(mode='VALID')

    def test_mode_supported_modes(self):
        for mode in SUPPORTED_MODES:
            self._test_mode(mode=mode)

    def test_cumulative_error(self):
        # Long filter (i.e. smallest input) seem to result in numerical errors
        # in backend functions, most probably due to cumulative error in the
        # sum
        length = 2000
        try:
            self._test_shape(in1_shape=(length,), in2_shape=(length,))
        except AssertionError as err:
            warnings.warn('Cumulative error test did not pass:\n{}'.format(
                str(err))
            )

    def _test_shape(self, in1_shape, in2_shape, mode: str = 'full'):

        for dtype in DTYPE:

            # Create objects
            kwargs = {
                'in1_shape': in1_shape, 'in2_shape': in2_shape, 'mode': mode,
                'dtype': dtype
            }
            conv_py_dir = self._cls_convol_py_dir(**kwargs)
            conv_host_dir = self._cls_convol_host(**kwargs)
            conv_device_dir = self._cls_convol_device(**kwargs)

            # Create random arrays
            in1 = PRNG.uniform(size=in1_shape).astype(dtype=dtype)
            in2 = PRNG.uniform(size=in2_shape).astype(dtype=dtype)
            out = np.zeros(conv_py_dir.output_shape, dtype=dtype)
            in1_gpu = gpuarray.to_gpu(in1)
            in2_gpu = gpuarray.to_gpu(in2)
            out_gpu = gpuarray.to_gpu(out)

            # Compute convolution
            res_py_dir = conv_py_dir.convolve(in1=in1, in2=in2)
            res_host_dir = conv_host_dir.convolve(in1=in1, in2=in2)
            conv_device_dir.convolve(in1=in1_gpu, in2=in2_gpu, out=out_gpu)
            res_device_dir = out_gpu.get()

            # Tests
            ground_truth = res_py_dir  # since uses NumPy
            np.testing.assert_allclose(res_host_dir, ground_truth, rtol=RTOL)
            np.testing.assert_allclose(res_device_dir, ground_truth, rtol=RTOL)

    def _test_mode(self, mode: str):

        in1_shape = (3, 2, 42)

        # Test odd in2 length
        in2_shape = (3, 2, 13)
        self._test_shape(in1_shape=in1_shape, in2_shape=in2_shape, mode=mode)

        # Test even in2 length
        in2_shape = (3, 2, 12)
        self._test_shape(in1_shape=in1_shape, in2_shape=in2_shape, mode=mode)


suite = unittest.TestLoader().loadTestsFromTestCase(TestConvolution)
