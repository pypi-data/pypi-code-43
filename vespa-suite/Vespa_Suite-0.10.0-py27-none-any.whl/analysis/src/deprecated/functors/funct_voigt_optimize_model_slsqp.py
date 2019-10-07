# Python modules
from __future__ import division


# 3rd party modules
import numpy as np
import scipy.optimize.fmin_slsqp as fmin_slsqp

# Our modules
import functor
import constants
import util_voigt
import vespa.common.util.generic_spectral as util_spectral

from constrained_levenberg_marquardt import constrained_levenberg_marquardt


class FunctVoigtOptimizeModelSlsqp(functor.Functor):
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
                
#                if self.optimize_scaling_flag:
#                    a, pscale, lim, data, baseline = util_voigt.parameter_scale(nmet, a, 
#                                                                               lim, data, 
#                                                                               baseline=chain.fit_baseline)
#                    chain.fit_baseline = baseline
                
                yfit, a, sig, chis, wchis, badfit = \
                            constrained_levenberg_marquardt(data, 
                                                            ww, 
                                                            a, 
                                                            lim, 
                                                            chain, 
                                                            chain.fit_function, 
                                                            itmax, 
                                                            toler)

                x0 = a
                func = chain.fit_function
                out, fx, its, imode, smode = fmin_slsqp(func, x0,   eqcons=[], 
                                                                    f_eqcons=None, 
                                                                    ieqcons=[], 
                                                                    f_ieqcons=None, 
                                                                    bounds=lim, 
                                                                    fprime=None, 
                                                                    fprime_eqcons=None, 
                                                                    fprime_ieqcons=None, 
                                                                    args=(), 
                                                                    iter=100, 
                                                                    acc=1e-06, 
                                                                    iprint=1, 
                                                                    disp=None, 
                                                                    full_output=0, 
                                                                    epsilon=1.4901161193847656e-08)



#                if self.optimize_scaling_flag:
#                    a, chis, wchis, baseline = util_voigt.parameter_unscale(nmet, a, 
#                                                                            pscale, 
#                                                                            chis, wchis, 
#                                                                            baseline=chain.fit_baseline)
#                    chain.fit_baseline = baseline
    
            chain.fit_results = a.copy()
            chain.fit_stats   = np.array([chis, wchis, badfit])
            
            chain.fitted_lw, _ = util_spectral.voigt_width(a[nmet*2], a[nmet*2+1], chain)
    
      
 
 
#The argument you're interested in is eqcons, which is a list of functions
#whose value should be zero in a successfully optimized problem.
#
#See the fmin_slsqp test script at
#http://projects.scipy.org/scipy/attachment/ticket/570/slsqp_test.py
#
#In particular, your case will be something like this
#
#x = fmin_slsqp(testfunc,[-1.0,1.0], args = (-1.0,), eqcons = [lambda x, y:
#x[0]-x[1] ], iprint = 2, full_output = 1)
#
#In your case, eqcons will be:
#[lambda x, y: x[0]+x[1]+x[2]-1, lambda x, y: x[3]+x[4]+x[5]-1 ]
#
#Alternatively, you can write a Python function that returns those two values
#in a sequence as pass it to fmin_slsqp as  f_eqcons.
#
#
#
#On Mon, May 4, 2009 at 2:00 PM, Leon Adams <skorpio11@gmail.com> wrote:
#
#> Hi,
#>
#> I was wondering what the status is of the Slsqp extension to the optimize
#> package. I am currently in need of the ability to place an equality
#> constraint on some of my input variables, but the available documentation on
#> slsqp seems insufficient.
#>
#> My Scenario:
#>
#> I have an objective fn: Obfn(x1,x2,x3,x4,x5,x6) that I would like to place
#> the additional constrain of
#> x1 + x2 + x3 = 1
#> x4 + x5 + x6 = 1
#>
#> If there is a good usage example I can be pointed to, it would be
#> appreciated
#>
#> Thanks in advance.
 
