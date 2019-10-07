# Python Modules.
from __future__ import division
import math

# 3rd party stuff
import numpy as np
import scipy as sp

# Local imports
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.transition_band as TB
import vespa.common.pulse_funcs.linear_setup as LS
import vespa.common.pulse_funcs.min_max_setup as MMS
import vespa.common.pulse_funcs.linear_filter as FILTL
import vespa.common.pulse_funcs.min_max_filter as FILTM
import vespa.common.pulse_funcs.inverse_slr as INVSLR
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


def slr_pulse(npoints, resolution, dwell_time, duration, tip_angle, pass_ripple, reject_ripple, ptype, bandwidth, 
                              is_single_band=True, separation=0.0, use_remez=True, n_zero_pad=0, 
                              bandwidth_convention=0, usage_type="none", extended_profile=False):

    '''Adapted from Matpulse - mplcalcc.m: 
       Script for pulse generation.
       
       npoints - the number of data points in the output waveform
       resolution - the calculation resolution for frequency domain computations.
       dwell_time - the spacing between points in microseconds.
       tip_angle - the desired tip angle, in radians
       pass_ripple - the desired pass band ripple, as a percent
       reject_ripple - the desired reject band ripple, as a percent
       ptype - the non-coalesced phase type:
           1 for linear
           2 for Max
           3 for Min
       bandwidth - the bandwidth for the pulse in kilohertz
       is_single_band - (True or False) True for single band; False for dual band.
       separation - the separation between the bands in kilohertz
       use_remez - (True or False) 
          True, specifies the use of the remez filter
          False, specifies the use of least-squares filter
       n_zero_pad - the number of points of zero padding at the beginning and end of the pulse
       bandwidth_convention:
           0 for "conventional" (default, FWHM)
           1 for spectroscopy convention (MINIMUM)
           2 for filter convention (MAXIMUM)
       usage_type - Used to specify the slr frequency profile type.
           A profile will be generated for the values listed below:
           excite, inversion, saturation, spinecho
       extended_profile - if True, an extended profile will be generated for looking further
                         out in the frequency domain - past the Nyquist frequency..
       
       slr_pulse returns a tuple of 3 items: 
       waveform, waveform_x_axis, slr_profiles
       These are defined below:
          waveform is the amplitude of the rf_pulse.
          waveform_x_axis is an array - the same size as waveform - and contains the corresponding x axis points.
          slr_profiles is a dictionary containing the SLR frequency_profile, frequecy_profile_x_axis
             and the frequency_profile_type and possibly their extended version cousins.
             Note: These are not the Bloch equation generated profiles. 
             The profile_type contains a variable of type pulse_funcs.constants.ProfileType.
             
       May raise (or throw) PulseFuncException
       
       See the following articles:
       
       J. Pauly, P. Le Roux, D. Nishimura, A. Macovski, 
       'Parmater Relations for the Shinnar-Le Roux Selective Excitation Pulse Design Algorithm',
       IEEE Transactions on Medical Imaging, Vol. 10, No. 1, pp 53-65, March 1991.
       
       G.B. Matson, 'An Integrated Program for Amplitude-Modulated RF Pulse Generation  
       andRe-mapping with Shaped Gradients', Magnetic Resonace Imaging, 
       Vol. 12, No. 8, pp 1205-1225, 1994'''

    # FIXME: Review how timepoints are handled in matlab vs rfpulse vs how they should be handled.


    # Check for excessive bandwidth
    if is_single_band == True:
        mplttbw = bandwidth
    else:        
        # Separation/2 + bandwidth.
        mplttbw = separation/2 + bandwidth
    
    if (0.8 * mplttbw) > (1000.0 / dwell_time) :
        error_message = 'Error: Excessive pulse bandwidth'
        raise pulse_func_exception.PulseFuncException(error_message, 1)

    # :FIXME: Check that resol is even (Do I still need this?)
    # resolution = 2 * int(np.ceil( resolution/2.0 ))
    
    mpltran = 0
    mpltran = TB.transition_band(npoints, resolution, dwell_time, duration, tip_angle, 
                                 pass_ripple, reject_ripple, ptype, bandwidth, is_single_band, 
                                 separation, n_zero_pad, bandwidth_convention)

    # Pulse Setup, starting with initial length (for z-padding)
    if n_zero_pad > 0:
        # Reduced for z-padding
        # nofp - local variable, number of points.
        nofp = npoints - 2 * n_zero_pad
    else:
        nofp = npoints
        
    
    if ptype == 1:
        
        # Refocussed or Linear pulse
        #
        # Input values: 
        #    nofp - number of points.
        #    dwell_time - dwell time in microseconds
        #    pass_ripple - bandpass ripple
        #    tip_angle - in radians        
        #    reject_ripple - bandreject ripple
        #    bandwidth - in kHz        
        #    is_single_band - band type; single or dual.        
        #    separation - in kHz
        #    bandwidth_convention

        mplfr, mplmag, mplwts, mplcrrctf = LS.linear_setup(nofp, dwell_time, tip_angle, pass_ripple, \
                                                           reject_ripple, bandwidth, is_single_band, \
                                                           separation, bandwidth_convention)
    else: 
        
        # Max or min phase
        mplfr, mplmag, mplwts, mplcrrctf = MMS.max_min_setup(nofp, dwell_time, tip_angle, pass_ripple, \
                                                            reject_ripple, bandwidth, is_single_band, \
                                                            separation, bandwidth_convention) 

    # Converted and Modified Code:
    # Jerry and I (DCT) agree that second if would never be executed,
    # Since the function would return first... Also, the second
    # block of code accesses an element of the array that does not
    # exist for a single band and only for a dual band.   
    # if is_single_band == True:      # Single band pulse
    #    if mplfr[1] < 0.0001:
    #        pf_constants.mplemtxt = 'Error: Inadequate bandwidth'
    #       return
    # elif is_single_band == False:      # Dual band pulse
    #    if mplfr[4] > 1:
    #        pf_constants.mplemtxt = 'Error: excessive bandwidth'
    #        return

            
    # NEW CODE ADDED... 
    # ...to test for monotonicity and for values between zero and one.
    #
    # Specific Bandwidth Tests - per Jerry Matson
    if bandwidth_convention == 0: 
        # default bandwidth convention (width at mid height)
        if is_single_band == True:
            if mplfr[1] < 0.0:
                error_message = 'Bandwidth Error: Increase Bandwidth or Increase Time for Pulse'
                raise pulse_func_exception.PulseFuncException(error_message, 1)
            if mplfr[2] > 1.0:
                error_message = 'Bandwidth Error: Decrease Bandwidth or Increase Time for Pulse'
                raise pulse_func_exception.PulseFuncException(error_message, 1)      
        else:    # if dual band
            if mplfr[1] < 0.0:
                error_message = 'Bandwidth Error: Decrease Bandwidth or Increase Time for Pulse'
                raise pulse_func_exception.PulseFuncException(error_message, 1)            
            if mplfr[4] > 1.0:
                error_message = 'Bandwidth Error: Decrease Bandwidth or Increase Time for Pulse'
                raise pulse_func_exception.PulseFuncException(error_message, 1)                
    elif bandwidth_convention == 1:  
        # specroscopic bandwidth convention (width at base of pulse)
        
        # :FIXME: implement this ... and the one just below it.
        raise NotImplementedError('Oops, forgot this case')        
    else:
        # filter bandwidth convention (width at top of pulse)
        raise NotImplementedError('Oops, forgot this case')   
    

    # General Check
    xold = 0.0
    for x in mplfr:
        if x < xold or x > 1.0:
            error_message = 'Values in fr need to be monotonic increasing, and between 0 and 1'
            raise pulse_func_exception.PulseFuncException(error_message, 1)
        else:
            xold = x        
            
    # Calculate the expansion factor
    expansion_factor = 1/(2*mplfr[2])
    if is_single_band == False:
        # Dual band pulse
        expansion_factor = 1/(2*mplfr[4])

    # Guarantee that expansion_factor >= 1 
    if expansion_factor < 1.:
        expansion_factor = 1


    # Calculate polynomials:
    if ptype == 1:    # Linear pulse
        # mplfr - pass and stop
        # mplmag - magnetization
        # mplwts - weights        
        # :FIXME: Doesn't the next call need to know whether this is single band or not?
        mpgbb, mpgaa, mplw = FILTL.linear_filter(mplfr, mplmag, mplwts, nofp, \
                                                 use_remez, resolution)
    else:
        # Note: The reason min_max_filter gets passed the "is_single_band" flag and 
        # the linear_filter does not is that min_max_filter does some pre-calculation
        # adjustments to try to reduce or eliminate the dc offset in the reject band or
        # region. This step is not done in the linear filter case.
        mpgbb, mpgaa, mplw = FILTM.max_min_filter(mplfr, mplmag, mplwts, nofp, \
                                                  use_remez, resolution, is_single_band)
      

    # Calculatel b1:
    # nofp - number of points.
    # dwell_time - dwell time in micro seconds.
    # mmgaa and mmgbb - returned from linear_filter or max_min_filter above.
    mpgb1 = INVSLR.inverse_slr(nofp, dwell_time, mpgaa, mpgbb)

    # mplcrrctf returned from setup routines above.
    if mplcrrctf != 0:
        mpgb1 = mplcrrctf * mpgb1

    # Add zero padding if asked for:
    if n_zero_pad > 0:
        mpgb1 = np.hstack([np.zeros(n_zero_pad), mpgb1, np.zeros(n_zero_pad)])

    # Reverse for max phase pulse
    if ptype == 2:
        # Max phase pulse    
        mpgb1 = mpgb1[::-1]

    waveform = mpgb1
    
    temparr = []
    pulse_time = duration/1000.0
    for ix in range(npoints):
        temparr.append(ix*pulse_time/(npoints))    
    
    waveform_x_axis = temparr


    # create empty dictionary that would hold 
    # output of next section (if requested)
    slr_profiles = {}

    if usage_type == "excite":     # Plot Mxy (Excite)
                
        # Declare local variables
        h = mpgbb  
        a = mpgaa 
        na = npoints
        
        nq = 1000.0/(2.0*dwell_time)

        # Rearrange h and a for plotting
        # Convert to row vectors
        h = h.conj().transpose()
        a = a.conj().transpose()
        l = h.size
        
        ld2 = int(math.floor(l/2))
        
        hn = np.hstack( (h[ld2:l], h[0:ld2]) )
        an = np.hstack( (a[ld2:l], a[0:ld2]) )
        acon = an.conj()
 
        fl = float(l)
        step = 2.0/fl
        wn = np.arange(-1.0, 1.0, step)   
        
        ax = wn * nq        
        profil = (acon * hn) * 2

        slr_profiles["frequency_profile"]        = profil
        slr_profiles["frequency_profile_x_axis"] = ax
        slr_profiles["frequency_profile_type"]   = pf_constants.ProfileType.M_XY

        
        if extended_profile == True:
            le = math.ceil(l/expansion_factor) 
            # Ensure le even
            le = 2 * int(math.ceil(le/2))   
            
            hnp = hn[ (l-le)/2 : (l+le)/2 ]        
            anp = acon[ (l-le)/2 : (l+le)/2 ]
              
            fl = float(l)
            step = 2/fl
            wn = np.arange(-le/fl, (le-1)/fl, step)
            
            ex_ax = wn*nq
            ex_profil = (anp*hnp)*2
            
            slr_profiles["extended_frequency_profile"] = ex_profil
            slr_profiles["extended_frequency_profile_x_axis"] = ex_ax
            slr_profiles["extended_frequency_profile_type"]   = pf_constants.ProfileType.M_XY

    elif usage_type == "spinecho":     # Spin echo (SE) pulse

        # ::FIXME:: GET CODE for mplsepro FROM MATPULSE
        # See vespa/rfpulse/resources/legacy_matpulse/mplsepro.py
        # function mplsepro(expansion_factor, mplpcde)

        slr_profiles["frequency_profile"]        = np.zeros(npoints)
        slr_profiles["frequency_profile_x_axis"] = np.zeros(npoints)
        slr_profiles["frequency_profile_type"]   = pf_constants.ProfileType.M_X_MINUS_Y        
        
        if extended_profile == True:
            slr_profiles["extended_frequency_profile"]        = np.zeros(npoints)
            slr_profiles["extended_frequency_profile_x_axis"] = np.zeros(npoints)
            slr_profiles["extended_frequency_profile_type"]   = pf_constants.ProfileType.M_X_MINUS_Y  

    elif usage_type=="inversion" or usage_type=="saturation":     
        
        # Inv/Sat plots, Plot Mz

        # Code from MPLZIPRO.M

        nq = 1000.0/(2.0*dwell_time)

        # Initialize plot code constants and decode pcde

        # Rearrange h for plotting
        h = mpgbb.conj().T
        l = h.size

        nslice = int(math.floor(l/2))
        hn = np.hstack( [ h[nslice:l], h[0:nslice] ] ) 

        step = 2.0/float(l)
        wn = np.arange(-1.0, 1.0, step)
        
        ax = nq * wn
        profil = ( 1 - 2*(hn*hn.conj()) ) 
        
        slr_profiles["frequency_profile_x_axis"] = ax     
        
        slr_profiles["frequency_profile"]        = profil    
        slr_profiles["frequency_profile_type"]   = pf_constants.ProfileType.M_Z
        
        if usage_type == "saturation":
            slr_profiles["frequency_profile"]        = -1*profil
            slr_profiles["frequency_profile_type"]   = pf_constants.ProfileType.M_MINUS_Z
        
        if extended_profile == True:
        
            le = math.ceil(float(l)/expansion_factor)
            le = int(2*math.ceil(le/2))  # Ensure le even        
            
            aa = (l-le)/2
            bb = (l+le)/2
            hnp = hn[ aa : bb ]
            
            fl = float(l)
            step = 2/fl
            wn = np.arange(-le/fl, (le-1)/fl, step)
           
            ex_ax = nq * wn
            ex_profil = 1 - 2*(hnp*hnp.conj())

            slr_profiles["extended_frequency_profile_x_axis"] = ex_ax  
                
            slr_profiles["extended_frequency_profile"]      = ex_profil      
            slr_profiles["extended_frequency_profile_type"] = pf_constants.ProfileType.M_Z
            if usage_type == "saturation":
                slr_profiles["extended_frequency_profile"]      = -1*ex_profil                      
                slr_profiles["extended_frequency_profile_type"] = pf_constants.ProfileType.M_MINUS_Z         

    return (waveform, waveform_x_axis, slr_profiles)

