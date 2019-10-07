# ocnon_stepcalc.py
from __future__ import division

# Python Modules.
import math
import cmath

# 3rd party stuff
import numpy as np

# Local imports
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.constants as constants


class StepcalcParams(object):
    def __init__(self):

        self.multiplier = 0.0
        self.deltab1 = np.array([], dtype=np.complex)
        self.residual_error = 0.0
        self.NOPER = 0.0

        self.pdwell = 10.0
        self.pulselength = 8.0
        self.pulspts = 250
        self.tip = 90.0          # Tip angle in degrees.
        self.linfact = 0.5
        self.dectol = 1.0e-004   # Error tolerance
        self.passband = 1.0      # Excitation band (PB)

        self.steps = 5           # B1 immunity steps
        self.pbparm = 41         # Passband points
        self.brange = 20         # Range of B1 immunity
        self.pulse_type = constants.UsageType.EXCITE
        self.phase_type = constants.PhaseType.NON_COALESCED


#function [nmult nnoper] = oc_non_stepcalc(handles)
def oc_nonselective_stepcalc(mpgb1, params):
    
    # Called by ocnon_calc
    # Initial optimal control routine stepsize calc

    ic = cmath.sqrt(-1)


    b1 = mpgb1.copy()
    
    mult = params.multiplier
    previous_residual_error = params.residual_error
    noper = params.NOPER
    
    nmult = mult    
    
    deltab1 = params.deltab1.copy() 
    
    # INITIAL CHECKS
    # Optimization can fail if deltab1 too small; 
    #   If this happens, try small decreases in nmult.
    # :FIXME: Should the next two if statements 
    #   return a string to display?
    nnoper = noper
    
    if np.sum(np.abs(deltab1)) < 10000*pf_constants.EPS: 
        nmult = mult/1.5
        nnoper = noper + 1 
        return nmult, nnoper
    
    # Need to limit mult*deltab1 
    b1abs = np.sum(np.abs(b1))
    deltab1abs = np.sum(np.abs(mult*deltab1))
    if deltab1abs > b1abs/20:
        nmult = mult*b1abs/(40*deltab1abs)
        return nmult, nnoper
    
    # Limit iterations to 10 here
    km = 10
    
    # Convert to local variables 
    dwell = params.pdwell
    plength = params.pulselength
    b1steps = params.pulspts
    tip = params.tip*math.pi/180
    linfact = params.linfact
    
    dectol = 1 + params.dectol       # Tolerance for inc. error
    pb = params.passband             # Excitation band (PB)
    
    steps = params.steps            # B1 immunity steps
    
    pbpts = params.pbparm
    immunity = params.brange/100
        
    # Frequency steps over excitation band (pb)
    delf = pb/(pbpts-1)
    
    #freqpts = -pb/2:delf:pb/2
    # :FIXME: see if the extra (delf/2) is needed...
    freqpts = np.arange(-pb/2, pb/2 + delf/2, delf)
    
    # GENERATE ZERO ERROR PROFILES *******
    if params.pulse_type != constants.UsageType.SPIN_ECHO:
        # Excite, sat, or invert pulse
        myin = ic*np.zeros(pbpts, dtype=np.complex)
        mzin = np.ones(pbpts, dtype=np.complex)
    
        myzepts = ic*np.sin(tip)*np.ones(pbpts, dtype=np.complex)
        mzzepts = np.cos(tip)*np.ones(pbpts, dtype=np.complex)
    else:
        # Spin echo pulse
        myin = ic*np.ones(pbpts, dtype=np.complex)
        mxin = np.ones(pbpts, dtype=np.complex)
        mzin = np.zeros(pbpts, dtype=np.complex)
        mxzin= np.zeros(pbpts, dtype=np.complex)
    
        myzepts = -ic*(np.sin(tip/2)**2)*np.ones(pbpts, dtype=np.complex)
        mxzepts = np.ones(pbpts, dtype=np.complex)
        mzzepts = -np.sin(tip)*np.ones(pbpts, dtype=np.complex)
        mxzzepts = np.zeros(pbpts, dtype=np.complex)
    
    # Add linear phase over PB on excite pulse if called for ****
    if params.phase_type == constants.NonCoalescedPhaseSubtype.LINEAR:
        myzepts = myzepts*np.exp(-ic*2*math.pi*freqpts*plength*linfact)
    
    # Support vector svect in kHz
    svect = freqpts.copy()
    pts = len(svect)
    
    # Preallocations forward profiles fp, reverse profiles rp
    fp = np.zeros((pts, b1steps+1), dtype=np.complex)
    fpz = np.zeros((pts, b1steps+1), dtype=np.complex)
    
    rp = np.zeros((pts, b1steps+1), dtype=np.complex)
    rp[:,b1steps]= myzepts
    
    # :FIXME: Do we need the extra "+1" here?
    rpz = np.zeros((pts, b1steps+1), dtype=np.complex) 
    rpz[:,b1steps]= mzzepts
    
    if params.pulse_type == constants.UsageType.SPIN_ECHO:
        fpx = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpx = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpx[:,b1steps] = mxzepts
        # :FIXME: fpxz is NOT initialized here in ocnon_stepclc.m!!
        fpxz = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpxz = np.zeros((pts, b1steps+1), dtype=np.complex)
        rpxz[:,b1steps] = mxzzepts
    
    # Bloch equations below  
    jn = b1steps
    gx = svect/pf_constants.GAMMA1H            # g*x term in mtesla 
    gxsq = gx*gx
    
    # Set up for steps values of b1
    constb = 2*math.pi*pf_constants.GAMMA1H*dwell/1000    # Units in radians/mtesla
    
    if steps > 1: 
        step = 2*immunity/(steps-1)
        # b1incr = 1-(steps-1)/2*step:step:1+(steps-1)/2*step
        b1incr = np.arange(1-(steps-1)/2*step, 1+(steps-1)/2*step+step/2, step)        
    else:
        b1incr = np.array([1.])
    
    # clear j k m
    j = 0
    m = 0
    # Removed "l" as it was not being used.
    k = 1
    n = 1
    
    # Preallocate
    merrornew = np.zeros((steps,1))
    
    # ***
    # :FIXME: Much of the code that follows looks like
    # a duplicate of what's in ocnon_calc. Perhaps they
    # could be make into a shared subroutine???
    # ***
    
    while (k < km): 
        m = 0
        b1m = np.outer(b1incr.conj().T, b1)        
        #b1mr = fliplr(b1m)
        b1mr = b1m[:,::-1]
       
        while m < steps:
            alphf = np.ones(pts, dtype=np.complex)
            betf = np.zeros(pts, dtype=np.complex)
                
            alphr = np.ones(pts, dtype=np.complex)
            betr = np.zeros(pts, dtype=np.complex)
             
            j = 0
            
            while j < jn:
                # B1 FORWARD    
                phibf = -constb*(np.sqrt(gxsq + b1m[m,j]*b1m[m,j].conj() )) 
                                
                if np.abs(b1m[m,j]) < 1000*pf_constants.EPS:    # For avoid divide by zero
                    # NEXT line is odd, but it works!
                    zs = np.nonzero(phibf == 0)
                    if np.any(zs):
                        zeps = 1000*pf_constants.EPS*(np.ones(zs.shape, dtype=np.complex))                                                    
                        # Replace 0s
                        for ii in zs:
                            phibf[ii] = zeps
                        b1m[m,j] = 0
                    else:
                        b1m[m,j] = 0
            
                # real b1 along x
                nx = np.real(b1m[m,j])*(constb/np.abs(phibf))
                
                # imaginary b1 along y
                ny = np.imag(b1m[m,j])*(constb/np.abs(phibf))
                
                nz = constb*(gx/np.abs(phibf))
                si = np.sin(phibf/2) 
                co = np.cos(phibf/2)
                
                alphaf = co - ic*nz*si
                betaf = -ic*(nx + ic*ny)*si
                alphnf = alphaf*alphf - (betaf.conj())*betf
                betnf = betaf*alphf + (alphaf.conj())*betf
                alphf = alphnf.copy() 
                betf = betnf.copy()
    
                fp[:,j+1] = (alphf.conj()**2)*myin - (betf**2)*myin.conj() \
                    + 2*(alphf.conj()*betf)*mzin
                    
                fpz[:,j+1] = -alphf.conj()*betf.conj()*myin - alphf*betf*myin.conj() \
                    + (alphf*alphf.conj() - betf*betf.conj())*mzin       
                    
                if params.pulse_type == constants.UsageType.SPIN_ECHO:
                   fpx[:,j+1] = (alphf.conj()**2)*mxin - (betf**2)*mxin.conj() \
                        + 2*(alphf.conj()*betf)*mxzin
                        
                   fpxz[:,j+1] = -alphf.conj()*betf.conj()*mxin - alphf*betf*mxin.conj() \
                        + (alphf*alphf.conj() - betf*betf.conj())*mxzin     
                
                j = j + 1
                
            if params.phase_type == constants.PhaseType.NON_COALESCED:           
                # Get angles and generate myzepts over passband
                fpya = np.angle(fp[:,jn])
                myzepts = (np.sin(tip))*( (np.cos(fpya)).conj().T + ic*(np.sin(fpya)).conj().T )
    
            # Reverse profiles
            j = 0
            while j < jn:
                # B1 REVERSE 
                phibr = constb*(np.sqrt(gxsq + b1mr[m,j]*(b1mr[m,j]).conj()))                
                 
                if np.abs(b1mr[m,j]) < 1000*pf_constants.EPS:    # For avoid divide by zero
                    zs = np.nonzero(phibr == 0)
                    if np.any(zs):
                        zeps = 1000*pf_constants.EPS*(np.ones(zs.shape, dtype=np.complex))
                        # Replace 0s with eps
                        for ii in zs:
                            phibf[ii] = zeps                        
                        b1mr[m,j] = 0
                    else:
                        b1mr[m,j] = 0
            
                nx = np.real(b1mr[m,j])*(constb/np.abs(phibr))    # real b1r along x
                ny = np.imag(b1mr[m,j])*(constb/np.abs(phibr))    # imag b1r along y
                nz = constb*(gx/abs(phibr))
                si = np.sin(phibr/2) 
                co = np.cos(phibr/2)
    
                alphar = co - ic*nz*si
                betar = -ic*(nx + ic*ny)*si
                alphnr = alphar*alphr - (betar.conj())*betr
                betnr = betar*alphr + (alphar.conj())*betr
                alphr = alphnr.copy() 
                betr = betnr.copy()       
             
                rp[:,jn-j-1] = (alphr.conj()**2)*myzepts - (betr**2)*myzepts.conj() \
                    + 2*(alphr.conj()*betr)*mzzepts
                    
                rpz[:,jn-j-1] = -alphr.conj()*betr.conj()*myzepts - alphr*betr*myzepts.conj() \
                    + (alphr*alphr.conj() - betr*betr.conj())*mzzepts
                    
                if params.pulse_type == constants.UsageType.SPIN_ECHO:
                    rpx[:,jn-j-1] = (alphr.conj()**2)*mxzepts - (betr**2)*mxzepts.conj() \
                        + 2*(alphr.conj()*betr)*mzzepts
                        
                    rpxz[:,jn-j-1] = -alphr.conj()*betr.conj()*mxzepts - alphr*betr*mxzepts.conj() \
                        + (alphr*alphr.conj() - betr*betr.conj())*mxzzepts             
               
                j = j + 1
                
                # END OF J LOOPS
      
            # Check error to see if improvement
            # Error from My for excite; Mx & My for spin echo; Mz for invert
            if params.pulse_type in (constants.UsageType.EXCITE, 
                                     constants.UsageType.SATURATION, ):
                # NOTE: jn+1 ==> jn in the next three statements.
                # merrornew(m,:) = (sum(abs((conj(fp(:,jn+1)')- myzepts))))/(steps*pts) ; 
                # :FIXME: make sure that the transpose is working properly here!!!
                # e.g. compare with Matlab.
                merrornew[m,:] = np.sum(np.abs((fp[:,jn].conj().T).conj()- myzepts)) / (steps*pts)        
            elif params.pulse_type == constants.UsageType.INVERSION:
                # merrornew(m,:) = (sum(abs(fpz(:,jn+1)'- mzzepts)))/(steps*pts) ;
                merrornew[m,:] = np.sum(np.abs( fpz[:,jn].conj().T- mzzepts) )/(steps*pts)
            elif params.pulse_type == constants.UsageType.SPIN_ECHO:
                # merrornew(m,:) = (sum(abs((conj(fp(:,jn+1)')- myzepts))))/(2*steps*pts) ...
                # + (sum(abs((conj(fpx(:,jn+1)')- mxzepts))))/(2*steps*pts) ;
                merrornew[m,:] = np.sum(np.abs((fp[:,jn].conj().T).conj() - myzepts)) / (2*steps*pts) \
                                    + np.sum(np.abs((fpx[:,jn].conj().T).conj()- mxzepts)) / (2*steps*pts)
            m = m+1
            
            # END OF M LOOP

     
        # Get summed error values
        if k > 1:
            previous_residual_error = current_residual_error
         
        current_residual_error = np.sum(merrornew)  
         
        # Don't want to keep reducing nmult
        if (current_residual_error > previous_residual_error) and (n < 6):
            deltab1 = deltab1/2
    
            b1 = b1 - deltab1
            # FIXME : Discuss with Jerry the fact
            # that the first time through n is 1, so 
            # pow(n,.25) is also 1.
            nmult = nmult/pow(n,.25) 
            n = n+1
            if k >= 2 or n == 5:
                k = km + 1
            else:
                k = k - 1
        else:
            nmult = pow(2,(1/2)*nmult)
            deltab1 = 0.1*nmult*deltab1 / (pf_constants.GAMMA1H*dwell)
            b1 = b1 + deltab1 
            
            # Need to limit deltab1 
            b1abs = np.sum(np.abs(b1)) 
            deltab1abs = np.sum(np.abs(deltab1))
            if deltab1abs > b1abs/20: 
                nmult = nmult*b1abs/(40*deltab1abs)
                return nmult, nnoper
        
        k = k + 1
    
        # END OF K (ITERATIONS) LOOP
    
    return nmult, nnoper
