# Python modules
from __future__ import division

# 3rd party modules
import numpy as np
import scipy as sp
import scipy.signal as sps

# Our modules
import vespa.common.pulse_funcs.fir_least_squares as fir_least_squares
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


def linear_filter(fr, mag, wts, na, use_remez, mmgresol):

    """
    Function to create a (linear phase) digital filter
    
    Parameters [fp fs], mag, [wt1, wt2], and na from pulse setup
    Returns h (b-polynomial (evaluated around the unit circle), 
    a (a-polynomial evaluated around the unit circle), and w (freq)
    
    May raise (or throw) PulseFuncException
    
    For more information see:
    J. Pauly, P. Le Roux, D. Nishimura, A. Macovski, 
    'Parmater Relations for the Shinnar-Le Roux Selective Excitation Pulse Design Algorithm',
    IEEE Transactions on Medical Imaging, Vol. 10, No. 1, pp 53-65, March 1991.
    """
    
    # Adapted for Python from Matlab:  MPLFILTL.M

    # fr - pass and stop
    # mag - magnetization
    # wts - weights
    
    f = np.array(fr)
    m = np.array(mag)
    wt = np.array(wts)    

    # Check for filter function wanted
    if use_remez == True:
        # FYI: The matlab documentation for the remez() function
        # is now included as part of "firpm()", the parks Mclellan function.
        #
        # remez() - 
        # Calculate the filter-coefficients for the finite impulse response
        # (FIR) filter whose transfer function minimizes the maximum error
        # between the desired gain and the realized gain in the specified bands
        # using the remez exchange algorithm.
        #
        # b = sps.remez(na-1, f, m, wt)
        # default sampling frequency is 1 Hz.  
        # Put in 2 Hz in order for this to work.        
        #
        b = sps.remez(na, f, m[::2], wt, 2)
    else:        
        # Group f values into pairs.
        fx = f/2.0
        i = 0
        fin = []
        for fi in fx:
            if i%2 == 0:
                fi_0 = fi
            else:
                fin.append( (fi_0, fi) )
            i += 1
                
        # Also, Take every other value out of m
        min = m[0::2]
               
        # NOTE: RESULTS (without weights) were NOT IN AGREEMENT 
        # WITH MATPULSE.
        #
        # ::FIXME:: Compare results with Matpulse to be sure
        # we are doing the weights correctly.
        # It looks good by visual inspection.
        #
        # b = firls(na-1, fin, m, wt)
        # Changed from na-1 to na, as we did in remez, so that it will 
        # work with an odd number of time steps / time points.
        if na%2 == 0:
            error_message = 'An odd number of time steps is required for least squares filtering.'
            raise pulse_func_exception.PulseFuncException(error_message, 1)
                
        b = fir_least_squares.firls(na, fin, min, wt)         


    whole = 1
    
    #[hr,wr] = sps.freqz(b, 1, mmgresol, 'whole') 
    (wr, hr) = sps.freqz(b, 1, mmgresol, whole) 
    h = hr.copy()
    w = wr.copy()
    
    # Next calculate the A(z)

    # at2 = (1-(real(h).^2 + imag(h).^2)) ;
    at2 = (1 - ( (np.real(h))**2 + (np.imag(h))**2) ) 

    #x = np.sqrt(at2) 
    # Need to use this version of sqrt because it will
    # work with negative numbers.
    # After fixing the remez calculation above this may no longer
    # be necessary, but probably won't hurt...
    x = np.lib.scimath.sqrt(at2)
    
    # (Filter from RCEPS.M)

    #n = length(x)
    n = x.size
    
    xhat = np.real(sp.fftpack.ifft(np.log(x)))
    
    # Not sure if pfy.epsilon is required, but will guarantee 
    # that we get the expected result: One of n is odd, else zero.
    odd = np.fix( n%2 + pf_constants.epsilon )
    
    # wm = [1; 2 * ones((n+odd)/2-1,1 ) ; 1; zeros((n-odd)/2-1, 1)]
    aa = (n+odd)/2 - 1
    bb = (n-odd)/2 - 1
    wm = np.vstack( [1, 2*np.ones((aa,1)), 1, np.zeros((bb,1))] )
 
    yhat = np.zeros(np.size(x), dtype=np.complex)

    yhat[:] = np.real(np.transpose(wm) * xhat)
    
    gg = sp.fft(yhat)
    theta = np.imag(gg)
    
    y = x * np.exp(1j*theta)
    
    a = y 
    
    return (h,a,w)