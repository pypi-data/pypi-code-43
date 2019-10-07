# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.analysis.src.chain_base as chain_base


class ChainRaw(chain_base.Chain):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral  
    MRS data processing.
    
    """
    
    def __init__(self, dataset, block):
        """
        Basically, no processing takes place in this chain because
        all this tab does is reflect the data and headers for the
        data that was read it.
        
        It exists because each processing block has to have an 
        associated chain object.
        
        """

        chain_base.Chain.__init__(self, dataset, block)
