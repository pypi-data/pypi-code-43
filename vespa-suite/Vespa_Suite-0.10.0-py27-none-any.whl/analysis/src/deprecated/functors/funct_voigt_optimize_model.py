# Python modules
from __future__ import division


# 3rd party modules
import numpy as np

# Our modules
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import functor
import constants
import util_voigt
import vespa.common.util.generic_spectral as util_spectral

from constrained_levenberg_marquardt import constrained_levenberg_marquardt


class FunctVoigtOptimizeModel(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    fitting chain for frequency domain spectral MRS data.
    
    """
    def __init__(self):
        functor.Functor.__init__(self)

        self.prior_peak_ppm = None
        self.optimize_method = None
        self.optimize_max_iterations = None
        self.optimize_stop_tolerance = None
        self.optimize_scaling_flag = None
        
        self.attribs = ["prior_peak_ppm",
                        "optimize_method",
                        "optimize_max_iterations",
                        "optimize_stop_tolerance",
                        "optimize_scaling_flag"
                       ]

    ##### Standard Methods and Properties #####################################
    
    def algorithm(self, chain):
        if self.optimize_method:

            data  = chain.data.copy()
            nmet  = chain.nmet
            a     = chain.fit_results.copy()
            ww    = chain.weight_array
            lim   = chain.limits.copy()
            itmax = self.optimize_max_iterations
            toler = self.optimize_stop_tolerance
        
            if self.optimize_method == constants.FitOptimizeMethod.CONSTRAINED_LEVENBERG_MARQUARDT:
                
                if self.optimize_scaling_flag:
                    a, pscale, lim, data, baseline = util_voigt.parameter_scale(nmet, a, lim, data, 
                                                                                baseline=chain.fit_baseline)
                    chain.fit_baseline = baseline
                
                yfit, a, sig, chis, wchis, badfit = \
                    constrained_levenberg_marquardt(data, ww, a, lim, chain.fit_function, itmax, toler)

                if self.optimize_scaling_flag:
                    a, chis, wchis, baseline = util_voigt.parameter_unscale(nmet, a, pscale, chis, wchis, 
                                                                            baseline=chain.fit_baseline)
                    chain.fit_baseline = baseline

    
            chain.fit_results = a.copy()
            chain.fit_stats   = np.array([chis, wchis, badfit])
            
            chain.fitted_lw, _ = util_spectral.voigt_width(a[nmet*2], a[nmet*2+1], chain)
            
