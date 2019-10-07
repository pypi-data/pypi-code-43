# Python modules
from __future__ import division

# 3rd party modules
import numpy as np
from scipy.interpolate import interp1d

# Our modules
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception

# Matpulse did a symmetrized interpolation, i.e.: 
# b1_a = np.interp(b1, npoints)          
# b1_b = np.interp(np.fliplr(b1), npoints)     
# Symmetrized
# b1_interpolated = (1/2)*(b1_a + np.fliplr(b1_b))
# If this makes any difference, we could add in a 
# new interpolation routine and make it an option.    


def interpolate_factor(yvals, xvals, ifactor):
    """
    Takes a user-supplied factor and creates
    a new series of x-value points, with spacing
    equal to the current spacing divided by
    the interpolation factor. 
    
    Current spacing is calculated using this formula:
    x[1] - x[0]
    
    Then performs a 2 sided linear interpolation 
    (appropriate for interpolating historgram-like graphs).
    
    May raise PulseFuncException.  
    """
    
    length = len(xvals)
    if length < 2:
        error_msg =  "Cannot calculate dwell_time with less than two points"
        raise pulse_func_exception.PulseFuncException(error_msg, 1)
    
    if not (ifactor > 0):
        error_msg =  "ifactor must be greater than zero"
        raise pulse_func_exception.PulseFuncException(error_msg, 1)    
    
    if not (xvals[1] > xvals[0]):
        error_msg =  "xvals[1] must be greater than xvals[0]"
        raise pulse_func_exception.PulseFuncException(error_msg, 1)
    
    new_dwell = (xvals[1] - xvals[0]) / ifactor
    
    return interpolate_dwell(yvals, xvals, new_dwell)



def _fliplr1d(y_in):
    yvals_flip = []
    i = len(y_in)
    while i > 0:
        yvals_flip.append(y_in[i-1])
        i -= 1
    return np.array(yvals_flip)



def interpolate_dwell(yvals, xvals, new_dwell):
    """
    This interpolation routine does a two sided 
    interpolation, first using the values from one
    side of the dwell_time range, and then the other,
    and averaging the two. 
    
    This type of interpolation is appropriate for a 
    histogram type graph.
    
    Attempts to cover the current duration.
    Assumes xvals are equally spaced.
    
    May raise PulseFuncException.
    """
    
    length = len(xvals)
    if length < 2:
        error_msg =  "Cannot do a meaningful linear interpolation with less than two points"
        raise pulse_func_exception.PulseFuncException(error_msg, 1)
    
    if not (new_dwell > 0):
        error_msg =  "new dwell time must be greater than zero"
        raise pulse_func_exception.PulseFuncException(error_msg, 1)       
    
    if not (xvals[1] > xvals[0]):
        error_msg =  "xvals[1] must be greater than xvals[0]"
        raise pulse_func_exception.PulseFuncException(error_msg, 1)    
    
    old_dwell = (xvals[1] - xvals[0])
    duration = xvals[length-1] + old_dwell
    
    time_step = xvals[0]+new_dwell
    # make sure at least 2 points.
    x = [xvals[0], time_step]
    while time_step + new_dwell < duration - pf_constants.small_epsilon:
       time_step += new_dwell
       x.append(time_step)  
        
    new_length = len(x)
    
    x = np.array(x)
    
    # Filling will be done at the very end of our waveform.
    # If we add more points we will have to fill - and it makes
    # the most sense to fill at the end with the value at the end.
    izzy1 = interp1d(xvals, yvals, kind='linear',
                    bounds_error=False, fill_value=yvals[length-1])
    
    # Tried to do this using np.fliplr
    # but received this error:
    # raise ValueError, "Input must be >= 2-d."

    yvals_flipped = _fliplr1d(yvals)
    
    izzy2 = interp1d(xvals, yvals_flipped, kind='linear',
                    bounds_error=False, fill_value=yvals_flipped[length-1])
    
    y1 = izzy1(x)
    y2 = izzy2(x)
    
    y = (y1 + _fliplr1d(y2))/2
    
    return y, x
