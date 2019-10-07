# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.constants as constants
import vespa.analysis.src.chain_spectral_identity as chain_spectral_identity

import vespa.common.util.ppm as util_ppm

import vespa.analysis.src.functors.funct_spectral_all       as funct_spectral_all
import vespa.analysis.src.functors.functor                  as functor




class ChainSpectral(chain_spectral_identity.ChainSpectralIdentity):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral  
    MRS data processing.
    
    """
    
    def __init__(self, dataset, block):
        """
        Due to the need to access settings and global parameter values, the
        base class keeps references to the parent (Block) and grandparent 
        (Dataset) objects.
        
        We create a dictionary of all possible functors, then we fill lists
        with subsets of these functors. That way we can process data starting
        at any point in the processing pipeline. Processing lists are referred
        to as 'entry points'.
        
        The functors in the processing lists all point at the same group of 
        functor object instances in the 'all_functors' dictionary, so 
        attributes set in one functor are set across all processing entry points. 
        
        Note. Results from processing the last call to run() are maintained in
        this object until overwritten by a subsequent call to run() or 
        reset_results_arrays(). This allows the View to update itself from 
        these arrays without having to re-run the pipeline every time
        
        """
        # base class sets:  self.data, self._block, self._dataset 
        chain_spectral_identity.ChainSpectralIdentity.__init__(self, dataset, block)

        self.raw_dims             = self._dataset.raw_dims
        self.raw_dim0             = self._dataset.raw_dims[0]
        self.raw_hpp              = self._dataset.raw_hpp
        
        # processing functions that can be used as entry points for chain
        self.functor_all = funct_spectral_all.do_processing_all

        self.reset_results_arrays()



    def reset_results_arrays(self):
        """
        Results array reset is in its own method because it may need to be 
        called at other times than just in the object initialization.
        
        """
        spectral_dim0 = self._dataset.spectral_dims[0]
        if len(self.data) != spectral_dim0:
            self.pre_roll        = np.zeros(self.raw_dim0, complex)
            self.kodata          = np.zeros(self.raw_dim0, complex)
            self.freq            = np.zeros(spectral_dim0, complex)
            self.data            = np.zeros(spectral_dim0, complex)

            self.time_fids       = np.zeros((20,self.raw_dim0), complex)
            self.sum_time_fids   = np.zeros(self.raw_dim0,      complex)

            self.svd_data              = np.zeros(spectral_dim0,      complex)
            self.svd_peaks_checked     = np.zeros((20,spectral_dim0), complex)
            self.svd_fids_all          = np.zeros((20,self.raw_dim0), complex)
            self.svd_peaks_checked_sum = np.zeros(spectral_dim0,      complex)
                        


    def run(self, voxels, entry='all'):
        """
        Run is the workhorse method that is typically called every time a
        processing setting is changed in the parent (block) object. Run can
        process data for one or more data voxels at a time. 
        
        Results from processing the last call to run() are maintained in
        this object until overwritten by a subsequent call to run(). This 
        allows the View to update itself from these arrays without having 
        to re-run the pipeline every time. Upon conclusion of a multi-voxel
        run, only the results for the last voxel are available in the chain 
        object
        
        Use of 'entry points' into the processing pipeline is used to provide
        flexibility in how the Chain is used by the Block and the widget View.
        
        """
        # copy 'global' parameters, that DO NOT change with voxel, from Dataset
        #  - these processing/data parameters have to be updated at run time 
        self.spectral_dims        = self._dataset.spectral_dims
        self.spectral_dim0        = self._dataset.spectral_dims[0]
        self.spectral_hpp         = self._dataset.spectral_hpp
        self.zero_fill_multiplier = self._dataset.zero_fill_multiplier
        self.phase_1_pivot        = self._dataset.phase_1_pivot
        
        for voxel in voxels:
            # local copy of input data
            self.data = self._dataset.get_source_data('spectral')
            self.data = self.data[voxel[2],voxel[1],voxel[0],:]
            self.data = self.data.copy()

            # copy 'global' parameters, that DO change with voxel, from Dataset
            self.frequency_shift = self._dataset.get_frequency_shift(voxel)
            self.phase0          = self._dataset.get_phase_0(voxel)
            self.phase1          = self._dataset.get_phase_1(voxel)
            
            # copy block parameters, that DO change with voxel, from Block
            svd_output = self._block.get_svd_output(voxel)

            self.ndp             = self._block.get_data_point_count(voxel)
            self.nssv            = self._block.get_signal_singular_value_count(voxel)
            self.do_fit          = self._block.get_do_fit(voxel)
            self.svd_output      = svd_output
            self.voxel           = voxel

            # select the chain processing functor based on the entry point
            if entry == 'all':
                self.functor_all(self)
            else:
                print 'oooops!'

            # save data and parameter results into the Block results arrays
            self._block.data[voxel[2],voxel[1],voxel[0],:] = self.freq.copy()
            self._block.set_svd_output(self.svd_output, voxel)
            self._block.set_do_fit(self.do_fit, voxel)  

        
        # This dictionary is where we return data to the calling object. 
        # Typically, this is the Tab that contains this Block.Chain and it
        # will use this data to update the plot_panel_spectrum object in the
        # panel on the right side of the Tab.
        
        plot_results = { 'svd_data'               : self.svd_data.copy(),
                         'svd_peaks_checked'      : self.svd_peaks_checked.copy(),
                         'svd_peaks_checked_sum'  : self.svd_peaks_checked_sum.copy(),
                         'svd_fids_checked_sum'   : self.svd_fids_checked.copy(),
                         'freq'                   : self.freq.copy()   }
                        
        return plot_results
