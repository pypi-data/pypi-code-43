import os
import numpy as np


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for XSHELLS(?) data. Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged (not used)
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    # load times
    times = np.loadtxt(os.path.join(dataDirectory, "T_yr_S1.dat"))

    # Reading MF in nT
    data = np.loadtxt(os.path.join(dataDirectory, "GNM_top_nT_S1.dat"))
    # detect lmax
    lmax = (-2 + np.sqrt(4 + 4 * data.shape[1])) / 2
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % data.shape[1])
    else:
        lmax = int(lmax)
    dataModel.addMeasure("MF", "MF", lmax, "nT", data, times=times)

    # Reading MF in km/yr
    data = np.loadtxt(os.path.join(dataDirectory, "TNM_kmperyr_S1.dat"))
    lmax = (-2 + np.sqrt(4 + 4 * (data.shape[1]) / 2)) / 2
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to 2*lmax*(lmax+2)" % data.shape[1])
    else:
        lmax = int(lmax)
    dataModel.addMeasure("U", "U", lmax, "km/yr", data, times=times)

    # Reading SV diff in nT/yr
    # data = np.loadtxt(os.path.join(dataDirectory,"SVdiffNM_nTperyr_S1.dat")) # data est un array
    # lmax = (-2+np.sqrt(4+4*data.shape[1]))/2
    # if int(lmax) != lmax:
    #     raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % data.shape[1])
    # else:
    #     lmax = int(lmax)
    # dataModel.addMeasure("Diff","SV",lmax,"nT/yr",data,times=times)

    return 0
