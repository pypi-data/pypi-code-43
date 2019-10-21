import numpy as np


def x_y_bin(x, y, statFunc, errFunc, maxBinSize=1000):
    '''
    Bin data point according to y and take median inside each bin.
    Parameters
    ----------
    x: numpy.array, x axis
    y: numpy.array, y axis
    statFunc: numpy.ufunc, function to perform in each bin
    errFunc: numpy.ufunc, function to estimate the error or each bin
    maxBinSize, int, default 1000, maximum number of stars in bin

    Returns
    -------
    x_stt, y_stt:
        Output with statFunc applied to each bin
    x_err, y_err:
        Output with errFunc applied to each bin
    '''
    to_pad = (maxBinSize - len(x) % maxBinSize) % maxBinSize
    # Pad the split the array
    x_split = np.pad(x, (0, to_pad), mode='constant', constant_values=np.NaN)
    x_split = x_split.reshape(-1, maxBinSize)
    y_split = np.pad(y, (0, to_pad), mode='constant', constant_values=np.NaN)
    y_split = y_split.reshape(-1, maxBinSize)
    # Size
    split_length = [maxBinSize] * (len(x_split) - 1)
    split_length.append(len(x) - len(split_length) * maxBinSize)
    split_length = np.array(split_length)
    # Main output
    x_stt = statFunc(x_split, split_length)
    y_stt = statFunc(y_split, split_length)
    # Uncertainty
    x_err = errFunc(x_split, split_length)
    y_err = errFunc(y_split, split_length)
    return x_stt, y_stt, x_err, y_err


def range_threshold(arr1, arr2, arr_min, arr_max):
    '''
    arr1[arr_min < arr2 < arr_max]

    Parameters
    ----------
    arr1: numpy.ndarray, the array the be thresholded
    arr2: numpy.ndarray, the array where selection is made
    arr_min: minimum value to accept in arr2
    arr_max: maximum value to accept in arr2

    Returns
    -------
    a thresholded numpy.ndarray
    '''
    return arr1[np.logical_and(arr2 < arr_max, arr2 > arr_min)]
