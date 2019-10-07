# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.common.pulse_funcs.linear_setup as LS
import vespa.common.pulse_funcs.min_max_setup as MMS


def transition_band(npoints, resolution, dwell_time, duration, tip_angle, pass_ripple, reject_ripple, ptype, bandwidth, 
                            is_single_band=True, separation=0.0, n_zero_pad=0, bandwidth_convention=0):
    '''Calculates transition band ("transb") in kHz'''
    
    # Adapted from Matlab: MPLTBNDC.M

    if n_zero_pad > 0:
        # Reduced for z-padding
        nofp = npoints - 2*n_zero_pad
    else:
        nofp = npoints


    if ptype == 1:
        # Linear (or refocused) pulse
        [mplfr, mplmag, mplwts, mplcrrctf] = LS.linear_setup(nofp, dwell_time, tip_angle, pass_ripple, \
                                                             reject_ripple, bandwidth, is_single_band, \
                                                             separation, bandwidth_convention)
    else:
        # Max or min phase
        mplfr, mplmag, mplwts, mplcrrctf = MMS.max_min_setup(nofp, dwell_time, tip_angle, pass_ripple, \
                                                             reject_ripple, bandwidth, is_single_band, \
                                                             separation, bandwidth_convention)
        
    # e.g. mpltran = (mplfr[2]-mplfr[1]) * 1000/(2*dwell_time)
    mpltran = (mplfr[2]-mplfr[1])*1000/(2*dwell_time)

    # mpltrans = num2str(mpltran, 4)
    # the "4" implies maximum precision.
    # mpltrans = "{0}".format(mpltran) # have to wait until version 3.0 for this!
    mpltrans = "%.4f" %(mpltran)
    
    return mpltran
