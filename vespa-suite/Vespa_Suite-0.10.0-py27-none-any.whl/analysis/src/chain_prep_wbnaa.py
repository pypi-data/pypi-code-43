# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.constants as constants
import vespa.analysis.src.chain_prep_identity as chain_prep_identity

import vespa.analysis.src.functors.funct_fidsum_wbnaa as funct_fidsum_wbnaa
import vespa.analysis.src.functors.functor as functor




class ChainPrepWbnaa(chain_prep_identity.ChainPrepIdentity):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain MRS data processing to combine
    multiple FID data sets into a single averaged FID data set.
    
    """
    
    def __init__(self, dataset, block):
        """
        Basically, no processing takes place in this chain because
        all this tab does is reflect the data and headers for the
        data that was read it.
        
        It exists because each processing block has to have an 
        associated chain object.
        
        """
        # base class sets:  self.data, self._block, self._dataset
        chain_prep_identity.ChainPrepIdentity.__init__(self, dataset, block)

        # processing functions that can be used as entry points for chain
        self.functor_all = funct_fidsum_wbnaa.do_processing_all
        
        # these are results for display in the Tab
        self.freq_summed  = None
        self.freq_current = None

        self.reset_results_arrays()
        
 
    def reset_results_arrays(self):
        """
        Results array reset is in its own method because it may need to be 
        called at other times that just in the object initialization.
        
        Note. we refresh the self.raw_xxx attributes here because we get these
        values from a property in the BlockPrepXxxx block. And this is always
        called right after the block._reset_dimensional_data() method. This is
        only the case here in the "prep" block, because it is a special case
        where this block provides the 'raw_xxx' values, so this is as early in
        the class as we can put them without running into circular references. 
        
        """
        raw_dim0 = self._dataset.raw_dims[0]
        
        if len(self.data) != raw_dim0:
            self.freq_current   = np.zeros(raw_dim0, complex)


 
    def run(self, voxels, entry='all', do_calculate=False):
        """
        Run is the workhorse method that is typically called every time a
        processing setting is changed in the parent (block) object. Run only
        processes data for a single voxel of data at a time.
        
        Results from processing the last call to run() are maintained in
        this object until overwritten by a subsequent call to run(). This 
        allows the View to update itself from these arrays without having 
        to re-run the pipeline every time. 
        
        Use of 'entry points' into the processing pipeline is used to provide
        flexibility in how the Chain is used by the Block and the widget View.
        
        """
        self.calculate_flag = do_calculate
        

        # Note. in this case we are processing all raw data into the data 
        #   attribute, so despite having multiple raw FIDs, we are really 
        #   only processing one voxel, so no for loop


        # local reference to input data
        self.raw = self._dataset.get_source_data('prep')

        # Choose voxel - for saving result for current single voxel plot
        self.voxel = voxels[0]

        # select the chain processing functor based on the entry point
        if entry == 'all':
            self.functor_all(self)
        else:
            print 'oooops!'

        # save data and parameter results into the Block results arrays
        self._block.data[0,0,0,:] = self.time_summed_offset.copy()
 
        # This dictionary is where we return data to the calling object. 
        # Typically, this is the Tab that contains this Block.Chain and it
        # will use this data to update the plot_panel_spectrum object in the
        # panel on the right side of the Tab.

        plot_results = { 'freq_current'       : self.freq_current.copy(),
                         'freq_summed'        : self.freq_summed.copy(),
                         'freq_summed_offset' : self.freq_summed_offset.copy()      }
                        
        return plot_results