# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import functor



class FunctVoigtInitializeForFit(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    fitting chain for frequency domain spectral MRS data.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)        


    ##### Standard Methods and Properties #####################################

    def algorithm(self, chain):
        chain.fit_results = chain.initial_values.copy()

