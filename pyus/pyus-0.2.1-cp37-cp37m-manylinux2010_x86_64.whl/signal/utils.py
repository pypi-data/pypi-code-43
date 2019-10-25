import scipy.signal
import numpy as np
from typing import Tuple, Optional, Union, Iterable
from pycuda import gpuarray

from pyus.signal.hilbert.basehilbertfir import compute_fir_hilbert
from pyus.core.cython.signal.utils import (
    magnitude_cuda, magnitude_cpp, env2bmode_cuda, env2bmode_cpp,
    iq2bmode_cuda, iq2bmode_cpp, rf2bmode_cuda, rf2bmode_cpp
)


def butter_bandpass(
        lowcut: float, highcut: float,
        sampling_frequency: float, order: int = 6
) -> Tuple[np.ndarray, np.ndarray]:

    nyq = 0.5 * sampling_frequency
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band', output='ba')

    return b, a


def butter_bandpass_filter(
        x: np.ndarray, lowcut: float, highcut: float,
        sampling_frequency: float, order: int = 6
        # TODO: add axis?
) -> np.ndarray:

    b, a = butter_bandpass(lowcut, highcut, sampling_frequency, order)
    y = scipy.signal.filtfilt(b=b, a=a, x=x)

    return y


def normalize(
        x: np.ndarray,
        norm: str = 'max',
        axis: Optional[int] = None,
        copy: bool = True,
) -> np.ndarray:

    if not isinstance(norm, str):
        raise TypeError('Must be a str')

    if axis is not None:
        if not isinstance(axis, int):
            raise TypeError('Must be an int')

    if norm.lower() == 'max':
        fact = np.max(np.abs(x), axis=axis, keepdims=True)
    elif norm.lower() == 'std':
        fact = np.std(x, axis=axis, keepdims=True)
    else:
        raise NotImplementedError('Unsupported norm \'{}\''.format(norm))

    # Pointer or copy depending on `copy` flag
    # TODO(@dperdios): remove copy flag and add optional `out`?
    out = x.copy() if copy else x

    # In-place division (broadcasting)
    out /= fact

    return out


def envelope(
        x: np.ndarray,
        method: str = 'hilbert',
        remove_dc: bool = False,
        axis: int = -1
) -> np.ndarray:

    if not isinstance(method, str):
        raise TypeError('Must be a str')

    # Remove DC offset depending on flag
    if remove_dc:
        x_nodc, dc = _remove_dc_offset(x=x, axis=axis)
    else:
        x_nodc, dc = x, 0

    if method.lower() == 'hilbert':
        env = envelope_hilbert(x=x_nodc, axis=axis)
    elif method.lower() == 'fir':
        env = envelope_fir(x=x_nodc, filter_size=15, axis=axis)
    else:
        raise NotImplementedError('Unsupported method')

    # Restore DC offset
    env += dc

    return env


def compress_log10(x: np.ndarray, copy: bool = True) -> np.ndarray:

    # Pointer or copy depending on `copy` flag
    # TODO(@dperdios): remove copy flag and add optional `out`?
    out = x.copy() if copy else x

    # Make sure no negative or zero values
    out[out <= 0] = np.spacing(1, dtype=x.dtype)
    np.log10(out, out=out)

    return out


def bmode(
        x: np.ndarray, norm: Optional[str] = None, axis: int = -1
) -> np.ndarray:

    # Envelope detection using FIR
    env = envelope_fir(x=x, filter_size=15, axis=axis)

    # Normalize
    if norm is not None:
        env = normalize(x=env, norm=norm, copy=False)

    # Log-compression
    bm = compress_log10(x=env, copy=False)
    bm *= 20

    return bm


def envelope_hilbert(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Envelope detection using Hilbert transform

    Note: input signal is assumed to be without DC
    """

    env = np.abs(scipy.signal.hilbert(x=x, axis=axis))

    return env


def envelope_fir(
        x: np.ndarray, filter_size: int = 15, axis: int = -1
) -> np.ndarray:
    """FIR-filter implementation for envelope detection

     Note: same as Matlab envelope function
     Note: input signal is assumed to be without DC
    """
    if axis != -1:
        raise NotImplementedError('Only axis=-1 supported')
    # TODO(@dperdios): generalize to any axis (using PyDirConvolution)

    beta = 8
    fir_hilbert = compute_fir_hilbert(filter_size=filter_size, beta=beta)

    # Apply filter and take the magnitude
    # TODO(@dperdios): use PyDirConvolution when more dtypes available
    env = np.zeros_like(x)
    #   Reshape array to iterate (generalize to any dim)
    x_it = x.reshape(-1, x.shape[-1])
    env_it = env.reshape(-1, env.shape[-1])
    for s, e in zip(x_it, env_it):
        sig_ana = np.convolve(s, fir_hilbert, 'same')  # complex128...
        np.abs(sig_ana, out=e)

    return env


def _remove_dc_offset(
        x: np.ndarray, axis: int = -1, copy=True
) -> Tuple[np.ndarray, np.ndarray]:

    # Pointer or copy depending on `copy` flag
    # TODO(@dperdios): remove copy flag and add optional `out`?
    out = x.copy() if copy else x

    dc = np.mean(x, axis=axis, keepdims=True)
    out -= dc

    return out, dc


def magnitude(
        x: Union[np.ndarray, gpuarray.GPUArray],
        out: Optional[Union[np.ndarray, gpuarray.GPUArray]] = None
):
    if out is None:
        out = np.zeros(x.shape, dtype=np.float32)

    if isinstance(x, gpuarray.GPUArray):
        out = gpuarray.to_gpu(out)
        magnitude_cuda(x, out)
    else:
        magnitude_cpp(x, out)

    return out


def env2bmode(
        envelope: Union[np.ndarray, gpuarray.GPUArray],
        norm: str = 'max',
        norm_factor: Union[Iterable, float] = 0,
        bmode: Optional[Union[np.ndarray, gpuarray.GPUArray]] = None
):

    norm_factors = np.array([norm_factor], dtype=np.float32).ravel()

    if bmode is None:
        bmode = np.zeros(envelope.shape, dtype=envelope.dtype)

    if isinstance(envelope, gpuarray.GPUArray):
        bmode = gpuarray.to_gpu(bmode)
        env2bmode_cuda(envelope, norm, norm_factors, bmode)
    else:
        env2bmode_cpp(envelope, norm, norm_factors, bmode)

    return bmode


def iq2bmode(
        iq_data: Union[np.ndarray, gpuarray.GPUArray],
        norm: str = 'max',
        norm_factor: Union[Iterable, float] = 0,
        bmode: Optional[Union[np.ndarray, gpuarray.GPUArray]] = None
):

    norm_factors = np.array([norm_factor], dtype=np.float32).ravel()

    if bmode is None:
        bmode = np.zeros(iq_data.shape, dtype=np.float32)

    if isinstance(iq_data, gpuarray.GPUArray):
        bmode = gpuarray.to_gpu(bmode)
        iq2bmode_cuda(iq_data, norm, norm_factors, bmode)
    else:
        iq2bmode_cpp(iq_data, norm, norm_factors, bmode)

    return bmode


def rf2bmode(
        rf_data: Union[np.ndarray, gpuarray.GPUArray],
        norm: str = 'max',
        norm_factor: Union[Iterable, float] = 0,
        bmode: Optional[Union[np.ndarray, gpuarray.GPUArray]] = None
):

    norm_factors = np.array([norm_factor], dtype=np.float32).ravel()

    fir_filter = compute_fir_hilbert(filter_size=21, beta=8)

    if bmode is None:
        bmode = np.zeros(rf_data.shape, dtype=rf_data.dtype)

    if isinstance(rf_data, gpuarray.GPUArray):
        bmode = gpuarray.to_gpu(bmode)
        rf2bmode_cuda(rf_data, fir_filter, norm, norm_factors, bmode)
    else:
        rf2bmode_cpp(rf_data, fir_filter, norm, norm_factors, bmode)

    return bmode