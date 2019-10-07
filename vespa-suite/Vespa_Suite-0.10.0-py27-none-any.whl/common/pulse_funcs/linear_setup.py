# Python modules
from __future__ import division
import math

# 3rd party modules
import numpy as np

# our modules
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


def linear_setup(nlength, dwell, tip_angle, pass_ripple, reject_ripple, bandwidth, 
                 is_single_band, separation, bandwidth_convention):

    '''
    Setup script for linear (or refocused) rf pulses. 
    
    May raise (or throw) PulseFuncException
    
    For detailed information on algorithms, see:
    K.J. Lee, 'General parameter relations for the Shinnar-Le Roux pulse design algorithm',
    J. Magnetic Resonance, 186, pp 272-258, 2007, 
    and:
    J. Pauly, P. Le Roux, D. Nishimura, A. Macovski, 
    'Parmater Relations for the Shinnar-Le Roux Selective Excitation Pulse Design Algorithm',
    IEEE Transactions on Medical Imaging, Vol. 10, No. 1, pp 53-65, March 1991.
    '''
                
    # Adapted from Matlab: MPLRB1C.M

    if not (pass_ripple > 0 and reject_ripple > 0):
        error_message = 'Error: passband and reject band ripple must both be greater than zero'
        raise pulse_func_exception.PulseFuncException(error_message, 1)

    # Set desired pass_ripple (bandpass) and reject_ripple (bandreject); 
    sigm1=pass_ripple/100 
    sigm2=reject_ripple/100

    # Initialize corrctf for later correction if needed
    corrctf = 0

    # Set local variable names
    na = nlength
    ang = tip_angle

    if is_single_band == True:
        bw = bandwidth        
    else:           
        # Dual band pulse
        # Get narrowest band.
        bw = separation
        if bandwidth < separation: 
            bw = bandwidth
        
    # pulse length (ms)
    ms = dwell*(na)/1000      
       
    # Time-bandwidth product
    tb = ms*bw
        
    # D(l), wts, and transb calculated using Lee
    sigi = sigm1
    sigo = sigm2
    phi = ang

    is180 = False
    # See if angle is either 180 or 90.
    if abs(tip_angle - np.pi) < pf_constants.epsilon:                 
        # SE pulse
        sigm1 = (1/(2*sigi))*(4*(1-sigi/2) - 4*math.sqrt(1-sigi))
        sigm2 = (1+sigm1)*math.sqrt(sigo) 
        is180 = True
        
    elif abs(tip_angle - np.pi/2.0) < pf_constants.epsilon:             
        # 90 pulse
        n = 0
        f = 0.1
        
        # sigm1 calc
        while abs(f) > .00001 and n < 100:
            sigin = abs( (2*math.sqrt(1 - math.pow((1+sigm1),2) * math.pow(math.sin(phi/2),2)) \
                                         *(1+sigm1)*math.sin(phi/2)-math.sin(phi))/math.sin(phi) )
            f = (sigi-sigin)/(2*sigi)
            sigm1 = abs(sigm1*(1 + f))
            n = n+1
        
        # sigm2 calc
        n = 0
        f = 0.1
        while abs(f) > .00001 and n < 100:
            sigin = abs(2*math.sqrt(1 - math.pow(sigm2,2) * math.pow(math.sin(phi/2),2))\
                                                           *sigm2*math.sin(phi/2)/math.sin(phi))
            f = (sigo-sigin)/(2*sigo)
            sigm2 = abs(sigm2*(1 + f))
            n = n+1

    # Re-adjust sigmas for dual band pulses
    if is_single_band == False:             
        sigm1 = 0.5*sigm1
        sigm2 = 2*sigm2

    # Calculate transition band (only approximate for dual band pulses)
    l1 = math.log10(sigm1)
    l2 = math.log10(sigm2)
    a1 = 5.309e-3
    a2 = 7.114e-2
    a3 = -4.761e-1
    a4 = -2.66e-3
    a5 = -5.941e-1
    a6 = -4.278e-1

    d = (a1 * pow(l1,2) + a2*l1 + a3)*l2 + (a4 * pow(l1,2) + a5*l1 + a6)

    wt1 = 1
    wt2 = sigm1/sigm2
    wid = d/tb
    transb = wid*bw
    nq = na/(2*ms)
    magn = math.sin(ang/2)
        
    # SE pulse        
    if is180:        
        if (magn + sigm1) > 1:    
            # B1 pulse needs correction
            magn = 1-sigm1
            corrctf = magn/(1-sigm1)
        

    # Calculate the bands (fp and fs)
    if is_single_band == True:
        if bandwidth_convention == 0:             
            # Usual convention (FWHM)
            fp = (bandwidth/2 - transb/2)/nq
            fs = (bandwidth/2 + transb/2)/nq
        elif bandwidth_convention == 1:            
            # Minimum
            fp = (bandwidth/2 - transb)/nq
            fs = (bandwidth/2) / nq
        elif bandwidth_convention == 2:            
            # Maximum
            fp = (bandwidth/2) / nq
            fs = (bandwidth/2 + transb)/nq

        fr = [0, fp, fs, 1]
        mag = [magn, magn, 0, 0]
        wts = [wt1, wt2]
        
    else:         
        
        # Dual band pulse
        if bandwidth_convention == 0:
            fp = (separation/2 - transb/2)/nq
            fs = (separation/2 + transb/2)/nq
        elif bandwidth_convention == 1:
            fp = (separation/2 - transb)/nq
            fs = (separation/2) / nq
        elif bandwidth_convention == 2:
            fp = (separation/2) / nq
            fs = (separation/2 + transb)/nq        
                
        if bandwidth_convention == 0 :
            fss = fs+(bandwidth-transb)/nq
            fpp = fss+(transb)/nq
        elif bandwidth_convention == 1:
            fss = fs+(separation/nq)
            fpp = fss+(transb)/nq
        elif bandwidth_convention == 2:
            fss = fp+(bandwidth-transb)/nq
            fpp = fss+(transb)/nq

        fr = [0, fp, fs, fss, fpp, 1]
        mag = [0, 0, magn, magn, 0, 0]
        wts = [wt2, wt1, wt2]
    
    
    rval = (fr, mag, wts, corrctf)
    
    return rval
