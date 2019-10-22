import os
import numpy as np


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for Coupled-Earth data. Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged (not used)
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well
    :rtype: int
    """
    print("read MF CED data...")
    # Reading MF @ CMB in NS units
    gnmE = np.loadtxt(os.path.join(dataDirectory, "Cor_gnm_r_o.dat"))

    print("... CED gnm data read !!")

    # Detect lmax
    lmax = (-2+np.sqrt(4+4*gnmE.shape[1]))/2
    print("lmax B=", lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % gnmE.shape[1])
    else:
        lmax = int(lmax)

    nt = gnmE.shape[0]

    # Load times
    times = np.linspace(1, nt, nt)

    data = gnmE  #* 10**9  #  scale to nT ??
    print("number of epochs:", nt)
    dataModel.addMeasure("MF", "MF", lmax, "nT", data, times=times)

################# deals with gnm below CMB

    print("read MF mid-path data below CMB...")
    # Reading MF @ CMB in NS units
    gnmE = np.loadtxt(os.path.join(dataDirectory,"Cor_gnm_r_o-delta.dat"))

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
    dgnmE = np.loadtxt(os.path.join(dataDirectory,"Cor_dgnm_r_o.dat"))

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
    tnmsnm = np.loadtxt(os.path.join(dataDirectory, "Cor_tnmsnm_r_o.dat"))

    print("... CED tnm+snm data read !!")

    # Detect lmax
    lmax = (-2+np.sqrt(4+4*(tnmsnm.shape[1])/2))/2
    print("lmax U=", lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to 2*lmax*(lmax+2)" % data.shape[1])
    else:
        lmax = int(lmax)

    # /!\ not the same sign convention from JA for tnm,snm (need to invert)
    data = tnmsnm * (-1)  # scale in km/yr
    dataModel.addMeasure("U", "U", lmax, "km/yr", data, times=times)

    return 0
