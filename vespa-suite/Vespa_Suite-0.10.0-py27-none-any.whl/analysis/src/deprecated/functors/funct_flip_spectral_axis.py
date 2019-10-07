# Python modules
from __future__ import division


# 3rd party modules
import numpy as np

# Our modules
import functor



class FunctFlipSpectralAxis(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.flip = False

        self.attribs = ("flip",)


    ##### Standard Methods and Properties #####################################

    def algorithm(self, chain):
        if self.flip:
            
            if len(chain.data.shape)>1:
                for i in range(chain.data.shape[0]):
                    chain.data[i,:] = chain.data[i,::-1].copy()
            else:
                chain.data = chain.data[::-1].copy()
            
            
            #chain.data = np.conj(chain.data)

