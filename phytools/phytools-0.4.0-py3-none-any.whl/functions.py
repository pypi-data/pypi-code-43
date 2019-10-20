import numpy as np
import warnings

from . import misc


def gaussian(x, a, x0, fwhm, offset):
    """ Compute Gaussian function.
    http://mathworld.wolfram.com/GaussianFunction.html

    Parameters
    ----------
    x : float
        parameter at which the Gaussian function is computed
    a : float
        amplitude
    x0 : float
        offset on x-axis
    fwhm : float
        Full-width-at-half-maximum (FWHM)
    offset : float
        amplitude offset

    Returns
    -------
    float
        Value of Gaussian function for x

    Notes
    -----
    If x is an np.array, a corresponding array is returned.
    """
    s = fwhm/(2*np.sqrt(2*np.log(2)))
    return a*np.exp(-(x-x0)**2/(2*s**2)) + offset


def gaussian2d(x, y, a, x0, y0, fwhm_x, fwhm_y, offset):
    """ Compute two-dimensioanl Gaussian function.

    Parameters
    ----------
    x : float
        x coordinate at which the Gaussian function is computed
    y : float
        y coordinate at which the Gaussian function is computed
    a : float
        amplitude
    x0 : float
        offset on x-axis
    y0 : float
        offset on y-axis
    fwhm_x : float
        Full-width-at-half-maximum (FWHM) along x axis
    fwhm_y : float
        Full-width-at-half-maximum (FWHM) along y axis
    offset : float
        amplitude offset

    Returns
    -------
    float
        Value of Gaussian function at coordinates x,y

    Notes
    -----
    If x is an np.mgrid (or meshgrid), a corresponding mgrid is returned.
    """
    s_x = fwhm_x/(2*np.sqrt(2*np.log(2)))
    s_y = fwhm_y/(2*np.sqrt(2*np.log(2)))

    return a*np.exp(-(x-x0)**2/(2*s_x**2) - (y-y0)**2/(2*s_y**2)) + offset


def lorentzian(x, a, x0, fwhm, offset):
    """ Compute Lorentzian function.
    http://mathworld.wolfram.com/LorentzianFunction.html
    The function is normalized not to its area, but to the amplitude a.

    Parameters
    ----------
    x : float
        parameter at which the Lorentzian function is computed
    a : float
        amplitude
    x0 : float
        offset on x-axis
    fwhm : float
        Full-width-at-half-maximum (FWHM)
    offset : float
        amplitude offset

    Returns
    -------
    float
        Value of Lorentzian function for x

    """
    return a*fwhm**2/4/((x-x0)**2 + (fwhm/2)**2) + offset


def boxcar(x_array, center, width):
    """ Compute boxcar (rectangular) function
    https://en.wikipedia.org/wiki/Boxcar_function

    Parameters
    ----------
    x_array : np.ndarray
        Array containing the x values of the function
    center : float
        Center of the box (rectangular pulse) in units of x_array
    width : float
        Center of the box (rectangular pulse) in units of x_array

    Returns
    -------
    np.ndarray
        Boxcar function
    """
    r = np.zeros(len(x_array))
    for idx, x in enumerate(x_array):
        if center-width/2 <= x <= center+width/2:
            r[idx] = 1
        else:
            r[idx] = 0
    return r


def boxcar_inverse(x_array, center, width):
    """ Compute inverse boxcar (rectangular) function

    Parameters
    ----------
    x_array : np.ndarray
        Array containing the x values of the function
    center : float
        Center of the box (rectangular pulse) in units of x_array
    width : float
        Center of the box (rectangular pulse) in units of x_array

    Returns
    -------
    np.ndarray
        Inverse boxcar function
    """
    r = np.zeros(len(x_array))
    for idx, x in enumerate(x_array):
        if center-width/2 <= x <= center+width/2:
            r[idx] = 0
        else:
            r[idx] = 1
    return r


def scale_lin2log(value):
    """
    Scale value to log scale: log10(value)*10

    Parameters
    ----------
    value : float or array-like
        Value or array to be scaled

    Returns
    -------
    float or array-like
        Scaled value
    """
    return np.log10(value)*10


def scale_log2lin(value):
    """
    Scale value from log10 to linear scale: 10**(value/10)

    Parameters
    ----------
    value : float or array-like
        Value or array to be scaled

    Returns
    -------
    float or array-like
        Scaled value
    """
    return 10**(value/10)


def scale(value, mode):
    """ Scale value

    Parameters
    ----------
    value : float or array-like
        Value or array to be scaled
    mode : str
        'log': scale to log10(value)*10
        'linear': scale to linear from log10

    Returns
    -------
    float or array-like
        Scaled value
    """
    warnings.warn('scale is deprecated. Use scale_log2lin or scale_lin2log instead.', DeprecationWarning)
    print('Warning: scale is deprecated. Use scale_log2lin or scale_lin2log instead.')

    if mode == 'linear':
        return scale_log2lin(value)
    elif mode == 'log':
        return scale_lin2log(value)


def initial_fit_values(data_x, data_y, mode):
    """ Guess initial values for a fit procedure

    Parameters
    ----------
    data_x : np.array
        x data
    data_y : np.array
        y_data
    mode : str
        Defines which function is assumed for fitting procedure. Can be one of the following:
        'gaussian', 'lorentzian'

    Returns
    -------
    List of initial values. Content of the list depends on "mode".
    mode == 'gaussian' or 'lorentzian': [amplitude (a), offset on x-axis (x0), full-width-at-half-maximum (fwhm),
        amplitude offset (offset)]
    """
    if mode == 'gaussian' or mode == 'lorentzian':
        max_index = np.argmax(data_y)
        x0_0 = data_x[max_index]
        a_0 = data_y[max_index]

        _, idx_right = misc.find_nearest(data_y[max_index:-1], a_0 / 2)
        _, idx_left = misc.find_nearest(data_y[0:max_index], a_0 / 2)
        y_right = data_y[max_index + idx_right]
        y_left = data_y[idx_left]
        fwhm_0 = np.abs(y_right - y_left)

        offset_0 = np.amin(data_y)

        return [a_0, x0_0, fwhm_0, offset_0]
