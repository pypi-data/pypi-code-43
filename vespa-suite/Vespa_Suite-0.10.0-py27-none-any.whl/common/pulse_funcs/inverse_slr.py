# Python modules
from __future__ import division

# 3rd party modules
import numpy as np
import scipy as sp

# Our modules
import vespa.common.pulse_funcs.constants as pf_constants

# function b1 = mplpmb1f(na,mpldtmu)

def inverse_slr(na, mpldtmu, mpgaa, mpgbb):
    '''Perform the inverse SLR transformation. 
       Gives b1 for a set of a & b polynomials. 
       
       See also:
       J. Pauly, P. Le Roux, D. Nishimura, A. Macovski, 
       'Parmater Relations for the Shinnar-Le Roux Selective Excitation Pulse Design Algorithm',
       IEEE Transactions on Medical Imaging, Vol. 10, No. 1, pp 53-65, March 1991.'''
       
    # Adapted from Matlab, MPLPMB1F.M
       
    # Define local constants (mtesla)
    
    # GAMMA1H - Gamma for protons (kHz/mT)
    const = (pf_constants.GAMMA1H/2) * (mpldtmu/1000.0) * 2.0 * np.pi
    a = mpgaa
    b = mpgbb 

    # Generate coefficients bc and ac 

    bc = sp.fftpack.ifft(b) 
    ac = sp.fftpack.ifft(a)
 
    # Preserve orig bc and ac (as 'aa' and 'bb')
    bb = bc.copy() 
    aa = ac.copy()

    # Inverse SLR Transform

    # idx = na
    # changed to na-1 to adapt to zero based indexing.
    idx = na-1
    
    etheta = np.zeros(na, dtype=complex)
    b1 = np.zeros(na, dtype=complex)
    c = np.zeros(na, dtype=complex)
    s = np.zeros(na, dtype=complex)


    while idx > -1:  # >= 0
    
        #etheta(idx) = bc(1)/ac(1)/(i*abs(bc(1)/ac(1)))
        # DCT 02/27/09 - convert to bc(0), etc.
        etheta[idx] = ( bc[0]/ac[0] ) / (1j * np.abs(bc[0]/ac[0]))

        b1[idx] = (1/const) * (etheta[idx]) * np.arctan( np.abs(bc[0]/ac[0]) )
                       
        c[idx] = np.cos( const * np.abs(b1[idx]) )
        s[idx] = 1j * etheta[idx] * np.sin(const * np.abs(b1[idx]))


        # acu = ac ; acu(1) = [] ;
        acu = np.delete(ac, 0)
        
        # acl = ac ; acl(l) = [] ;
        acl = np.delete(ac, idx)        
      
        # bcu = bc ; bcu(1) = [] ;
        bcu = np.delete(bc, 0)
             
        # bcl = bc ; bcl(l) = [] ;
        bcl = np.delete(bc, idx)
        
        qc = c[idx]        
        qs = s[idx]
        
        # ac = c[idx] * acl + conj( s[idx] ) * bcl
        ac =  qc*acl + (qs.conj())*bcl    
        
        bc = -qs*acu + qc*bcu
      
        idx = idx-1

    # b1 = -imag(b1) ; # matlab code
    # b1 = -np.imag(b1) is bad!  It converts the complex array to a real array.
    # Doing as shown below preserves the values as complex numbers.
    for ii in range(len(b1)):
        b1[ii] = -np.imag(b1[ii])
    
    return b1
