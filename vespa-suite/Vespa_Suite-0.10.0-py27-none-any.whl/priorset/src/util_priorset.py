# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.common.util.ppm as util_ppm
import vespa.common.util.math_ as util_math
import vespa.common.wx_gravy.common_dialogs as common_dialogs


def make_prior_basis(amp0, fre0, pha0, priorset=None):
    """
    Sums all the ASCII lines for a given metabolite into a complex FID at the
    resolution of the current values for the data in the FINFO structure.
    Outputs a complex array containing an FID represetation of the summed lines 
    of the metabolite, created according to the SW, AcqPts, etc values currently in
    the FINFO structure.

    """
    sw = priorset.sw
    dim0 = priorset.dims[0]
    resppm = priorset.resppm
    frequency = priorset.frequency
    
    td   = 1.0 / sw
    hpp  = sw / dim0
    arr1 = np.zeros(dim0) + 1.0
    fre  = util_ppm.ppm2hz(fre0, priorset) * 2.0 * np.pi
    pha  = pha0 * np.pi / 180.0
    npk  = np.size(fre0)
    xx   = (np.arange(dim0*npk).reshape(npk,dim0) % dim0) * td
    
    am   = np.outer(amp0,arr1)
    fr   = np.outer(fre,arr1)
    ph   = np.outer(pha,arr1)
    
    val1 = 1j * fr * xx
    val2 = 1j * ph
    tmp  = am * np.exp(val1) * np.exp(val2)
    
    #if np.rank(tmp) > 1: 
    if np.ndim(tmp) > 1: 
        tmp = np.sum(tmp, axis=0)

    return tmp
    


def generic_spectrum(amp0, fre0, pha0,  ta=0.07, 
                                        tb=0.07,
                                        priorset=None):
    """
    Creates a spectrum from input parameters

    """
    sw = priorset.sw
    dim0 = priorset.dims[0]
    resppm = priorset.resppm
    frequency = priorset.frequency
    
    basis = make_prior_basis(amp0, fre0, pha0, priorset=priorset)
    
    # Create Lineshape ---
    td = 1.0 / sw
    off = dim0 * 0 / td  # replace 0 with echopk, if necessary
    xx = np.arange(dim0) * td
    xxx = abs(xx-off)
    
    decay = xx/ta + (xxx/tb)**2
    lshape = util_math.safe_exp(-decay)
    
    # Create Spectrum with FFT and LineShape ---
    tmp = np.zeros(dim0, complex)
    tmp[0:dim0] = basis * lshape
    
    return tmp

