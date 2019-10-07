# Python modules
from __future__ import division
import abc


class Chain(object):
    """This is the (abstract) base class for all chain objects. It can't 
    be instantiated, but all chains inherit from it and implement the interface
    defined below.
    """
    __metaclass__ = abc.ABCMeta


    @abc.abstractmethod
    def __init__(self, dataset, block):
        # Subclassers may want to override this
        self._dataset = dataset
        self._block   = block
        self.data     = []

        # Set local values for data acquisiton parameters.
        #  - these do not change over time, so we can set them here
        
        self.sw        = dataset.sw
        self.frequency = dataset.frequency
        self.resppm    = dataset.resppm
        self.midppm    = dataset.midppm
        self.echopeak  = dataset.echopeak
        self.is_fid    = dataset.is_fid
        self.seqte     = dataset.seqte
        self.nucleus   = dataset.nucleus
        

    def reset_results_arrays(self):
        # Subclassers may want to override this
        pass


    def run(self, voxel, entry='all', do_init=True):
        # Subclassers may want to override this
        pass


    def update(self):
        # Subclassers may want to override this
        pass
