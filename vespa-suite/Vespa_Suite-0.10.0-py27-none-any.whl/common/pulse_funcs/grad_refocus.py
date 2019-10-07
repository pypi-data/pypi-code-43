# grad_refocus.py
from __future__ import division

# Python Modules.
import math

# 3rd party stuff
import numpy as np
import scipy as sp

# Local imports
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


# Routine (script) to refocus profile
# Translated from mrefocus.m

# Use ic as sqrt(-1)
ic = complex(0,1)

def interpolate(a, a0, a1, b0, b1):
    if not ((a0 <= a and a <= a1) or (a1 <= a and a <= a0)):
        error_message = 'Interpolation Failed. Target point is not between end points'
        raise pulse_func_exception.PulseFuncException(error_message, 1)
    # Approximate from the closer point  
    if abs(a-a0) < abs(a1-a):
        val = b0 + (a-a0)*(b1-b0)/(a1-a0)
    else:
        val = b1 - (a1-a)*(b1-b0)/(a1-a0)

    return val

def get_bandwidth(ax, profile):
    
    start = False
    middle = False
    end = False
    minimum = False
    restart = False
    x1 = 0
    x2 = 0
    for i in range(len(ax)):
        if abs(profile[i]) >= 0.5 and not start:
            x1 = ax[i]
            if i>0 and abs(profile[i]) != 0.5: # Then interpolate
                x1 = interpolate(.5, abs(profile[i-1]), abs(profile[i]), ax[i-1], ax[i])
            start = True
        if abs(profile[i]) > .8 and not middle:
            middle = True
        if middle and not end and abs(profile[i]) <= 0.5:
            x2 = ax[i]
            if i>0 and abs(profile[i]) != 0.5: # Then interpolate
                x2 = interpolate(.5, abs(profile[i-1]), abs(profile[i]), ax[i-1], ax[i])
            end = True
        if end and not minimum and abs(profile[i]) <= 0.25:
            minimum = True
        if minimum and not restart and abs(profile[i]) >= 0.5:
            error_message = 'Interpolation Failed. This appears to be a dual band pulse'
            raise pulse_func_exception.PulseFuncException(error_message, 1)
        
    if start and middle and end:
        return x2 - x1
    else:        
        return -1
        

def grad_refocus(mblax, mblprofil, mpgpulms):
    """
    For single band pulses: Calculates the optimal
    refocusing gradient as a fractional real number.
     
    mblax - The "x-axis" points of the profile - as an array (units of kHz)
    mblprofil - The "y-axis" points of the profile (units of fractional magnetization -1 to 1)
    mpgpulms - The pulse length in milliseconds.
    mpgbdwd - The pulse bandwidth in khz.
    """
    
    # Get the bandwidth from the profile
    mpgbdwd = get_bandwidth(mblax, mblprofil)
    if mpgbdwd < 0:
        error_message = 'Calculated bandwidth was less than zero'
        raise pulse_func_exception.PulseFuncException(error_message, 1)           
    
    # Get axis range over just bandwidth
    ax = mblax.copy()
    pro = mblprofil.copy()
    hbw = mpgbdwd/2.0
    
    
    found_ax1 = False 
    found_ax2 = False
    index = 0
    for ii in ax:
        if ii > -hbw and not found_ax1:
            # Want the first one, so if find one, don't reassign.
            ax1 = index
            found_ax1 = True
        if ii < hbw:
            # Keep reassigning, since want last one.
            ax2 = index
            found_ax2 = True
        index += 1
        
    found_ax11 = False 
    found_ax22 = False
    index = 0
    for ii in ax:
        if ii > -2*hbw and not found_ax11:
            # Want the first one, so if find one, don't reassign.
            ax11 = index
            found_ax11 = True
        if ii < 2*hbw:
            # Keep reassigning, since want last one.
            ax22 = index
            found_ax22 = True
        index += 1

            
    # If not (found_ax1 and found_ax2), throw an error.
    if not (found_ax1 and found_ax2 and found_ax11 and found_ax22):
        error_message = 'Unable to locate the bandwidth edges'
        raise pulse_func_exception.PulseFuncException(error_message, 1)        

    if (ax1 == ax2) or (ax11 == ax22):
        error_message = 'Invalid Bandwidth edges: They are the same point'
        raise pulse_func_exception.PulseFuncException(error_message, 1) 

    # figure
    # plot(real(pro(ax1:ax2)))
    
    # FIRST, ENSURE THAT REFOCUS AXIS IS Y
    # Find angle at zero frequency
    indx = int(ax1 + math.ceil((ax2-ax1)/2.0))
    rot = np.angle(pro[indx])
         
    pro = np.exp(-ic*rot)*pro 
    
    # INITIAL REFOCUS APPROXIMATION
    # Use fft to get no of cycles (fre)
    # First zero-pad the profile (rpro)
    rpro = pro[ax1:ax2+1] 
    
    nrpro = np.hstack( [ np.zeros(len(rpro)), rpro, np.zeros(len(rpro))] ) 
    
    fre0 = np.fft.fft(nrpro)
    length = len(fre0)
    fre =  np.append(fre0[int(math.ceil(length/2)):], fre0[:int(math.ceil(length/2))])
    
    # figure
    # plot(abs(fre))
    
    # maxfre = max(fre)
    # If two values in fre are the same in magnitude
    # matlab actually looks at the phase and finds the one
    # with the biggest phase, which we're not doing here.
    # However, since we are using the first value in the
    # array that matches maxfre, fre_pos = np.nonzero(...),
    # the phase thing is not and issue - according to Jerry.
    absfre = np.abs(fre)
    maxfre = np.max(absfre)
    
    #fre_pos = find(fre == maxfre)
    fre_pos = np.nonzero(absfre==maxfre)
    
    # Since fre_pos is an array of arrays,
    # (most likely with only one value), 
    # this pulls out the first value. 
    fre_pos = fre_pos[0][0]
    
    # The +1" is added at the end to purposely throw off 
    # the fit so that the iterations (below) give a good
    # curve for getting the maximum area.
    fre_n = (1.0/3.0)*(fre_pos - len(nrpro)/2 +1)    
        
    # Get rotation factor
    rotf = -fre_n/(mpgbdwd*mpgpulms)
    
    # Apply refocus to profile (pro)
    npro = np.exp(ic*2*math.pi*rotf*ax*mpgpulms)*pro
    
    # # Uncomment for figure
    # figure
    # plot(ax, real(npro),'b')
    # hold on
    # plot(ax, imag(npro),'g')
    
    # Get initial area under real component, over twice the bandwidth
    # Added the next line so the following one would make sense.
    aarea = np.zeros(1)
    aarea[0] = np.sum(np.real(npro[ax11-1:ax22]))
    
    # ITERATIVE FINE RE-PHASING ******************************
    # Now select just half the bandwidth
    lnhnax = int(math.floor(len(rpro)/4.0))
    hnpro = np.imag(npro[ax1+lnhnax-1:ax2-lnhnax]) 
    hnax = ax[ax1+lnhnax-1:ax2-lnhnax]
    
    p = np.polyfit(hnax,hnpro,1)
    
    # # Uncomment for figure
    # figure
    # plot(hnax, hnpro)
    
    # Slope of line is p[0], intercept is p[1]
    
    nrotf = np.zeros((40))
    barea = np.zeros((40))
        
    mtheta = math.atan(p[0])
    
    nrotf[0] = -mtheta/(2.0*math.pi)
    nnpro =  np.exp(ic*2.0*math.pi*nrotf[0]*ax*mpgpulms/8.0) * npro
    barea[0] = np.sum(np.real(nnpro[ax11-1:ax22]))
    
    niter = 1
    while abs(p[0]) > .001 and niter < 19:
        hnpro = np.imag(nnpro[ax1+lnhnax-1:ax2-lnhnax]) 
        p = np.polyfit(hnax,hnpro,1)
        mtheta = math.atan(p[0])
        nrotf[niter] = -mtheta/(2.0*math.pi)
        nnpro =  np.exp(ic*2.0*math.pi*nrotf[niter]*ax*mpgpulms/8.0)*nnpro
        barea[niter] = np.sum(np.real(nnpro[ax11-1:ax22]))
        niter = niter + 1
        
    # See if convergence failed.
    if niter >= 19:
        error_message = 'Convergence Failed'
        raise pulse_func_exception.PulseFuncException(error_message, 1)   
        
    # niter = niter-1 
    nrotf = nrotf[0:niter]
    refocus_value = (rotf + np.sum(nrotf)/8.0)

    # # Uncomment for figure
    # figure
    # plot(ax, real(nnpro),'b')
    # hold on
    # plot(ax, imag(nnpro),'g')
    # title('First effort at refocus')
    
    # Continue rotations to symetrize data
    nrotf = np.append(nrotf, nrotf[::-1] )
    
    for niter in range(niter,(2*niter)):
        nnpro =  np.exp(ic*2.0*math.pi*nrotf[niter]*ax*mpgpulms/8.0)*nnpro
        barea[niter] = np.sum(np.real(nnpro[ax11-1:ax22]))
    
    barea = np.append(aarea, barea[0:niter])
    carea =  1000.0/barea
    nrotf = nrotf[0:niter]
    frot = rotf + np.cumsum(nrotf/8)
    frot = np.append(rotf, frot)
    
    # # Uncomment for plot (rot vs inverse area)
    # figure
    # plot(frot,carea)
    
    
    # FINE TUNE FOR MAX AREA UNDER REAL PROFILE
    pa = np.polyfit(frot,carea,2)
    y = np.polyval(pa,frot)
    
    # # Uncomment to see plot
    # figure
    # plot(frot,y)
    
    # This is the value considering areas
    frotn = -pa[1]/(2.0*pa[0])    
    
    # # Uncomment for figure
    # figure
    # plot(ax, real(nnpro),'b')
    # hold on
    # plot(ax, imag(nnpro),'g')
    
    # If p[0] > .001, or p[1]>.001, or niter > 19, iterations failed?
    # :FIXME: Can frotn be greater than 1.0 ??? ask Jerry.
    
    if frotn < 0:
        error_message = 'Invalid Result: Fraction less than zero'
        raise pulse_func_exception.PulseFuncException(error_message, 1)           
    
    return frotn
