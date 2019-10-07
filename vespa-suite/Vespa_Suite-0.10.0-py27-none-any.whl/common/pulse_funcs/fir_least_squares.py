# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# our modules
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception

# ::FIXME:: Test this against Matpulse code and verify
# the algorithm for adding weights into this code (see 
# a digital filter design book, or something similar).

def firls(N,f,D,wts=None):
    """
    Least-squares FIR filter routine.
    
    N -- filter length, must be odd
    f -- list of tuples of band edges
         Units of band edges are Hz with 0.5 Hz == Nyquist
         and assumed 1 Hz sampling frequency
    D -- list of desired responses, one per band
    wts -- list of weights for each of the bands
    
    May raise (or throw) PulseFuncException
    """
        
    if wts == None:
        wts = [1.0 for d in D]
        
    assert len(D) == len(f), "must have one desired response per band"

    h = np.zeros(N)    
    
    if N%2:    
        L = (N-1)//2
        k = np.arange(L+1)
        k.shape = (1, L+1)
        j = k.T
    
        R = 0
        r = 0
        for i, (f0, f1) in enumerate(f):
            R += wts[i]*np.pi*(f1*np.sinc(2*(j-k)*f1) - f0*np.sinc(2*(j-k)*f0) + \
                               f1*np.sinc(2*(j+k)*f1) - f0*np.sinc(2*(j+k)*f0))
    
            r += wts[i]*D[i]*2*np.pi*(f1*np.sinc(2*j*f1) - f0*np.sinc(2*j*f0))
    
        a = np.dot(np.linalg.inv(R), r)
        a.shape = (-1,)

        h[:L] = a[:0:-1]/2.
        h[L] = a[0]
        h[L+1:] = a[1:]/2.
    else:
        # FIXME: Can we make this work for an even number of points?
        # It looks plausible that doing so should be possible.
        # L = N//2
  
        error_message = 'Error: Increase (or decrease) the number of points by one'
        raise pulse_func_exception.PulseFuncException(error_message, 1)

    return h
    
    
def plot_response(h, name):
    H = np.fft.fft(h, 2000)
    f = np.arange(2000)/2000.
    figure()
    semilogy(f, abs(H))
    grid()
    setp(gca(), xlim=(0, .5))
    xlabel('frequency (Hz)')
    ylabel('magnitude')
    title(name)

    
#if __name__ == '__main__':
#    h = firls(31, [(0, .2), (.3, .5)])
#    from matplotlib.pyplot import *
#    plot_response(h, 'lowpass')
#    h = firls(51, [(0, .25), (.35, .5)], [0, 1])
#    plot_response(h, 'highpass')
#    h = firls(51, [(0, .1), (.2, .3), (.4, .5)], [0, 1, 0])
#    plot_response(h, 'bandpass')
#    show()

# ___________________________________________
#
# Matlab firls()

