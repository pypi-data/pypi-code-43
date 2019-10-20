import numpy as np
from . import constants as const


def wl_to_freq(wl):
    """ Convert wavelength (in vacuum) to frequency

    Parameters
    ----------
    wl : float
        Wavelength

    Returns
    -------
    float
        Frequency
    """
    return const.C0/wl


def freq_to_wl(freq):
    """ Convert frequency to wavelength (in vacuum)

    Parameters
    ----------
    freq : float
        Frequency

    Returns
    -------
    float
        Wavelength

    """
    return const.C0/freq


def spectral_width_freq(width_wl, wl0):
    """ Compute spectral frequency width from spectral wavelength width

    Parameters
    ----------
    width_wl : float
        Spectral wavelength width (in m)
    wl0 : float
        Center wavelength (in m)

    Returns
    -------
    float
        Spectral frequency width (in 1/s)

    """
    return width_wl*const.C0/wl0**2


def spectral_width_wl(width_freq, wl0):
    """ Compute spectral wavelength width from spectral frequency width

    Parameters
    ----------
    width_freq : float
        Spectral frequency width (in 1/s)
    wl0 : float
        Center wavelength (in m)

    Returns
    -------
    float
        Spectral wavelength width (in m)

    """
    return wl0**2/const.C0*width_freq


def free_spectral_range(length):
    """ Compute free-spectral range of an optical cavity with given length.

    Parameters
    ----------
    length : float
        Cavity length (in m)

    Returns
    -------
    float
        Free-specral range (in 1/s)
    """
    return const.C0/(2*length)


def fpi_transmission(delta: float, r1: float, r2: float) -> float:
    """
    Compute transmission through a Fabry-Perot interferometer.
    The transmission is described by the Airy function.

    Parameters
    ----------
    delta : float
        Round-trip phase inside the cavity (in radians)
    r1 : float
        Reflection coefficient (field value) for mirror 1
    r2 : float
        Reflection coefficient (field value) for mirror 2

    Returns
    -------
    float
        Transmission (power value)

    Notes
    -----
    [1] Saleh, Bahaa EA, and Malvin Carl Teich. Fundamentals of photonics, 2007
    """
    f = 4*r1*r2/(1-r1*r2)**2  # f: "finesse coefficient", note: finesse=pi*sqrt(f)/2=pi*sqrt(r1*r2)/(1-r1*r2)
    a = (1-r1**2)*(1-r2**2)/(1-r1*r2)**2

    return a/(1+f*np.sin(delta/2)**2)


def fpi_circulating_power(delta: float, r1: float, r2: float) -> float:
    """
    Compute the intra-cavity circulating power inside a Fabry-Perot interferometer.

    Parameters
    ----------
    delta : float
        Round-trip phase inside the cavity (in radians)
    r1 : float
        Reflection coefficient (field value) for mirror 1. This is the mirror where the light enters the cavity.
    r2 : float
        Reflection coefficient (field value) for mirror 2. This is the mirror where the light exists the cavity.

    Returns
    -------
    float
        Factor by which the input power is increased inside the cavity
    """
    transmission_2 = 1 - r2**2
    return fpi_transmission(delta, r1, r2)/transmission_2
