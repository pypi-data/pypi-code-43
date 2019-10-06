'''Self calibrating GROG implementation.

Based on the MATLAB GROG implementation found here:
https://github.com/edibella/Reconstruction
'''

from multiprocessing import Pool
from functools import partial

import numpy as np
from tqdm import tqdm, trange
from scipy.linalg import fractional_matrix_power
from primefac import factorint # pylint: disable=E0401

def fracpowers(idx, Gx, Gy, dkxs, dkys):
    '''Wrapper function to use during parallelization.

    Parameters
    ----------
    idx : array_like
        Indices of current fractioinal power GRAPPA kernels
    Gx : array_like
        GRAPPA kernel in x
    Gy : array_like
        GRAPPA kernel in y
    dkxs : array_like
        Differential x k-space coordinates
    dkys : array_like
        Differential y k-space coordinates

    Returns
    -------
    ii : array_like
        row indices
    jj : array_like
        col indices
    Gxf : array_like
        Fractional power of GRAPPA kernel in x
    Gyf : array_like
        Fractional power of GRAPPA kernel in y
    '''
    ii, jj = idx[0], idx[1]
    try:
        Gxf = fractional_matrix_power(Gx, dkxs[ii, jj])
    except ValueError:
        Gxf = np.zeros(Gx.shape, dtype=Gx.dtype)
    try:
        Gyf = fractional_matrix_power(Gy, dkys[ii, jj])
    except ValueError:
        Gyf = np.zeros(Gy.shape, dtype=Gy.dtype)
    return(ii, jj, Gxf, Gyf)

def grog_interp(kspace, Gx, Gy, traj, cartdims, prime_fac=False):
    '''Moves radial k-space points onto a Cartesian grid via the GROG.

    Parameters
    ----------
    kspace : array_like
        A 3D (sx, sor, soc) slice of k-space
    Gx : array_like
        The unit horizontal cartesian GRAPPA kernel
    Gy : array_like
        Unit vertical cartesian GRAPPA kernel
    traj : array_like
        k-space trajectory
    cartdims : tuple
        (nrows, ncols), size of Cartesian grid

    Returns
    -------
    array_like
        Interpolated cartesian kspace.
    '''

    sx, nor, noc = kspace.shape[:]
    nrows, ncols = cartdims[0:2]

    kxs = np.real(traj)*nrows
    kys = np.imag(traj)*ncols

    # Pre-allocate kspace_out with an extra row,col
    kspace_out = np.zeros((nrows+1, ncols+1, noc), dtype='complex')
    countMatrix = np.zeros((nrows+1, ncols+1), dtype='int')

    # Find nearest integer coordinates
    kxs_round = np.round(kxs)
    kys_round = np.round(kys)

    # Find distance between kxys and rounded kxys, these will be
    # Gx,Gy powers
    dkxs = kxs_round - kxs
    dkys = kys_round - kys

    # Compute fractional matrix powers - this part takes a long time
    # Let's parallelize this since it doesn't matter what order we
    # do it in and elements don't depend on previous elements. Notice
    # that order is not preserved here -- instead we just keep track
    # of indices at each compute.
    if not prime_fac:
        fracpowers_partial = partial(
            fracpowers, Gx=Gx, Gy=Gy, dkxs=dkxs, dkys=dkys)
        tot = len(list(np.ndindex((sx, nor))))
        with Pool() as pool:
            res = list(tqdm(
                pool.imap_unordered(
                    fracpowers_partial, np.ndindex((sx, nor)),
                    chunksize=100), total=tot, leave=False,
                desc='Frac mat pwr'))
    else:

        # Turn into integers (assume single precision)
        scale_fac = 1e34
        dkxs = dkxs.astype(np.single).flatten()
        dkys = dkys.astype(np.single).flatten()
        # scale_fac = 1e20
        # dkxs = dkxs.flatten()
        # dkys = dkys.flatten()
        dxi = (np.exp(np.abs(dkxs))*scale_fac).astype(object)
        dyi = (np.exp(np.abs(dkys))*scale_fac).astype(object)

        # Find prime factorizations
        Dx, Dy = [], []
        for dx0, dy0 in tqdm(
                zip(dxi, dyi), total=dxi.size, leave=False):
            Dx.append(factorint(int(dx0)))
            Dy.append(factorint(int(dy0)))

        # Start a dictionary of fractional matrix powers
        frac_mats_x = {}
        frac_mats_y = {}

        # First thing we need is the scale factor, note that we will
        # assume the inverse!
        lscale_fac = np.log(scale_fac)
        frac_mats_x[lscale_fac] = np.linalg.pinv(
            fractional_matrix_power(Gx, lscale_fac))
        frac_mats_y[lscale_fac] = np.linalg.pinv(
            fractional_matrix_power(Gy, lscale_fac))

        res = []
        for kk, idx in tqdm(
                enumerate(np.ndindex((sx, nor))),
                total=sx*nor, leave=False, desc='Prime fact'):
            ii, jj = idx[:]
            rx = Dx[kk]
            ry = Dy[kk]

            # Component fractional powers are log of prime factors;
            # add in the scale_fac term here so we get it during the
            # multi_dot later.  We explicitly cast to integer because
            # sometimes we run into an MPZ object that doesn't play
            # nice with numpy
            lpx = np.log(np.array(
                [int(r) for r in rx.keys()] + [scale_fac])).squeeze()
            lpy = np.log(np.array(
                [int(r) for r in ry.keys()] + [scale_fac])).squeeze()
            lpx_unique = np.unique(lpx)
            lpy_unique = np.unique(lpy)

            # Compute new fractional matrix powers we haven't seen
            for lpxu in lpx_unique:
                if lpxu not in frac_mats_x:
                    frac_mats_x[lpxu] = fractional_matrix_power(
                        Gx, lpxu)
            for lpyu in lpy_unique:
                if lpyu not in frac_mats_y:
                    frac_mats_y[lpyu] = fractional_matrix_power(
                        Gy, lpyu)

            # Now compose all the matrices together for this point
            nx = list(rx.values()) + [1] # +1 to account for scale_fac
            ny = list(ry.values()) + [1]
            Gxf = np.linalg.multi_dot([
                np.linalg.matrix_power(frac_mats_x[lpx0], n0) for
                lpx0, n0 in zip(lpx, nx)])
            Gyf = np.linalg.multi_dot([
                np.linalg.matrix_power(frac_mats_y[lpy0], n0) for
                lpy0, n0 in zip(lpy, ny)])

            # Hand back answer the way the program usually expects it
            res.append((ii, jj, Gxf, Gyf))


    # Now we need to stick the results where they belong and get a
    # density estimation
    for r in res:
        # Look up the indices associated with this result
        ii, jj = r[0], r[1]

        # Find matrix indices corresponding to kspace coordinates
        # while we're at it:
        xx = int(kxs_round[ii, jj] + nrows/2)
        yy = int(kys_round[ii, jj] + ncols/2)

        # Load result into output matrix and bump the counter
        try:
            kspace_out[xx, yy, :] += np.linalg.multi_dot(
                [r[2], r[3], kspace[ii, jj, :]])
        except IndexError:
            continue
        countMatrix[xx, yy] += 1


    # Lastly, use point-wise division of kspace_out by weightMatrix
    # to average
    nonZeroCount = countMatrix > 0
    countMatrixMasked = countMatrix[nonZeroCount]
    kspace_out[nonZeroCount] /= np.tile(
        countMatrixMasked[:, None], noc)

    # Regridding results in +1 size increase so drop first row,col
    # arbitrarily
    return kspace_out[1:, 1:]

def scgrog(kspace, traj, Gx, Gy, cartdims=None, prime_fac=False):
    '''Self calibrating GROG interpolation.

    Parameters
    ----------
    kspace : array_like
        A 4D (sx, sor, nof, soc) matrix of complex k-space data
    traj : array_like
        k-space trajectory
    Gx : array_like
        The unit horizontal cartesian GRAPPA kernel
    Gy : array_like
        Unit vertical cartesian GRAPPA kernel
    cartdims : tuple
         Size of Cartesian grid.

    Returns
    -------
    kspace_cart : array_like
        Cartesian gridded k-space.
    mask : array_like
        Boolean mask where kspace is nonzero.

    Notes
    -----
    If cartdims=None, we'll guess the Cartesian dimensions are
    (kspace.shape[0], kspace.shape[0], kspace.shape[2],
        kspace.shape[3]).
    '''

    # If the user didn't give us the desired cartesian dimensions...
    # ...guess
    if cartdims is None:
        cartdims = (kspace.shape[0], kspace.shape[0], kspace.shape[2],
                    kspace.shape[3])

    # Permute time to end of 4D data for convenience
    if kspace.ndim == 4:
        kspace = np.transpose(kspace, (0, 1, 3, 2))
        tmp = list(cartdims)
        tmp[2], tmp[3] = tmp[3], tmp[2]
        cartdims = tuple(tmp)

    # Interpolate frame-by-frame
    kspace_cart = np.zeros(cartdims, dtype='complex')
    for ii in trange(kspace.shape[-1], desc='Frame', leave=False):
        time_frame = kspace[:, :, :, ii]
        traj_frame = traj[:, :, ii]
        kspace_cart[:, :, :, ii] = grog_interp(
            time_frame, Gx, Gy, traj_frame, cartdims, prime_fac)

    # Permute back if needed
    if kspace_cart.ndim == 4:
        kspace_cart = np.transpose(kspace_cart, (0, 1, 3, 2))

    # Create mask
    mask = (np.abs(kspace_cart) > 0)

    return(kspace_cart, mask)

if __name__ == '__main__':
    pass
