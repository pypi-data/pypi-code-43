# Python modules
from __future__ import division

# 3rd party Modules
import numpy
import numpy.linalg as linalg
import scipy
import scipy.interpolate as interpolate

## Routines for converting B1 fields to polynomial roots and vice versa 
## using the SLR type polynomial generating algorithm  

def b1_to_roots(b1,dwell=10.0,maxangle=0.1):
    """
    Given a B1 field this routine returns the roots of the corresponding
    SLR A and B polynomials and logical arrays of the same length as the 
    arrays of returned roots, with value TRUE corresponding to  "flipable" 
    roots, i.e. those whose angle in the complex plane is less than a
    specified maximum angle.
    
    Flipping roots (reflection through the unit circle) should preserve 
    the magnitude profile for all pulse angles, and preserve the real and 
    imaginary profile for 180 degree (spin-echo) pulses.

    Parameters
    ----------
    b1 : complex ndarray
         complex array containing a B1 pulse 
    dwell : float, optional, default = 10.0
            dwell time (usec) - change this as per pulse
    maxangle: float, optional, default = 0.1
           the maximum angle for "flipable" roots in the complex plane

    Returns
    -------
    aa : complex ndarray
        a filter polynomial coefficients
    Anorm: float
        the norm of the a polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm 
    aplotroots: ndarray
        array containing the roots of the SLR A polynomial
    bb :complex  ndarray
        b filter polynomial coefficients
    bnorm: float
        the norm of the b polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm
    bplotroots: ndarray
        array containing the roots of the SLR B polynomial
    leadzeros: int
        number of leading zeros in B1 - these are truncated and
        returned for the conveniance of replacing them in reconstructed 
        pulses
    lagzeros: int
        number of trailing zeros in B1 - these are truncated and
        returned for the conveniance of replacing them in reconstructed 
        pulses
    """
    # Check for leading and lagging zeros in B1 and truncate accordingly
    count = 0
    while numpy.abs(b1[0]) == numpy.PZERO:
        count += 1
        b1 = b1[1:len(b1)]
    leadzeros = count
    count = 0
    while numpy.abs(b1[len(b1)-1]) == numpy.PZERO:
        count += 1
        b1 = b1[0:len(b1)-1]
    lagzeros = count

    # Get a and b polynomials
    [apoly,anorm,bpoly,bnorm] =  b1_to_polynomials(b1,dwell=10.0)
    # Get roots
    [aroots,aplotroots] = polynomials_to_roots(apoly,maxangle=maxangle,numroots=0)
    [broots,bplotroots] = polynomials_to_roots(bpoly,maxangle=maxangle,numroots=0)
    return [aroots,aplotroots,anorm,broots,bplotroots,bnorm,leadzeros,lagzeros];

def b1_to_polynomials(b1,dwell=10.0):
    """
    Given a B1 field this routine calculates SLR A and B filter
    polynomials

    Parameters
    ----------
    b1 : complex ndarray
         complex array containing a B1 pulse 
    dwell : float, optional, default = 10.0
            dwell time (usec) - change this as per pulse

    Returns
    -------
    aaf : ndarray
        the frequency domain a filter polynomial
    anorm: float
        the norm of the a polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm 
    bbf : ndarray
        the frequency domain b filter polynomial
    bnorm: float
        the norm of the b polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm 
    """

    # Check if b1 is too big - INTERPOLATION DISABLED FOR NOW
    # b1lenorig = len(b1)
    # if b1lenorig > pulse_func_globals.b1rootlimit:
    #    print "Interpolating b1..."
    #    # linsp = numpy.linspace(0., b1lenorig, pulse_func_globals.b1rootlimit)
    #    # gr = interpolate.UnivariateSpline(numpy.arange(b1lenorig),numpy.real(b1),k=2,s=0)
    #    # gi = interpolate.UnivariateSpline(numpy.arange(b1lenorig),numpy.imag(b1),k=2,s=0)
    #    # b1r = gr(linsp)
    #    # b1i = gi(linsp)
    #    gr = interpolate.interp1d(numpy.arange(b1lenorig),numpy.real(b1))
    #    gi = interpolate.interp1d(numpy.arange(b1lenorig),numpy.imag(b1))
    #    newx = numpy.arange(0,b1lenorig-1,numpy.float(b1lenorig)/pulse_func_globals.b1rootlimit)
    #    b1r = gr(newx)
    #    b1i = gi(newx)
    #    b1 = b1r + 1j*b1i
    
    # Initialization
    # b1 = -1j*b1 # Don't need this now - matlab did conplex conjugate on transpose
    b1len = len(b1)
    # const = 2.*numpy.pi*pulse_func_globals.GAMMA1H*dwell/2000.
    const = 1.0
    aa = 1.
    bb = 0.
    c = numpy.zeros(b1len,numpy.float64)
    s = numpy.zeros(b1len+1,numpy.complex128)
    theta = numpy.zeros(b1len)

    # Polynomial calculations
    ct = 0
    while ct < b1len:
        theta[ct] = numpy.angle(b1[ct])
        c[ct] = numpy.cos(const*numpy.abs(b1[ct]))
        s[ct] = 1j*numpy.exp(1j*theta[ct])*numpy.sin(const*numpy.abs(b1[ct]))
        aa1n = c[ct]*aa
        aa1 = numpy.array(numpy.hstack((aa1n, 0.)))
        aa2n = -numpy.conjugate(s[ct])*bb
        aa2 = numpy.array(numpy.hstack((0., aa2n)))
        bb1n = s[ct]*aa
        bb1 = numpy.array(numpy.hstack((bb1n, 0.)))
        bb2n = c[ct]*bb
        bb2 = numpy.array(numpy.hstack((0., bb2n)))
        aa = aa1+aa2
        bb = bb1+bb2
        ct += 1

    # aaf, w = signal.freqz(aa, a=1., worN = 4*len(aa),whole=True)
    # anorm = linalg.norm(aaf)
    # bbf, w = signal.freqz(bb, a=1., worN = 4*len(bb),whole=True)
    # bnorm = linalg.norm(bbf)
    # return [aaf, anorm, bbf, bnorm]

    # Delete last (0) element of polynomials
    aa = numpy.delete(aa,len(aa)-1)
    bb = numpy.delete(bb,len(bb)-1)
    # Note: sign of polynomial can get reversed in root() so include it in norm... 
    anorm = numpy.sign(aa[0])*linalg.norm(aa)
    bnorm = numpy.sign(bb[0])*linalg.norm(bb)
    return [aa, anorm, bb, bnorm]
        
def polynomials_to_roots(poly,maxangle=0.1,minangle = 0.01,numroots=0):

    """
    This routine calculate the roots of a polynomial and returns an
    array containg the roots and the norm of the polynomial

    Parameters
    ----------
    poly : complex ndarray
           complex array containing the complex coefficients of a polynomial 
    maxangle: float, optional, default = 0.1
           the maximum angle for "flipable" roots in the complex plane
    minangle: float, optional, default = 0.01
           the minimum angle for "flipable" roots in the complex plane
    numroots : int, optional, default = 0
            the maximum size of the array returned roots; if set to 0
            will just use the size of the array of polynomial coefficients

    Returns
    -------
    r : complex ndarray
        array of roots of the polynomial
    rsinti: bool ndarray
        array containing TRUE for "flippable" roots in the corresponding element
    """

    #Re-Generate aa polynomial coefficients from frequency domain coeeficients
    # aa1 = sp.ifft(zpoly)
    aa1 = poly
    
    # If no limit on number of roots sent in
    if numroots == 0:
        aa = aa1
    else:
        aa = aal[0:numroots]
    # Get roots of interest
    r = numpy.roots(aa)
    ra = numpy.angle(r)
    rasi = numpy.argsort(ra)
    ras = ra[rasi]
    r = r[rasi]
    # Select roots that satisfy <= maxangle condition and > 0
    rsinti = (maxangle >= numpy.abs(ras)) & (numpy.abs(ras) > minangle)
    return [r,rsinti]


def roots_to_b1(aroots,anorm,broots,bnorm,num=0,maxb1=0.0,dwell=10.0,leadzeros=0,lagzeros=0):
    """
    Given 2 sets of polnomial roots, treated as the roots of SLR A nad B
    polynomials, this routine returns the corresponding B1 field

    Parameters
    ----------
    aroots : complex ndarray
        the roots of the a filter polynomial
    anorm: complex
        the norm of the a polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm 
    broots : complex ndarray
        the roots of the b filter polynomial
    bnorm: complex
        the norm of the b polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm
    num: int, optional, default = 0
        the size of the output B1 fieild; if no value specified will
    default to length of input polynomials
    maxb1: float, optional default = 0
        maximum size to clip B1 at; usually used to supress spikes at end
        of sequence
    dwell : float, optional, default = 10.0
        dwell time (usec) - change this as per pulse
    leadzeros: int, optional, default = 0
        number of zeros to prepend to B1 - included because b1_to_roots
        truncates leading zeros (and returns the number truncated) - this
        provideds the option of adding them back to B1
    lagzeros: int, optional, default = 0
        number of zeros to append to B1 - included because b1_to_roots
        truncates trailing zeros (and returns the number truncated) - this
        provideds the option of adding them back to B1

    Returns
    -------
    b1 : complex ndarray
         complex array containing a B1 pulse
    """
   
    apoly = roots_to_polynomial(aroots,anorm)
    bpoly = roots_to_polynomial(broots,bnorm)
    b1 = polynomials_to_b1(apoly,bpoly,num,maxb1,dwell,leadzeros,lagzeros)
    return b1

def roots_to_polynomial(roots,norm):
    """
    Given a set of polnomial roots, this routine returns the 
    corresponding polynomial 

    Parameters
    ----------
    roots : complex ndarray
        the roots of a filter polynomial
    norm: complex
        the norm of the a polynomial - typically used 
        to calculate new polynomial from modified 
        roots but having same norm

    Returns
    -------
    poly : complex ndarray
        a complex array of polynomial coefficients corresponding
        the roots roots, and normalized via norm
    """

    pol = numpy.poly(roots)
    # Have to account for possible sign flip by poly (poly normalizes
    # polynomial coefficients such that the leading coefficient is +1)
    return numpy.sign(numpy.real(norm))*(numpy.abs(norm)/linalg.norm(pol))*pol

def polynomials_to_b1(apoly,bpoly,num=0,maxb1=0.0,dwell=10.0,leadzeros=0,lagzeros=0):
    """
    Given a set of SLR A and B filter polynomials this routine returns the
    coreeponding B1 field

    Parameters
    ----------
    apoly : complex ndarray
        SLR A filter polynomial coefficients
    bpoly : complex ndarray
        SLR B filter polynomial coefficients
    num: int, optional, default = 0
        the size of the output B1 fieild; if no value specified will
    default to length of input polynomials
    maxb1: float, optional default = 0
        maximum size to clip B1 at; usually used to supress spikes at end
        of sequence
    dwell : float, optional, default = 10.0
        dwell time (usec) - change this as per pulse
    leadzeros: int, optional, default = 0
        number of zeros to prepend to B1 - included because b1_to_roots
        truncates leading zeros (and returns the number truncated) - this
        provideds the option of adding them back to B1
    lagzeros: int, optional, default = 0
        number of zeros to append to B1 - included because b1_to_roots
        truncates trailing zeros (and returns the number truncated) - this
        provideds the option of adding them back to B1

    Returns
    -------
    b1 : complex ndarray
        complex array containing a B1 pulse 
    """
    # const = 2.*numpy.pi*pulse_func_globals.GAMMA1H*dwell/2000.
    const = 1.0
    # Generte coefficients
    ac = numpy.copy(apoly)
    bc = numpy.copy(bpoly)
    # Preserve original bc and ac
    acn = numpy.copy(ac)
    bcn = numpy.copy(bc)

    b1len = len(apoly)
    etheta = numpy.zeros(b1len,numpy.complex128)
    b1 = numpy.zeros(b1len,numpy.complex128)
    c = numpy.zeros(b1len,numpy.complex128)
    s = numpy.zeros(b1len,numpy.complex128)

    q = b1len
    while  q > 0:
        ftheta = numpy.angle(-1j*bcn[0]/acn[0])
        etheta[q-1] = numpy.exp(1j*ftheta)
        b1[q-1] = (1./const)*(etheta[q-1])*numpy.arctan(numpy.abs(bcn[0]/acn[0]))
        c[q-1] = numpy.cos(const*numpy.abs(b1[q-1]))
        s[q-1] = 1j*etheta[q-1]*numpy.sin(const*numpy.abs(b1[q-1]))

        acu = acn.copy()
        acu = numpy.delete(acu,0)
        acl = acn.copy()
        acl = numpy.delete(acl,q-1)
        bcu = bcn.copy()
        bcu = numpy.delete(bcu,0)
        bcl = bcn.copy()
        bcl = numpy.delete(bcl,q-1)

        #%clear acn bcn ;
        acn = c[q-1]*acl + numpy.conjugate(s[q-1])*bcl ;
        bcn = -s[q-1]*acu + c[q-1]*bcu ;

        q = q-1

    # Check if num (size of desired b1) jibes with polynomial length
    # there could be a mismatch of e.g. too long a pulse was tried
    # with root reflect and b1 was therefore truncated so that estimatin
    # of roots was feasbible - in that case num can be set to the original
    # pulse length and the bit of code below will upsample to the original
    # resolution using spline inteprolation - CURRENTLY DISABLED

    # if ((num != len(b1)) and (num !=0)):
    #    # linsp = numpy.linspace(0, b1len, num)
    #    #gr = interpolate.UnivariateSpline(numpy.arange(len(b1)),numpy.real(b1),k=1,s=0)
        
    #    # gi = interpolate.UnivariateSpline(numpy.arange(len(b1)),numpy.imag(b1),k=1,s=0)
    #    # b1r = gr(linsp)
    #    # b1i = gi(linsp)
    #    gr = interpolate.interp1d(numpy.arange(len(b1)),numpy.real(b1))
    #    gi = interpolate.interp1d(numpy.arange(len(b1)),numpy.imag(b1))
    #    newx = numpy.arange(0,len(b1),numpy.float(len(b1))/num)
    #    b1r = gr(newx)
    #    b1i = gi(newx)
    #    b1 = b1r + 1j*b1i
    #if maxb1 > 0.0: # Clip B1 if requested
    #    b1r = numpy.clip(numpy.real(b1),-maxb1,maxb1)
    #    b1i = numpy.clip(numpy.imag(b1),-maxb1,maxb1)
    #    b1 = b1r + 1j*b1i

    # Optionally add back originall truncated zeros to beggining and end
    # of pulse
    b1 = numpy.hstack([numpy.zeros(leadzeros),b1,numpy.zeros(lagzeros)])
    return 1j*b1

