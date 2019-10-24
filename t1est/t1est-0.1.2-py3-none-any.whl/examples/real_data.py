'''Use actual data.'''

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from t1est import t1est

if __name__ == '__main__':

    fft = lambda x0, axes: np.fft.ifftshift(np.fft.fft2(
        np.fft.fftshift(x0, axes=axes),
        axes=axes), axes=axes)
    ifft = lambda x0, axes: np.fft.fftshift(np.fft.ifft2(
        np.fft.ifftshift(x0, axes=axes),
        axes=axes), axes=axes)

    path = (
        '/home/nicholas/Documents/rawdata/'
        'P043018-20190710T193153Z-001/P043018/')
    filename = 'FID12461.mat'
    d = loadmat(path + filename)['kspace']
    d = ifft(d, axes=(0, 1))
    time_frames = [0, 5, 1, 6, 2, 7, 3, 4]
    d = d[..., time_frames, :]
    sx4 = int(d.shape[0]/4)
    d = d[sx4:-sx4, ...]
    sx, sy, st, sc = d.shape[:]

    # Get magnitude data
    mag = True
    d = np.sqrt(np.sum(np.abs(d)**2, axis=-1))
    d = 100*d/np.max(d.flatten())

    # # Use complex data
    # mag = False
    # phi = np.zeros((sx, sy, st))
    # for tt in range(st):
    #     phi[..., tt] = virtcoilphase(d[..., tt])
    # d = np.sqrt(np.sum(np.abs(d)**2, axis=-1))
    # d = d*phi
    # plt.imshow(np.abs(d[..., 0]))
    # plt.show()

    TIs = np.array([
        117., 257., 1172., 1282., 2172., 2325., 3174., 4189.])
    TIs *= 1e-3

    mask = np.zeros((sx, sy), dtype=bool)
    sx4, sy4 = int(sx/3), int(sy/3)
    mask[sx4:-sx4, sy4:-sy4] = True

    T1map = t1est(
        d, TIs, time_axis=-1, mask=mask, method='lm',
        T1_bnds=(0, 3), chunksize=10, molli=True, mag=mag)

    plt_args = {'vmin':0, 'vmax':3}
    plt.imshow(T1map, **plt_args)
    plt.show()
