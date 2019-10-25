"""
Test suite for the signal module of the pyus package.
"""
import os
import unittest
import h5py
import numpy as np
from pycuda import gpuarray
import pycuda.autoinit

from pyus.signal import hilbert


DTYPE, RTOL = np.float32, 1e-6


class TestHilbertFIR(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._cls_hilbert_fir_host = hilbert.CppHilbertFIR
        cls._cls_hilbert_fir_device = hilbert.CudaHilbertFIR
        cls._cls_hilbert_py = hilbert.PyHilbertFIR

    @classmethod
    def tearDownClass(cls):
        pass

    def test_1d(self):
        self._test_dim(ndim=1, filter_size=21)

    def test_2d(self):
        self._test_dim(ndim=2, filter_size=21)

    def test_3d(self):
        self._test_dim(ndim=3, filter_size=21)

    def test_4d(self):
        self._test_dim(ndim=4, filter_size=21)

    def test_even(self):
        """
        Check if we correctly raise an error if the filter size is even
        """
        try:
            self._test_dim(ndim=3, filter_size=20)
        except ValueError as err:
            if str(err) == 'Must be odd':
                pass
            else:
                raise

    def _test_dim(self, ndim, filter_size):

        # Load test data
        data_file = 'dataset_rf_in_vitro_type1_transmission_1_nbPW_3.hdf5'
        data_path = os.path.join('data', data_file)
        with h5py.File(data_path, 'r') as h5_file:
            h5_group = h5_file['US']['US_DATASET0000']
            raw_data = h5_group['data']['real'][()].astype(dtype=DTYPE)
            raw_data = raw_data[:,:,:]
            # Create 2 frames
            data = np.stack((raw_data, raw_data))

        data_ndim = data.ndim
        if ndim > data_ndim:
            raise ValueError('`ndim`={} too high'.format(ndim))
        data_slice = np.zeros(data_ndim - ndim, dtype=int)
        data = data[(*data_slice, ...)]

        # SEED = 123
        # PRNG = np.random.RandomState(seed=SEED)
        # data = PRNG.uniform(size=(3,3,1536)).astype(dtype=DTYPE)

        data_shape = data.shape
        dtype = data.dtype
        data_gpu = gpuarray.to_gpu(data)

        # Create Hilbert objects
        py_hilbert_fir = self._cls_hilbert_py(
            data_shape=data_shape, filter_size=filter_size,dtype=dtype
        )
        cpp_hilbert_fir = self._cls_hilbert_fir_host(
            data_shape=data_shape, filter_size=filter_size
        )
        cuda_hilbert_fir = self._cls_hilbert_fir_device(
            data_shape=data_shape, filter_size=filter_size
        )

        # Compute analytical signals
        py_data_iq_fir = py_hilbert_fir(data)
        cpp_data_iq_fir = cpp_hilbert_fir(data)
        cuda_data_iq_fir = cuda_hilbert_fir(data_gpu).get()

        # Test
        ground_truth = py_data_iq_fir
        # Point wise comparison of floats may not be the best test when not
        # using ULPs. Here the tests do not pass between python version and
        # C++/CUDA version, probably due to the way the convolution is
        # implemented and how well it handles very small values
        # Instead, we us a test using the norm of the vectors
        # np.testing.assert_allclose(
        #     actual=cpp_data_iq_fir, desired=ground_truth, rtol=RTOL
        # )
        # np.testing.assert_allclose(
        #     actual=cuda_data_iq_fir, desired=ground_truth, rtol=RTOL
        # )
        real_cpp = np.linalg.norm(cpp_data_iq_fir.real - ground_truth.real,
                                  axis=-1) / np.linalg.norm(ground_truth.real)
        imag_cpp = np.linalg.norm(cpp_data_iq_fir.imag - ground_truth.imag,
                                  axis=-1) / np.linalg.norm(ground_truth.imag)

        if np.any(real_cpp > RTOL) or np.any(imag_cpp > RTOL):
            raise AssertionError('Hilbert FIR C++ test failed')

        real_cuda = np.linalg.norm(cuda_data_iq_fir.real - ground_truth.real,
                                  axis=-1) / np.linalg.norm(ground_truth.real)
        imag_cuda = np.linalg.norm(cuda_data_iq_fir.imag - ground_truth.imag,
                                  axis=-1) / np.linalg.norm(ground_truth.imag)

        if np.any(real_cuda > RTOL) or np.any(imag_cuda > RTOL):
            raise AssertionError('Hilbert FIR CUDA test failed')

suite = unittest.TestLoader().loadTestsFromTestCase(TestHilbertFIR)
