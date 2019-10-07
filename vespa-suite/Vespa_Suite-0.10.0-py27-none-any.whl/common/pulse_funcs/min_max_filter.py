# Python modules
from __future__ import division
import math

# 3rd party modules
import numpy as np
import scipy as sp
import scipy.signal as sps

# Our modules
import vespa.common.pulse_funcs.fir_least_squares as fir_least_squares


def max_min_filter(frz, magz, wtz, na, use_remez, mmgresol, is_single_band):
    '''
    Function to create the (min/max phase) digital filter
    
    Parameters [fp fs], mag, [wt1, wt2], and na from pulse setup.
    Returns h (b-polynomial), a (a-polynomial), and w (freq)
    
    May raise (or throw) PulseFuncException    
    
    For more information see:
    J. Pauly, P. Le Roux, D. Nishimura, A. Macovski, 
    'Parameter Relations for the Shinnar-Le Roux Selective 
    Excitation Pulse Design Algorithm',
    IEEE Transactions on Medical Imaging, 
    Vol. 10, No. 1, pp 53-65, March 1991.
    '''
    
    # Based on Matpulse code, MPLFILTM.M
    
    fr = np.array(frz)
    mag = np.array(magz)
    wts = np.array(wtz)         
    
    # A pre-calculation will be done first...
    # This pre-calculation is to determine the
    # dc offset and then correct for it in the real,
    # full length calculation, so the reject band
    # is closer to zero. 
    
    # 2011.04.06 
    # Jerry believes he got this idea from Pauly and
    # his collaborators in a private conversation.
    
    nb = 2*na-1
    
    # First determine bias on shorter length pulse   
    frnn = 0 
    nn = na

    # determine pulse length
    while frnn < 0.6:        
        if is_single_band == True:     
            # Single band
            frnn = fr[2]*nb/nn
        else:    
            # Dual band
            frnn = fr[3]*nb/nn
        nn = nn/2

    # Suggested initial pulse length
    nn = 4*nn-1        

    # Don't let nn be too small
    nn = int(math.ceil(nn))
    if nn < 63:
        nn = 63

    if is_single_band == True:

        #frn = [fr(1) fr(2)*nb/nn fr(3)*nb/nn fr(4)];
        nbdnn = float(nb)/nn
        frn = np.hstack([ fr[0], fr[1]*nbdnn, fr[2]*nbdnn, fr[3] ])
        
        #fs = frn(3) ;
        fs = frn[2] 

        # check that fs less than 0.82
        if fs > 0.82:
            error_message = 'Error: Try a larger number of steps'
            raise pulse_func_exception.PulseFuncException(error_message, 1)


        # Check for filter function wanted
        if use_remez == True:        
            # b-poly coefficients
            bp = sps.remez(nn, frn, mag[::2], wts, 2)
        else:            
            # Group f values into pairs.
            fx = frn/2.0
            i = 0
            fin = []
            for fi in fx:
                if i%2 == 0:
                    fi_0 = fi
                else:
                    fin.append( (fi_0, fi) )
                i += 1
                    
            # Also, Take every other value out of m
            min = mag[0::2]            
            
            #bp = firls(nn-1,frn,mag,wts)
            bp = fir_least_squares.firls(nn, fin, min, wts)

        # evaluated on unit/2 circle
        wp,hp = sps.freqz(bp, 1, mmgresol)
        
        local_resol = len(wp)
        
        selct = int(np.ceil( 1.2*fs*local_resol ) )

        # partt = [zeros(1,selct) ones(1,mmgresol-selct)]' ;
        # The conjugation method (') does not seem to be needed here since 
        # the arrays are all reals, and the subsequent array multiplication 
        # works without any problem.
        partt = np.hstack( [np.zeros((1, selct)), np.ones((1, local_resol-selct))] )

        bias = 0.93 * np.max(np.ravel((np.abs(hp))*partt))

        # Set bias for calc
        magn = mag + np.hstack([0.0, 0.0, bias, bias])

    else:     
        
        # Dual band pulse

        # frn = [0 fr(2)*nb/nn fr(3)*nb/nn fr(4)*nb/nn 1.1*fr(4)*nb/nn 1] ;
        nbdnn = float(nb)/nn
        frn = np.hstack( [0.0, fr[1]*nbdnn, fr[2]*nbdnn, fr[3]*nbdnn, 1.1*fr[3]*nbdnn, 1.0] )

        fs = frn[4] 

        # check that fs is less than 0.82
        if fs > 0.82:
            error_message = 'Error: Try a larger number of steps'
            raise pulse_func_exception.PulseFuncException(error_message, 1)

        # Check for filter function wanted
        if use_remez == True:
            # b-poly coefficients
            bp = sps.remez(nn, frn, mag[::2], wts, 2)
        else:
            # Group f values into pairs.
            fx = frn/2.0
            i = 0
            fin = []
            for fi in fx:
                if i%2 == 0:
                    fi_0 = fi
                else:
                    fin.append( (fi_0, fi) )
                i += 1
                    
            # Also, Take every other value out of m
            min = mag[0::2]                   
            
            #bp = firls(nn-1,frn,mag,wts)
            bp = fir_least_squares.firls(nn, fin, min, wts)

        # evaluated on unit/2 circle
        wp,hp = sps.freqz(bp, 1, mmgresol)
        
        local_resol = len(wp)
        
        fs = frn[1]
        
        selct = int( math.ceil(0.8 * fs * local_resol)  )
        
        partt = np.hstack([np.ones( (1,selct) ), np.zeros( (1, local_resol-selct) )])
        
        # Changed from .9 to .02 (7/15/05) (JM)
        bias = 0.02 * np.max(np.ravel(np.abs(hp) * partt))

        # Set bias for calc
        magn = mag + np.hstack([bias, bias, 0.0, 0.0, 4*bias, 4*bias])


    # Next the B(z) (h,w) (evaluated on the unit circle)

    # Check for filter function wanted
    #
    # FIXME: The calls to remez (and firls below) are using
    # nb, and not na. Why? nb = 2*na-1 so if na=16, nb=31    
    if use_remez == True:
        b = sps.remez(nb, fr, magn[::2], wts, 2)
    else:
        # Group f values into pairs.
        fx = fr/2.0
        i = 0
        fin = []
        for fi in fx:
            if i%2 == 0:
                fi_0 = fi
            else:
                fin.append( (fi_0, fi) )
            i += 1
                
        # Also, Take every other value out of m
        min = magn[0::2]    
    
        #b = firls(nb-1,fr,magn,wts)
        b = fir_least_squares.firls(nb, fin, min, wts)

    whole = 1
    wr, hr = sps.freqz(b, 1, mmgresol, whole)

    w = wr.copy()
    hr = np.lib.scimath.sqrt(np.abs(hr))
    x = np.abs(hr)
    n = x.size
    xhat = np.real(sp.fftpack.ifft(np.log(x))) 
    
    #odd = fix(rem(n,2))
    odd = int(np.fix( n % 2 ))    
    
    # wm = [1; 2*ones((n+odd)/2-1,1) ; 1; zeros((n-odd)/2-1,1)];
    aa = (n+odd)/2 - 1
    bb = (n-odd)/2 - 1
    wm = np.vstack([1.0, 2*np.ones((aa,1)), 1.0, np.zeros((bb,1))])
    
    yhat = np.zeros(x.size) 

    wmxf = wm.transpose() * xhat    

    yhat[:] = np.real(wmxf)

    theta = np.imag(sp.fft(yhat))
    
    y = x * (np.exp(1j*theta))
    
    h = y.copy()

    
    # Next the A(z)

    at2 = (1 - (np.real(h)**2 + np.imag(h)**2) )
    
    x = np.sqrt(at2)

    # (Filter from RCEPS.M)

    n = x.size
    
    xhat = np.real(sp.fftpack.ifft(np.log(x)))
    
    #odd = fix(rem(n,2))
    odd = int(np.fix(n % 2))
    
    # wm = [1; 2*ones((n+odd)/2-1,1) ; 1; zeros((n-odd)/2-1,1)];
    aa = (n+odd)/2 - 1
    bb = (n-odd)/2 - 1
    wm = np.vstack([1, 2*np.ones((aa,1)), 1, np.zeros((bb,1))])
    
    yhat = np.zeros( x.size, dtype=np.complex)

    yhat[:] = np.real(wm.transpose() * xhat)
    
    theta = np.imag(sp.fft(yhat))
    
    y = x * np.exp(1j*theta)
    
    a = y.copy()
    
    return (h,a,w)

