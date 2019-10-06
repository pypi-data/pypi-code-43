'''Manually find least K GRAPPA operators.'''

from time import time
# import itertools

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree # pylint: disable=E0611
# from scipy.optimize import minimize
from phantominator import radial

if __name__ == '__main__':


    # Radial sampling coordinates
    t0 = time()
    N = 256
    kx, ky = radial(N, N)
    kx = np.reshape(kx, (N, N)).flatten('F')
    ky = np.reshape(ky, (N, N)).flatten('F')

    # Cartesian grid
    tx, ty = np.meshgrid(
        np.linspace(np.min(kx), np.max(kx), N),
        np.linspace(np.min(ky), np.max(ky), N))
    tx, ty = tx.flatten(), ty.flatten()
    outside = np.argwhere(
        np.sqrt(tx**2 + ty**2) > np.max(kx)).squeeze()
    inside = np.argwhere(
        np.sqrt(tx**2 + ty**2) <= np.max(kx)).squeeze()
    tx = np.delete(tx, outside)
    ty = np.delete(ty, outside)
    txy = np.concatenate((tx[:, None], ty[:, None]), axis=-1)
    print('Took %g seconds to load coordinates' % (time() - t0))

    # Desired shifts
    t0 = time()
    kxy = np.concatenate((kx[:, None], ky[:, None]), axis=-1)
    kdtree = cKDTree(kxy)
    _, idx = kdtree.query(txy, k=1)
    dx, dy = tx - kx[idx], ty - ky[idx]
    print('Took %g seconds to find shifts' % (time() - t0))

    # Make the differences integers
    scale_fac = 1e34
    dx = (
        np.exp(np.abs(dx)).astype(np.single)*scale_fac).astype(object)
    for dx0 in dx[:10]:
        print('%d' % dx0)

    from primefac import primefac, factorint
    res = []
    for dx0 in dx:
        res.append(factorint(int(dx0)))

    # Find all unique prime factors
    s = set()
    _ = [s.update(list(d.keys())) for d in res]
    # print(s)
    print(len(s), dx.size)
    assert False

    # What are the unique factors?
    dx_recon = np.zeros(dx.size)
    for ii, r0 in enumerate(res):
        n = np.array(list(r0.values()))
        p = np.array(list(r0.keys()))
        dx_recon[ii] = np.sum(n*np.log(p)) - np.log(scale_fac)
        # print(dx_recon[ii])
        # print(np.log(dx[0]/scale_fac))
        # assert False


    # tot = 1
    # for f in res:
    #     tot = tot*f
    # print(tot)

    # # Initalize
    # M = dx.size
    # K0 = M
    # print('K0: %d' % K0, 'M: %d' % M)
    # A = np.eye(M)[:, :K0]
    # d = np.linalg.solve(A.T @ A, A.T @ dx)


    # done = False
    # d = []
    # todo = np.sort(dx.copy())
    # plt.plot(todo)
    # plt.show()
    # while not done:
    #
    #     d0 = np.min(np.abs(todo))
    #     d.append(d0)
    #
    #     # Search for integer solutions
