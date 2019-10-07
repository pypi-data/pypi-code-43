# Python modules
from __future__ import division
import math

# 3rd party modules
import numpy as np
import scipy.integrate as integrate
import scipy.stats.distributions as distributions


# Our Modules
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.util.math_ as util_math

# Converted from Matpulse code (2011.02.27)
# from: function [g, y, z] = mllcalcf(mllparam)

def scale_pulse(b1, dwell_time, angle, pulse_type):  

    # Scale b1 to requested angle.
    # multiplier = 1000*(angle*math.pi/180) / (2*math.pi)        
    multiplier = 1000*(angle/360.0)
    if pulse_type == pf_constants.AnalyticType.HYPERBOLIC_SECANT:
        sfact = np.sum(np.abs(b1))
    else:
        sfact = np.sum(b1)
    nfact = multiplier/(pf_constants.GAMMA1H * dwell_time * sfact) 
    return nfact*b1 


def filter_pulse(b1, xvals, filter_type, filter_percent):
    
    length = len(b1)
    if length%2 == 0:
        even_flag = 1  
    else:
        even_flag = 0     
    
    # seq to ~ pi/2 **    
    maxx = np.amax(xvals)
    f = (xvals*math.pi/maxx/2.0)*(filter_percent/100.0)

    # Cosine apodization
    if filter_type == pf_constants.ApodizationFilterType.COSINE:   
        g = np.cos(f) 
    # Hamming apodization
    elif filter_type == pf_constants.ApodizationFilterType.HAMMING:              
        g = 0.5*(1 - np.cos(math.pi+2*f)) 
    else:
        g = np.ones(len(f))

    if even_flag == 1:
        g = np.hstack([g[::-1], g]) 
    else:     
        h = g.copy() 
        h = np.delete(h,0)
        g = np.hstack([h[::-1], g]) 

    z = g*b1
    
    return z 


# Calculate pulses

# These next three routines use the "analytic_pulse" function to calculate result.

def hyperbolic_secant(nop, cycles, filter_type, filter_percent, angle, n, mu, dwell_time):
    pulse_type = pf_constants.AnalyticType.HYPERBOLIC_SECANT   
    return analytic_pulse(pulse_type,nop,cycles,filter_type,filter_percent,angle,n,mu,dwell_time)

def sinc_gaussian(nop, cycles, filter_type, filter_percent, angle):
    pulse_type = pf_constants.AnalyticType.SINC_GAUSSIAN
    return analytic_pulse(pulse_type,nop,cycles,filter_type,filter_percent,angle)

def gaussian(nop, cycles, filter_type, filter_percent, angle):
    pulse_type = pf_constants.AnalyticType.GAUSSIAN
    return analytic_pulse(pulse_type,nop,cycles,filter_type,filter_percent,angle)

def analytic_pulse(pulse_type, nop, cycles, filter_type, filter_percent, \
                                        angle, n=1, mu=1, dwell_time=100):
    '''
    Used for the creation of waveforms with 
    Hyperbolic-Secant, Sinc-Gaussian, and
    Gaussian pulse profile types.
    
    pulse_type - SINC_GAUSSIAN, GAUSSIAN, HYPERBOLIC_SECANT
    nop - Number of points
    cycles - Number of cycles before truncating pulse.
    filter_Type - ApodizationFilterType: HAMMING or COSINE
    filter_percent - How much to apply the filter (0.0 to 100.0)
    angle - Total rotation angle in degrees (used for hyperbolic-secant).
    n - Power of hyperbolic secant function.
    mu - Parameter that defines sharpness of function.
    dwell_time - The dwell time in microseconds.
    ''' 
    
    # Set local values
    
    g = np.ones(nop)
    y = g.copy()
    z = g.copy()
    
    # Determine whether nop even or odd (even = 1 or 0)
    if nop%2 == 0:
        even_flag = 1  
    else:
        even_flag = 0 
    
    # Generate symmetric sequence
    # starts at 0 for odd, at +1/2 for even
    if even_flag == 1:          
        # even_flag, starts at 1/2
        # matlab code; x = (1:nop/2) - 1/2
        x = np.arange(nop/2) + 1/2
    else:
        # odd, starts at 0
        # matlab code; x = (1:(nop+1)/2) -1
        x = np.arange((nop+1)/2)

    # Calculate shape
    if pulse_type == pf_constants.AnalyticType.SINC_GAUSSIAN:
        # Sinc pulse
        y = np.sinc(x*cycles*math.pi/(2*nop)) 
        
    elif pulse_type == pf_constants.AnalyticType.GAUSSIAN:
        # Gaussian pulse
        # 2.8 = magic number ?

        # the call to exp() tends to underflow with larger durations
        y = util_math.safe_exp(-(x*cycles*2.8/nop)**2, 0)
        
    # pulse_type == pf_constants.AnalyticType.HYPERBOLIC_SECANT
    else: 
    
        # HS pulse
        # sech(beta*t), where tmax = 1; so beta = cycles/2
        if n == 1:
             y = pow( math.pi*distributions.hypsecant.pdf(x*cycles/nop), complex(1, mu) ) 
        else:
            sqrtn = math.sqrt(n)
            s = (cycles/(sqrtn*nop))*x
            y = math.pi*distributions.hypsecant.pdf(s**n) 
        
            # wfunct = @(s) np.sech(s.^n).^2
            wfunct = lambda q: math.pi*distributions.hypsecant.pdf(q**n)**2
            
            w = np.zeros(len(s))
               
            for k in range(len(s)): 
                integral = integrate.quad(wfunct, 0, s[k])
                w[k] = integral[0]
                w[k] *= -mu*2.0*math.pi
                 
            dphi = s[1]*w
             
            #phi = cumsum(dphi) 
            phi = dphi.cumsum(axis=0)
            
            y = y * np.exp(complex(0,1)*phi)

    
    # Note that beta, when n = 1, is cycles/2;
    # Gives width = mu*beta/pi = cycles*mu/pi
    
    if even_flag == 1:
        y = np.hstack([y[::-1], y]) 
    else:
        z = y.copy() 
        z = np.delete(z,0)
        y = np.hstack([z[::-1], y])
        
    # Check for apodization (Filter funct = g)
    # Then use apodization
    if not filter_type:
        z = y        
    else:
        z = filter_pulse(y, x, filter_type, filter_percent)

    z = scale_pulse(z, dwell_time, angle, pulse_type)    

    return z


def gaussian2(nop, dwell_time, bandwidth, filter_type, filter_percent, angle):
    
    dwell = dwell_time*.000001
    
    # Determine whether nop even or odd (even = 1 or 0)
    if nop%2 == 0:
        is_even = True
        points = nop//2 
    else:
        is_even = False
        points = nop//2 + 1
             
    width = 1000.0*bandwidth
    a = math.pi*width
    a = a*a/(4*math.log(2))

    xvals = np.zeros(points)
    
    if is_even:
        for i in range(points):
            xvals[i] = (i+.5)*dwell
    else:
        for i in range(points):
            xvals[i] = i*dwell 
    
    twos = 2*np.ones(points)

    # the call to exp() tends to underflow with larger durations
    y = util_math.safe_exp(-a*np.power((xvals), twos), 0)
    
    # Make a "whole" pulse from half...
    if is_even:
        yw = np.hstack([y[::-1], y]) 
    else:
        z = y.copy() 
        z = np.delete(z,0)
        yw = np.hstack([z[::-1], y])
    
    yf = filter_pulse(yw, xvals, filter_type, filter_percent)    
        
    pulse_type = pf_constants.AnalyticType.GAUSSIAN
    ys = scale_pulse(yf, dwell_time, angle, pulse_type)  
    
    # Convert real array to complex array.
    yret = np.zeros(len(ys), dtype=np.complex)
    for ii in range(len(ys)):
        yret[ii] = ys[ii]
        
    return yret


def gaussian3(npts, dwell_time, bandwidth, filter_type, filter_percent, angle):
    '''
    Bandwidth is set up in Hz, but we need to calc in time domain so we convert
    to time. Note that Gaussian is typically described by a standard deviation
    variable, sigma, rather than full width at half height. So we have to 
    ensure that our 'sigma^2' or 'gb' value, is solved for time at which we are
    at half height. 
    
    y = exp(-(t^2)/(2 * sigma^2))

    solving for t in this equation for t = T(1/2 height) we get a sqrt(ln(2))
    constant, which is the 0.83255461 constant below
    '''
    dwell = dwell_time*0.000001
    sw    = 1.0 // dwell
    gb    = 1.0 / (1.92 * bandwidth * 1000.0)   # 1.92
    # this used to be a factor of 2.0, but empirically 1.92 works better
    # to get a full width half max bandwidth of 1kHz for a 90 degree 
    # pulse of 8ms duration and 250 points. This is due to the interaction
    # of a Gaussian pulse with the Bloch equation for something other than
    # a small (1-20 degrees) tip angle. For small tip angles the Fourier 
    # Transform approximation is pretty good for FWHM estimation. As we go
    # to larger tip angles, we have to be more empirical about getting the 
    # actual bandwith we want. Which is why we plot the Freq Profile for
    # the user to look at and measure.
    
    # Determine whether npts even or odd (even = 1 or 0)
    if npts%2 == 0:
        is_even = True
        xvals = (np.arange(npts//2)+0.5) * dwell 
    else:
        is_even = False
        xvals = np.arange(npts//2 + 1) * dwell
    
    gb = (0.83255461 / gb)
    # the call to exp() tends to underflow with larger durations
    y = util_math.safe_exp(-((gb * xvals)**2 ), 0)

    # Make a "whole" pulse from half...
    if is_even:
        yw = np.hstack([y[::-1], y]) 
    else:
        z = y.copy() 
        z = np.delete(z,0)
        yw = np.hstack([z[::-1], y])
    
    yf = filter_pulse(yw, xvals, filter_type, filter_percent)    
        
    pulse_type = pf_constants.AnalyticType.GAUSSIAN
    ys = scale_pulse(yf, dwell_time, angle, pulse_type)  
    
    # Convert real array to complex array.
    yret = ys + 1j * np.zeros(len(ys))
        
    return yret


def randomized(time_points):
    """Given the number of points expected in the array, returns a complex
    array of microTesla values with each real/imag value randomized in the 
    interval (-1, 1).
    """
    rand = np.random.rand
    
    y = (2 * rand(time_points) - 1) + (2j * rand(time_points) - 1j)
    
    # We want values in microtesla
    return y / complex(1000, 1000)
