# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.constants as constants
import vespa.analysis.src.block_fit_identity as block_fit_identity
import vespa.analysis.src.chain_quant_identity as chain_quant_identity

from vespa.analysis.src.constants import FitMacromoleculeMethod



class ChainQuantWatref(chain_quant_identity.ChainQuantIdentity):
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
        
        Note. Results from processing the last call to run() are maintained in
        this object until overwritten by a subsequent call to run() or 
        reset_results_arrays(). This allows the View to update itself from 
        these arrays without having to re-run the pipeline every time
        
        """
        # base class sets:  self.data, self._block, self._dataset 
        chain_quant_identity.ChainQuantIdentity.__init__(self, dataset, block)

        self.raw_dims             = self._dataset.raw_dims
        self.raw_dim0             = self._dataset.raw_dims[0]
        self.raw_hpp              = self._dataset.raw_hpp
        
        # Note. Not using functor call here since calculation is trivial 
        
        self.reset_results_arrays()


    def reset_results_arrays(self):
        """
        Results array reset is in its own method because it may need to be 
        called at other times than just in the object initialization.
        
        """
        block = self._block
        dims  = self._dataset.spectral_dims
        fit   = self._dataset.blocks['fit']
        
        nparam = fit.nparam 

        if block.watref_results is None:
            block.watref_results = np.zeros((nparam, dims[1], dims[2], dims[3]))      
        else:
            param_dims = list(dims)
            param_dims[0] = nparam

            # maintain results if no dimension has changed
            if block.watref_results.shape[::-1] != param_dims:
                block.watref_results = np.zeros((nparam, dims[1], dims[2], dims[3]))     


    def run(self, voxels, entry='all'):
        """
        Run is the workhorse method that is typically called every time a
        processing setting is changed in the parent (block) object. Run can
        process data for one or more data voxels at a time. 
        
        Use of 'entry points' into the processing pipeline is used to provide
        flexibility in how the Chain is used by the Block and the widget View.
        
        """
        block = self._block  
        set   = self._block.set
        fit   = self._dataset.blocks['fit']

        nmet = len(fit.set.prior_list)  
        
        # molar conc of pure water - 55.5 M/L   google
        # water in gm - 46.8 umol/g - my disseration ref 76
        # water in wm - 39.2 umol/g
        # from ISMRM fitting challenge  wat_mole_wt = 18.015  # g/mol - by definition
        #   can be converted to         wat_conc = 1000 / 18.015  = 55.5093 M (M/L actually, but volumes are the same)
        
        wat_conc = 55509.3  # mM = 55.5 M  
        
        if block.set.apply_metabolite_correction:
            met_relax_corr = np.exp(-1.0*set.sequence_te/set.metabolite_t2)
        else:
            met_relax_corr = 1.0

        avgs_corr = np.sqrt(set.water_averages) / np.sqrt(set.metabolite_averages)
        
        if block.set.apply_water_correction:
            wat_relax_corr  = (wat_conc*(set.tissue_content_gm /100.0) * set.water_content_gm  * np.exp(-set.sequence_te/set.water_t2_gm))
            wat_relax_corr += (wat_conc*(set.tissue_content_wm /100.0) * set.water_content_wm  * np.exp(-set.sequence_te/set.water_t2_wm))
            wat_relax_corr += (wat_conc*(set.tissue_content_csf/100.0) * set.water_content_csf * np.exp(-set.sequence_te/set.water_t2_csf))
        else:
            wat_relax_corr = 1.0 * wat_conc
            
        plot_results = {'met_relax_corr' : unicode(met_relax_corr), 
                        'wat_relax_corr' : unicode(wat_relax_corr/1000.0), 
                        'averages_corr'  : unicode(avgs_corr)  }
         
        # check results arrays for proper dimensionality
        block.check_parameter_dimensions(self._dataset)
        
        # get updated water area
        water_dataset = self._dataset.blocks['quant'].set.watref_dataset
        if water_dataset is None:
            return plot_results             
        
        water_fit_block = water_dataset.blocks['fit']
        if type(water_fit_block) is block_fit_identity.BlockFitIdentity:
            return plot_results
        
        water_areas = water_fit_block.get_fitted_water_area()
        if water_areas is None:
            return plot_results
        
        for voxel in voxels:

            water_area = water_areas[0,voxel[0],voxel[1],voxel[2]]
            results    = fit.fit_results[:,voxel[0],voxel[1],voxel[2]].copy()  # local variable

            # create calibration scale value
            scale = (1.0/water_area) * (wat_relax_corr/met_relax_corr) * avgs_corr
            results[0:nmet] = scale * results[0:nmet]

            # save data and parameter results into the Block results arrays
            block.watref_results[:,voxel[0],voxel[1],voxel[2]] = results
        
        # This dictionary is where we return data to the calling object. 
        # Typically, this is the Tab that contains this Block.Chain and it
        # will use this data to update the plot_panel_spectrum object in the
        # panel on the right side of the Tab.
        
        return plot_results
