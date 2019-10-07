# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Vespa modules
import vespa.common.pulse_funcs.constants as pf_constants

# Rescaling code: From Matpulse, MFLCALCC.M
# Translated to Python

# Still working on function signature...
#
# :FIXME: We should consider passing in a flag 
# e.g. do_total_rotation and if True due the first bit
# and if False do the second. But not sure if that is
# the exact logic...
# 
# Regarding this fixme: I asked Jerry (on 04/19/11), and he 
# suggested instead that we use a different algorithm to see 
# if we should use total rotation or net rotation... e.g. by 
# looking at the avg. phase over the pulse and then look at the 
# maximum deviation from that average. If it is greater than
# 3% then we should use total rotation. Jerry defined phase
# like this: 
# phase = angle(|b1(real)| + i*|b1(imag)|)
# Note: we should also return a flag to indicate which type
# of rotation we performed (total or net).

def rescale(b1b2, angle, dwell_time):
       
    eps = pf_constants.EPS
    if np.max(np.abs(np.imag(b1b2))) > 10000*eps:
        # If there is any significant imaginary component    
        scale_factor = angle/((pf_constants.GAMMA1H) * \
                       (dwell_time/1000)*np.sum(np.abs(b1b2))*360)
    else:
        # Only real, i.e. not significant imaginary component
        scale_factor = angle/((pf_constants.GAMMA1H) * \
                        (dwell_time/1000)*np.sum(b1b2)*360)
    
    return b1b2 * scale_factor
    
        

