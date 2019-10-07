# Python modules
from __future__ import division
import math

# 3rd party modules
import numpy as np

# our modules
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


def max_min_setup(nlength, dwell, tip_angle, pass_ripple, reject_ripple, bandwidth, 
                  is_single_band, separation, bandwidth_convention):
    
    '''
    SETUP Script for RF pulse for max & min phase pulses
    
    May raise (or throw) PulseFuncException
    
    For detailed information on algorithms, see:
    K.J. Lee, 'General parameter relations for the Shinnar-Le Roux pulse design algorithm',
    J. Magnetic Resonance, 186, pp 272-258, 2007, 
    and:
    J. Pauly, P. Le Roux, D. Nishimura, A. Macovski, 
    'Parmater Relations for the Shinnar-Le Roux Selective Excitation Pulse Design Algorithm',
    IEEE Transactions on Medical Imaging, Vol. 10, No. 1, pp 53-65, March 1991.
    '''

    # Converted from Matpulse: MPLMB1C.M
    
    if not (pass_ripple > 0 and reject_ripple > 0):
        error_message = 'Error: passband and reject band ripple must both be greater than zero'
        raise pulse_func_exception.PulseFuncException(error_message, 1)    

    # Bandpass ripple (%) 
    sigm1 = pass_ripple/100.0 
    
    # Bandreject ripple (%)
    sigm2 = reject_ripple/100.0

    # Initialize corrctf for later correction if needed
    corrctf = 0

    # Set local variable names
    na = nlength  
    ang = tip_angle
        
    if is_single_band == True:
        bw = bandwidth
    else:
        bw = separation
        # Get narrowest band for dual band pulses 
        if bandwidth < separation:
            bw = bandwidth

    # pulse length (ms)
    ms = dwell*(na)/1000.0
        
    # Time-bandwidth product
    tb = ms*bw            
        
    # D(l), wts, and transb calculated

    is180 = False
    if abs(tip_angle - np.pi) < pf_constants.epsilon:            
        # 180 pulse
        sigm1 = sigm1/8.0 
        sigm2 = math.sqrt(sigm2/2.0)
        is180 = True
    elif abs(tip_angle - np.pi/2.0) < pf_constants.epsilon:            
        # 90 pulse
        sigm1 = sigm1/2.0 
        sigm2 = math.sqrt(sigm2)

    # add'l fudges (JM). 
    # Notes, from conversaton with JM on 04/19/11: Apparently this
    # fudge (and the 0.3 "fudge" 21 lines down) is here to reduce,
    # or zero out, the dc offset in the rejection band.
    # Per JM, these "fudges" should be calculate dynamically and 
    # not statically to have the best effect. 
    sigm1 = 2.0*sigm1 
    sigm2 = (sigm2**2.0)/2.0 

    # Re-adjust sigmas for dual band pulses
    if is_single_band == False:             
        # Dual band pulse
        sigm1 = 0.5*sigm1 
        sigm2 = 2.0*sigm2        

    # Calculate transition band (only approximate for dual band pulses)
    l1 = math.log10(sigm1) 
    l2 = math.log10(sigm2)
    a1 = 5.309e-3 
    a2 = 7.114e-2 
    a3 = -4.761e-1
    a4 = -2.66e-3 
    a5 = -5.941e-1 
    a6 = -4.278e-1

    # Note: 0.3 is fudge for min/max phase filters
    d = .3*( a1*pow(l1,2) + a2*l1 + a3 )*l2 + ( a4*pow(l1,2) + a5*l1 + a6 )

    wt1 = 1.0
    wt2 = sigm1/sigm2
    wid = d/tb 
    transb = float(wid)*bw 
    nq = na/(2.0*ms)
    magn = math.pow(math.sin(ang/2.0), 2.0) 
        
    if is180:         
        # SE pulse
        if (magn + sigm1) > 1.0:    
            # B1 pulse needs correction
            magn = 1.0-sigm1 
            corrctf = magn/(1.0-sigm1)


    if is_single_band == True:

        # Calculate the bands (fp and fs)
        if bandwidth_convention == 0:                     
            # Usual convention
            fp = (bandwidth/2.0 - transb/2.0)/nq  
            fs = (bandwidth/2.0 + transb/2.0)/nq
        elif bandwidth_convention == 1:                    
            # Minimum
            fp = (bandwidth/2.0 - transb)/nq 
            fs = (bandwidth/2.0)/nq
        elif bandwidth_convention == 2:                    
            # Maximum
            fp = (bandwidth/2.0)/nq  
            fs = (bandwidth/2.0 + transb)/nq

        fr = [0.0, fp, fs, 1.0]
        mag = [magn, magn, 0.0, 0.0]
        wts = [wt1, wt2]
        
    else:
        
        # Calculate the bands (fp and fs)
        if bandwidth_convention == 0:                     
            # Usual conven.
            fp = (separation/2.0 - transb/2.0)/nq  
            fs = (separation/2.0 + transb/2.0)/nq
        elif bandwidth_convention == 1:                    
            # Minimum
            fp = (separation/2.0 - transb)/nq 
            fs = (separation/2.0)/nq
        elif bandwidth_convention == 2:                    
            # Maximum
            fp = (separation/2.0)/nq  
            fs = (separation/2.0 + transb)/nq        
        
        if bandwidth_convention == 0:
            fss = fs + (bandwidth-transb)/nq  
            fpp = fss + (transb)/nq
        elif bandwidth_convention == 1:
            fss = fs + (separation/nq) 
            fpp = fss + (transb)/nq
        elif bandwidth_convention == 2: 
            fss = fp + (bandwidth-transb)/nq  
            fpp = fss + (transb)/nq

        fr = [0.0, fp, fs, fss, fpp, 1.0]
        mag = [0.0, 0.0, magn, magn, 0.0, 0.0]
        wts = [wt2, wt1, wt2]

    rval = (fr, mag, wts, corrctf)
    
    return rval
