# Python modules
from __future__ import division


# 3rd party modules



# Our modules
import functor



class FunctAmplitudeOffset(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.amplitude = 1.0
        self.dc_offset = 0.0

        self.attribs = ("amplitude","dc_offset")
        

    ##### Standard Methods and Properties #####################################

    
    def algorithm(self, chain):
        chain.data = chain.data * self.amplitude + self.dc_offset



      
 
