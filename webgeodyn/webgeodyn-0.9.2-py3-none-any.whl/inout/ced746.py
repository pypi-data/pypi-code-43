
# CLEAR COMPILED WEBGEODYN FILES
import os
import webgeodyn

dir_name = webgeodyn.__path__[0]

for root, dir, files in os.walk(dir_name):
    for file in files:
        if file.endswith(".pyc"):
            os.remove(os.path.join(root,file))

# CLEAR COMPILED WEBGEODYN FILES
#############################################################

import os
import re
import numpy as np
from webgeodyn.processing import spectra
from webgeodyn.filters import time
from webgeodyn.constants import rE, rC
from webgeodyn.models import Models, Model
import scipy.io

def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for Coupled-Earth data."""
    #load times
    print("!! enter coupled-earth data !!")

#    times = np.loadtxt(os.path.join(dataDirectory,"time_midpath.dat"))
#    times=np.linspace(1,1000,1000)

#    nt=times.shape[0]
#    print(nt)
################# deals with gnm @ CMB

    print("read MF mid-path data...")
    # Reading MF @ CMB in NS units
    gnmE = np.loadtxt(os.path.join(dataDirectory,"gnm"))

    print("... mid-path gnm data read !!")

    # Detect lmax
    lmax = (-2+np.sqrt(4+4*gnmE.shape[1]))/2
    print("lmax B=",lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % gnmE.shape[1])
    else:
        lmax = int(lmax)

    n=lmax*(lmax+2)
    nt=gnmE.shape[0]

    # Load times
    times=np.linspace(1, nt, nt)

    data = gnmE #* 10**9 # scale to nT ??
    print("number of epochs:", nt)
    dataModel.addMeasure("MF", "MF", lmax, "nT", data, times=times)

################# deals with gnm below the CMB

    print("read MF mid-path data below CMB...")
    # Reading MF @ CMB in NS units
    gnmE = np.loadtxt(os.path.join(dataDirectory,"gnm_below"))

    print("... mid-path gnm data below CMB read !!")

    # Detect lmax
    lmax = (-2+np.sqrt(4+4*gnmE.shape[1]))/2
    print("lmax B=",lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % gnmE.shape[1])
    else:
        lmax = int(lmax)

    n=lmax*(lmax+2)
    nt=gnmE.shape[0]

    # Load times
    times=np.linspace(1, nt, nt)

    data = gnmE #* 10**9 # scale to nT ??
    print("number of epochs:", nt)
    dataModel.addMeasure("MFsub", "MF", lmax, "nT", data, times=times)

################# deals with dgnm/dt

    print("read SV mid-path data...")
    # Reading MF @ CMB in NS units
    dgnmE = np.loadtxt(os.path.join(dataDirectory,"dgnm"))

    print("... mid-path dgnm/dt data read !!")

    # Detect lmax
    lmax = (-2+np.sqrt(4+4*dgnmE.shape[1]))/2
    print("lmax B=",lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % dgnmE.shape[1])
    else:
        lmax = int(lmax)

    n=lmax*(lmax+2)
    nt=dgnmE.shape[0]

    # Load times
    times=np.linspace(1, nt, nt)

    data = dgnmE #* 10**9 # scale to nT ??
    print("number of epochs:", nt)
    dataModel.addMeasure("SV", "SV", lmax, "nT/yr", data, times=times)

################# now deals with tnm, snm

    # Reading flow U @ CMB in NS units
    tnmsnm = np.loadtxt(os.path.join(dataDirectory, "tnmsnm"))
    print(tnmsnm.shape)
    print(gnmE.shape)

    print("... mid-path tnm+snm data read !!")

    # Detect lmax
    lmax = (-2+np.sqrt(4+4*(tnmsnm.shape[1])/2))/2
    print("lmax U=",lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to 2*lmax*(lmax+2)" % data.shape[1])
    else:
        lmax = int(lmax)

    data = tnmsnm  # scale in km/yr
    dataModel.addMeasure("U", "U", lmax, "km/yr", data, times=times)
