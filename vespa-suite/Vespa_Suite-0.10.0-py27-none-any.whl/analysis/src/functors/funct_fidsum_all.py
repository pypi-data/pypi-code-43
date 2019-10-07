# Python modules
from __future__ import division


# 3rd party modules
import numpy as np


# Our modules
import functor
#import functors.funct_coil_combine as funct_combine
import funct_coil_combine as funct_combine
import vespa.common.constants as common_constants
import vespa.common.minf_parabolic_info as minf
import vespa.common.util.ppm  as util_ppm
import vespa.common.util.generic_spectral as util_spectral

from vespa.common.constants import DEGREES_TO_RADIANS as DTOR



def funct_optimize_phase0(rad, info):
    """
    Optimization function used optimize the zero order phase for FIDs
    in a FidSum dataset. Each FID is compared to the sum of all FIDs.
    A least squared difference is calculated for a phase 0 value that
    best matches the FID to the reference absorption spectrum.
    
    INPUT:
        rad:  current phase in radians
        info: control structure, see optimize_phase0 for definition
    
    """
    phase = np.exp(1j*rad)
    dat   = info['dat'].copy() * phase
    
    istr = info['pts'][0]
    iend = info['pts'][1]
    datt = dat[istr:iend].copy()
    reff = info['ref'][istr:iend].copy()  

    diff = np.sum((datt.real - reff.real)**2)    
#    print diff    
    
    return  diff       
   
   
def optimize_phase0(data, modfn, pts):
    """
    Returns the zero order phase in deg at which the least squares
    difference between the data and modfn  absorption spectra are 
    minimized
    
    INPUT:
     data:  array of complex data to be phased
     modfn: string array of model function to be used (obsolete)
     pts:   list, start and end point region used for leastsqr calculation
    
    """
    info = {'dat'     : data,  
            'ref'     : modfn,
            'pts'     : pts     }
    
    # Parabolic interpolation, Brent's method 1-d minimization routine
    
    phase_a = -1*np.pi   # lower bound
    phase_b = np.pi*0.1  # "some" point in the middle
    phase_c =  2*np.pi   # upper bound
    
    phaseat, maxit = minf.minf_parabolic_info( phase_a, phase_b, phase_c,
                                               funct_optimize_phase0, info)
    phdeg = phaseat*180.0/np.pi
    if phdeg > 180.0:
        phdeg = phdeg - 360.0
    
    return phdeg   


def do_processing_all(chain):
    """
    Because we are bumping the zero fill factor here by a factor of 4 to 
    better find the peak max, we can not use the standard util_ppm 
    functions to calculate some conversions.  So long hand here for us.
    
    """
    block   = chain._block
    set     = chain._block.set
    dataset = chain._dataset
    
    #------------------------------------------------------
    # Global inits and one time calculations
    
    zfmult = 4      # larger zfmult here improves peak shift accuracy
    raw_dim0 = dataset.raw_dims[0]
    raw_hpp  = dataset.sw / raw_dim0
    fid_dim0 = raw_dim0 * zfmult
    fid_hpp  = dataset.sw / fid_dim0
    
    # reset results arrays and temporary arrays
    chain.time_summed = np.zeros((raw_dim0),complex)
    chain.freq_summed = np.zeros((raw_dim0),complex)
    xx = np.arange(raw_dim0) / dataset.sw
    search = np.zeros((raw_dim0 * zfmult),complex)

    # convert algorithm values from PPM to points
    search_start = set.reference_peak_center + set.peak_search_width
    search_end   = set.reference_peak_center - set.peak_search_width
    refpt        = (fid_dim0 / 2) - (dataset.frequency * (set.reference_peak_center - dataset.resppm) / fid_hpp)
    search_start = int((fid_dim0 / 2) - (dataset.frequency * (search_start - dataset.resppm) / fid_hpp))
    search_end   = int((fid_dim0 / 2) - (dataset.frequency * (search_end - dataset.resppm) / fid_hpp))
    
    ph0_start    = set.phase0_range_start
    ph0_end      = set.phase0_range_end
    ph0_start    = int((raw_dim0 / 2) - (dataset.frequency * (ph0_start - dataset.resppm) / raw_hpp))
    ph0_end      = int((raw_dim0 / 2) - (dataset.frequency * (ph0_end   - dataset.resppm) / raw_hpp))

    # one time calculations        
    apod = util_spectral.apodize(xx, set.gaussian_apodization, 'Gaussian')
    chop  = ((((np.arange(raw_dim0) + 1) % 2) * 2) - 1)
    apod *= chop

    nfids = chain.raw.shape[2]
    
    if set.apply_data_exclusion:
        nfids_excluded = nfids - len(block.exclude_indices)
    else:
        nfids_excluded = nfids

    #--------------------------------------------------------------------------
    # Coil combination section
    #
    # - do not combine if only 1 coil, no need

    if chain.raw.shape[1] > 1:      # number of coils

        if set.coil_combine_method=='Siemens':
            raw_combined, weights, phases = funct_combine.coil_combine_siemens(chain)
        elif set.coil_combine_method=='CMRR':
            raw_combined, weights, phases = funct_combine.coil_combine_cmrr(chain)
        elif set.coil_combine_method=='CMRR-Sequential':
            raw_combined, weights, phases = funct_combine.coil_combine_cmrr_sequential(chain)
        elif set.coil_combine_method=='CMRR-Hybrid':
            raw_combined1, weights1, phases1 = funct_combine.coil_combine_siemens(chain)
            raw_combined2, weights2, phases2 = funct_combine.coil_combine_cmrr(chain)
            
            phases1 = np.angle(np.sum(phases1, axis=0), deg=True)
            phases2 = np.angle(np.sum(phases2, axis=0), deg=True)

            a    = phases2 - phases1 
            vals = (a + 180) % 360 - 180
            delta = np.mean(vals) * np.pi / 180.0
#            print 'cmmr-hybrid delta = ', delta

            raw_combined3, weights3, phases3 = funct_combine.coil_combine_cmrr(chain, delta=delta)
            
            raw_combined = raw_combined3
            weights = weights3
            phases  = phases3 
            
        elif set.coil_combine_method=='External Dataset':
            raw_combined, weights, phases = funct_combine.coil_combine_external_dataset(chain)

        elif set.coil_combine_method=='External Dataset with Offset':
            raw_combined1, weights1, phases10 = funct_combine.coil_combine_external_dataset(chain)
            raw_combined2, weights2, phases20 = funct_combine.coil_combine_siemens(chain)
            
            phases1 = np.angle(np.sum(phases10, axis=0), deg=True)
            phases2 = np.angle(np.sum(phases20, axis=0), deg=True)
            
            # these two lines find the minimum angle between the two methods,
            # note that depending on lead/lag and whether the angles span the
            # dislocation at 0/359 degrees.
            a = phases1 - phases2
            vals = (a + 180) % 360 - 180
            
            # get rid of outliers if we have enough coils to do so
            # - this keeps a few wrong numbers from skewing the mean offset
            ncoil = len(vals)
            if   ncoil >= 32: nout = 4
            elif ncoil >= 8:  nout = 2
            else: nout = 0
            
            if nout:
                cmean  = np.mean(vals)
                cdiff  = np.abs(cmean - vals)
                for n in range(nout):
                    indx = np.argmax(cdiff)
                    cdiff = np.delete(cdiff, indx)
                    vals  = np.delete(vals,  indx)
            
            # then we take the mean value and use it as the overall offset
            delta = np.mean(vals)
#            print 'External Dataset-hybrid delta = ', delta
            delta = delta * np.pi / 180.0

            raw_combined3, weights3, phases3 = funct_combine.coil_combine_external_dataset(chain, delta=-delta)
            
            raw_combined = raw_combined3
            weights = weights3
            phases  = phases3 
    
    else:
        # single coil, copy first channel only
        raw_combined = funct_combine.coil_combine_none(chain) 
        weights = None
        phases  = None   

    chain.coil_combine_weights = weights
    chain.coil_combine_phases  = phases   
     
    #--------------------------------------------------------------------------
    # FID correction and combination section
    #
    # - this first loop creates a baseline 'time_summed' and 'freq_current'
    #   result whether B0 shift method is on or not
    # - these results have the previous or updated B0 and Ph0 values applied
    # - the second loop, if active' has an up to date chain.time_summed array
    #   to use in its algorithm.
    # - in both loops, if data exclude is on, then data is excluded if index
    #   is in the exclusion list.

    for i in range(nfids):
        
        time = raw_combined[0,0,i,:].copy()
        
        if set.fid_left_shift != 0:
            # shift fid to the left and set last points to zero
            time = np.roll(time, -set.fid_left_shift) 
            time[-set.fid_left_shift:] = time[0]*0.0  
        
        if set.apply_peak_shift and chain.calculate_flag:
            # Calculate peaks shift if flag set, use oversized zfmult
            # Peak search is performed over user-set range on magnitude data
            search *= 0.0
            search[0:raw_dim0] = time * apod
            search = np.fft.fft(search) 
            temp   = np.abs(search)
            imax = temp[search_start:search_end].argmax()
            delta = (refpt-(search_start+imax))*fid_hpp
            block.frequency_shift[i] = delta
        
        # Phase 0 NOT calculated here because reference peak has to be 
        # calculated from summed peak-shifted data

        # Apply freq shift and phase0 corrections to the time data
        time *= np.exp(1j * 2.0 * np.pi * block.frequency_shift[i] * xx)
        time *= np.exp(1j * block.phase_0[i] * common_constants.DEGREES_TO_RADIANS)
        
        # Sum up FIDs for display, and calculate current voxel if needed
        
        if set.apply_data_exclusion:
            if i not in block.exclude_indices:
                chain.time_summed += time
        else:
            chain.time_summed += time
            
        if i == chain.voxel:
            tmp = time.copy()
            tmp[0] *= 0.5
            chain.freq_current = (np.fft.fft(tmp * apod) / len(chain.freq_summed))
            # match signal height using the SNR averaging factor 
            # note. we are not matching noise here, just the signals
            chain.freq_current *= nfids_excluded 

    
    # Calculate Phase0 optimization if flag set ON in widget. We need 
    # to do this in a second loop, since we need the peaks shifted before 
    # we create a reference spectrum from the summed FIDs
    
    if set.apply_phase0 and chain.calculate_flag:
        # create reference spectrum and optimize range from CURENT time_summed array
        freq_summed     = chain.time_summed.copy() * apod
        freq_summed[0] *= 0.5
        freq_summed     = (np.fft.fft(freq_summed) / len(freq_summed))
        freq_summed    /= nfids       # scale for comparison to single FID (not nfids_excluded here)
        ph0range        = [ph0_start, ph0_end]
        
        # reset global variable so as to fill in below with new ph0 values
        chain.time_summed *= 0  
        
        for i in range(nfids):

            # time = chain.raw[0,0,i,:].copy()
            time = raw_combined[0,0,i,:].copy()

            if set.fid_left_shift != 0:
                # shift fid to the left and set last points to zero
                time = np.roll(time, -set.fid_left_shift) 
                time[-set.fid_left_shift:] = time[0]*0.0  
            
            time *= np.exp(1j * 2.0 * np.pi * block.frequency_shift[i] * xx)                
            
            # this is where phase 0 is optimized ...
            tmp = time.copy()
            tmp[0] *= 0.5
            tmp_freq = (np.fft.fft(tmp * apod) / len(tmp))
            phdeg = optimize_phase0(tmp_freq, freq_summed, ph0range)
            block.phase_0[i] = phdeg
            
            time *= np.exp(1j * block.phase_0[i] * common_constants.DEGREES_TO_RADIANS)
            
            if set.apply_data_exclusion:
                if i not in block.exclude_indices:
                    chain.time_summed += time
            else:
                chain.time_summed += time
        
            if i == chain.voxel:
                tmp = time.copy()
                tmp[0] *= 0.5
                chain.freq_current = (np.fft.fft(tmp * apod) / len(chain.freq_summed))
                # match signal height using the SNR averaging factor 
                # note. we are not matching noise here, just the signals
                chain.freq_current *= nfids_excluded 

    if set.global_phase1 != 0.0:
        # move summed time result into frequency domain
        time_summed = chain.time_summed.copy()
        time_summed[0] *= 0.5
        time_summed  = np.fft.fft(time_summed * chop)
        
        # calc phase 1 
        piv    = np.round(util_ppm.ppm2pts(dataset.phase_1_pivot, dataset, acq=True))
        xx     = (np.arange(raw_dim0,dtype=float)-piv)/raw_dim0
        phase1 = np.exp(1j * (set.global_phase1 * DTOR * xx))
        
        # apply to spectral data and invert fourier transform
        time_summed *= phase1
        time_summed = np.fft.ifft(time_summed)
        chain.time_summed = time_summed * chop

        
    chain.freq_summed  = chain.time_summed.copy() * apod
    chain.freq_summed[0] *= 0.5
    chain.freq_summed  = (np.fft.fft(chain.freq_summed) / len(chain.freq_summed))
    


