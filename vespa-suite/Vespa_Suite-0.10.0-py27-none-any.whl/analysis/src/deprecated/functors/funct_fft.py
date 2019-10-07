# Python modules
from __future__ import division


# 3rd party modules
import numpy as np


# Our modules
import functor


class FunctFft(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.zero_fill_multiplier = 1
        self.fft = True

        self.attribs = ("fft",
                        "zero_fill_multiplier")


    ##### Standard Methods and Properties #####################################
            
    
    def algorithm(self, chain):

        # need to half the value of first point of FID data to get proper area
        if chain.is_fid:
            if len(chain.data.shape) > 1:
                chain.data[:,0] *= 0.5
            else:
                chain.data[0] *= 0.5

        # calculate if zerofilling is required
        dim0 = chain.raw_dim0 * self.zero_fill_multiplier

        # apply FFT if needed    
        if self.fft:
            chain.data = np.fft.fft(chain.data, n=dim0) / float(dim0)
        else:
            if self.zero_fill_multiplier > 1:
                temp = np.zeros(dim0, 'complex')
                temp[0:chain.raw_dim0] = chain.data
                chain.data = temp

