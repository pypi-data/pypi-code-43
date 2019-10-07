import numpy as np
from typing import Optional


def _data_to_coeffs(
        data: np.ndarray,   # N-D array with last dimension to filter
        poles: np.ndarray,  # 1D array
        boundary: str,
        tol: Optional[float] = None
):
    """In-place pre-filtering"""
    # Tolerance (if not provided, defaults to data-type tolerance)
    if tol is None:
        # Note: not safe to check data.dtype (may be complex)
        tol = np.spacing(1, dtype=poles.dtype)

    # Flatten data-view except last dimension (on which interpolation occurs)
    data_len = data.shape[-1]
    data_it = data.reshape(-1, data_len)

    # Make sure `poles` is a numpy array
    poles = np.asarray(poles)

    # Compute and apply overall gain
    gain = np.prod((1 - poles) * (1 - 1 / poles))
    data_it *= gain

    for pole in poles:
        # Causal initialization
        data_it[:, 0] = _init_causal_coeff(
            data=data_it, pole=pole, boundary=boundary, tol=tol
        )

        # Causal recursion
        for n in range(1, data_len):
            data_it[:, n] += pole * data_it[:, n - 1]

        # Anti-causal initialization
        data_it[:, -1] = _init_anticausal_coeff(
            data=data_it, pole=pole, boundary=boundary
        )

        # Anti-causal recursion
        for n in reversed(range(0, data_len - 1)):
            data_it[:, n] = pole * (data_it[:, n + 1] - data_it[:, n])  # w/ gain
            # data_it[:, n] = pole * data_it[:, n + 1] + (1 - pole) ** 2 * data_it[:, n]  # w/o gain

    return data


def _init_causal_coeff(data: np.ndarray, pole: float, boundary: str, tol: float):
    """First coefficient of the causal filter"""

    # Pre-computations
    data_len = data.shape[-1]
    horizon = data_len
    if tol > 0:
        horizon = int(np.ceil(np.log(tol)) / np.log(np.abs(pole)))

    if boundary.lower() in ['mirror', 'reflect']:
        zn = float(pole)  # copy to hold power (not sure float() is required)
        if horizon < data_len:
            # Approximation (accelerated loop)
            c0 = data[:, 0]
            for n in range(1, horizon):
                c0 += zn * data[:, n]
                zn *= pole
        else:
            # Exact expression (full loop)
            iz = 1 / pole
            z2n = pole ** (data_len - 1)
            c0 = data[:, 0] + z2n * data[:, -1]
            z2n *= z2n * iz
            for n in range(1, data_len):
                c0 += (zn + z2n) * data[:, n]
                zn *= pole
                z2n *= iz
            c0 /= (1 - zn ** 2)
    elif boundary.lower() == 'zero':
        # zn = 1  # TODO: probably wrong
        zn = pole
        mul = pole * pole / (1 - pole * pole)
        if horizon < data_len:
            # Approximation (accelerated loop)
            c0 = data[:, 0]
            for n in range(1, horizon):
                c0 -= mul * zn * data[:, n]
                zn *= pole
        else:
            # Exact expression (full loop)
            zN = pole ** (data_len + 1)
            c0 = data[:, 0] - data[:, -1] * zN
            for n in range(1, data_len - 1):
                c0 -= mul * zn * (data[:, n] - zN * data[:, -1 - n])
                zn *= pole
        c0 *= (1 - pole * pole) / (1 - pole ** (2 * data_len + 2))
    else:
        raise NotImplementedError('Unknown boundary condition')

    return c0


def _init_anticausal_coeff(data: np.ndarray, pole: float, boundary: str):
    """Last coefficient of the anticausal filter"""
    if boundary.lower() in ['mirror', 'reflect']:
        cn = (pole / (pole * pole - 1)) * (pole * data[:, -2] + data[:, -1])
        return cn
    elif boundary.lower() == 'zero':
        return -pole * data[:, -1]  # w/ gain
        # return (1 - pole) ** 2 * data[:, -1]  # w/o gain
    else:
        raise NotImplementedError('Unknown boundary condition')


def direct_filter(fk, pole, boundary, tol=0):
    # tol = 1e-9 # Admissible relative error. Set it to 0 to use exact expression
    N = fk.size

    # Cubic B-Spline pole
    # pole = np.sqrt(3) - 2

    # Compute gain
    # gain = (1 - pole) * (1 - 1 / pole)

    # Causal initialization
    M = N
    if tol > 0:
        M = int(np.ceil(np.log(tol) / np.log(np.abs(pole))))

    if boundary is 'reflect':
        if M < N:
            # Approx
            c_plus_0 = fk[0]
            for i in range(1, M):
                c_plus_0 += fk[i] * pole ** i
        else:
            # Exact
            c_plus_0 = fk[0] + fk[N - 1] * pole ** (N - 1)
            for i in range(1, N - 1):
                c_plus_0 += fk[i] * (pole ** i + pole ** (2 * N - 2 - i))
            c_plus_0 *= 1 / (1 - pole ** (2 * N - 2))
    elif boundary is 'edge':
        if M < N:
            # Approx
            c_plus_0 = fk[0]
            for i in range(0, M):
                c_plus_0 += fk[i] * pole ** (i + 1)
        else:
            # Exact
            c_plus_0 = fk[0]
            for i in range(0, N):
                c_plus_0 += fk[i] * (pole ** (i + 1) + pole ** (2 * N - i))
            c_plus_0 *= 1 / (1 - pole ** (2 * N))
            # c_plus_0 *= gain / (1 - pole ** (2 * N))
    elif boundary in ['constant', 'zero']:
        if M < N:
            # Approx
            c_plus_0 = fk[0]
            for i in range(1, M):
                c_plus_0 -= (pole ** 2 / (1 - pole ** 2)) * pole ** i * fk[i]
            c_plus_0 *= (1 - pole ** 2) / (1 - pole ** (2 * N + 2))
            # c_plus_0 *= gain * (1 - pole ** 2) / (1 - pole ** (2 * N + 2))
        else:
            # Exact
            c_plus_0 = fk[0] - fk[N - 1] * pole ** (N + 1)
            for i in range(1, N - 1):
                c_plus_0 -= (pole ** 2 / (1 - pole ** 2)) * pole ** i * (
                        fk[i] - pole ** (N + 1) * fk[N - 1 - i])
            c_plus_0 *= (1 - pole ** 2) / (1 - pole ** (2 * N + 2))
            # c_plus_0 *= gain * (1 - pole ** 2) / (1 - pole ** (2 * N + 2))
    elif boundary is 'zero_fk':
        if M < N:
            raise NotImplementedError
        else:
            c_plus_0 = fk[0]
    else:
        raise NotImplementedError('Unknown boundary {}'.format(boundary))

    ck_plus = np.zeros(fk.shape)

    ck_plus[0] = c_plus_0

    # Causal recursion
    for i in range(1, ck_plus.size):
        ck_plus[i] = fk[i] + pole * ck_plus[i - 1]
        # ck_plus[i] += gain * fk[i] + pole * ck_plus[i - 1]
    ck = np.zeros(fk.shape)

    # Anti-causal initialization
    if boundary is 'reflect':
        ck[-1] = (1 - pole) ** 2 / (1 - pole ** 2) * (
                pole * ck_plus[-2] + ck_plus[-1])
        # ck[-1] = (pole / (pole ** 2 - 1)) * (pole * ck[-2] + ck[-1])
    elif boundary is 'edge':
        ck[-1] = (1 - pole) * ck_plus[-1]
        # ck[-1] = (pole / (pole - 1)) * ck[-1]
    elif boundary in ['constant', 'zero']:
        ck[-1] = (1 - pole) ** 2 * ck_plus[-1]
        # ck[-1] = -pole * ck_plus[-1]
    elif boundary is 'zero_fk':
        ck[-1] = (1 - pole) / (1 + pole) * ck_plus[-1]
    else:
        raise NotImplementedError('Unknown boundary: {}'.format(boundary))

    # Anticausal recursion
    for i in range(ck.size - 2, -1, -1):
        ck[i] = pole * ck[i + 1] + (1 - pole) ** 2 * ck_plus[i]
        # ck[i] = pole * (ck[i + 1] - ck_plus[i])

    return ck
