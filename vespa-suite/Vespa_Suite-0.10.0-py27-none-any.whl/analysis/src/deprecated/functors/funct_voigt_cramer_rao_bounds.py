# Python modules
from __future__ import division


# 3rd party modules
import numpy as np

# Our modules
import functor
import util_voigt
import vespa.common.util.ppm as util_ppm

from constants  import FitMacromoleculeMethod


class FunctVoigtCramerRaoBounds(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    fitting chain for frequency domain spectral MRS data.
    
    """
    
    def __init__(self):
        functor.Functor.__init__(self)
       
        self.cramer_rao_ppm_start = None
        self.cramer_rao_ppm_end = None
        self.optimize_scaling_flag = None
        
        
        self.attribs = ["cramer_rao_ppm_start",
                        "cramer_rao_ppm_end",
                        "optimize_scaling_flag",
                       ]
        
        

    ##### Standard Methods and Properties #####################################
    
    def algorithm(self, chain):
        nmet    = chain.nmet
        dim0    = chain.spectral_dims[0]
        dat     = chain.data.copy() 
        a       = chain.fit_results
        bas     = chain.fit_baseline

        # FIXME-bjs maybe use chain.nparam here?

        nparam = nmet*2+4
        if chain.macromol_model == FitMacromoleculeMethod.SINGLE_BASIS_DATASET:
            nparam += 2 

        # Pick fraction of points starting from right edge of spectrum
        # for estimating variance

        nstr = round(util_ppm.ppm2pts(self.cramer_rao_ppm_end, chain))
        nstr = int(np.where(nstr > 0, nstr, 0))
        nend = round(long(util_ppm.ppm2pts(self.cramer_rao_ppm_start, chain)))
        nend = int(np.where(nend < dim0-1, nend, dim0-1))

        if nstr > nend: 
            nstr, nend = nend, nstr     # swap

        # Subtract calculated baseline from data to start residual calculation 
        resid = dat-bas
        b = a.copy()

        # we scale the area parameters here to try to keep the PDER array well
        # behaved, but we also have to scale the residual below if we do this
        savscal = self.optimize_scaling_flag
        self.optimize_scaling_flag = True
        b, pscale, _, _, _ = util_voigt.parameter_scale(nmet, b)

        # Cramer-Rao calcs here for this voxel - stored in fitt_data.cramer_rao 
        # First dimension organized as follows:
        #     areas (for N metabs), freqs (xN) , Ta, Tb, Ph0, Ph1
        yfit, _ = chain.fit_function(a, pderflg=False, nobase=True)
        _, pder = chain.fit_function(b, nobase=True)

        # Finish residual calculation and calculate variance ---
        resid = (resid - yfit) / pscale[0]
        section = resid[nstr:(nend+1)] 
        vari  = np.std(np.concatenate((section.real,section.imag)))
        #vari  = np.std(np.concatenate((resid[nstr:nend+1],resid[dim0+nstr:dim0+nend+1])))
        vari  = vari*vari

        """
         NB. pder returns a fltarr(dim0*2,nparam), the dim0*2 is because the
               representation of complex numbers in the VeSPA program is to
               append the imag portion to the real portion in one long fltarr

         We are estimating the Fisher information matrix here using the covariance
          matrix calculated from the partial derivs of the non-linear optimization

         NB. the complex calculation: invert(float((conj(transpose(pderc))#pderc)))
             is equivalent to the 'pseudo-complex (double length real matrix)'
             calculation: invert((transpose(pder)#pder))
        """

        # here we are using only the real part of the PDER array as per Bolan 
        try:
            tmp = np.dot(pder[0:dim0,:].real, pder[0:dim0,:].real.transpose())
            cr = np.linalg.inv(tmp)

            # If Cramer-Rao is not singular take the sqrt of the diagonal
            # elements of CR times the estimated variance as CR bounds    
            crdiag = np.sqrt(vari*cr.diagonal())

            crdiag, _, _, _ = util_voigt.parameter_unscale(nmet, crdiag, pscale)

#            print 'cr   = ', cr.diagonal()
#            print 'vari = ', vari
#            print 'crdi = ', crdiag * 100 / a

            crdiag[0:nmet]      = crdiag[0:nmet] * 100.0 / a[0:nmet]  # % change in area
            crdiag[nmet:nmet*2] = crdiag[nmet:nmet*2]/chain.frequency # delta Hz to delta PPM
            crdiag[nmet*2+2]    = crdiag[nmet*2+2] * 180.0 / np.pi  # radians to deg
            chain.cramer_rao = crdiag

            # this algorithm is based on the example shown in Bolan, MRM 50:1134-1143 (2003)
            # the factor of 2 here is used since we fit the complex data rather than
            # just the real data.

        except np.linalg.LinAlgError:    
            # If Cramer-Rao array is singular or contains a small
            # pivot return zero's for CR bounds
            chain.cramer_rao = np.zeros(nparam, float)    
 
