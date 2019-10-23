import numpy as np
from webgeodyn.filters import coeffilter, modelfilter
from scipy.signal import butter, lfilter


@coeffilter
def removemean(coefs):
    """ Subtracts the temporal mean from the value of
    spherical harmonic coefficients.
    """
    return coefs - np.mean(coefs, axis=0)


@modelfilter
def subsample(model, n):
    """ Subsamples by n the time axis of the whole model. """
    print('Subsampling, 1 over ', n)
    for measureName in model.measures:
        if (measureName in model.measures) and (model.measures[measureName] is not None):
            newcoef = model.measures[measureName].data[::n]
            model.measures[measureName].setData(newcoef)
        if (measureName in model.measures_rms) and (model.measures_rms[measureName] is not None):
            newcoef_rms = model.measures_rms[measureName].data[::n]
            model.measures_rms[measureName].setData(newcoef_rms)
    model.times = model.times[::n]
    return model


@modelfilter
def subtime(model, it0, it1):
    """ Extracts a time window given by [it0, it1] of the whole model. """
    for measureName in model.measures:
        if (measureName in model.measures) and (model.measures[measureName] is not None):
            newcoef = model.measures[measureName].data[it0:it1]
            model.measures[measureName].setData(newcoef)
        if (measureName in model.measures_rms) and (model.measures_rms[measureName] is not None):
            newcoef_rms = model.measures_rms[measureName].data[it0:it1]
            model.measures_rms[measureName].setData(newcoef_rms)

    model.times = model.times[it0:it1]
    return model


@modelfilter
def mean(model):
    """ Performs the temporal mean of the whole model. """
    for measureName in model.measures:
        if (measureName in model.measures) and (model.measures[measureName] is not None):
            newcoef = np.mean(model.measures[measureName].data,axis=0,keepdims=True)
            model.measures[measureName].setData(newcoef)
        if (measureName in model.measures_rms) and (model.measures_rms[measureName] is not None):
            newcoef_rms = np.mean(model.measures_rms[measureName].data,axis=0,keepdims=True)
            model.measures_rms[measureName].setData(newcoef_rms)

    model.times = ['Mean']
    return model


def butterfilter(btype, fs, order, Wn):
    """ Butterworth filter from scipy. """
    nyq = 0.5 * fs
    if type(Wn) is list:
        Wn_nyq = [Wn[0] / nyq, Wn[1] / nyq]
    else:
        Wn_nyq = Wn / nyq
    b, a = butter(order, Wn_nyq, btype=btype, analog=False)
    return b, a


@coeffilter
def butterworth(coefs, btype, fs, order, Wn):
    """ Applies a Butterworth filter from scipy to coefs.
    TODO : Check fs, Wn
    Parameters :
    btype : {'lowpass', 'highpass', 'bandpass', 'bandstop'}
        Type of the Butterworth filter
    fs : float
        Sample frequency
    order : int
        Order of the Butterworth filter
    Wn : ?
    """
    b, a = butterfilter(btype, fs, order, Wn)
    return lfilter(b, a, coefs, axis=0)


def deriv_series(A, t):
    """ Derivates A with respect to t. """
    [n,nt]=A.shape  # Extracts the time dimension nt
#    print(A.shape)
#    dAdt = (A[:,1:nt] - A[:,0:nt-1]) / (t[1:nt]-t[0:nt-1])
#    tm = (t[0:nt-1]+t[1:nt])/2.
    dAdt = (A[:,2:nt] - A[:,0:nt-2]) / (t[2:nt]-t[0:nt-2])
    tm = (t[0:nt-2]+t[2:nt])/2.
#    print(dAdt.shape)

    return dAdt, tm
