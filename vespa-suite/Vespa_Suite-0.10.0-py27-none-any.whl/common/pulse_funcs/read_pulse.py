# read_pulse.py

# Python Modules.
from __future__ import division
import math
import cmath

# 3rd party stuff
import numpy as np

# Our modules
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.constants as constants

def _crect(r, phi):
    # The useful function rect() wasn't added to the cmath module until
    # Python 2.6. We use it when it exists. Python 2.5 users get the 
    # simplified implementation (which doesn't handle inf correctly).
    if hasattr(cmath, "rect"):
        return cmath.rect(r, phi)
    else:
        return r * (math.cos(phi) + math.sin(phi)*1j)

    
def read_pulse(file_path, use_max=True, max_intensity=1.0,
               scale_factor = 1.0,
               format=constants.ImportFileFormat.AMPLITUDE_PHASE_DEGREES,
               is_phase_degrees=True):
    
    """ 
    file_path - complete path of file to read, as a string.
    use_max - Boolean to determine if you want to rescale 
              to the Maximum Intensity or choose the alternative
              which is to multiply the whole pulse by a Scale Factor.
    max_intensity - the maximum intensity to which to scale the 
                    pulse at its absolute peak, as a float
    scale_factor  - multiplicative factor used for scaling
                    the whole pulse.
    format - the import format type, one of the constants from 
             vespa.common.constants.ImportFileFormat.
    
    Return a numpy array containing the pulse field intensity
    as a function of time. 
    """
    
    # We only do Amplitude-Phase-degrees format for now
    if format != constants.ImportFileFormat.AMPLITUDE_PHASE_DEGREES: 
        errstr = "Not familiar with this file format (%d)" % format
        raise pulse_func_exception.PulseFuncException(errstr, -1)        
    
    try:
        f = open(file_path)        
    except IOError, ioe:
        errstr = "File I/O Error: %s" % ioe.message
        raise pulse_func_exception.PulseFuncException(errstr, -1)          

    rf_y = []

    for ll, line in enumerate(f.readlines()):
        line = line.strip()

        # Ignore blank lines and comments
        if (not len(line)) or line.startswith('#') or line.startswith(';'):
            continue
            
        # Split any/all whitespace; also strip that whitespace from the 
        # substrings
        substrings = line.split()

        # validate that this data line has a valid format.
        if len(substrings) != 2:
            errstr = "Only two arguments per line allowed, found %d: Error on line %d" %(len(substrings), ll)
            raise pulse_func_exception.PulseFuncException(errstr, -1)

        amplitude, phase = substrings
        
        try:
            amplitude = float(amplitude)
        except ValueError, tpe:
            errstr = "Could not convert %s into a float, on line %d" %(amplitude, ll)
            raise pulse_func_exception.PulseFuncException(errstr, -1)
        
        try:
            phase = float(phase)
        except ValueError, tpe:
            errstr = "Could not convert %s into a float, on line %d" %(phase, ll)
            raise pulse_func_exception.PulseFuncException(errstr, -1)            
        
        ph_radians = phase
        if is_phase_degrees == True:
            # Convert phase to radians.
            ph_radians = phase * constants.DEGREES_TO_RADIANS
        c = _crect(amplitude, ph_radians)
        rf_y.append(c)
        
    rf_y = np.array(rf_y)
    
    if len(rf_y) < 2:
        errstr = "Pulse file has less than 2 points"
        raise pulse_func_exception.PulseFuncException(errstr, -1)             
        
    if use_max:
        max_ = np.max(np.abs(rf_y))
        # Scale pulse to user specified maximum intensity.
        # The 1000 in the denominator is used because we internally
        # represent these pulses in milliTesla (but display as microTesla).
        rf_y = rf_y * max_intensity / (max_*1000)
    else:
        rf_y = rf_y * scale_factor      
    
    return rf_y
