from scipy import misc
import numpy as np
from webgeodyn.constants import rE, rC
#import matplotlib.pyplot as plt

def spatial_spectrum_mag(array2D,nt,lmax):

    [n1,nt1] = array2D.shape
    if nt1 != nt:
        raise ValueError("array2D dimension nt1= %i does not correspond to nt= %i" % (nt1,nt))

    n = lmax*(lmax+2)
    if n1 != n:
        raise ValueError("array2D dimension np= %i does not correspond to lmax*(lmax+2)= %i" % (n1,n))

    fac_l = np.zeros((lmax))
    fac_c2a = np.zeros((lmax))
    for j in range(lmax):
        l=j+1
        fac_l[j] = l+1
        fac_c2a[j] = (rC/rE)**(2*l+4)

    '''
    # gnm: from core surface to earth's surface
    gnm = np.zeros((n,nt))
    k=0
    for j in range(lmax):
        l=j+1
        for m in range (2*l+1):
            gnm[k,:] = array2D[k,:]*np.sqrt(fac_c2a[j])
            k=k+1
    '''

    S = np.zeros((lmax,nt))
    for i in range(nt):
        k=0
        for j in range(lmax):
            l=j+1
            tmp=0.
            for m in range (2*l+1):
                #tmp = tmp + fac_l[j]*gnm[k,i]**2
                tmp = tmp + fac_l[j]*array2D[k,i]**2
                k=k+1
            S[j,i] = tmp

    return S

def spatial_spectrum_flow(array2D,nt,lmax):

    [n1,nt1] = array2D.shape
    if nt1 != nt:
        raise ValueError("array2D dimension nt1= %i does not correspond to nt= %i" % (nt1,nt))

    nts = lmax*(lmax+2)
    n = 2*nts
    if n1 != n:
        raise ValueError("array2D dimension np= %i does not correspond to 2*lmax*(lmax+2)= %i" % (n1,n))

    fac_l = np.zeros((lmax))
    fac_c2a = np.zeros((lmax))
    for j in range(lmax):
        l=j+1
        fac_l[j] = l*(l+1)/(2*l+1)

    S = np.zeros((lmax,nt))
    for i in range(nt):
        k=0
        for j in range(lmax):
            l=j+1
            tmp=0.
            for m in range (2*l+1):
                tmp = tmp + fac_l[j]*(array2D[k,i]**2 + array2D[k+nts,i]**2)
                k=k+1
            S[j,i] = tmp

    return S
