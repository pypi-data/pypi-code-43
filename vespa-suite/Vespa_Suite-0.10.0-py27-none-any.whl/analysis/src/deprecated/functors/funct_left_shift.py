# Python modules
from __future__ import division


# 3rd party modules
import numpy as np

# Our modules
import functor



class FunctLeftShift(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.kiss_off_point_count = 0

        self.attribs = ("kiss_off_point_count",)


    ##### Standard Methods and Properties #####################################

    def algorithm(self, chain):
        if self.kiss_off_point_count:
            # this shifts the data by N points left in its array and then
            # zeros the N data points on the far right of the array
            
            chain.data = np.roll(chain.data, -self.kiss_off_point_count)
            chain.data[-self.kiss_off_point_count:] = chain.data[0]*0.0  
        

        


      
 
