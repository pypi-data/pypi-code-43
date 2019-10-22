from scipy import misc
import numpy as np

import timestep as tsp
import math

def plms(Lsv,Lb,Lu, tmax):
    """ initialize the plms (and their derivatives) that enter radmats
    : input:
        - truncation degrees Lsv, Lb and Lu for db/dt, b and
        - tmax
    : outputs: gauth, psv, pb, pu and their 1st and 2nd derivatives
    """
    pmax=2*tmax
    gauth = np.zeros((tmax), order='F')
    gauwt = np.zeros((tmax), order='F')
    tsp.init.gauleg (-1.0, 1.0, gauth, gauwt, tmax)
    nsv=Lsv*(Lsv+2)
    nb=Lb*(Lb+2)
    nu=Lu*(Lu+2)
    LLsv=(Lsv+1)*(Lsv+2)/2
    LLsv=np.int(LLsv)
    LLb=(Lb+1)*(Lb+2)/2
    LLb=np.int(LLb)
    LLu=(Lu+1)*(Lu+2)/2
    LLu=np.int(LLu)

    psv = np.zeros((LLsv,tmax), order='F')
    dpsv = np.zeros((LLsv,tmax), order='F')
    d2psv = np.zeros((LLsv,tmax), order='F')
    pb = np.zeros((LLb,tmax), order='F')
    dpb = np.zeros((LLb,tmax), order='F')
    d2pb = np.zeros((LLb,tmax), order='F')
    pu = np.zeros((LLu,tmax), order='F')
    dpu = np.zeros((LLu,tmax), order='F')
    d2pu = np.zeros((LLu,tmax), order='F')
    for i in range (tmax):
        tsp.init.plmbar2 (psv[:,i], dpsv[:,i], d2psv[:,i], gauth[i], Lsv, 1)
        tsp.init.plmbar2 (pu[:,i], dpu[:,i], d2pu[:,i], gauth[i], Lu, 1)
        tsp.init.plmbar2 (pb[:,i], dpb[:,i], d2pb[:,i], gauth[i], Lb, 1)

    for i in range (tmax):
        gauth[i]= math.acos(gauth[i])

    return gauth, gauwt, psv, dpsv, d2psv, pb, dpb, d2pb, pu, dpu, d2pu
