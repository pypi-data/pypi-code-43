# Python modules
from __future__ import division


# 3rd party modules
import numpy as np
from scipy.stats import distributions


# Our modules
import functor
import constants
import util_voigt
import vespa.common.minf_parabolic_info as minf
import vespa.common.util.generic_spectral as util_spectral

from constants import FitLineshapeModel


class FunctVoigtConfidenceIntervals(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    fitting chain for frequency domain spectral MRS data.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)

        class _Anonymous(object):
            pass
        
        self.cinfo = _Anonymous()
        
        self.confidence_alpha = None 
        self.confidence_area_flag = None 
        self.confidence_ppm_flag = None 
        self.confidence_linewidth_flag = None 
        self.confidence_phase_flag = None 
        self.lineshape_model = None 
        
        self.attribs = ["confidence_alpha",
                        "confidence_area_flag",
                        "confidence_ppm_flag",
                        "confidence_linewidth_flag",
                        "confidence_phase_flag", 
                        "lineshape_model",
                       ]


    ##### Standard Methods and Properties #####################################
    
    def algorithm(self, chain):
        nmet    = chain.nmet
        dim0    = chain.spectral_dims[0]
        dat     = chain.data.copy() 
        a       = chain.fit_results
        bas     = chain.fit_baseline
        ww      = chain.weight_array
        lim     = chain.limits
        na      = np.size(a)

        chain.confidence = chain.confidence * 0     # init results array

        # Calculate T-distribution factor for the current alpha ---
        nfree  =  np.size(dat) - na
        alpha  =  1.0 - self.confidence_alpha

        factor = 1.0 + (1.0 * na / (dim0-na)) * distributions.f.ppf(1-alpha,na,dim0-na)

        func1 = _confidence_interval_function
        mets, _  = chain.fit_function(a, pderflg=False, nobase=True, indiv=True)

        # Prepare structure for passing to the confidence limit routine ---
        if nmet != 1:
            fit = np.sum(mets,axis=0) + bas
        else:
            fit = mets + bas

        if dat.dtype in ['complex64','complex128']:
            dat = np.concatenate([dat.real,dat.imag])
            fit = np.concatenate([fit.real,fit.imag])
            ww  = np.concatenate([ww.copy(),ww.copy()])
            
        wchi = np.sum(ww * (dat-fit)**2) / nfree
        
        indx = 0
        self.cinfo.indx     = 0
        self.cinfo.a        = a.copy()
        self.cinfo.dat      = dat
        self.cinfo.fit      = fit
        self.cinfo.bas      = bas
        self.cinfo.wchi     = wchi
        self.cinfo.ww       = ww
        self.cinfo.nfree    = nfree
        self.cinfo.factor   = factor
        self.cinfo.mets     = mets
        self.cinfo.data     = chain
        self.cinfo.fit_function = chain.fit_function

        # Now do conf limit search for all area params ---
        if self.confidence_area_flag:
            for i in range(nmet):
                self.cinfo.indx = i
                self.cinfo.a    = a.copy()

                xa = a[self.cinfo.indx] * 1.0
                xb = a[self.cinfo.indx] * 1.01
                xc = a[self.cinfo.indx] * 1.5    # reasonable limit for upper bound

                amphi, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                xa = a[self.cinfo.indx] * 0.999
                xb = a[self.cinfo.indx] * 0.99
                xc = a[self.cinfo.indx] * 0.5    # reasonable limit for lower bound

                amplo, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                # save the confidence interval as a percentage of the metabolite area
                chain.confidence[self.cinfo.indx] =  100.0 * (amphi - amplo) / a[i]

        if self.confidence_ppm_flag:
            for i in range(nmet):
                self.cinfo.indx = nmet + i

                frehi = a[self.cinfo.indx]     # use these if optimization hit a limit
                frelo = a[self.cinfo.indx]

                if a[self.cinfo.indx] > lim[0,self.cinfo.indx] and \
                   a[self.cinfo.indx] < lim[1,self.cinfo.indx]: 
                    xa = a[self.cinfo.indx] + 0.0
                    xb = a[self.cinfo.indx] + 1.0
                    xc = lim[1,self.cinfo.indx]     # reasonable limit for upper bound

                    #lower confidence limit calculation
                    frehi, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)
                    xa = a[self.cinfo.indx] - 0.01
                    xb = a[self.cinfo.indx] - 1.0
                    xc = lim[0,self.cinfo.indx]        # reasonable limit for lower bound

                    #lower confidence limit calculation
                    frelo, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                # save the confidence interval as it's width in PPM (tends to be tight)
                chain.confidence[self.cinfo.indx] =  (frehi - frelo) / chain.frequency

        if self.confidence_linewidth_flag: 
            # Voigt or Lorentzian 
            self.cinfo.indx = nmet*2 + 0

            tahi = a[self.cinfo.indx]    # use these if optimization hit a limit
            talo = a[self.cinfo.indx]

            if (self.lineshape_model == FitLineshapeModel.VOIGT or 
                self.lineshape_model == FitLineshapeModel.LORENTZ): 
                if a[self.cinfo.indx] > lim[0,self.cinfo.indx] and \
                   a[self.cinfo.indx] < lim[1,self.cinfo.indx]: 
                    xa = a[self.cinfo.indx] * 1.0
                    xb = a[self.cinfo.indx] + abs(a[self.cinfo.indx]) * 0.01
                    xc = lim[0,self.cinfo.indx]        # reasonable limit for upper bound

                    #lower confidence limit calculation
                    tahi, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                    xa = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.0001
                    xb = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.01
                    xc = lim[1,self.cinfo.indx]        # reasonable limit for lower bound

                    #lower confidence limit calculation
                    talo, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

            # Voigt or Gaussian
            self.cinfo.indx = nmet*2 + 1

            tbhi = a[self.cinfo.indx]    # use these if optimization hit a limit
            tblo = a[self.cinfo.indx]

            if (self.lineshape_model == FitLineshapeModel.VOIGT or 
                self.lineshape_model == FitLineshapeModel.GAUSS): 
                if a[self.cinfo.indx] > lim[0,self.cinfo.indx] and \
                   a[self.cinfo.indx] < lim[1,self.cinfo.indx]: 
                    xa = a[self.cinfo.indx] * 1.0
                    xb = a[self.cinfo.indx] + abs(a[self.cinfo.indx]) * 0.01
                    xc = lim[0,self.cinfo.indx]        # reasonable limit for upper bound

                    #lower confidence limit calculation
                    tbhi, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                    xa = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.0001
                    xb = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.01
                    xc = lim[1,self.cinfo.indx]        # reasonable limit for lower bound

                    #lower confidence limit calculation
                    tblo, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

            # calc what the max and min lw could be for given Ta and Tb values
            lwmax, _ = util_spectral.voigt_width(tahi, tbhi, chain)
            lwmin, _ = util_spectral.voigt_width(talo, tblo, chain)

            # save the confidence interval for max and min LW in Hz
            chain.confidence[nmet*2 + 0] = talo - tahi # lwmin
            chain.confidence[nmet*2 + 1] = tblo - tbhi # lwmax

        if self.confidence_phase_flag: 
            # Zero Order Phase
            self.cinfo.indx = nmet*2 + 2

            ph0hi = a[self.cinfo.indx]    # use these if optimization hit a limit
            ph0lo = a[self.cinfo.indx]

            if a[self.cinfo.indx] > lim[0,self.cinfo.indx] and \
               a[self.cinfo.indx] < lim[1,self.cinfo.indx]: 
                xa = a[self.cinfo.indx]
                xb = a[self.cinfo.indx] + abs(a[self.cinfo.indx]) * 0.01
                xc = lim[1,self.cinfo.indx]        # reasonable limit for upper bound

                #lower confidence limit calculation
                ph0hi, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                xa = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.0001
                xb = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.01
                xc = lim[0,self.cinfo.indx]        # reasonable limit for lower bound

                #lower confidence limit calculation
                ph0lo, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

            # save the confidence interval as it's width in Hz (tends to be tight)
            chain.confidence[self.cinfo.indx] =  (ph0hi - ph0lo) * 180. / np.pi    

            # Zero Order Phase
            self.cinfo.indx = nmet*2 + 3

            ph1hi = a[self.cinfo.indx]    # use these if optimization hit a limit
            ph1lo = a[self.cinfo.indx]

            if a[self.cinfo.indx] > lim[0,self.cinfo.indx] and \
               a[self.cinfo.indx] < lim[1,self.cinfo.indx]: 
                xa = a[self.cinfo.indx]
                xb = a[self.cinfo.indx] + abs(a[self.cinfo.indx]) * 0.01
                xc = lim[1,self.cinfo.indx]        # reasonable limit for upper bound

                #lower confidence limit calculation
                ph1hi, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

                xa = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.0001
                xb = a[self.cinfo.indx] - abs(a[self.cinfo.indx]) * 0.01
                xc = lim[0,self.cinfo.indx]        # reasonable limit for lower bound

                #lower confidence limit calculation
                ph1lo, _ = minf.minf_parabolic_info(xa, xb, xc, func1, self.cinfo, tol=1e-6)

            # save the confidence interval as it's width in Hz (tends to be tight)
            chain.confidence[self.cinfo.indx] =  (ph1hi - ph1lo) * 180. / np.pi
            chain.minmaxlw = [lwmin,lwmax]

        


def _confidence_interval_function(xq, cinfo):
    """ 
    calculation of the weighted chi squared to adjust the fitted array a
    """
    a = cinfo.a.copy()
    a[cinfo.indx] = xq

    yfit, _ = cinfo.fit_function(a, pderflg=False)
    if yfit.dtype in ['complex64','complex128']:
        yfit = np.concatenate([yfit.real,yfit.imag])
    wchisqr1 = np.sum(cinfo.ww*(yfit-cinfo.dat)**2)/cinfo.nfree
    
    goal = abs(wchisqr1-cinfo.wchi*cinfo.factor)
    
    return goal
      
 
