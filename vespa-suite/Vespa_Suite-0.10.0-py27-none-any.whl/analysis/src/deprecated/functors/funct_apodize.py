# Python modules
from __future__ import division


# 3rd party modules
import numpy as np


# Our modules
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import constants
import functor
import vespa.common.util.generic_spectral as util_generic_spectral


class FunctApodize(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.apodization = constants.Apodization.NONE
        self.apodization_width = 0.0

        self.attribs = ("apodization","apodization_width")
        

    ##### Standard Methods and Properties #####################################
    
    
    def algorithm(self, chain):
        if self.apodization:
            if self.apodization == constants.Apodization.GAUSSIAN:
                type_ = 'Gaussian'
            else:
                type_ = 'Lorentzian'

            xx = np.arange(chain.raw_dim0) / chain.sw

            lineshape = util_generic_spectral.apodize(xx, 
                                                      self.apodization_width, 
                                                      type_)

            # had to put this seterr() pair here to avoid an underflow error 
            # which I have no idea why it is occurring ...
            old_settings = np.seterr(all='ignore')
            
            # numpy broadcasting deals with (N,dim0) sized data arrays
            chain.data = chain.data * lineshape
            
            np.seterr(**old_settings)

