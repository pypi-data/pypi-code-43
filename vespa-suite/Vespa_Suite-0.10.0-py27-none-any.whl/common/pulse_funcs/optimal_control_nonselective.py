# Python Modules.
from __future__ import division
import math
import cmath
import time

# 3rd party stuff
import numpy as np

# Our modules
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception
import vespa.common.pulse_funcs.optimal_control_nonselective_step as ocn_step
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.constants as constants
import vespa.common.util.config as util_config

# When _DEBUG is True, this code prints out a bunch of stuff only a developer
# would want.
_DEBUG = False

# _HEADS_UP_ITERATIONS is the number of iterations at which this code 
# checks to see if any of the suspend criteria (other than # of iterations)
# have been met. 100 is somewhat abritrary, but David said, "checking every 
# 100 iterations was what [Jerry] found empirically to be very reasonable, 
# regarding the errors and how they change". 
_HEADS_UP_ITERATIONS = 100

# We create a slightly more readable alias for the current time
now = time.time


class OCNParams(object):
    def __init__(self):

        # Note that in practice these defaults don't get used. See 
        # OCNParameterDefaults in rfp_optimal_control_nonselective.py.
        self.pdwell = 10.0
        self.pulselength = 8.0
        self.pulspts = 250
        self.tip = 90.0
        self.dectol = 1.0e-004
        self.passband = 1.0            # Excitation band (PB)
        self.bmax = 25                 # Max B1
        self.steps = 5                 # B1 immunity steps
        self.pbparm = 41               # Passband points
        self.brange = 20               # Range of B1 immunity
        self.pulse_type = constants.UsageType.EXCITE
        
        self.initial_calculation = False
        
        self.phase_type = constants.PhaseType.NON_COALESCED
        self.linfact = 0.5
         
        self.halt_max_iterations = True
        self.max_iterations = 64
        
        self.halt_residual_error = False
        self.residual_error_tolerance = 0.2
        
        self.halt_differential_error = False
        self.differential_error_tolerance = 1.0e-004
        
        self.halt_increasing_error = False
        
        self.halt_max_time = False
        # max_time is in seconds although we ask the user to express the time
        # in minutes because this code can't offer single second granularity.
        # 300 seconds is 5 minutes.
        self.max_time = 300
        
        self.limit_sar = False
        self.sar_factor = 0.5       

        # Step size options are Average, Fixed, and Compute.
        # average ==> Use increases as criteria to set mult
        self.step_size_modification = constants.StepSizeModification.AVERAGE
        self.step_size = 0.0
        
        # Enforce symmetry is only meaningful for Spin Echo pulses
        self.enforce_symmetry = True
        
        
    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("--- OCNParams ---")
    
        lines.append("pdwell = %f" % self.pdwell)
        lines.append("pulselength = %f" % self.pulselength)
        lines.append("pulspts = %d" % self.pulspts)
        lines.append("tip = %f" % self.tip)
        lines.append("dectol = %f" % self.dectol)
        lines.append("passband = %f" % self.passband)
        lines.append("bmax = %f" % self.bmax)
        lines.append("steps = %d" % self.steps)
        lines.append("pbparm = %d" % self.pbparm)
        lines.append("brange = %f" % self.brange)
        pulse_type = self.pulse_type["display"] if self.pulse_type else "None"
        lines.append("pulse type = %s" % pulse_type)

        phase_type = self.phase_type["display"] if self.phase_type else "None"
        lines.append("phase type = %s" % phase_type)
        
        lines.append("linfact = %f" % self.linfact)
        lines.append("halt_max_iterations = %s" % self.halt_max_iterations)
        lines.append("max_iterations = %d" % self.max_iterations)
        lines.append("halt_differential_error = %s" % self.halt_differential_error)
        lines.append("differential_error_tolerance = %f" % self.differential_error_tolerance)
        lines.append("halt_residual_error = %s" % self.halt_residual_error)
        lines.append("residual_error_tolerance = %f" % self.residual_error_tolerance)
        lines.append("halt_increasing_error = %s" % self.halt_increasing_error)
        lines.append("halt_max_time = %s" % self.halt_max_time)
        lines.append("max_time = %d" % self.max_time)
        lines.append("limit_sar = %d" % self.limit_sar)
        lines.append("sar_factor = %f" % self.sar_factor)


        lines.append("initial_calculation = %d" % self.initial_calculation)
        lines.append("step_size_modification = %s" % self.step_size_modification["display"])
        lines.append("step_size = %f" % self.step_size)
        lines.append("enforce_symmetry = %d" % self.enforce_symmetry)
        
        return u'\n'.join(lines)



def oc_nonselective_calc(mpgb1, params, pstate, verbose=None):
    """
    Initial optimal control routine for:
      EXCITATION, INVERSION, AND SE PULSES
      Coalesced, uncoalesced, and linear phase
    Includes term for SAR minimization
       
    The uses for Non-Slice-Selective pulses generated from optimal control.
    * Useful for high field (>=3T)
    * Designed for 3D MRI sequences
    * Provide Immunity to B1 inhomogeneities and resonance offset
    * Can be applied using conventional coils
    * Applicable to high resolution NMR Spectroscopy
    * One can generate a large range of tip angles. 
    
    Input:
    mpgb1: rfpulse as a series of magnetic field intensities.
    params: An instance of OCNParams. Holds most of the input data.
    pstate: An instance of OCNState that holds the previous 
            state. If there is no previous state, the caller is expected to 
            provide reasonable defaults.
    verbose: True or False to indicate whether or not this function should
             print output to the console at each 100 iterations. The value 
             None (the default) indicates that the verbose flag should be
             read from vespa.ini from a flag called "verbose_oc" in a section
             called [debug]. If the flag isn't present, verbose defaults 
             to False.


    Translated from the Matpulse (matlab) file, ocnon_calc.m
    """
    if verbose is None:
        # By default we get the value of this flag from the INI file.
        config = util_config.VespaConfig()
        if ("debug" in config) and ("verbose_oc" in config["debug"]):
            verbose = config["debug"].as_bool("verbose_oc")
        else:
            verbose = False
            
    ic = cmath.sqrt(-1)
    
    start_time = now()
    
    # MULT and DELTAB1 start off as empty, and are 
    # updated at the end of the routine.
    MULT = pstate.multiplier
    DELTAB1 = pstate.deltab1
    global_smerror = pstate.residual_errors[0]

    # PS - I think stop_iterating is a flag that combines all of the 
    # reasons for halting iteration. In other words, if any of the halt_xxx
    # conditions have been triggered, the code sets stop_iterating to True.
    # I think.
    stop_iterating = False
    noper = 0
    
    if _DEBUG:
        print params

    # Set step size, error if params.initial_calculation = True
    if params.initial_calculation or \
       (params.step_size_modification == constants.StepSizeModification.FIXED):
        # 2.5 was the value that worked the best here
        # based on Jerry's *limited* experience.
        mult = params.step_size/2.5   
        DELTAB1 = np.zeros(len(mpgb1), dtype=np.complex)
    else:
        # Iterations are continuing
        mult = MULT
    
    if params.initial_calculation:
        # Values assigned here are somewhat arbitrary. It's just important
        # that newer values are smaller than older.
        pstate.residual_errors = [1, 2, 4, 8]
    #else:
        # pstate.residual_errors is already set
    
    # Convert to local variables 
    b1 = np.copy(mpgb1)
    
    dwell = params.pdwell
    plength = params.pulselength
    b1steps = params.pulspts
    
    tip = params.tip*math.pi/180.0   # Convert tip angle to radians
    linfact = params.linfact         # Value of "Linear Factor" chosen.
    
    dectol = 1 + params.dectol       # Error Increase Tolerance
                                     # :FIXME: Consider coming up with
                                     # a better variable name. 
    pb = params.passband             # Excitation band
                                     # Bandwidth and Passband are often used
                                     # interchangeably by Jerry (perhaps based
                                     # on context).
               
    # Check that passband is not too large for dwell
    # i.e. passband > 0.5*(1/dwell) # plus all the unit factors.
    if pb > 500/dwell:
        msg = 'Passband (bandwidth) too large for dwell. Reduce (shorten) passband'
        raise pulse_func_exception.PulseFuncException(msg, -2)
    
    b1max = params.bmax/1000.0       # Max B1 (microTesla ... convert to milliTesla)
    steps = params.steps             # B1 immunity steps
    
    pbpts = params.pbparm            # Passband points
    immunity = params.brange/100.0   # Range of B1 immunity. Convert from % to fraction.
    
    sar_factor = params.sar_factor
    
    if _DEBUG:
        print params
        
    # **** START COMPARISON WITH ocn_step.
    # This is here as a reminder to see if ocn_step
    # and the code between the start and end comparison
    # could be combined into a common subroutine.
    
    # Frequency steps over excitation band (pb)
    deltaf = pb/(pbpts-1)
    
    #freqpts = -pb/2:deltaf:pb/2
    # matlab includes last point, Python does not.
    freqpts  = np.arange(-pb/2,pb/2+deltaf/2,deltaf)
    
    if _DEBUG:
        print deltaf
        print freqpts        
    
    
    # GENERATE ZERO ERROR (IDEAL) PROFILES
    if params.pulse_type != constants.UsageType.SPIN_ECHO:
        # Excite, sat, or invert pulse
        myin = ic*np.zeros(pbpts, dtype=np.complex)
        mzin = np.ones(pbpts, dtype=np.complex)
    
        myzepts = ic*math.sin(tip)*np.ones(pbpts, dtype=np.complex)
        mzzepts = math.cos(tip)*np.ones(pbpts, dtype=np.complex)
        
        if _DEBUG:
            print "myin:"
            print myin   
            print     
            print mzin
            print
            print myzepts
            print
            print mzzepts        
        
    else:
        # Spin echo pulse (Calcs done twice, first for my and then for mx).
        myin = ic*np.ones(pbpts, dtype=np.complex)
        mxin = np.ones(pbpts, dtype=np.complex)
        mzin = np.zeros(pbpts, dtype=np.complex)
        mxzin= np.zeros(pbpts, dtype=np.complex)
    
        # myzepts = -ic * math.sin(tip/2.0)^2 * np.ones(pbpts)    
        myzepts = -ic * math.pow(math.sin(tip/2.0), 2) * np.ones(pbpts, dtype=np.complex)
        mxzepts = np.ones(pbpts, dtype=np.complex)
        mzzepts = -math.sin(tip)*np.ones(pbpts, dtype=np.complex)
        mxzzepts = np.zeros(pbpts, dtype=np.complex)
    
    # Add linear phase over PB on excite pulse if called for
    if params.phase_type == constants.NonCoalescedPhaseSubtype.LINEAR:
        myzepts = myzepts * np.exp(-ic*2.0*math.pi*freqpts*plength*linfact)
        if _DEBUG: 
            print myzepts
    
    # Preallocations foreward profiles fp, reverse profiles rp
    pts = pbpts
        
    delb1 = np.zeros((steps, b1steps), dtype=np.complex)
    fp = np.zeros((pts, b1steps+1), dtype=np.complex)
    fpz = np.zeros((pts, b1steps+1), dtype=np.complex)
    
    rp = np.zeros((pts, b1steps+1), dtype=np.complex)
    rp[:,b1steps]= myzepts
            
    rpz = np.zeros((pts, b1steps+1), dtype=np.complex)
    rpz[:,b1steps] = mzzepts
    
    if params.pulse_type == constants.UsageType.SPIN_ECHO:
        fpx = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpx = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpx[:,b1steps] = mxzepts
        fpxz = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpxz = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpxz[:,b1steps] = mxzzepts
    
    # Bloch equations below  
    deltab1 = DELTAB1.copy()
    jn = b1steps
    
    # g*x term in mtesla
    gx = freqpts/pf_constants.GAMMA1H 
    gxsq = gx * gx
    
    # Set up for steps values of b1
    # Units in radians/mtesla
    constb = 2*math.pi*pf_constants.GAMMA1H*dwell/1000
    delb1 = np.zeros((steps,len(b1)+1), dtype=np.complex)
    
    if _DEBUG:
        print jn
        print gx
        print gxsq
        print constb
        print delb1        
    
    # Set factors (b1incr) for b1 strengths
    step = 0
    if steps > 1: 
        step = 2*immunity/(steps-1)
        #b1incr = 1-(steps-1)/2*step:step:1+(steps-1)/2*step
        b1incr = np.arange(1-(steps-1)/2*step, 1+(steps-1)/2*step+step/2, step)
    else:
        b1incr = np.array([1.])
    
    if _DEBUG:
        print "step = %f" %step
        print b1incr
    
    l = 0
    tl = 0
    oldl = 0
    incn = 0
    
    k = 0
    n = 1
    
    # Preallocate
    merrornew = np.zeros((steps,1))
       
    do_once = True
    do_only_once = True
           
    while not stop_iterating:
                
        m = 0
        b1m = np.outer(b1incr.conj().T, b1)        
        #b1mr = fliplr(b1m)
        b1mr = b1m[:,::-1]
       
        if do_only_once and _DEBUG:
            print "m:"
            print m
            print b1
            print b1m
            print b1mr
            do_only_once = False
       
        while m < steps:
            alphf = np.ones(pts, dtype=np.complex)
            betf = np.zeros(pts, dtype=np.complex)
            alphr = np.ones(pts, dtype=np.complex)
            betr = np.zeros(pts, dtype=np.complex)
            
            j = 0
            
            while j < jn:
                
                # B1 FORWARD
                phibf = -constb*(np.sqrt(gxsq + b1m[m,j]*b1m[m,j].conj() )) 
                
                #For avoid divide by zero
                if np.abs(b1m[m,j]) < (1000 * pf_constants.EPS):
                    # This is an odd construct, but does work.
                    # We are using the "nonzero" command to find element
                    # that ARE equal to zero, by supplying a condition statement.
                    zs = np.nonzero(phibf == 0)
                    
                    if np.any(zs):
                        # In Matlab, 2011a, eps = 2.2204e-16, which is what we call,
                        # constants.EPS = pow(2,-52), which is the same value within 
                        # rounding error.
                        #
                        # Note: eps is the distance between 1.0 and the next
                        # largest double precision number.... 
                        #zeps = 1000*eps*(ones(size(zs)))
                        zeps = 1000*pf_constants.EPS*(np.ones(zs.shape, dtype=np.complex))
                        
                        # Replace 0s
                        for ii in zs:
                            phibf[ii] = zeps
                        b1m[m,j] = 0
                    else:
                        b1m[m,j] = 0
                                        
                # Matrix division...
                # nx = np.real(b1m[m,j]) * (np.abs(phibf).\constb)    
                # real b1 along x
                nx = np.real(b1m[m,j]) * (constb/np.abs(phibf))
                
                # ny = imag(b1m(m,j))*(abs(phibf).\constb)    
                # imag b1 along y
                ny = np.imag(b1m[m,j]) * (constb/np.abs(phibf))
                
                # nz = constb*(abs(phibf).\gx)
                nz = constb * (gx/np.abs(phibf))

                si = np.sin(phibf/2)
                co = np.cos(phibf/2)
                                
                alphaf = co - ic*(nz*si)
                betaf = -ic*((nx + ic*ny)*si)
                
                alphnf = alphaf*alphf - (betaf.conj())*betf
                betnf = betaf*alphf + (alphaf.conj())*betf
                
                alphf = alphnf.copy() 
                betf = betnf.copy()
    
                # :FIXME: Check this on matlab fp(:,j+1) vs Python fp[:j]
                # fp(:,j+1) = (conj(alphf).^2).*myin - (betf.^2).*conj(myin) \
                #    + 2*(conj(alphf).*betf).*mzin
                fp[:,j+1] = (alphf.conj()**2)*myin - (betf**2)*myin.conj() \
                    + 2*(alphf.conj()*betf)*mzin
                                          
                fpz[:,j+1] = -alphf.conj()*betf.conj()*myin - alphf*betf*myin.conj() \
                    + (alphf*alphf.conj() - betf*betf.conj())*mzin     

                if do_once and _DEBUG:
                    print m
                    print j
                    print nx
                    print ny
                    print nz
                    print si
                    print alphaf
                    print alphnf
                    print betnf
                    print alphf
                    print fp
                    print fpz
                    do_once = False
                      
                if params.pulse_type == constants.UsageType.SPIN_ECHO: 
                    # fpx(:,j+1) = (conj(alphf).^2).*mxin - (betf.^2).*conj(mxin) \
                    #     + 2*(conj(alphf).*betf).*mxzin                    
                    fpx[:,j+1] = (alphf.conj()**2)*mxin - (betf**2)*mxin.conj() \
                        + 2*(alphf.conj()*betf)*mxzin
                
                    # fpxz(:,j+1) = -conj(alphf).*conj(betf).*mxin -alphf.*betf.*conj(mxin) \ 
                    #    + (alphf.*conj(alphf) - betf.*conj(betf)).*mxzin     
                    fpxz[:,j+1] = -alphf.conj()*betf.conj()*mxin - alphf*betf*mxin.conj() \
                        + (alphf*alphf.conj() - betf*betf.conj())*mxzin     
                
                j = j + 1
                
                # End of first "j" loop
               
            if params.phase_type == constants.PhaseType.NON_COALESCED:
                # Fet angles and generate myzepts over passband
                # :FIXME: not clear if we should use jn or 'the orginal' 
                # (jn+1) in the next line
                fpya = np.angle(fp[:,jn])
                
                # myzepts = (sin(tip))*(cos(fpya)' + ic*sin(fpya)')
                myzepts = (np.sin(tip)) * (np.cos(fpya).conj().T + ic*np.sin(fpya).conj().T)
    
            # Reverse profiles
            j = 0
            
            while j < jn:
                
                # B1 REVERSE
                phibr = constb*(np.sqrt(gxsq + b1mr[m,j]*b1mr[m,j].conj() ))
                 
                # For avoid divide by zero
                if np.abs(b1mr[m,j]) < (1000 * pf_constants.EPS):
                    zs = np.nonzero(phibr == 0)
                    if np.any(zs):
                        zeps = 1000*pf.globals.EPS*(np.ones(zs.shape, dtype=np.complex))
                        for ii in zs:
                            # Replace 0s with eps
                            phibr[ii] = zeps
                        b1mr[m,j] = 0
                    else:
                        b1mr[m,j] = 0
                        
                # real b1r along x
                nx = np.real(b1mr[m,j])*(constb/np.abs(phibr))
                # imag b1r along y
                ny = np.imag(b1mr[m,j])*(constb/np.abs(phibr))
                
                nz = constb*(gx/np.abs(phibr))
                si = np.sin(phibr/2) 
                co = np.cos(phibr/2)
                
                alphar = co - ic*nz*si
                betar = -ic*(nx + ic*ny)*si
                
                alphnr = alphar*alphr - (betar.conj())*betr
                betnr  = betar*alphr + (alphar.conj())*betr
                alphr = alphnr.copy() 
                betr = betnr.copy()
             
                rp[:,jn-j-1] = (alphr.conj()**2)*myzepts - (betr**2)*myzepts.conj() \
                    + 2*(alphr.conj()*betr)*mzzepts
                    
                rpz[:,jn-j-1] = -alphr.conj()*betr.conj()*myzepts - alphr*betr*myzepts.conj() \
                    + (alphr*alphr.conj() - betr*betr.conj())*mzzepts
                    
                if params.pulse_type == constants.UsageType.SPIN_ECHO: 
                    rpx[:,jn-j-1] = (alphr.conj()**2)*mxzepts - (betr**2)*mxzepts.conj() \
                        + 2*(alphr.conj()*betr)*mxzzepts
                        
                    rpxz[:,jn-j-1] = -alphr.conj()*betr.conj()*mxzepts - alphr*betr*mxzepts.conj() \
                        + (alphr*alphr.conj() - betr*betr.conj())*mxzzepts
               

               
                j = j + 1
                
                # END OF second j LOOP
            
            # Check error to see if improvement
            # Error from My for excite; Mx & My for spin echo; Mz for invert
                 
            if params.pulse_type in (constants.UsageType.EXCITE, 
                                     constants.UsageType.SATURATION, ):
                # guts = conj( fp(:,jn+1)' ) - myzepts
                # merrornew(m,:) = (sum(abs( guts ))/(steps*pts)
                guts = (fp[:,jn].conj().T).conj() - myzepts
                merrornew[m,:] = (np.sum(np.abs( guts )))/(steps*pts)        
            elif params.pulse_type == constants.UsageType.INVERSION:
                # merrornew(m,:) = (sum(abs(fpz(:,jn+1)'- mzzepts)))/(steps*pts)
                merrornew[m,:] = (np.sum(np.abs(fpz[:,jn].conj().T - mzzepts)))/(steps*pts)
            elif params.pulse_type == constants.UsageType.SPIN_ECHO:
                my = -(betf**2)*myin.conj()
                merrornew[m] = (np.sum(np.abs(my-myzepts)))/(2*steps*pts)
                
            
            
            # Following Skinner, use cross prod for corrections.
            # delB1x = -(fpy*rpz-fpz*rpy)
            # delB1y = -(fpz*rpx-fpx*rpz)    
            delb1[m,:] = -np.sum( (np.imag(fp)*rpz - fpz*np.imag(rp)), axis=0) \
                -ic*(np.sum((fpz*np.real(rp) - np.real(fp)*rpz), axis=0))
                
            if params.pulse_type == constants.UsageType.SPIN_ECHO: 
                delb1[m,:] = (0.6)*delb1[m,:] - \
                   (0.4)*(np.sum( (np.imag(fpx)*rpxz - fpxz*np.imag(rpx)), axis=0) \
                   +ic*(np.sum( (fpxz*np.real(rpx) - np.real(fpx)*rpxz), axis=0)))            
                    
            m = m+1 
            
            # END OF M LOOP
      
        # Get summed error values. This call to np.sum() returns a 
        # numpy.float64 which we convert to a standard Python float for 
        # ease of handling later on. 
        current_error = float(np.sum(merrornew))
           
        # Could allow for slight increase in error in early iterations
        #     if (merrornew > (1.0 + declinetol*exp(-k/kn))*merror)
        # DON'T WANT TO GET CAUGHT IN FIRST LOOP FOREVER
        # n counts local loops of inc err, l counts total loops of inc err
                
        if ((current_error > dectol * pstate.residual_error) and (n < 6)):  
            deltab1 = deltab1 / 2.0 # OK. 10/6/11. checked with Jerry.
            mult = mult/(math.pow(n,(1/4)))
            b1 = b1 - deltab1
            n = n + 1
            l = l + 1
            k = k - 1
        else:
            # deltab1_0 = sum(delb1,1)/steps
            deltab1_0 = delb1.sum(axis=0)/steps
             
            # Averaging of nearby points is being done here.
            deltab1_1 = deltab1_0[0:jn]
            deltab1_2 = deltab1_0[1:jn+1]
            
            deltab1 = 0.5*(deltab1_1 + deltab1_2)
            deltab1 = 0.1*mult*deltab1/(pf_constants.GAMMA1H*dwell)
            b1 = b1 + deltab1  

            n = 1
            
            # Cycle residual error terms -- prune the last element, stick
            # the most recent error at the front of the list.
            del pstate.residual_errors[-1]
            pstate.residual_errors.insert(0, current_error)
            
            # Add SAR limitation if asked for (scaled to mult)
            if params.limit_sar:
                b1sq = np.abs(b1**2)
                sar_factor = (mult/(pf_constants.GAMMA1H*dwell))*b1steps*sar_factor/(1*np.sum(b1sq))
                b1 = b1 - sar_factor*b1sq
    
        # Limit b1 to b1max
        zs = np.nonzero(np.abs(b1) > b1max)
        
        if np.any(zs):
            b1[zs] = b1max*b1[zs]/np.abs(b1[zs])        
                        
        k = k + 1
        
        
        # *** END COMPARISON WITH ocn_step
        
        
        # See if time elapsed is greater than max_time.
        if params.halt_max_time and ((now() - start_time) > params.max_time):
            stop_iterating = True  
            pstate.met_max_time = True        
        
        if (params.halt_max_iterations) and (k == params.max_iterations):
            stop_iterating = True  
            pstate.met_max_iterations = True        
        
        # Every _HEADS_UP_ITERATIONS iterations, we check to see if it's time
        # for us to stop based on the limits expressed in the params. 
        if (k+l) % _HEADS_UP_ITERATIONS == 0:
            
            if params.halt_differential_error:
                residual_error_differences = pstate.residual_error_differences
                
                residual_error_differences = \
                        [residual_error_difference < params.differential_error_tolerance 
                                            for residual_error_difference
                                            in  residual_error_differences]
                if all(residual_error_differences):
                    stop_iterating = True
                    pstate.met_differential_error = True
            
            if params.halt_residual_error and \
               (pstate.residual_error < params.residual_error_tolerance):         
                stop_iterating = True
                pstate.met_residual_error = True
                     
            if params.halt_increasing_error and \
               all(pstate.residual_error_comparisons):
                # End if errors increasing (incn counts loops of inc error)
                if incn == 3:
                    stop_iterating = True  
                    pstate.met_increasing_error = True
                else:
                    mult = mult/2 
                    incn = incn+1
            
            mpgb1 = b1.copy()

            # "Update of [what used to be] Globals"
            MULT = mult
            global_smerror = pstate.residual_error
            
            DELTAB1 = deltab1.copy()
            NOPER = noper
       
            # Prepare for next iteration (assuming there will be one!)
            if not stop_iterating:
           
                if params.step_size_modification == \
                   constants.StepSizeModification.FIXED:
                    # reset mult's value.
                    mult = params.step_size          
                              
                elif params.step_size_modification == \
                      constants.StepSizeModification.AVERAGE:
                    # do step size (mult) that gives improvement
                    nl = l - oldl         
                    if nl > 8:
                        mult = mult/2
                    elif nl < 2:
                        mult = math.sqrt(2)*mult                         
                    oldl = l
                    
                else:
                    # implied: 
                    # step_size_modification == StepSizeModification.COMPUTE              
                    sc_params = ocn_step.StepcalcParams()
                    
                    # :FIXME: Add appropriate values to object.
                    # There may be a way to combine this with the
                    # "Update" of Globals above.
                    sc_params.multiplier = MULT
                    sc_params.residual_error = global_smerror
                    sc_params.NOPER = NOPER
                    sc_params.deltab1 = DELTAB1 # will be copied in subroutine.
    
                    # :FIXME: Perhaps we could put these into a common sub-object
                    # with OCNParams OR remove the above 4 items and pass them
                    # in on the command line, with the others still in the original
                    # params object.
                    sc_params.pdwell = params.pdwell
                    sc_params.pulselength = params.pulselength
                    sc_params.pulspts = params.pulspts
                    sc_params.tip = params.tip 
                    sc_params.linfact = params.linfact 
                    sc_params.dectol = params.dectol 
                    sc_params.passband = params.passband 
                    sc_params.bmax = params.bmax 
                    sc_params.steps = params.steps 
                    sc_params.pbparm = params.pbparm
                    sc_params.brange = params.brange 
                    sc_params.pulse_type = params.pulse_type 
                    sc_params.phase_type = params.phase_type
    
                    # Compute stepsize  
                    mult, noper = ocn_step.oc_nonselective_stepcalc(mpgb1, sc_params)
            
            
            # If noper over 40, system stuck
            # Assignment of params.max_iterations to k should drop us out of the loop
            # This is proably because stepcalc did not work right.
            # FIXME: See what tends to happen with "average" or "fixed"
            # instead of "computer".
            if noper > 40:
                k = params.max_iterations
                
            if verbose:   
                # print these out every 100 "k+l" iterations
                print "iterations (limit): %d (%d)" % (k, params.max_iterations)
                print "residual error (limit): %.12f (%.12f)" % (pstate.residual_error, params.residual_error_tolerance)
                print "differential error (limit): %.12f (%.12f)" % (pstate.differential_error, params.differential_error_tolerance)
                print "minutes elapsed (limit): %.1f (%d)" % ((now() - start_time) / 60, params.max_time // 60)
                print "l = %d" %l
                print "step size = %f" % mult
                # print "deltab1:" 
                # print deltab1
                  
            # Update counts               
            tl = tl + l        
            l = 0
            oldl = 0 
     
            # Advanced Options
            
            # Symmetrize b1 (Make antisymmetric)
            # We do this only once every 100 times through loop.
            # The thinking is that once we make it symmetric and 
            # it's converging on a minimum, it should only deviate
            # to a small degree. However, it may be worth playing
            # with this and doing it more often (or making the 
            # frequency of symmetryization a parameter).
            if params.enforce_symmetry and \
               (params.pulse_type == constants.UsageType.SPIN_ECHO):
                b1 = 1/2*(b1 + (b1.conj())[::-1] )
            
            # NOTE: Based on feedback from Jerry, 
            # will ignore most of the "advanced" options section.
            # ADVACED OPTIONS (other then Symmetrize) were removed from this location.

            # End of every 100 iterations loop

        # END OF K (ITERATIONS) LOOP
    
    if l > tl:
        tl = l    
    
    # Outputs of this round of optimization.
    mpgb1 = b1.copy()
    params.pdwell = dwell    

    pstate.multiplier = mult
    pstate.deltab1 = deltab1.copy()
    
    # Outputs to command line window
    iterations = k
    decreases = tl
    
    if verbose:
        print "Iterations   = %d" % iterations
        print "Decreases    = %d" % decreases
        print "Stepsize     = %f" % mult
        print "Residual     = %f" % pstate.residual_error
        print "Differential = %f" % pstate.differential_error
    
    if noper > 40:
        errorstr = 'Halting on 40 no_operations; stuck in local minimum'
        raise pulse_func_exception.PulseFuncException(errorstr, -2)        
    
    if verbose:
        if pstate.met_increasing_error:
            print 'Halting on error increasing; try smaller step or smaller tolerance'
        
        if pstate.met_differential_error:
            print 'Halting on differential error; try larger step'
        
        if pstate.met_residual_error:
            print 'Halting on residual error'
        
        if pstate.met_max_time:
            print 'Halting on time limit of %d minutes' % (params.max_time//60)

        if pstate.met_max_iterations:
            print 'Halting on max iterations'
    
    elapsed_time = now() - start_time

    if verbose:
        print 'Elapsed time is %f seconds' %elapsed_time

    pstate.run_time = elapsed_time
    pstate.iterations = iterations
    pstate.decreases = decreases
    
    return mpgb1

