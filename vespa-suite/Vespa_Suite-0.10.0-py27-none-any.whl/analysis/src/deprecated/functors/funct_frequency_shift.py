# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import functor


class FunctFrequencyShift(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)


    ##### Standard Methods and Properties #####################################
            
            
    def algorithm(self, chain):
        if chain.frequency_shift != 0.0:
            
            xx = np.arange(chain.raw_dim0) / chain.sw
            
            shift  = chain.frequency_shift
            phroll = np.exp(1j * 2.0 * np.pi * shift * xx)
            
            # had to put this seterr() pair here to avoid an underflow error 
            # which I have no idea why it is occurring ...
            old_err_state = np.seterr(all='ignore')
            
            # numpy broadcasting deals with (N,dim0) sized data arrays
            chain.data = chain.data * phroll
            
            np.seterr(**old_err_state)


      
 
