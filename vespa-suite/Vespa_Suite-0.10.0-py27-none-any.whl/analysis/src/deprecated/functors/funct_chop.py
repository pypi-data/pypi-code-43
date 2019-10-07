# Python modules
from __future__ import division


# 3rd party modules
import numpy as np

# Our modules
import functor



class FunctChop(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.chop = False

        self.attribs = ("chop",)


    ##### Standard Methods and Properties #####################################
            
    
    def algorithm(self, chain):
        """ 
        Alternates points between positive and negative
        That is, even points are multiplied by 1
        and odd points are multiplied by -1
        """
        if self.chop:
            chop_array = ((((np.arange(chain.raw_dim0) + 1) % 2) * 2) - 1)

            # numpy broadcasting deals with (N,dim0) sized data arrays
            chain.data = chain.data * chop_array
        


      
 
