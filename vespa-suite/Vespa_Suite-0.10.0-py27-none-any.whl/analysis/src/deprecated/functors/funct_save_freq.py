# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import functor



class FunctSaveFreq(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)


    ##### Standard Methods and Properties #####################################
    
    def algorithm(self, chain):
        chain.freq = chain.data.copy()
