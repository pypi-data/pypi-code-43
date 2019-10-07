# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import util
import util_voigt
import functor
import constants
import lowess
import vespa.common.constants as common_constants
import vespa.common.minf_parabolic_info as minf
import vespa.common.util.ppm as util_ppm
import vespa.common.util.generic_spectral as util_spectral

# import util_file as ufile       # used for debug

from xy_b0_correction import b0_correction
from xy_auto_correlate import auto_correlate
from xy_savitzky_golay import savitzky_golay
from xy_optimize_phase import optimize_phase0_correlation
from xy_optimize_phase import optimize_phase1_correlation
from xy_optimize_phase import optimize_phase0_integration
from xy_optimize_phase import optimize_phase1_integration

from vespa.common.constants import DEGREES_TO_RADIANS as DTOR
from constants import FitLineshapeModel
from constants import VoigtDefaultFixedT2
from constants import FitInitialSmallPeakFreqs
from constants import FitInitialSmallPeakAreas
from constants import FitInitialBaselineMethod
from constants import FitInitialPhaseMethod
from constants import FitOptimizeWeightsMethod
from constants import FitInitialB0ShiftMethod
from constants import FitInitialLinewidthMethod
from constants import FitMacromoleculeMethod

DTOR = common_constants.DEGREES_TO_RADIANS
RTOD = common_constants.RADIANS_TO_DEGREES


class FunctInitialValues(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    fitting chain for frequency domain spectral MRS data.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        #----------------------------------------------------------------
        # set up a "model" attribute 
        #  - this can have parameters added to it
        #  - this is due to porting the IDL code
        #----------------------------------------------------------------

        self.prior_ppm_start                    = 1.0
        self.prior_ppm_end                      = 4.1
        self.prior_list                         = [ ]
        self.prior_area_scale                   = [ ]
        self.prior_peak_ppm                     = [ ]
        self.prior_search_ppm                   = [ ]
        self.prior_db_ppm                       = [ ]
        self.prior_fix_t2                       = [ ]
        self.prior_search_ph0                   = [ ]
        
        self.lineshape_model                    = FitLineshapeModel.VOIGT 
        self.fix_t2_center                      = VoigtDefaultFixedT2.CENTER

        self.initial_b0_shift_method            = constants.FitInitialB0ShiftMethod.MANUAL
        self.initial_b0_value                   = 0.0       # initial b0 shift in hz
        self.initial_baseline_method            = constants.FitInitialBaselineMethod.NONE
        self.initial_baseline_lowess_width        = 35.0    # Hz
        self.initial_baseline_lowess_delta        = 3.2     # 
        self.initial_baseline_lowess_ignore_width = 15.0    # Hz
        self.initial_cr_cho_separation          = True
        self.initial_peak_search_abs            = False
        self.initial_small_peak_areas           = constants.FitInitialSmallPeakAreas.NAA_RATIO
        self.initial_small_peak_freqs           = constants.FitInitialSmallPeakFreqs.REF_PEAK
        self.initial_linewidth_method           = constants.FitInitialLinewidthMethod.MANUAL 
        self.initial_linewidth_value            = 5.0       # initial linewidth in hz
        self.initial_linewidth_range_start      = 4.1       # NB this is *LW* optimization range
        self.initial_linewidth_range_end        = 1.9       #  start/end in ppm
        self.initial_linewidth_fudge            = 1.0       # LW fudge value (linear scaler)
        self.initial_phase_method               = constants.FitInitialPhaseMethod.MANUAL  
        self.initial_phase0_value               = 0.0       # initial phase0 in deg
        self.initial_phase1_value               = 0.0       # initial phase1 in deg
        self.initial_apply_ko_filter            = False
        self.initial_ko_linewidth_minimum       = 20
        self.initial_ko_points                  = 30
        self.initial_phase1_fid_constant        = 0.0       # for ultra-short FID data phase1 unwrap
        self.initial_lac_method                 = 2

        self.macromol_single_basis_dataset_start_area = 1.0

        self.optimize_limits_range_area         = 50.0          # %
        self.optimize_limits_range_ppm          = 5.0           # Hz
        self.optimize_limits_range_phase0       = 45.0          # deg
        self.optimize_limits_range_phase1       = 2000.0        # deg
        self.optimize_limits_max_linewidth      = 1.0
        self.optimize_limits_min_linewidth      = 0.04
        self.optimize_weights_method            = constants.FitOptimizeWeightsMethod.LOCAL_WEIGHTING
        self.optimize_weights_scale_factor      = 1000.0        # multiplier for weighted optimization
        self.optimize_weights_width_factor      = 3.0           # multiplier for width of weighted regions
        self.optimize_weights_water_flag        = True          # Off/On zero water region
        self.optimize_weights_water_start       = 4.1           # water suppression affected region
        self.optimize_weights_water_end         = 5.3           #  start/end in ppm
        self.optimize_weights_lipid_flag        = False         # Off/On zero lipid region
        self.optimize_weights_lipid_start       = -0.5          # region with lipid - lower weight here
        self.optimize_weights_lipid_end         = 1.1           #  start/end in ppm
        self.optimize_weights_small_peak_factor = 1.0           # scale multiple for small peak regions

        self.prior = None

        self.attribs = ["prior_ppm_start",
                        "prior_ppm_end",
                        "prior_list",
                        "prior_area_scale",
                        "prior_peak_ppm",
                        "prior_search_ppm",
                        "prior_db_ppm",
                        "prior_fix_t2",
                        "prior_search_ph0",
                        "lineshape_model",
                        "initial_b0_shift_method",
                        "initial_b0_value",
                        "initial_baseline_method",
                        "initial_baseline_lowess_width",
                        "initial_baseline_lowess_delta",
                        "initial_baseline_lowess_ignore_width",
                        "initial_cr_cho_separation",
                        "initial_peak_search_abs",
                        "initial_small_peak_areas",
                        "initial_small_peak_freqs",
                        "initial_linewidth_method",
                        "initial_linewidth_value",
                        "initial_linewidth_range_start",
                        "initial_linewidth_range_end",
                        "initial_linewidth_fudge",
                        "initial_phase_method",
                        "initial_phase0_value",
                        "initial_phase1_value",
                        "initial_apply_ko_filter",
                        "initial_ko_linewidth_minimum",
                        "initial_ko_points",
                        "initial_phase1_fid_constant",
                        "initial_lac_method",
                        "macromol_single_basis_dataset_start_area",
                        "optimize_limits_range_area",
                        "optimize_limits_range_ppm",
                        "optimize_limits_range_phase0",
                        "optimize_limits_range_phase1",
                        "optimize_limits_max_linewidth",
                        "optimize_limits_min_linewidth",
                        "optimize_weights_method",
                        "optimize_weights_scale_factor",
                        "optimize_weights_width_factor",
                        "optimize_weights_water_flag",
                        "optimize_weights_water_start",
                        "optimize_weights_water_end",
                        "optimize_weights_lipid_flag",
                        "optimize_weights_lipid_start",
                        "optimize_weights_lipid_end",
                        "optimize_weights_small_peak_factor",
                        "prior",
                       ]        
        
        
    ##### Standard Methods and Properties #####################################
    
    def algorithm(self, chain):
        nmet    = chain.nmet
        dim0    = chain.spectral_dims[0]
        dat     = chain.data 

        # convert a few lists to numpy arrays since they are stored as lists in
        # the block object so they can be stored more easily, but are easier to 
        # use here as numpy arrays
        self.prior_area_scale = np.array(self.prior_area_scale)
        self.prior_peak_ppm   = np.array(self.prior_peak_ppm)
        self.prior_peak_ppm   = np.round(util_ppm.ppm2pts(self.prior_peak_ppm, chain))
        self.prior_search_ppm = np.array(self.prior_search_ppm)
        self.prior_search_ppm = util_ppm.ppm2pts(self.prior_search_ppm, chain, rel=True)
        self.prior_search_ph0 = np.array(self.prior_search_ph0)
        
        self.find_initial_values(chain)

        # Calculate parameter initial values
        a = np.hstack([chain.init_area, 
                       chain.init_freq, 
                       chain.init_ta, 
                       chain.init_tb, 
                       chain.init_ph0,
                       chain.init_ph1 ])

        # Update parameter constraints 
        #
        # Areas constraints    
        areamax = chain.init_area * (1.0 + self.optimize_limits_range_area/100.0)
        areamin = chain.init_area *  1e-8   # no zeros, else derivatives blow up in optimization

        # PPM constraints
        fredel  = self.optimize_limits_range_ppm * 2.0 * np.pi
        fremin  = chain.init_freq - fredel
        fremax  = chain.init_freq + fredel

        # Linewidth constraints - start with VOIGT assumptions
        lwAmin = self.optimize_limits_min_linewidth
        lwAmax = self.optimize_limits_max_linewidth
        lwBmin = self.optimize_limits_min_linewidth
        lwBmax = self.optimize_limits_max_linewidth

        if self.lineshape_model == FitLineshapeModel.LORENTZ:  
              lwBmin = 1000.0 - 0.001
              lwBmax = 1000.0 + 0.001
        elif self.lineshape_model == FitLineshapeModel.GAUSS:  
              lwAmin = self.fix_t2_center - 0.001
              lwAmax = self.fix_t2_center + 0.001

        # Phase0 constraints
        ph0min = chain.init_ph0 - (self.optimize_limits_range_phase0 * np.pi / 180.0)
        ph0max = chain.init_ph0 + (self.optimize_limits_range_phase0 * np.pi / 180.0)

        # Phase1 constraints
        ph1min = chain.init_ph1 - self.optimize_limits_range_phase1
        ph1max = chain.init_ph1 + self.optimize_limits_range_phase1

        # Actual constraints
        bot = np.hstack([areamin, fremin, lwAmin, lwBmin, ph0min, ph1min])
        top = np.hstack([areamax, fremax, lwAmax, lwBmax, ph0max, ph1max])

        if chain._block.set.macromol_model == FitMacromoleculeMethod.SINGLE_BASIS_DATASET:
            
            mmol_area     = self.macromol_single_basis_dataset_start_area
            mmol_fre      = 1.0
            mmol_area_max = mmol_area * 10.0
            mmol_area_min = mmol_area * 0.01
            mmol_fre_max  = mmol_fre + 3.0
            mmol_fre_min  = mmol_fre - -3.0

            a   = np.hstack([a, mmol_area, mmol_fre])
            bot = np.hstack([bot, mmol_area_min, mmol_fre_min])
            top = np.hstack([top, mmol_area_max, mmol_fre_max])

        lim = np.array([bot,top])

        # Save results and calculate some other initial value parameters
        chain.initial_values = a.copy()
        chain.limits = lim
        chain.current_lw = self.initial_linewidth_value   

        # set the weight array
        chain.weight_array = self.set_weight_array( chain )




    #########################################################################
    #
    #                           Public Methods
    #
    #########################################################################

    def find_initial_values(self, chain):
        """
        General call to determine initial values for optimization parameters.  Based
        on info in the optimization control structure chain (typically TE and field 
        strength), a procedure call is made to calculate these values.
    
        chain: ptr to optimization control structure
        
         Allows differents assumptions/procedures to be used to set
         the starting values for the ampl/lw-t2s/freq of the DB line
         models based on the field, nucleus, acqseq, and whatever
         else we come up with
    
        """
        prior   = self.prior
        metinfo = chain.metinfo
        
        if chain.frequency < 250.0:
            field = "low"
            te = "short" if (chain.seqte < 90.0) else "long"
    
        else:
            field = "high"
            te = ""
        
        self._initvals_1h(chain, field, te)
    
    
    def set_weight_array(self, chain, lwidth=None, wtmult=None, wtmax=None):
        """
        Creates a weight array to be used in the optimization based on setting in
        the chain structure.  *(self.wtarr)) is set as the output.
        
        chain: ptr to optimization control structure
    
        """
        
        prior     = self.prior
        metinfo   = chain.metinfo

        abbr = [metinfo.get_abbreviation(item) for item in self.prior_list]
    
        dim0    = chain.spectral_dims[0]
    
        if not lwidth:
            lwidth = self.initial_linewidth_value
        else: 
            lwidth = float(lwidth) if lwidth > 0.1 else 0.1
        
        if not wtmult:
            wtmult = self.optimize_weights_width_factor  
        else: 
            wtmult = float(wtmult) if wtmult>0.0001 else 0.001
            
        if not wtmax:
            wtmax  = dim0-1  
        else: 
            wtmax  = float(wtmax)
    
        wtarr = np.zeros(dim0, float)
    
        if self.optimize_weights_method == FitOptimizeWeightsMethod.EVEN_WEIGHTING:
            wtarr = wtarr + 1.0  
    
        elif self.optimize_weights_method == FitOptimizeWeightsMethod.LOCAL_WEIGHTING:
            
            lw = lwidth / chain.spectral_hpp   # in points
            centers = chain.peakpts
    
            wid = lw * wtmult
            wid = wid if lw<wtmax else wtmax
    
            for ctr in chain.peakpts:
                cs  = int(np.where(round(ctr-wid)>0, round(ctr-wid), 0))
                cs  = int(np.where(cs<dim0, cs, dim0))
                ce  = int(np.where(round(ctr+wid)>0, round(ctr+wid), 0))
                ce  = int(np.where(ce<dim0, ce, dim0))
                wtarr[cs:ce] = 1.0  
    
            # set small pk weight scale higher if needed len(chain.peakpts)
            if self.optimize_weights_small_peak_factor != 1.0:
                
                ws = np.clip(int(round(util_ppm.ppm2pts(14.0, chain))),0,dim0)
                we = np.clip(int(round(util_ppm.ppm2pts(1.25, chain))),0,dim0)
                wtarr[ws:we] = wtarr[ws:we] * self.optimize_weights_small_peak_factor

                if 'lac' in abbr:
                    ws = np.clip(int(round(util_ppm.ppm2pts(1.45, chain))),0,dim0)
                    we = np.clip(int(round(util_ppm.ppm2pts(1.25, chain))),0,dim0)
                    wtarr[ws:we] = 1.0  

                if 'naa' in abbr:
                    ws = np.clip(int(round(util_ppm.ppm2pts(2.12, chain))),0,dim0)
                    we = np.clip(int(round(util_ppm.ppm2pts(1.85, chain))),0,dim0)
                    wtarr[ws:we] = 1.0  

                if 'cr' in abbr or 'cho' in abbr:
                    ws = np.clip(int(round(util_ppm.ppm2pts(3.30, chain))),0,dim0)
                    we = np.clip(int(round(util_ppm.ppm2pts(2.85, chain))),0,dim0)
                    wtarr[ws:we] = 1.0  
    
            # Set and filter the weights
            indx0 = np.where(wtarr == 0.0)[0]
            if np.size(indx0) != 0: 
                wtarr[indx0] = 1.0 / self.optimize_weights_scale_factor        

            # set pks in water suppression low
            if self.optimize_weights_water_flag:
                ws = np.clip(int(round(util_ppm.ppm2pts(self.optimize_weights_water_end, chain))),0,dim0)
                we = np.clip(int(round(util_ppm.ppm2pts(self.optimize_weights_water_start, chain))),0,dim0)
                wtarr[ws:we] = 1.0 / self.optimize_weights_scale_factor
    
            # set pks in lipid area low
            if self.optimize_weights_lipid_flag == 1:
                ws = np.clip(int(round(util_ppm.ppm2pts(self.optimize_weights_lipid_end, chain))),0,dim0)
                we = np.clip(int(round(util_ppm.ppm2pts(self.optimize_weights_lipid_start, chain))),0,dim0)
                wtarr[ws:we] = 1.0 / self.optimize_weights_scale_factor
    
            wtarr = wtarr / max(wtarr)
    
        return wtarr
    
    
    #########################################################################
    #
    #                   Private/Internal Use Only Methods
    #
    #########################################################################
    
    def _apply_phase01(self, data, ph0, ph1, piv, chain):
        """
        Applies zero and first order phase to a given complex array
    
        INPUT:
    
         data: complex array
         ph0: zero order phase to apply to data, in degrees
         ph1: first order phase to apply to data, in degrees
         piv: first order phase pivot, in ppm units
         chain: ptr to optimization control structure
    
        KEYWORDS:
    
         phase: returns the complex array with zero/first order phase terms
    
        ph0 and ph1 in Degrees
        piv in ppm
        data must be complex
    
        """
    
        prior   = self.prior
        metinfo = chain.metinfo
    
        dsiz = data.shape
        pts  = data.shape[0]
        
        if 'complex' not in data.dtype.name:
            return data
        
        if ph0 == 0.0 and ph1 == 0.0:
            return data, 1
        
        pivot  = util_ppm.ppm2pts(piv, chain)
        phase0 = ph0 * DTOR
        phase1 = ph1 * DTOR * (np.arange(pts)-pivot)/pts
        phase  = np.exp(1j*(phase0+phase1))
        
        if data.ndim == 1:
            data = phase*data
        
        elif data.ndim == 2:
            for i in np.arange(data.shape[1]):
                data[:,i] = phase*data[:,i]
    
        elif data.ndim == 3:
            for j in np.arange(data.shape[2]):
                for i in np.arange(data.shape[1]):
                    data[:,i,j] = phase*data[:,i,j]
    
        elif data.ndim == 4:
            for k in np.arange(data.shape[3]):
                for j in np.arange(data.shape[2]):
                    for i in np.arange(data.shape[1]):
                        data[:,i,j,k] = phase*data[:,i,j,k]
        return data, phase
    
        
    
    def _baseline_estimation_lowess(self, data, chain, widmul=1.0):
        """
        Initial baseline smoothing/estimate via Lowess filter wrap to C/Fortran DLL call
        
        INPUT:
         dat:   array, data
         chain:  ptr to optimization control structure
        
        KEYWORDS:
         widmul: linewidth multiplier
        
        """
        prior   = self.prior
        metinfo = chain.metinfo
        
        dat = data.copy()
        
        if chain.nucleus == '1H': #and np.round(chain.frequency) == 64:
            # Special rule if we have Cho/Cre
            # - keeps calcs from being made from Cho/Cr peak values
            cho = int(util_ppm.ppm2pts(3.35, chain))
            cre = int(util_ppm.ppm2pts(2.85, chain))
        
        width  = self.initial_baseline_lowess_width
        delta  = self.initial_baseline_lowess_delta
        
        if self.prior_list:
            # De-emphasize regions containing known peaks
            # pkloc - the location of the known peaks (in pts) in data array
            # pkwid - the width about the known peaks to de-emphasize
                
            pkloc = self.prior_peak_ppm    # these are in pts here
                  
            pkwid = int(round(self.initial_baseline_lowess_ignore_width * widmul / chain.spectral_hpp))
        
    #        # new pkloc source - auto_prior ppm array ... if any
    #        if self.initial_baseline_lowess_peak_source == 1:
    #    
    #            pkloc = nd.array(list(chain.auto_prior.values_ppm))
    #            pkloc = np.round(util_ppm.ppm2pts(pkloc, chain))
        
            npts = len(dat)
            npks = len(pkloc)
        
            for i in range(npks):
        
                ym  = int(pkloc[i])
                ys  = int(round((ym - int(pkwid/2))))
                ye  = int(round((ym + int(pkwid/2))))
                ys  = ys if ys>0 else 0
                ye  = ye if ye<npts else npts
                ny  = ye - ys 
                tmp = np.arange(ny)
        
                lhs = ys - 1
                rhs = ye + 1
                lhs = lhs if lhs>0 else 0
                rhs = rhs if rhs<npts else npts
                
                if chain.nucleus == '1H': #AND ROUND(chain.frequency)) EQ 64:
        
                    # Special rule if we have Cho/Cre
                    # - keeps calcs from being made from Cho/Cr peak values
        
                    if (lhs < cre) and (lhs > cho):
                        lhs = cho
                    if (rhs < cre) and (rhs > cho):
                        rhs = cre
        
                lhs1 = lhs - 2
                lhs1 = lhs1 if lhs1>0 else 0
                rhs1 = rhs+2
                rhs1 = rhs1 if rhs1<npts else npts
        
                ms  = np.median(dat[lhs1:lhs])
                me  = np.median(dat[rhs:rhs1])
        
                a   = (me-ms)/(ny+4)
        
                tmp = tmp*a + ms
        
                dat[ys:ye] = tmp
            
            
            if chain.nucleus == '1H' and np.round(chain.frequency) > 250:
                # Special rule if we have high field
                lhs = int(round(util_ppm.ppm2pts(4.12, chain)))
                rhs = int(round(util_ppm.ppm2pts(3.4, chain)))
                
                lhs = lhs - 1
                rhs = rhs + 1
                lhs = lhs if lhs>0 else 0
                rhs = rhs if rhs<npts else npts
                
                ny  = rhs - lhs + 1
                tmp = np.arange(ny)
    
                lhs1 = lhs - 2
                lhs1 = lhs1 if lhs1>0 else 0
                rhs1 = rhs+2
                rhs1 = rhs1 if rhs1<npts else npts
    
                ms  = np.median(dat[lhs1:lhs])
                me  = np.median(dat[rhs:rhs1])
                a   = (me-ms)/(ny+4)
                tmp = tmp*a + ms
            
                dat[lhs:rhs] = tmp
        
        width = width / chain.sw            # convert from Hz to % points
        base  = lowess.lowess(dat, frac=width, delta=delta)
        
        return base
    
    
    def _baseline_estimation_savgol(self, data, chain, widmul=1.0):
        """
        Initial baseline smoothing/estimate via Savitzgy-Golay filter 
        
        INPUT:
         dat:   array, data
         chain:  ptr to optimization control structure
        
        KEYWORDS:
         widmul: linewidth multiplier
        
        """
        prior   = self.prior
        metinfo = chain.metinfo
        
        dat = data.copy()
        
        if chain.nucleus == '1H': #and np.round(chain.frequency) == 64:
            # Special rule if we have Cho/Cre
            # - keeps calcs from being made from Cho/Cr peak values
            cho = int(util_ppm.ppm2pts(3.35, chain))
            cre = int(util_ppm.ppm2pts(2.85, chain))
        
        width  = self.initial_baseline_lowess_width
        delta  = self.initial_baseline_lowess_delta
        
        if self.prior_list:
            # De-emphasize regions containing known peaks
            # pkloc - the location of the known peaks (in pts) in data array
            # pkwid - the width about the known peaks to de-emphasize
                
            pkloc = self.prior_peak_ppm    # these are in pts here
                  
            pkwid = int(round(self.initial_baseline_lowess_ignore_width * widmul / chain.spectral_hpp))
    
    #        # new pkloc source - auto_prior ppm array ... if any
    #        if self.initial_baseline_lowess_peak_source == 1:
    #    
    #            pkloc = nd.array(list(chain.auto_prior.values_ppm))
    #            pkloc = np.round(util_ppm.ppm2pts(pkloc, chain))
        
            npts = len(dat)
            npks = len(pkloc)
        
            for i in range(npks):
        
                ym  = int(pkloc[i])
                ys  = int(round((ym - int(pkwid/2))))
                ye  = int(round((ym + int(pkwid/2))))
                ys  = ys if ys>0 else 0
                ye  = ye if ye<npts else npts
                ny  = ye - ys 
                tmp = np.arange(ny)
        
                lhs = ys - 1
                rhs = ye + 1
                lhs = lhs if lhs>0 else 0
                rhs = rhs if rhs<npts else npts
                
                if chain.nucleus == '1H': #AND ROUND(chain.frequency)) EQ 64:
        
                    # Special rule if we have Cho/Cre
                    # - keeps calcs from being made from Cho/Cr peak values
        
                    if (lhs < cre) and (lhs > cho):
                        lhs = cho
                    if (rhs < cre) and (rhs > cho):
                        rhs = cre
        
                lhs1 = lhs - 2
                lhs1 = lhs1 if lhs1>0 else 0
                rhs1 = rhs+2
                rhs1 = rhs1 if rhs1<npts else npts
                ms   = np.median(dat[lhs1:lhs])
                me   = np.median(dat[rhs:rhs1])
                a    = (me-ms)/(ny+4)
                tmp  = tmp*a + ms
                dat[ys:ye] = tmp
            
            if chain.nucleus == '1H' and np.round(chain.frequency) > 250:
                # Special rule if we have high field
                #
                # This draws a straight line from one side of this region to the
                # other because there is such a mix of narrow and broad peaks
                lhs = int(round(util_ppm.ppm2pts(4.21, chain)))
                rhs = int(round(util_ppm.ppm2pts(3.325, chain)))
                
                lhs = lhs - 1
                rhs = rhs + 1
                lhs = lhs if lhs>0 else 0
                rhs = rhs if rhs<npts else npts
                
                ny  = rhs - lhs
                tmp = np.arange(ny)
    
                lhs1 = lhs - 2
                lhs1 = lhs1 if lhs1>0 else 0
                rhs1 = rhs+2
                rhs1 = rhs1 if rhs1<npts else npts
    
                ms  = np.median(dat[lhs1:lhs])
                me  = np.median(dat[rhs:rhs1])
                a   = (me-ms)/(ny+4)
                tmp = tmp*a + ms
            
                dat[lhs:rhs] = tmp
        
        width = int(width / chain.spectral_hpp)            # convert from Hz to % points
        if width % 2 != 1:
            width += 1
        
        base  = savitzky_golay( dat, width, 2, deriv=0)
        
        return base    

    
    
    def _find_lw(self, dat, ds, de, magnitude=False):
        """
        Calculate the full width half max linewidth for a given region of data.
        Calculation takes the region, auto-correlates it with itself to get a
        correlation plot for the lineshape(s) in the region, and calcs the FWHM
        of the tallest peak.
    
        dat: complex array of data to search
        ds: starting point
        de: ending point
    
        magnitude   bool, flag, performs calc only on magnitude data
    
        """
        # dependencies: util_spectral.full_width_half_max, a_correlate
    
        if ds > de: ds, de = de, ds
    
        pts = de-ds+1
        lag = np.arange(pts) - long(pts/2)
    
        a   = auto_correlate(np.abs(dat[ds:de]), lag)
        lwa = util_spectral.full_width_half_max(a)
        if magnitude:
            return lwa  
    
        b   = auto_correlate(dat[ds:de].real, lag)
        c   = auto_correlate(dat[ds:de].imag, lag)
        lwb = util_spectral.full_width_half_max(b)
        lwc = util_spectral.full_width_half_max(c)
        lw = min([lwa, lwb, lwc])
    
        return lw
    
    
    def _find_lw2(self, dat0, ds0, de0, chain, minfloor=0, positive=False):
        # FIXME PS - This needs some documentation, and the docstring below
        # ain't it. I can say that the chain param is at least sometimes 
        # a ChainVoigt object.
        """
        
        dat:
        ds:
        de:
        chain:
        
        minfloor:
        positive:
    
        """
        prior   = self.prior
        metinfo = chain.metinfo
    
        ds  = ds0 if ds0<de0 else de0
        de  = ds0 if ds0>de0 else de0
        pts = de-ds+1
        if pts < 5:
            ds = (ds-5) if (ds-5)>0 else 0
            de = (de+5) if (de+5)<chain.spectral_dims[0] else chain.spectral_dims[0]
    
        pkloc = np.array(list(chain.user_prior.spectrum.values_ppm))
        pkamp = np.array(list(chain.user_prior.spectrum.values_area))
    
        pkloc = np.round(util_ppm.ppm2pts(pkloc, chain))
        pkloc = pkloc.astype(np.int16)
    
        delta = np.zeros(chain.spectral_dims[0])
        delta[pkloc] = pkamp
        delta = delta[ds:de]
        delta = delta + 1j*delta*0.0
    
        iend = (pts-2) if (pts-2)>1 else 1
    
        bob  = np.convolve(dat0[ds:de],delta[0:iend],'same')
    
    #    # Example of how we might calc a phase for the data from this
    #
    #    ctr  = np.argmax(np.abs(bob))
    #    ph0  = np.angle(bob[ctr])
    #    tmp  = dat0[ds:de] * np.exp(1j*(-ph0))
    
        lw = util_spectral.full_width_half_max(bob.real, minfloor=minfloor, positive=positive)
    
        return lw
    
    
    def _get_metinfo(self, abbr0, chain, defconc=0.3, defprot=1.0, deffudge=1.0, defwidth=0.17):
        """
        Values saved in tab delineated METABOLITE INFO section of the processing
        parameter file are used to guess initial values.  This procedure finds
        these values from the arrays stored in chain, given the text string
        abbreviation of the metabolite name
        
        If no values exist, conc = 0.3, prot = 1.0, fudge = 1.0
        Unless DEFCON, DEFPRO, or DEFFUD are set, then these default
        values get returned
        
        abbr0: string, abbreviation of the metabolite requested
        chain: Ptr to optimization control structure
        
        DEFCON: default concentration value
        DEFPRO: default proton number
        DEFFUD: default amplitude fudge multiplier value
        
        OUTPUT:
        
        conc: concentration, in mM
        prot: number of protons
        fudge: amplitude estimate fudge multiplier
    
        
        # Values saved in tab delineated METABOLITE INFO section of the processing
        # parameter file are used to guess initial values.  This procedure finds
        # these values from the arrays stored in chain, given the text string
        # abbreviation of the metabolite name
        #
        # If no values exist, conc = 0.3, prot = 1.0, fudge = 1.0
        # Unless DEFCON, DEFPRO, or DEFFUD are set, then these default
        # values get returned
        
        """
    
        prior   = self.prior
        metinfo = chain.metinfo
    
        all_abbr = [item.lower() for item in metinfo.abbreviations]
        abbr = abbr0.lower()
        if abbr in all_abbr:
            indx = all_abbr.index(abbr)
            conc  = metinfo.concentrations[indx]
            prot  = metinfo.spins[indx]
        else:
            conc  = defconc
            prot  = defprot
    
        return conc, prot
    
    
    def _inital_estimate_baseline(self, data, chain):
        """
        Generates an estimate of baseline signal using a lowess filtered version of
        the data in which known peak contributions have been de-emphasized. 
        Returns a copy of the data with the base estimate subtracted out
        
        data: complex array, spectral data
        chain: ptr to optimization control structure
    
        """
        prior   = self.prior
        metinfo = chain.metinfo
    
        dat   = data.copy()
        
        if self.initial_baseline_method == FitInitialBaselineMethod.LOWESS_FILTER:
            base1 = self._baseline_estimation_lowess(dat.real, chain, widmul=1.0)
            base2 = self._baseline_estimation_lowess(dat.imag, chain, widmul=1.4) # 1.4 for dispersion lineshape
    
        elif self.initial_baseline_method == FitInitialBaselineMethod.SAVGOL_FILTER:
            base1 = self._baseline_estimation_savgol(dat.real, chain, widmul=1.0)
            base2 = self._baseline_estimation_savgol(dat.imag, chain, widmul=1.4) # 1.4 for dispersion lineshape
    
        base = base1+1j*base2
        dat  = data.copy() - base
    
        chain.init_baseline = base
    
        return dat
    
    
    def _inital_estimate_phase(self, data, chain):
        """
        Estimates zero and or first order phase, using either a correlation or 
        integration auto optimization method.
        
        data: complex array of data to be phased
        chain: ptr to optimization control structure
        pha: phased copy of data
    
        """
        prior   = self.prior
        metinfo = chain.metinfo
    
        pha  = data.copy()
        ddat = data.copy()
    
        if self.initial_phase_method == FitInitialPhaseMethod.MANUAL:
            # manually set phase
            phres  = [chain.phase0,chain.phase1]
            phased, phase = self._apply_phase01(ddat, 
                                          chain.phase0, 
                                          chain.phase1, 
                                          chain.auto_phase1_pivot,
                                          chain)
    
        elif self.initial_phase_method == FitInitialPhaseMethod.CORRELATION_PHASE0:
            # maximize correlation of phase 0 of real spectrum to ideal spectrum
            cdeg  = 5
            pstr  = chain.auto_b0_range_start
            pend  = chain.auto_b0_range_end
            phres, phase = self._optimize_phase01_correlation(ddat, 
                                              chain.user_prior_spectrum,  
                                              chain, 
                                              zero=True,  
                                              one=False,   
                                              b0str=pstr, 
                                              b0end=pend, 
                                              cdeg=cdeg)
    
        elif self.initial_phase_method == FitInitialPhaseMethod.CORRELATION_PHASE01:
            # maximize correlation of phase 0/1 of real spectrum to ideal spectrum
            cdeg  = 5
            pstr  = chain.auto_b0_range_start
            pend  = chain.auto_b0_range_end
            phres, phase = self._optimize_phase01_correlation(ddat, 
                                              chain.user_prior_spectrum,  
                                              chain, 
                                              zero=True,  
                                              one=True,   
                                              b0str=pstr, 
                                              b0end=pend, 
                                              cdeg=cdeg)
    
        elif self.initial_phase_method == FitInitialPhaseMethod.INTEGRATION_PHASE0:
            # maximize integral of phase 0 of real spectrum to ideal spectrum 
            phres, phase = self._optimize_phase01_integration(ddat, chain, zero=True, one=False)
    
        elif self.initial_phase_method == FitInitialPhaseMethod.INTEGRATION_PHASE01:
            # maximize integral of phase 0/1 of real spectrum to ideal spectrum 
            phres, phase = self._optimize_phase01_integration(ddat, chain, zero=True, one=True)
    
        return np.array(phres), phase
    
    
    def _check_array_range(self, istart, iend, npts):
        """
        Takes two indices, checks that they are in the correct order, ie. start
        is smaller than end, checks that start>=0 and end<=npts, and checks 
        that start!=end.
        
        """
        istart = int(istart if istart<iend else iend)
        iend   = int(istart if istart>iend else iend)
    
        istart = istart if istart>0   else 0
        iend   = iend   if iend<=npts else npts
        if istart == iend:    
            # ensure that istart and iend are not the same
            if istart > 0:
                istart = istart-1
            else:
                iend = iend+1
                
        return istart, iend
            
    
    
    def _initvals_1h(self, chain, field, te):
        """
        Initial value procedure.
    
        Calculates from the spectral data starting values for Amplitude, Frequency,
        Phase0, Phase1, Ta and Tb (and occasionally, starting baseline estimates).
        Sets these values in the chain control structure.
    
        chain: ptr to optimization control structure
        field: 'low' (64/128 MHz) or 'high' (above 250 Mhz)
        te: 'long' or 'short' or ''. When field is 'high', te is ignored. 
        """
        if (field == "low") and (te == "short"):
            MED_PPM = 0.17
        else:
            MED_PPM = 0.20
    
        if field == "low":
            BIG_PPM = 0.25
        else:
            BIG_PPM = 0.30
    
    
        prior   = self.prior
        metinfo = chain.metinfo
    
        dat   = chain.data.copy()
        dim0  = chain.spectral_dims[0]
        pivot = chain.auto_phase1_pivot
    
        #--------------------------------------------------------
        # Constant phase 1 removal due to FID delay
    
        constph1 = self.initial_phase1_fid_constant
        if constph1 != 0.0:
            dat, _  = self._apply_phase01(dat, 0.0, constph1, pivot, chain)
    
    
        #--------------------------------------------------------
        # B0 Shift section 
    
        if self.initial_b0_shift_method == FitInitialB0ShiftMethod.MANUAL:
            shft = chain.init_b0
            
        elif self.initial_b0_shift_method == FitInitialB0ShiftMethod.AUTO_CORRELATE:
            ps0  = util_ppm.ppm2pts(chain.auto_b0_range_start, chain)
            pe0  = util_ppm.ppm2pts(chain.auto_b0_range_end, chain)
            ps   = int(ps0 if ps0<pe0 else pe0)
            pe   = int(ps0 if ps0>pe0 else pe0)
            ref  = chain.user_prior.spectrum.summed.flatten()
            ref  = ref[ps:pe]
            bdat = dat[ps:pe]
            shft, _ = b0_correction(bdat,ref)
            chain.init_b0 = shft * chain.spectral_hpp     # in Hz
            
        shft = int(round(chain.init_b0 / chain.spectral_hpp))     # in pts
        dat  = np.roll(dat, shft)
    
    
        #---------------------------------------------------------
        # Phase and Baseline estimate section
        #
        # - the phase 0/1 values and the phased data are returned here
        # - this phased data may then have a baseline estimated for it,
        #   and if so, then the stored estimate has to be back phased
        #   for proper display in the plot window
    
        phres, phase = self._inital_estimate_phase(dat.copy(), chain)   # initial phase guess
        
        ddat = dat * phase
        
        chain.init_ph0 = -phres[0] * DTOR
        chain.init_ph1 = -phres[1] - constph1 
    
        if self.initial_baseline_method:
            # subtract out the baseline estimate
            ddat = self._inital_estimate_baseline(ddat, chain)  
            chain.init_baseline, _ = self._apply_phase01(chain.init_baseline,
                                                 -phres[0],
                                                 -phres[1]-constph1,
                                                  pivot, 
                                                  chain)
    
    
        #---------------------------------------------------------
        # Linewidth section
    
        ptmax = int(round(util_ppm.ppm2pts(self.initial_linewidth_range_start, chain))) # NB the min/max switch here
        ptmin = int(round(util_ppm.ppm2pts(self.initial_linewidth_range_end, chain)))
    
        if self.initial_linewidth_method == FitInitialLinewidthMethod.MANUAL:
            lw = self.initial_linewidth_value
        elif self.initial_linewidth_method == FitInitialLinewidthMethod.DECONVOLUTION:
            lw = self._find_lw( ddat, ptmin, ptmax)
            lw = lw * chain.spectral_hpp * np.abs(self.initial_linewidth_fudge)
        elif self.initial_linewidth_method == FitInitialLinewidthMethod.AUTO_CORRELATE:
            lw = self._find_lw2(ddat, ptmin, ptmax, chain, minfloor=True)   
            lw = lw * chain.spectral_hpp * np.abs(self.initial_linewidth_fudge)
    
        chain.initial_linewidth_value = lw if lw>2.0 else 2.0

        if self.lineshape_model == FitLineshapeModel.VOIGT:
            res = self._calc_height2area_ratio( chain.initial_linewidth_value, chain )            # Free LorGauss constraints
            chain.init_ta = res[0]
            chain.init_tb = res[0]
        elif self.lineshape_model == FitLineshapeModel.LORENTZ:
            res = self._calc_height2area_ratio( chain.initial_linewidth_value, chain, tb=1000.0 ) # Pure Lorentz - user sets Gauss, def=1000 sec
            chain.init_ta = res[0]
            chain.init_tb = 1000.0
        elif self.lineshape_model == FitLineshapeModel.GAUSS:
            # if all fixed T2 values are large then we are doing a 'pure' 
            # gaussian model rather than a physiological Voigt model with T2
            # values that approximate metabolite T2 values. 
            if all(np.array(self.prior_fix_t2) >= 1.0):
                ctr = 1000.0
            else:
                ctr = self.fix_t2_center    # typically 0.250 [sec]
            res = self._calc_height2area_ratio( chain.initial_linewidth_value, chain, ta=ctr )    # Pure Gauss - user sets Lorentz, def=0.250 sec
            # Note. for a physiologic Gaussian lineshape, we allow the user to 
            # set a fixed T2 value for each metabolite. In the model call 
            # (chain_fit_voigt.internal_lorgauss()) we create a lineshape array 
            # that takes each fixed value into account.
            # BUT! we are still passing in a Tb parameter here, and though that 
            # parameter will be tightly constrained, it should still be in the 
            # range of the fixed physiologic params choosen by the user. At the 
            # moment, we have choosen to just set this parameter to 0.250 sec, 
            # which should be a reasonable average of 1H metabolite T2 values 
            # in the brain. It is then allowed to bop plus or minus 0.001 as set 
            # in constraints in the algorithm call below.  
            # In the fitting function, we adjust each fixed value by the delta 
            # from 0.250 so that the pder will fluctuate as the parameter 
            # changes and not confuse the poor optimization routine. In reality,
            # the 0.250 is never used, just the delta amount of the actual a[nmet*2]
            # parameter from that value.
            chain.init_ta = self.fix_t2_center
            chain.init_tb = res[0]
        else:
            res = self._calc_height2area_ratio( chain.initial_linewidth_value, chain )            # Free LorGauss constraints
            chain.init_ta = res[0]
            chain.init_tb = res[0]
    
    
    
        #--------------------------------------------------------
        # Peak Areas and PPMs section
        #
        # Set if initial values are taken from real or abs(real) data
    
        ndat    = len(ddat)
        nmet    = len(self.prior_list)
        foff    = 0.0
        chcrflg = 0
        naoff   = 0.0
        croff   = 0.0
        naamp   = None
        xsm     = int(round(util_ppm.ppm2pts(0.03, chain, rel=True)))
        small   = int(round(util_ppm.ppm2pts(0.10, chain, rel=True)))
        med     = int(round(util_ppm.ppm2pts(MED_PPM, chain, rel=True)))
        big     = int(round(util_ppm.ppm2pts(BIG_PPM, chain, rel=True)))
        
        noramp = res[1] # NB. this comes from Lineshape sections, be careful it does not change
        fampl  = []
        ffreq  = []
    
        if self.initial_lac_method == 1:
            large_metabs = ['naa','cr','cho','h2o','pk0','oth']
        else:
            large_metabs = ['naa','cr','cho','lac','h2o','pk0','oth']
    
        if (field == "low") and (te == "short"):
            large_metabs.append('s-ino')
    
        orig = ddat.copy()
    
        #---------------------------------------------------
        # Loop 1 set large metabolite values based on peak picking
    
        for i in range(nmet):
    
            pkppm  = self.prior_peak_ppm[i]
            fudge  = self.prior_area_scale[i]
            width  = int(round(self.prior_search_ppm[i]))
            dbflag = self.prior_db_ppm[i]
            pkph0  = self.prior_search_ph0[i]
    
                # apply indiv metabolite ph0 prior to peak search,
                # used mostly for UTE data with phase 1 issues
            if pkph0 != 0.0:
                ddat, _  = self._apply_phase01(dat, pkph0, 0.0, pivot, chain)
    
                # convert data to abs(real) if desired.
            ddat = orig.real
            if self.initial_peak_search_abs:
                orig = orig.real
                ddat = np.abs(ddat)
    
                # theoretical center of pk to be measured
            ctr  = int(round(pkppm))
    
                # calc a value for the base the pk sits on  metinfo.get_abbreviation(self.prior_list[1].lower())
            tabbr = metinfo.get_abbreviation(self.prior_list[i].lower())
    
            if 'oth' in tabbr:
                tabbr = 'oth'
            if 'pk0' in tabbr:
                tabbr = 'pk0'
    
            if tabbr == 'cho':
                conc, prot = self._get_metinfo( 'cho', chain, defconc=3.0, defprot=9.0)
                bs  = np.round(ctr - width  )
                be  = np.round(ctr + small)
                bs, be = self._check_array_range(bs, be, ndat)
                bas = np.min(ddat[bs:be])
                bas = bas if bas>0 else 0
                chcrflg = chcrflg+1
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas)
                pkval[0] = pkval[0] * fudge / prot
                
            elif tabbr == 'cr':
                conc, prot = self._get_metinfo( 'cr', chain, defconc=7.0, defprot=3.0)
                bs  = np.round(ctr - small)
                be  = np.round(ctr + width  )
                bs, be = self._check_array_range(bs, be, ndat)
                bas = np.min(ddat[bs:be])
                bas = bas if bas>0 else 0
                chcrflg = chcrflg+1
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas)
                pkval[0] = pkval[0] * fudge / prot
                croff = pkval[1] - ctr
            
            elif tabbr == 'naa':
                cnaa, pnaa = self._get_metinfo( 'naa', chain, defconc=12.0, defprot=3.0)
                bs  = np.round(ctr - width)
                be  = np.round(ctr + width)
                bs, be = self._check_array_range(bs, be, ndat)
                bas = np.min(ddat[bs:be])
                bas = bas if bas>0 else 0
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas)
                pkval[0] = pkval[0] * fudge / pnaa
                naoff = pkval[1] - ctr
                naamp = pkval[0] * noramp
            
            elif tabbr == 'lac':
                conc, prot = self._get_metinfo( 'lac', chain, defconc=2.0, defprot=2.0)
                bs  = np.round(ctr - width)
                be  = np.round(ctr + width)
                bs, be = self._check_array_range(bs, be, ndat)
                bas = 0  
                bas = bas if bas>0 else 0
                pkval = util_voigt.find_peakfreq(np.abs(ddat), bs, be, base=bas, fixed_peak=True)
                pkval[0] = pkval[0] * fudge / prot
            
            elif tabbr == 's-ino':
                conc, prot = self._get_metinfo( 's-ino', chain, defconc=2.0, defprot=3.0)
                bs  = np.round(ctr - width)
                be  = np.round(ctr + width)
                bs, be = self._check_array_range(bs, be, ndat)
                if field == "low":
                    bas = np.min(ddat[bs:be]) > 0
                else:
                    bas = np.min(ddat[bs:be])
                bas = bas if bas>0 else 0
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas)
                pkval[0] = pkval[0] * fudge / prot
    
            elif tabbr == 'h2o':
                conc, prot = self._get_metinfo( 'h2o', chain, defconc=10.0, defprot=2.0)
                bs  = np.round(ctr - width)
                be  = np.round(ctr + width)
                bs, be = self._check_array_range(bs, be, ndat)
                bas = np.min(ddat[bs:be])
                bas = bas if bas>0 else 0
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas, orig=orig)
                pkval[0] = pkval[0] * fudge / prot
                if self.initial_peak_negative_flag != 0:
                    if pkval[2] != 0:
                        pkval[0] = -pkval[0]
            
            elif tabbr == 'oth':
                conc, prot = self._get_metinfo(self.prior_list[i].lower(), chain, defconc=1.0, defprot=1.0)
                bs  = np.round(ctr - width)
                be  = np.round(ctr + width)
                bas = 0
                bs, be = self._check_array_range(bs, be, ndat)
                bas = bas if bas>0 else 0
                if field == "low":
                    orig_param = orig
                else:
                    orig_param = None
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas, orig=orig_param)
                pkval[0] = pkval[0] * fudge / prot
                if self.initial_peak_negative_flag != 0:
                    if pkval[2] != 0:
                        pkval[0] = -pkval[0]
            
            elif tabbr == 'pk0':
                conc, prot = self._get_metinfo(self.prior_list[i].lower(), chain, defconc=1.0, defprot=1.0)
                bs  = np.round(ctr - width)
                be  = np.round(ctr + width)
                bas = 0
                bs, be = self._check_array_range(bs, be, ndat)
                bas = bas if bas>0 else 0
                if field == "low":
                    orig_param = orig
                else:
                    orig_param = None
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas, orig=orig)
                pkval[0] = pkval[0] * fudge / prot
                if self.initial_peak_negative_flag != 0:
                    if pkval[2] != 0:
                        pkval[0] = -pkval[0]
            else:
                # there is a chance that the user will de-select n-acetylaspartate
                # in which case the naa-ratio method will not work, so here we
                # find start values using a peak_search method first, and later we
                # can replace them with naa-ratio values if valid
    
                conc, prot = self._get_metinfo( tabbr, chain, defconc=1.0, defprot=1.0)
                bs = np.round(ctr - width)
                be = np.round(ctr + width)
                bs, be = self._check_array_range(bs, be, ndat)
                
                bas = np.min(ddat[bs:be])
                bas = bas if bas>0 else 0
                pkval = util_voigt.find_peakfreq(ddat, bs, be, base=bas)
                pkval[0] = pkval[0] * fudge / prot
                if tabbr == 'm-ino':
                    pkval[1] = ctr
                if self.initial_small_peak_areas == 'peak_search':
                    pkval[1] = ctr
    #            else:
    #                # this is for 'naa_ratio' option
    #                pkval = [1.0/noramp,ctr]
    
            if dbflag:
                # use the database value for PPM if flag checked
                pkval[1] = ctr  
    
            fampl.append(pkval[0])
            ffreq.append(pkval[1])
    
            # this is avg of all the pk offsets
            foff = foff + (pkval[1]-ctr) / nmet
    
    
        chain.init_area = np.array(fampl) * noramp
        chain.init_freq = np.array(ffreq)

        if self.initial_apply_ko_filter:
            
            kodata = chain.kodata.copy()
            kopoints = self.initial_ko_points 
            kominlw  = self.initial_ko_linewidth_minimum
        
            dim0    = chain.spectral_dims[0]
            acqdim0 = chain.raw_dims[0]
            acqsw   = chain.sw
        
            data = np.zeros([dim0],'complex')
            data[0:len(kodata[kopoints:])] = kodata[kopoints:]

            # numpy broadcasting deals with (N,dim0) sized data arrays
            chop_array = ((((np.arange(acqdim0) + 1) % 2) * 2) - 1)
            data = data * chop_array
            
            data = np.fft.fft(data, n=dim0) / float(dim0)
            data = np.abs(data)

            # create a line shape to apply to basis functions 
            xx = np.arange(acqdim0)/float(acqsw)
            lshape = np.exp(-(chain.initial_linewidth_value * np.pi * xx * 0.6 )**2)     # Gaussian
        
            # get area and frequency estimates
            height = np.zeros([nmet], 'float')
            area0  = np.zeros([nmet], 'float')
            freq0  = np.zeros([nmet], 'float')
            area   = np.zeros([nmet], 'float')
            basis0 = np.zeros([nmet,acqdim0], 'complex')
        
            # get start peak height and broaden basis set
            for i in range(nmet):

                ctr   = int(round(self.prior_peak_ppm[i]))
                bs  = np.round(ctr - small)
                be  = np.round(ctr + small)
                bs, be = self._check_array_range(bs, be, len(data))
                val = util_voigt.find_peakfreq(data, bs, be, base=0)

                area0[i] = val[0]
                freq0[i] = val[1]
        
                basis0[i,:] = chain.basis_mets[i,:] * lshape
        
            # bootstrap from kofilter[0] to kofilter[N] for each metabolite height
            for j in range(4):
        
                basis = basis0.copy()
                if j == 0:
                    area = area0.copy()
        
                for k in range(nmet):
                    basis[k,:] = area[k] * basis[k,:]
        
                basis = np.sum(basis,axis=0)
        
                tmp = np.zeros([dim0],'complex')
                tmp[0:len(basis[kopoints:])] = basis[kopoints:]
                tmp = np.fft.fft(tmp) / float(dim0)
                tmp = np.abs(tmp)
        
                for k in range(nmet):
                    bs  = np.round(freq0[k] - small)
                    be  = np.round(freq0[k] + small)
                    bs, be = self._check_array_range(bs, be, len(tmp))
                    val = util_voigt.find_peakfreq(tmp, bs, be, base=0)
        
                    height[k] = val[0]
                    area[k]  *=  area0[k]/val[0]
            
            # done with estimate, now replace as needed in chain init values  
            for i in range(nmet):
                tabbr = metinfo.get_abbreviation(self.prior_list[i].lower())
                fudge = self.prior_area_scale[i]
                ctr   = int(round(self.prior_peak_ppm[i]))
                if tabbr == 'naa':
                    large_metabs = ['naa']
                    orig = chain.init_area[i]
                    chain.init_area[i] = area[i] * fudge
                    chain.init_freq[i] = freq0[i]
                    naoff = freq0[i] - ctr
                    croff = naoff               # since we use NAA only as ref peak
                    naamp = area[i] * fudge
                    if True:
                        name = self.prior_list[i]
                        #print "Name = "+name+"  area = "+str(area[i])+"   height = "+str(height[i])+"  peak_pick = "+str(orig)
                elif tabbr == 'cr':
                    chain.init_freq[i] = ctr
                elif tabbr == 'cho':
                    chain.init_freq[i] = ctr

    
        #---------------------------------------------------
        # Loop 2 sets Small Metab values via NAA conc ratio
    
        reference_peak_offset = 0.0    
        if self.initial_small_peak_freqs == FitInitialSmallPeakFreqs.REF_PEAK:
            reference_peak_offset = (naoff + croff)/2.0  # general offset
    
        if naamp and (self.initial_small_peak_areas == FitInitialSmallPeakAreas.NAA_RATIO):
            for i in range(nmet): 
    
                fudge  = self.prior_area_scale[i]
                metstr = metinfo.get_abbreviation(self.prior_list[i].lower())
                if 'oth' in metstr: metstr = 'oth'
                if 'pk0' in metstr: metstr = 'pk0'
    
                conc, prot = self._get_metinfo( metstr, chain, defconc=5.0, defprot=3.0)
    
                if metstr not in large_metabs:
                    mult   = naamp * fudge * (pnaa*conc)/(cnaa*prot)
                    genoff = reference_peak_offset
                    chain.init_area[i]  = mult
                    chain.init_freq[i] += genoff
    
        # End Areas and PPMs
        #---------------------------------------------------------
    
    
        #---------------------------------------------------------
        # cho/cr separation section
    
        if self.initial_cr_cho_separation and (chcrflg >= 2):
    
            cho    = int(round(util_ppm.ppm2pts(3.2, chain)))
            cre    = int(round(util_ppm.ppm2pts(3.0, chain)))
            ppm01  = int(round(util_ppm.ppm2pts(0.1, chain, rel=True)))
            ppm02  = int(round(util_ppm.ppm2pts(0.2, chain, rel=True)))
            delcho = 0.0
            delcho = 0.0
    
            prior_list = self.prior_list
            abbr_list = [metinfo.get_abbreviation(item).lower() for item in self.prior_list]
    
            chox   = abbr_list.index('cho')
            fcho   = chain.init_freq[chox]
            delcho = np.abs(fcho - cho)
            crex   = abbr_list.index('cr')
            fcre   = chain.init_freq[crex]
            delcre = np.abs(fcre - cre)
    
            if np.abs(fcho-fcre) < ppm01:               # too close
                if delcho <= delcre:                    # reset Cre
                    chain.init_freq[crex] = fcho + ppm02
                else:                                   # reset Cho
                    chain.init_freq[chox] = fcre - ppm02
    
    
        #---------------------------------------------------------
        # store freq as radians
        chain.init_freq = util_ppm.pts2hz(chain.init_freq, chain, rel=True) * 2.0 * np.pi    # in radians
    
    
    
    
    def _optimize_phase01_correlation(self, data, modfn, chain, 
                                            zero=False, 
                                            one=False,   
                                            nlag=3, 
                                            cdeg=1, 
                                            b0str=3.4, 
                                            b0end=2.8  ):
        """
        Main call for correlation auto phase algorithm.  Returns the phase
        in deg at which the real part is maxed as a two element float array 
        with optimal zero and first order phases.
        
        INPUT:
          data:   complex data to be phased
          modfn:  complex model function against which corrections will be made
          chain:   optimization control structure
        
        KEYWORDS:
          zero:   flag, set to optimize zero order phase
          one:    flag, set to optimize first order phase
          nlag:   number of points to lag in the correlation
          cdeg:   degree of mixing for calculation CSUMM VALUE in correlation
          b0str:  in ppm, start point for B0 correction region
          b0end:  in ppm, end point for B0 correction region
    
        OUTPUT
          phased: returns the input DATA with 0/1 phase applied
    
        
        """
        prior   = self.prior
        metinfo = chain.metinfo
        
        if len(modfn.shape)>1: 
            modfn = modfn.flatten()
        cdeg = np.abs(cdeg)
        if nlag <= 0: 
            nlag = 1
        
        dim0 = len(data)
        ph0  = 0.001
        ph1  = 0.001
        res  = [0.0,0.0]
        pts2 = [0.0,0.0]
        pts4 = [0.0,0.0,0.0,0.0]
        
        # B0 Correction Section!  Must have good alignment or else.
        
        pstr = int(round(util_ppm.ppm2pts(b0str, chain)))
        pend = int(round(util_ppm.ppm2pts(b0end, chain)))
        ps = np.clip(pstr,0,dim0)
        pe = np.clip(pend,0,dim0)
        if ps > pe:
            ps,pe = pe,ps
        
        if ps == 0:
            pe = pe+3 
            pe = np.clip(pe,0,dim0)
        elif ps == dim0:
            pe = dim0
            ps = dim0-3
            ps = ps if ps>0 else 0
        else:
            ps = ps-1
            ps = np.clip(ps,0,dim0)
            pe = pe+1
            pe = np.clip(pe,0,dim0)
        
        dat  = data[ps:pe].copy()
        ref  = modfn[ps:pe].copy()
        
        shft, csum = b0_correction(dat,ref)
    
        dat  = np.roll(data.copy(), shft)
        
        # Set Correlation Limits
        
        str0 = chain.auto_phase0_range_start
        end0 = chain.auto_phase0_range_end
        str1 = chain.auto_phase1_range_start
        end1 = chain.auto_phase1_range_end
        max0 = str0 if str0>end0 else end0
        min0 = str0 if str0<end0 else end0
        max1 = str1 if str1>end1 else end1
        min1 = str1 if str1<end1 else end1
        
        pts4[0] = int(util_ppm.ppm2pts(max0, chain))
        pts4[1] = int(util_ppm.ppm2pts(min0, chain))
        pts4[2] = int(util_ppm.ppm2pts(max1, chain))
        pts4[3] = int(util_ppm.ppm2pts(min1, chain))
        
        # Phasing section
        
        if zero and not one:        # zero order phase only
        
            ph0, _ = optimize_phase0_correlation(dat, modfn, pts4, nlag, cdeg)
            phase  = np.exp(1j * ph0 * DTOR)
            res    = [ph0,ph1]
        
        if one and not zero:        # first order phase only
        
            pivot  = util_ppm.ppm2pts(chain.auto_phase1_pivot, chain)
            ph1, _ = optimize_phase1_correlation(dat, modfn, pts4, pivot, nlag, cdeg)
            phase  = np.exp(1j * ph1 * DTOR * (np.arange(dim0)-pivot)/dim0)
            res    = [ph0,ph1]
        
        if zero and one:            # full phase
    
            pivot = util_ppm.ppm2pts(chain.auto_phase1_pivot, chain)
            
            ph01, csum01 = optimize_phase0_correlation(dat.copy(), modfn, pts4, nlag, cdeg)
            phase0 = np.exp(1j * ph01 * DTOR)
            dat1  = phase0 * dat.copy()
            
            ph11, csum11  = optimize_phase1_correlation(dat1.copy(), modfn, pts4, pivot, nlag, cdeg)
            phase1 = np.exp(ph11 * DTOR * (np.arange(dim0)-pivot)/dim0)
            
            phase_dat1 = phase0 * phase1
            # ----------
            
            pts2[0] = pts4[2]
            pts2[1] = pts4[3]
            
            ph02, csum02 = optimize_phase0_correlation(dat.copy(), modfn, pts2, nlag, cdeg)
            phase0 = np.exp(1j * ph02 * DTOR)
            dat2   = phase0 * dat.copy()
            
            ph12, csum12 = optimize_phase1_correlation(dat2.copy(), modfn, pts4, pivot, nlag, cdeg)
            phase1 = np.exp(1j * ph12 * DTOR * (np.arange(dim0)-pivot)/dim0)
            
            phase_dat2 = phase0 * phase1
            
            #----------
            if csum11 > csum12:
                phase  = phase_dat1
                res = [ph01,ph11]
            else:
                phase  = phase_dat2
                res = [ph02,ph12]
        
        return res, phase    
    
    
        
    def _optimize_phase01_integration(self, data, chain, zero=False, one=False):
        """
        Main call for real integration auto phase algorithm.  Returns the phase
        in deg at which the real part is maxed. Outputs a two element float 
        array with optimal zero and first order phases in degrees.
        
        INPUT:
          data:
          chain: pointer to optimization control structure
        
        KEYWORDS:
          ZERO: flag, set to optimize zero order phase
          ONE:  flag, set to optimize first order phase
        
        """
        prior   = self.prior
        metinfo = chain.metinfo
        
        dim0 = chain.spectral_dims[0]
    
        ph0 = 0.001
        ph1 = 0.001
        phase0 = 1
        phase1 = 1
    
        str0 = chain.auto_phase0_range_start
        end0 = chain.auto_phase0_range_end
        str1 = chain.auto_phase1_range_start
        end1 = chain.auto_phase1_range_end
        max0 = str0 if str0>end0 else end0
        min0 = str0 if str0<end0 else end0
        max1 = str1 if str1>end1 else end1
        min1 = str1 if str1<end1 else end1
    
        dat = data.copy()
        weight = np.zeros(chain.spectral_dims[0])
        
        if zero:        # zero order phase part
        
            ps = int(round(util_ppm.ppm2pts(max0, chain)))
            pe = int(round(util_ppm.ppm2pts(min0, chain)))
            weight[ps:pe] = 1.0
            ph0 = optimize_phase0_integration(data.copy(), weight)
            
            phase0 = np.exp(1j * ph0 * DTOR)
            phased = phase0 * data.copy()
        
        
        if one:         # first order phase part
        
            ps = int(round(util_ppm.ppm2pts(max1, chain)))
            pe = int(round(util_ppm.ppm2pts(min1, chain)))
            pivot = int(round(util_ppm.ppm2pts(chain.auto_phase1_pivot, chain)))
            weight = weight * 0.0
            weight[ps:pe] = 1.0
            
            ph1 = optimize_phase1_integration(phased.copy(), weight, pivot)
            
            phase1 = np.exp(1j * ph1 * DTOR * (np.arange(dim0)-pivot) / dim0)
            phased = phase1 * phased
        
        phase = phase0 * phase1
        res = [ph0,ph1]
    
        return res, phase    

    
    def _height2area_function(self, val, info):
        """
        This is the minimization function used by minf_parabolic_info in the
        _calc_height2area_ratio() call. The val parameter is the decay value
        for which we need to calculate a FWHM line width. Because we are minimizing
        in this optimization, we subtract the calculated value from the original
        line width values (in Hz) and take the absolute value.
    
        """
        
        ta = val if info["ta"] == -1 else info["ta"]
        tb = val if info["tb"] == -1 else info["tb"]
        
        width_hz, peak = util_spectral.voigt_width(ta, tb, info["chain"])
        
        info["peak"] = peak
        
        return np.abs(info["orig_lw"] - width_hz)
    
    
    
    def _calc_height2area_ratio(self, lw, chain, ta=-1.0, tb=-1.0 ):
        """
        We know the value of the full width half max line width in Hz that we have
        in our data, and want to find the Ta and Tb values that yield this.
         
        This function uses the minf_parabolic_info routine to optimze Ta and Tb
        to values between 0.005 and 0.5, however either of the two parameters can
        also be set to constant values by setting the TA and TB keywords to this
        function to the constant value desired. This way we can calculate Pure 
        Gauss or Pure Lorentz lineshape starting values as well as Voigt/LorGauss
        line shape values.
          
        The optimization calls the fitt_height2area_function() to determine the 
        minimization function. As part of that call, we calculate the height of the
        peak for Ta and Tb, which is stored in the info.peak parameter. This is 
        used to provide a normalization value for peak height to peak area 
        conversion on return of this function.
          
         lw - float, linewidth in Hz
         chain - pointer to control structure
         ta - keyword, float, constant value for Ta in the optimization
         tb - keyword, float, constant value for Tb in the optimization
    
        """
        info = { 'ta':ta, 'tb':tb, 'orig_lw':lw, 'chain':chain, 'peak':-1.0 }
        
        # Call parabolic interpolation, Brent's method
        # 1-d minimization routine
        
        val_a = 0.005  # lower bound
        val_b = 0.06   # "some" point in the middle
        val_c = 0.5    # upper bound
        
        finalval, maxit = minf.minf_parabolic_info( val_a, val_b, val_c,
                                                    self._height2area_function, 
                                                    info ) 
        return [finalval, info["peak"]]
    
