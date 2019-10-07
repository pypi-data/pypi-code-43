# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.constants as constants
import vespa.analysis.src.chain_spectral_identity as chain_spectral_identity

import vespa.analysis.src.functors.funct_left_shift         as funct_left_shift
import vespa.analysis.src.functors.funct_apodize            as funct_apodize
import vespa.analysis.src.functors.funct_chop               as funct_chop
import vespa.analysis.src.functors.funct_fft                as funct_fft
import vespa.analysis.src.functors.funct_flip_spectral_axis as funct_flip_spectral_axis
import vespa.analysis.src.functors.funct_svd_filter         as funct_svd_filter
import vespa.analysis.src.functors.funct_frequency_shift    as funct_frequency_shift
import vespa.analysis.src.functors.funct_amplitude_offset   as funct_amplitude_offset
import vespa.analysis.src.functors.funct_save_kodata        as funct_save_kodata
import vespa.analysis.src.functors.funct_save_pre_roll      as funct_save_pre_roll
import vespa.analysis.src.functors.funct_save_freq          as funct_save_freq
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
        chain_spectral_identity.ChainSpectralIdentity.__init__(self, dataset, block)
        self.raw_dims             = self._dataset.raw_dims
        self.raw_dim0             = self._dataset.raw_dims[0]
        self.raw_hpp              = self._dataset.raw_hpp

        # these will be the functor lists used in the actual chain processing
        self.functor_list_all       = []
        
        # these are all available functors for building the chain
        self.functors = {'ecc_filter'        : self._block.set.ecc_handler,
                         'save_pre_roll'     : funct_save_pre_roll.FunctSavePreRoll(),
                         'svd_filter'        : funct_svd_filter.FunctSvdFilter(),
                         'left_shift'        : funct_left_shift.FunctLeftShift(),
                         'frequency_shift'   : funct_frequency_shift.FunctFrequencyShift(),
                         'water_filter'      : self._block.set.water_handler,
                         'apodize'           : funct_apodize.FunctApodize(),
                         'save_kodata'       : funct_save_kodata.FunctSaveKoData(),
                         'chop'              : funct_chop.FunctChop(),
                         'fft'               : funct_fft.FunctFft(),
                         'flip_spectral_axis': funct_flip_spectral_axis.FunctFlipSpectralAxis(),
                         'amplitude_offset'  : funct_amplitude_offset.FunctAmplitudeOffset(),
                         'save_freq'         : funct_save_freq.FunctSaveFreq(),
                        }

        for funct in self.functors.values():
            if isinstance(funct, functor.Functor):
                funct.update(self._block.set)

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
                        

    def update(self):
        """
        Each processing list of functors is recreated in here from the main
        dictionary of all functor objects.
         
        Then the processing settings in each functor is updated from the 
        values currently set in the parent (self._block.set) object
        
        """
        self.functor_list_all = []

        #------------------------------------------------------------
        # setup All Functors chain

        self.functor_list_all.append(self.functors['ecc_filter'])
        self.functor_list_all.append(self.functors['save_pre_roll'])
        self.functor_list_all.append(self.functors['svd_filter'])
        self.functor_list_all.append(self.functors['water_filter'])
        self.functor_list_all.append(self.functors['left_shift'])
        self.functor_list_all.append(self.functors['frequency_shift'])
        self.functor_list_all.append(self.functors['apodize'])
        self.functor_list_all.append(self.functors['save_kodata'])
        self.functor_list_all.append(self.functors['chop'])
        self.functor_list_all.append(self.functors['fft'])
        self.functor_list_all.append(self.functors['flip_spectral_axis'])
        self.functor_list_all.append(self.functors['amplitude_offset'])
        self.functor_list_all.append(self.functors['save_freq'])

        for funct in self.functor_list_all:
            funct.update(self._block.set)


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
        # update processing parameter values that DO NOT change with voxel
        self.update() 

        # select the functor chain list based on the entry point
        if entry == 'all':
            functors = self.functor_list_all
        
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

            # loop through functor.algorithms() in functor list
            for funct in functors:
                funct.algorithm(self)

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
                         'freq'                   : self.freq.copy()   }
                        
        return plot_results
