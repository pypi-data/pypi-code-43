import numpy as np
import scipy.linalg as LA
import math
import warnings


def moving_average_filter(signal: np.ndarray, taps: int) -> np.ndarray:
    """
    Apply moving average filter to "signal".
    See http://www.analog.com/media/en/technical-documentation/dsp-book/dsp_book_Ch15.pdf

    Parameters
    ----------
    signal : np.ndarray
        The signal to be filtered
    taps : int
        width of filter window

    Returns
    -------
    np.ndarray
        filtered input signal
    """
    filter_window = np.ones(taps)/taps
    output = np.convolve(signal, filter_window, 'same')
    return output


def scale_array(array: np.ndarray, lower: float, upper: float) -> np.ndarray:
    """
    Scale values in array to range [lower, upper]

    See: https://stats.stackexchange.com/questions/281162/scale-a-number-between-a-range

    Parameters
    ----------
    array : np.ndarray
    lower : float
        lower end of range
    upper : float
        upper end of range

    Returns
    -------
    np.ndarray
        Scaled array
    """
    min_value = np.min(array)
    max_value = np.max(array)

    scaled = np.array([(upper-lower)*(x-min_value)/(max_value-min_value)+lower for x in array])
    return scaled


def normalize_array(array):
    """ Normalize array to 1.

    :param array: Array to be normalized
    :return: Normalized array
    """
    warnings.warn('Obsolete function. Use scale_array instead.', DeprecationWarning)

    #return array/max(array)
    array_tmp = array.copy()
    if np.min(array) < 0:
        array_tmp -= np.min(array)
    array_tmp /= np.max(array_tmp)
    return array_tmp


def baseline(y, deg=3, max_it=100, tol=1e-3):
    """Computes the baseline of a given data.

    Iteratively performs a polynomial fitting in the data to detect its
    baseline. At every iteration, the fitting weights on the regions with
    peaks are reduced to identify the baseline only.

    Parameters
    ----------
    y : ndarray
        Data to detect the baseline.
    deg : int
        Degree of the polynomial that will estimate the data baseline. A low
        degree may fail to detect all the baseline present, while a high
        degree may make the data too oscillatory, especially at the edges.
    max_it : int
        Maximum number of iterations to perform.
    tol : float
        Tolerance to use when comparing the difference between the current
        fit coefficient and the ones from the last iteration. The iteration
        procedure will stop when the difference between them is lower than
        *tol*.

    Returns
    -------
    ndarray
        Array with the baseline amplitude for every original point in *y*

    Information:
    This function is stolen from https://bitbucket.org/lucashnegri/peakutils
    Documentation: https://pythonhosted.org/PeakUtils/reference.html
    (MIT License)
    """
    order = deg + 1
    coeffs = np.ones(order)

    # try to avoid numerical issues
    cond = math.pow(y.max(), 1. / order)
    x = np.linspace(0., cond, y.size)
    base = y.copy()

    vander = np.vander(x, order)
    vander_pinv = LA.pinv2(vander)

    for _ in range(max_it):
        coeffs_new = np.dot(vander_pinv, y)

        if LA.norm(coeffs_new - coeffs) / LA.norm(coeffs) < tol:
            break

        coeffs = coeffs_new
        base = np.dot(vander, coeffs)
        y = np.minimum(y, base)

    return base
