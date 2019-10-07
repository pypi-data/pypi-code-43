import numpy as np
from pycuda import gpuarray
from pyus.core.cython.imaging.interpolator.prefilter import (
    call_prefilter_host, call_prefilter_iq_host, call_prefilter_device,
    call_prefilter_iq_device
)

def prefilter_backend(data, boundary: str, interpolator):

    # Expand data to 4D
    if data.ndim < 4:
        missing_dims = 4 - data.ndim
        expand_dims = np.ones(missing_dims, dtype=int)
        new_shape = np.append(expand_dims, data.shape)
        data = data.reshape(new_shape.tolist())

    # Check boundary
    if boundary.lower() in ['mirror', 'reflect']:
        boundary_cpp = 'm'
    elif boundary.lower() == 'zero':
        boundary_cpp = 'z'
    else:
        raise NotImplementedError('Unknown boundary condition')

    # Copy data
    data_filt = data.copy()

    # Dispatch according to data container and data dtype
    if isinstance(data_filt, np.ndarray):
        if data_filt.dtype == np.float32:
            data_filt = call_prefilter_host(
                data_filt, boundary_cpp, interpolator._functor
            )
        elif data_filt.dtype == np.complex64:
            data_filt = call_prefilter_iq_host(data_filt, boundary_cpp,
                                               interpolator._functor)
        else:
            raise TypeError

    elif isinstance(data_filt, gpuarray.GPUArray):
        if data_filt.dtype == np.float32:
            data_filt = call_prefilter_device(data_filt, boundary_cpp,
                                              interpolator._functor)
        elif data_filt.dtype == np.complex64:
            data_filt = call_prefilter_iq_device(data_filt, boundary_cpp,
                                                 interpolator._functor)
        else:
            raise TypeError

    else:
        raise TypeError

    return data_filt.squeeze()