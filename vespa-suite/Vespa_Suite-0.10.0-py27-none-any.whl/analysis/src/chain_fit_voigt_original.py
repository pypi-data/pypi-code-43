# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.analysis.src.constants as constants
import vespa.analysis.src.chain_fit_identity as chain_fit_identity

import vespa.common.util.ppm                      as util_ppm
import vespa.common.util.math_                    as util_math
import vespa.common.util.generic_spectral         as util_spectral
import vespa.analysis.src.functors.funct_voigt_save_yfit             as funct_voigt_save_yfit
import vespa.analysis.src.functors.funct_voigt_save_yini             as funct_voigt_save_yini
import vespa.analysis.src.functors.funct_voigt_b0_correction         as funct_voigt_b0_correction
import vespa.analysis.src.functors.funct_voigt_initial_filter_phase0 as funct_voigt_initial_filter_phase0
import vespa.analysis.src.functors.funct_voigt_initial_filter_phase1 as funct_voigt_initial_filter_phase1
import vespa.analysis.src.functors.funct_voigt_initialize_for_fit    as funct_voigt_initialize_for_fit
import vespa.analysis.src.functors.funct_voigt_update_iteration      as funct_voigt_update_iteration
import vespa.analysis.src.functors.funct_voigt_global_filtering      as funct_voigt_global_filtering
import vespa.analysis.src.functors.funct_voigt_baseline_model        as funct_voigt_baseline_model
import vespa.analysis.src.functors.funct_voigt_optimize_model        as funct_voigt_optimize_model
import vespa.analysis.src.functors.funct_voigt_confidence_intervals  as funct_voigt_confidence_intervals
import vespa.analysis.src.functors.funct_voigt_cramer_rao_bounds     as funct_voigt_cramer_rao_bounds
import vespa.analysis.src.functors.funct_initial_values              as funct_initial_values
import vespa.analysis.src.functors.functor                           as functor

from vespa.common.constants import DEGREES_TO_RADIANS as DTOR
from vespa.analysis.src.constants              import FitLineshapeModel
from vespa.analysis.src.constants              import VoigtDefaultFixedT2
from vespa.analysis.src.constants              import FitMacromoleculeMethod


class ChainFitVoigt(chain_fit_identity.ChainFitIdentity):
    """ 
    This is a building block object that can be used to create a  
    processing chain for frequency domain spectral MRS data fitting.
    
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
        chain_fit_identity.ChainFitIdentity.__init__(self, dataset, block)
        self.raw_dims             = self._dataset.raw_dims
        self.raw_dim0             = self._dataset.raw_dims[0]
        self.raw_hpp              = self._dataset.raw_hpp
        self.sw                   = self._dataset.sw
        
        self.fit_function   = self.lorgauss_internal

        # these will be the functor lists used in the actual chain processing t
        self.functors_initial      = []
        self.functors_full_fit     = []
        self.functors_plot_refresh = []
        
        # these are all available functors for building the chain
        self.all_functors = { 'save_yfit'             : funct_voigt_save_yfit.FunctVoigtSaveYfit(),
                              'save_yini'             : funct_voigt_save_yini.FunctVoigtSaveYini(),
                              'b0_correction'         : funct_voigt_b0_correction.FunctVoigtB0Correction(),
                              'initial_values'        : funct_initial_values.FunctInitialValues(),
                              'initialize_for_fit'    : funct_voigt_initialize_for_fit.FunctVoigtInitializeForFit(),
                              'update_iteration'      : funct_voigt_update_iteration.FunctVoigtUpdateIteration(),
                              'baseline_model'        : funct_voigt_baseline_model.FunctVoigtBaselineModel(),
                              'optimize_model'        : funct_voigt_optimize_model.FunctVoigtOptimizeModel(),
                              'confidence_intervals'  : funct_voigt_confidence_intervals.FunctVoigtConfidenceIntervals(),
                              'cramer_rao_bounds'     : funct_voigt_cramer_rao_bounds.FunctVoigtCramerRaoBounds()
                             }

        for funct in self.all_functors.values():
            if isinstance(funct, functor.Functor):
                funct.update(self._block.set)

        self.reset_results_arrays()


    def reset_results_arrays(self):
        """
        Results array reset is in its own method because it may need to be 
        called at other times that just in the object initialization.
        
        """
        nmet   = len(self._block.set.prior_list)
        nparam = nmet*2+4
        nmmol  = 0
        if self._block.set.macromol_model == FitMacromoleculeMethod.SINGLE_BASIS_DATASET:
            nmmol = 2 
        spectral_dim0 = self._dataset.spectral_dims[0]

        if len(self.data) != spectral_dim0:
            self.data           = np.zeros(spectral_dim0, complex)
            self.yini           = np.zeros((nmet+nmmol, spectral_dim0), complex)
            self.yfit           = np.zeros((nmet+nmmol, spectral_dim0), complex)
            self.base           = np.zeros(spectral_dim0, complex)
            self.initial_values = np.zeros(nparam+nmmol, float)
            self.fit_results    = np.zeros(nparam+nmmol, float)
            self.fit_baseline   = np.zeros(spectral_dim0, complex)
            self.weight_array   = np.zeros(spectral_dim0, complex)      
            self.limits         = np.zeros((2,nparam+nmmol), float)   
            self.fitted_lw      = 0.0   
        
                        

    def update(self):
        """
        Each processing list of functors is recreated in here from the main
        dictionary of all functor objects.
         
        Then the processing settings in each functor is updated from the 
        values currently set in the parent (self._block.set) object
        
        """
        self.functors_initial      = []
        self.functors_full_fit     = []
        self.titles_initial        = []
        self.titles_full           = []
        self.functors_plot_refresh = []
    
        #------------------------------------------------------------
        # setup Initial Value Only chain

        self.functors_initial.append(self.all_functors['b0_correction'])
        self.functors_initial.append(self.all_functors['initial_values'])
        self.functors_initial.append(self.all_functors['save_yini'])
        self.titles_initial.append('b0_correction')
        self.titles_initial.append('initial_values')
        self.titles_initial.append('save_yini')

        for funct in self.functors_initial:
            funct.update(self._block.set)
        
        #------------------------------------------------------------
        # setup Full Fit chain

        self.functors_full_fit.append(self.all_functors['b0_correction'])
        self.functors_full_fit.append(self.all_functors['initial_values'])
        self.functors_full_fit.append(self.all_functors['initialize_for_fit'])
        self.titles_full.append('b0_correction')
        self.titles_full.append('initial_values')
        self.titles_full.append('initialize_for_fit')
                                    
        for i in range(self._block.set.optimize_global_iterations):
            self.functors_full_fit.append(self.all_functors['update_iteration'])
            self.functors_full_fit.append(self.all_functors['baseline_model'])
            self.functors_full_fit.append(self.all_functors['optimize_model'])
            self.titles_full.append('update_iteration')
            self.titles_full.append('baseline_model')
            self.titles_full.append('optimize_model')

        if self._block.set.confidence_intervals_flag:
            self.functors_full_fit.append(self.all_functors['confidence_intervals'])
            self.titles_full.append('confidence_intervals')
        if self._block.set.cramer_rao_flag:
            self.functors_full_fit.append(self.all_functors['cramer_rao_bounds'])
            self.titles_full.append('cramer_rao_bounds')

        self.functors_full_fit.append(self.all_functors['save_yini'])
        self.functors_full_fit.append(self.all_functors['save_yfit'])
        self.titles_full.append('save_yini')
        self.titles_full.append('save_yfit')

        for funct in self.functors_full_fit:
            funct.update(self._block.set)

        #------------------------------------------------------------
        # setup Refresh Plots chain

        self.functors_plot_refresh.append(self.all_functors['b0_correction'])
        self.functors_plot_refresh.append(self.all_functors['initial_values'])
        self.functors_plot_refresh.append(self.all_functors['save_yini'])
        self.functors_plot_refresh.append(self.all_functors['save_yfit'])

        for funct in self.functors_plot_refresh:
            funct.update(self._block.set)

  

    def run(self, voxels, entry='initial_only', statusbar=None):
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
        # update processing parameter values that DO NOT change with voxel
        
        self.update() 

        # select the functor chain list based on the entry point

        if entry == 'initial_only':
            functors = self.functors_initial
            titles   = self.titles_initial

        elif entry == 'full_fit' or entry == 'all':
            functors = self.functors_full_fit
            titles   = self.titles_full            

        elif entry == 'plot_refresh':
            functors = self.functors_plot_refresh
            titles   = None        
        

        # copy 'global' parameters, that DO NOT change with voxel, from Dataset
        #  - these processing/data parameters have to be updated at run time 
        
        self.spectral_dims           = self._dataset.spectral_dims
        self.spectral_dim0           = self._dataset.spectral_dims[0]
        self.spectral_hpp            = self._dataset.spectral_hpp
        self.zero_fill_multiplier    = self._dataset.zero_fill_multiplier
        self.phase_1_pivot           = self._dataset.phase_1_pivot
        self.phase_1_pivot           = util_ppm.ppm2pts(self.phase_1_pivot, self)
        self.user_prior              = self._dataset.user_prior
        self.metinfo                 = self._dataset.user_prior.metinfo
        
        self.user_prior_spectrum     = self._dataset.user_prior_summed_spectrum
        self.auto_b0_range_start     = self._dataset.user_prior.auto_b0_range_start
        self.auto_b0_range_end       = self._dataset.user_prior.auto_b0_range_end
        self.auto_phase0_range_start = self._dataset.user_prior.auto_phase0_range_start
        self.auto_phase0_range_end   = self._dataset.user_prior.auto_phase0_range_end
        self.auto_phase1_range_start = self._dataset.user_prior.auto_phase1_range_start
        self.auto_phase1_range_end   = self._dataset.user_prior.auto_phase1_range_end
        self.auto_phase1_pivot       = self._dataset.user_prior.auto_phase1_pivot

        # copy block parameters, that DO NOT change with voxel, from Block
        block = self._block  
        prior = self._block.set.prior
        
        self.prior_list = block.set.prior_list
        nmet = len(block.set.prior_list)
        if nmet < 1: 
            self.yini = self.yini * 0
            voxel = voxels[0]
            self.data = self._dataset.get_source_data('fit')
            self.data = self.data[voxel[2],voxel[1],voxel[0],:]
            
            plot_results = { 'fitted_lw'    : 3.0,
                             'minmaxlw'     : [1,5],
                             'init_b0'      : 0.0,
                             'init_ph0'     : -self._dataset.get_phase_0(voxel) * np.pi/180.0,
                             'init_ph1'     : -self._dataset.get_phase_1(voxel),
                             'data'         : self.data.copy(),
                             'weight_array' : self.data.copy() * 0,
                             'fit_baseline' : self.data.copy() * 0,
                             'yfit'         : self.data.copy() * 0,
                             'yini'         : self.data.copy() * 0,
                             'init_baseline': self.data.copy() * 0      }
            
            return plot_results

        nparam = nmet*2+4
        nmmol  = 0
        if block.set.macromol_model == FitMacromoleculeMethod.SINGLE_BASIS_DATASET:
            nmmol = 2 
            
        self.nmet        = nmet
        self.nmmol       = nmmol
        self.nparam      = nparam
        self.init_b0     = 0.0
        self.init_lw_hz  = 3.0
        self.init_ta     = 0.8
        self.init_tb     = 0.03
        self.init_ampl   = None
        self.init_area   = None

        # need this to refresh widget after initial value call
        self.initial_linewidth_value = block.set.initial_linewidth_value

        self.prior_peak_ppm = np.array(block.set.prior_peak_ppm)
        self.fit_baseline   = 0.0  # needed for LORGAUSS call


        # retrieve FIDs for selected metabolite names, also get all ppm values
        # for each metabolite to use to create weight array
        basis_mets = []
        ppms       = []
        for name in block.set.prior_list:
            basis_set_item = prior.basis_set[name]
            basis_mets.append(basis_set_item.fid.copy())
            ppms += basis_set_item.all_ppms
        self.peakpts    = util_ppm.ppm2pts(np.array(ppms), self)   
        self.basis_mets = np.array(basis_mets)

        self.weight_array    = np.zeros(self.spectral_dims[0], complex)      
        self.limits          = np.zeros((2,self.nparam+self.nmmol), float)      
        self.fit_function    = self.lorgauss_internal
        self.minmaxlw        = [0,0]
        self.lineshape_model = self._block.set.lineshape_model
        self.prior_fix_t2    = self._block.set.prior_fix_t2
        self.fix_t2_center   = VoigtDefaultFixedT2.CENTER
        
        self.macromol_model = block.set.macromol_model
        self.basis_mmol = None
        if block.set.macromol_model == FitMacromoleculeMethod.SINGLE_BASIS_DATASET:
            if block.set.macromol_single_basis_dataset:
                tmp = block.set.macromol_single_basis_dataset.blocks['raw']
                self.basis_mmol = tmp.data.copy()
                
        block.check_parameter_dimensions(self) # check results arrays for proper dimensionality
        

        for voxel in voxels:
            # local copy of input data
            self.data = self._dataset.get_source_data('fit')
            self.data = self.data[voxel[2],voxel[1],voxel[0],:]
            self.data = self.data.copy()

            # FIXME - bjs, if we ever batch all processing this is a fail point
            self.chain = self._dataset.get_source_chain('fit')
            self.kodata = self.chain.kodata.copy()


            # copy 'global' parameters, that DO change with voxel, from Dataset
            self.phase0               = self._dataset.get_phase_0(voxel)
            self.phase1               = self._dataset.get_phase_1(voxel)
            self.init_ph0             = self._dataset.get_phase_0(voxel)
            self.init_ph1             = self._dataset.get_phase_1(voxel)

            # copy block parameters, that DO change with voxel, from Block
            self.frequency_shift      = self._dataset.get_frequency_shift(voxel)
            self.fit_baseline         = block.fit_baseline[:,voxel[0],voxel[1],voxel[2]].copy()
            self.init_baseline        = self.fit_baseline.copy() * 0


            # setup chain results arrays 
            tmp1 = voigt_checkout(nmet, block.initial_values[:,voxel[0],voxel[1],voxel[2]], self)
            tmp2 = voigt_checkout(nmet, block.fit_results[   :,voxel[0],voxel[1],voxel[2]], self)
            self.initial_values = tmp1
            self.fit_results    = tmp2
            self.fit_stats      = block.fit_stats[ :,voxel[0],voxel[1],voxel[2]].copy()
            self.cramer_rao     = block.cramer_rao[:,voxel[0],voxel[1],voxel[2]].copy()
            self.confidence     = block.confidence[:,voxel[0],voxel[1],voxel[2]].copy()
        
            self.iteration = 0  # global index used in functors as a trigger

            # loop through functor.algorithms() in functor list
            for i,funct in enumerate(functors):
                if titles and statusbar:
                    statusbar.SetStatusText(' Functor = %s (%d/%d)' % (titles[i],i+1,len(functors)), 0)
                funct.algorithm(self)

            if statusbar:
                statusbar.SetStatusText(' Fitting Done', 0)

            # one last lw calc to refresh HTLM window on opening VIFF file
            self.fitted_lw, _ = util_spectral.voigt_width(self.fit_results[nmet*2], self.fit_results[nmet*2+1], self)

            # save data and parameter results into the Block results arrays
            block.set.initial_linewidth_value = self.initial_linewidth_value 

            block.initial_values[:,voxel[0],voxel[1],voxel[2]] = voigt_checkin(nmet, self.initial_values, self)
            block.fit_results[   :,voxel[0],voxel[1],voxel[2]] = voigt_checkin(nmet, self.fit_results, self)
            block.fit_stats[     :,voxel[0],voxel[1],voxel[2]] = self.fit_stats.copy()
            block.fit_baseline[  :,voxel[0],voxel[1],voxel[2]] = self.fit_baseline.copy()
            block.cramer_rao[    :,voxel[0],voxel[1],voxel[2]] = self.cramer_rao.copy()
            block.confidence[    :,voxel[0],voxel[1],voxel[2]] = self.confidence.copy()


        # This dictionary is where we return data to the calling object. 
        # Typically, this is the Tab that contains this Block.Chain and it
        # will use this data to update the plot_panel_spectrum object in the
        # panel on the right side of the Tab.
        
        plot_results = { 'fitted_lw'    : self.fitted_lw,
                         'minmaxlw'     : self.minmaxlw,
                         'init_b0'      : self.init_b0,
                         'init_ph0'     : self.init_ph0,
                         'init_ph1'     : self.init_ph1,
                         'data'         : self.data.copy(),
                         'weight_array' : self.weight_array.copy(),
                         'fit_baseline' : self.fit_baseline.copy(),
                         'yfit'         : self.yfit.copy(),
                         'yini'         : self.yini.copy(),
                         'init_baseline': self.init_baseline.copy()      }
                        
        return plot_results



    def lorgauss_internal(self, a, pderflg=True, 
                                   nobase=False, 
                                   indiv=False,   
                                   finalwflg=False):
        """
        =========
        Arguments 
        =========
        **a:**         [list][float] parameters for model function
        **dataset:**   [object][dataset (or subset)] object containing fitting 
                         parameters
        **pderflg:**   [keyword][bool][default=False] xxxx
        **nobase:**    [keyword][bool][default=False] flag, do not include 
                        baseline contribs from (*dood).basarr
        **indiv:**     [keyword][bool][default=False] flag, return individual 
                         metabolites, not summed total of all
        **finalwflg:** [keyword][float][default=False] xxxx
          
        =========== 
        Description
        ===========   
        Returns the parameterized metabolite model function.
    
        A contains : [[am],[fr],Ta,Tb,ph0,ph1]  - LorGauss complex
    
        Peak ampls and freqs are taken from the DB info in info,
        so the values in [am] and [fr] are relative multipliers
        and additives respectively.  That is why there is only
        one value for each compound in each array
    
        If the relfreq flag is ON, then [fr] is a single value that
        is added to each peak freq equivalently.  Ie. the whole
        spectrum can shift, but relative ppm separations between
        all metabolites are maintained exactly.  If the flag is OFF,
        then metabs may shift independently from one another,
        however, within groups of peaks belonging to the same
        metabolite, relative ppm separtaions are maintained.
    
        am    - peak amplitude
        fr    - peak frequency offsets in PPM
        Ta    - T2 decay constant in sec
        Tb    - T2 star decay const in sec
        ph0/1 - zero/first order phase in degrees
    
        coef  - are the spline coefs for the lineshape, knot locations are in info
    
        ======    
        Syntax
        ====== 
        ::
        
          f = self.lorgauss_internal(a, pderflg = False, 
                                        nobase  = False, 
                                        indiv   = False, 
                                        finalwflg = False)
        """    
        # Setup constants and flags
        
        nmet    = self.nmet
        npts    = self.raw_dims[0]
        zfmult  = self.zero_fill_multiplier
        nptszf  = round(npts * zfmult)
        sw      = 1.0*self.sw
        td      = 1.0/sw
        piv     = util_ppm.ppm2pts(self.phase_1_pivot, self, acq=True)
        t2fix   = self.prior_fix_t2
        
        arr1    = np.zeros(npts,float) + 1.0
        f       = np.zeros((nmet,nptszf),complex)  
        mf      = np.zeros((nptszf,),complex)
        
        t = (np.arange(nmet * npts) % npts) * td
        t.shape = nmet, npts
        mt = np.arange(npts) * td
    
        # get prior max peak ppm vals for metabs which are flagged ON
        peaks   = self.prior_peak_ppm
            
#         # setup Lineshape 
#         expo     = t/a[nmet*2] + (t/a[nmet*2+1])**2
#         lshape   = util_math.safe_exp(-expo)

        # setup Lineshape 
        if self.lineshape_model != FitLineshapeModel.GAUSS:
            # voigt and lorentzian models
            expo     = t/a[nmet*2] + (t/a[nmet*2+1])**2
            lshape   = util_math.safe_exp(-expo)
        else:
            # Note. in the case of the Gaussian lineshape, we now allow the user to 
            # set a fixed T2 value for each metabolite. In the model call (fitt_funct.pro)
            # we now create a lineshape array that takes each fixed value into account.
            # BUT! we are still passing in a Tb parameter here, and though that parameter
            # will be tightly constrained, it should still be in the range of the fixed
            # physiologic params choosen by the user. At the moment, we have choosen to
            # just set this parameter to 0.250 sec, which should be a reasonable average
            # of 1H metabolite T2 values in the brain. It is then allowed to bop plus or
            # minus 0.001 as set further below.  In the fitting function, we adjust each 
            # fixed value by the delta from 0.250 so that the pder will fluctuate as the
            # parameter changes and not confuse the poor optimization routine. In reality,
            # the 0.250 is never used, just the delta amount of the actual a[nmet*2]
            # parameter from that value.
            
            ma     = (self.fix_t2_center - a[nmet*2]) + t2fix    # delta for Ta param that is set at 0.25 sec
            ma     =  t/np.outer(ma, arr1)
            mb     = (t / a[nmet*2+1])**2
            expo   = ma+mb
            lshape = util_math.safe_exp(-expo)            
        
        
        if finalwflg:  
            finalw = lshape[:,0]
            finalw = util_spectral.full_width_half_max(np.fft.fft(util_spectral.chop(finalw))/len(finalw)) * self.spectral_hpp
            return finalw
        
        # if FID, then for correct area, first point must be divided by 2
        
        tmp  = self.basis_mets.copy()  
        fre  = a[nmet:nmet*2] - util_ppm.ppm2hz(peaks,self)*2.0*np.pi    # in Radians here
        fre  = np.exp( 1j * (np.outer(fre, arr1)) * t ) # outer is matrix multiplication
        amp  = np.outer(a[0:nmet], arr1)
        ph0  = np.outer(np.exp(1j * (np.zeros(nmet) + a[nmet*2+2])), arr1)    
        tmp *= amp * fre * ph0 * lshape
        f[:,0:npts] = tmp  
        
        f[:,0] = f[:,0] / 2.0  
    
        # Calc Phase1 
        phase1 = np.exp(1j * (a[nmet*2+3]*DTOR*(np.arange(nptszf,dtype=float)-piv)/nptszf))
        
        # Calculate Partial Derivatives  
        pder = None
        if pderflg:
            pder = np.zeros((len(a),nptszf), complex)
        
            pall = np.sum(f,axis=0)   # all lines added
        
            pind = f
            tt         = np.zeros(nptszf,float)
            tt[0:npts] = np.arange(npts,dtype=float) * td
        
            for i in range(nmet):   # Calc the Ampl and Freq pders
                pder[i,:]      = (np.fft.fft(pind[i,:] / a[i]   )/nptszf) * phase1
                pder[i+nmet,:] = (np.fft.fft(tt * 1j * pind[i,:])/nptszf) * phase1
            pder[nmet*2+0,:]  = (np.fft.fft(     tt     * pall/(a[nmet*2+0]**2))/nptszf) * phase1
            pder[nmet*2+1,:]  = (np.fft.fft(2.0*(tt**2) * pall/(a[nmet*2+1]**3))/nptszf) * phase1
        
            pder[nmet*2+2,:]  = (np.fft.fft(1j*pall)/nptszf) * phase1 * nptszf
            pder[nmet*2+3,:]  = (np.fft.fft(   pall)/nptszf) * (1j*DTOR*(np.arange(nptszf,dtype=float)-piv)/nptszf) * phase1
            
            
        # Do the FFT 
        if indiv:   # return individual lines
            if nmet != 1: 
                for i in range(nmet): 
                    f[i,:] = (np.fft.fft(f[i,:])/nptszf) * phase1
            else:
                f = (np.fft.fft(f[0,:])/nptszf) * phase1
        else:  # return summed spectrum    
            if (nmet) != 1: 
                f = np.sum(f,axis=0)
                f = (np.fft.fft(f)/nptszf) * phase1
            else:
                f = (np.fft.fft(f[0,:])/nptszf) * phase1
            
        # Add in baseline unless nobase is True ---
        if not nobase:
            if f.ndim > 1: 
                for i in range(len(f)): f[i,:] = f[i,:] + self.fit_baseline
            else: 
                f = f + self.fit_baseline
    
    
        if self.macromol_model == FitMacromoleculeMethod.SINGLE_BASIS_DATASET:

            if self.basis_mmol:

                mfre  = a[self.nparam+1]
                mtmp  = self.basis_mmol.copy()
                chop  = ((((np.arange(npts) + 1) % 2) * 2) - 1)
                mtmp *= chop
                marea = a[self.nparam]
                fre   = mfre*2.0*np.pi    # in Radians here
                fre   = np.exp( 1j * fre * mt )      
                ph0   = np.exp( 1j * a[nmet*2+2])    
                
                mtmp *= marea * fre * ph0
                mf[0:npts] = mtmp
                mf[0]      = mf[0] / 2.0            
    
                mind = mf.copy()
    
                mf = (np.fft.fft(mf)/nptszf) * phase1
    
                if f.ndim > 1: 
                    mf.shape = 1,mf.shape[0]
                    f = np.concatenate([f, mf],axis=0)
                else: 
                    f = f + mf
                    
                if pderflg:
                    mtt         = np.zeros(nptszf,float)
                    mtt[0:npts] = np.arange(npts,dtype=float) * td
                    
                    pder[nmet*2+4,:] = (np.fft.fft(mind / marea)/nptszf) * phase1
                    pder[nmet*2+5,:] = (np.fft.fft(mtt * 1j * mind)/nptszf) * phase1
    
        return f, pder   

   
   
def voigt_checkin(nmet, source, dataset):
    """
    Converts some of the parameters from the initial value calculation OR the
    model optimized to fit the data before saving these values into long term
    storage. Phase0 converts from radians to degrees, and frequency 
    terms from Hz to ppm. 
    """
    dest = source.copy()
    dest[nmet:nmet*2] = util_ppm.hz2ppm(dest[nmet:nmet*2]/(2.0*np.pi), dataset, acq=True)
    dest[nmet*2+2]    = dest[nmet*2+2] * 180.0 / np.pi
    return dest
    
    
def voigt_checkout(nmet, source, dataset):
    """
    Converts some of the long term stored parameters from the initial value 
    calculation OR the model optimized to fit the data before using them in 
    the main program. Phase0 converts from degrees to radians, and frequency 
    terms from ppm to Hz.
    """
    dest = source.copy()
    dest[nmet:nmet*2] = util_ppm.ppm2hz(dest[nmet:nmet*2], dataset, acq=True)*2.0*np.pi
    dest[nmet*2+2]    = dest[nmet*2+2] * np.pi / 180.0 
    if dest[nmet*2]   == 0.0: dest[nmet*2]   = 0.000001
    if dest[nmet*2+1] == 0.0: dest[nmet*2+1] = 0.000001
    return dest
