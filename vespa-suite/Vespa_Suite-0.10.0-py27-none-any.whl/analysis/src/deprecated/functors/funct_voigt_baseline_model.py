# Python modules
from __future__ import division


# 3rd party modules
import numpy as np


# Our modules
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import functor
import constants
import lowess
import splines
import vespa.common.constants as common_constants


class FunctVoigtBaselineModel(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    fitting chain for frequency domain spectral MRS data.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        self.prior_peak_ppm = None
        self.optimize_global_iterations = None
        self.baseline_method = None
        self.baseline_smoothing_flag = None
        self.baseline_skip_last_smooth = None
        self.baseline_smoothing_width = None
        self.baseline_spline_order = None
        self.baseline_spline_nknots = None
        self.baseline_spline_spacing = None
        self.baseline_wavelet_scale = None
        self.baseline_wavelet_min_dyad = None
        self.baseline_underestimate = None
        
        self.attribs = ["prior_peak_ppm",
                        "optimize_global_iterations",
                        "baseline_method",
                        "baseline_smoothing_flag",
                        "baseline_skip_last_smooth",
                        "baseline_smoothing_width",
                        "baseline_spline_order",
                        "baseline_spline_nknots",
                        "baseline_spline_spacing",
                        "baseline_wavelet_scale",
                        "baseline_wavelet_min_dyad",
                        "baseline_underestimate",
                       ]
        

    ##### Standard Methods and Properties #####################################

    def algorithm(self, chain):
        if self.baseline_method:

            data = chain.data.copy()
    
            a = chain.fit_results.copy()
            model, _ = chain.fit_function(a, pderflg=False, nobase=True)
    
            # Subtract metabolite model from data 
            basr = data.real - model.real
            basi = data.imag - model.imag
            
            hpp = chain.spectral_hpp
        
            # Smooth the remaining features
            if self.baseline_smoothing_flag: 
                if not (chain.iteration == self.optimize_global_iterations and 
                        self.baseline_skip_last_smooth): 
                    wid  = self.baseline_smoothing_width / chain.sw    # convert Hz into % points
                    basr = lowess.lowess(basr, frac=wid, delta=3.2)
                    basi = lowess.lowess(basi, frac=wid, delta=3.2)

            # Calculate the baseline

            if self.baseline_method == constants.FitBaselineMethod.BSPLINE_VARIABLE_KNOT:
                ny     = np.size(basr)
                korder = self.baseline_spline_order
                nknots = self.baseline_spline_nknots
    
                # Start with evenly distributed interior knots 
                baser  = splines.splinevar(basr, nknots, korder, hz_per_pt=hpp)
                basei  = splines.splinevar(basi, nknots, korder, hz_per_pt=hpp)    
            
            elif self.baseline_method == constants.FitBaselineMethod.BSPLINE_FIXED_KNOT:
                ny     = np.size(basr)
                korder = self.baseline_spline_order
                nknots  = chain.sw / (self.baseline_spline_spacing*chain.spectral_hpp)
    
                # Calculate an even distribution of the interior knots 
                baser  = splines.splinefix(basr,nknots,korder)
                basei  = splines.splinefix(basi,nknots,korder)
            
            elif self.baseline_method == constants.FitBaselineMethod.WAVELET_FILTER_BASIC:
                # PyWavelets is an optional dependency; it might not be 
                # installed.
                if constants.PYWAVELETS_AVAILABLE:
                    # The import of wavelet_filter is inline here because it 
                    # imports PyWavelets which isn't safe to do unless 
                    # guarded by the condition above.
                    import wavelet_filter

                    # wavelet filter - Requires data to have power of 2 length 
                    thresh  = chain.current_lw / chain.spectral_hpp
                    scale   = int(self.baseline_wavelet_scale)
                    dyadmin = int(self.baseline_wavelet_min_dyad)
    
                    baser = wavelet_filter.wavelet_filter(basr, thresh, scale, dyadmin=dyadmin)
                    basei = wavelet_filter.wavelet_filter(basi, thresh, scale, dyadmin=dyadmin)
                else:
                    # PyWavelets is not available. We rely on the GUI to 
                    # note this and inform the user.
                    baser = basr * 0.0
                    basei = basi * 0.0
            else:
                raise ValueError, 'Unknown baseline method "%s"' % str(self.baseline_method)
    
            if chain.iteration == 1 and self.baseline_underestimate: 
                # Account for when metabolites are inverted due to phase 
                orient = 1.0
                if abs(a[chain.nmet*2+2] / common_constants.DEGREES_TO_RADIANS) > 90.0: 
                    orient = -1.0 
    
                # Set the underestimation for first pass 
                baser = baser - (self.baseline_underestimate/100.0)*abs(baser)*orient
                basei = basei - (self.baseline_underestimate/100.0)*abs(basei)*orient
                
            base = baser + 1j * basei  # Make complex array from real and imaginary parts

            chain.fit_baseline = base

