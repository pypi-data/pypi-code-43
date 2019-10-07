# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import functor



class FunctVoigtSaveYfit(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)


    ##### Standard Methods and Properties #####################################

    def algorithm(self, chain):
        yfit, _ = chain.fit_function(chain.fit_results, pderflg=False, nobase=True, indiv=True)
        
        chain.yfit = yfit
