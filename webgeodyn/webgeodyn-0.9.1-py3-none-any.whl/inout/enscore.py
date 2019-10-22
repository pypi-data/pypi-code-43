import os
import re
import numpy as np


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for the Gillet_gnm_2015 model.  Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged (not used)
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    modelname = "mod013"

    # Reading measure U from ens flow models
    # List realisation
    realisations = []
    for file in os.listdir(dataDirectory):
        matchfile = re.match('^'+modelname+'_real(.*[^.zip])$', file)
        if matchfile is not None:
            realisations.append(os.path.join(dataDirectory, file))

    if len(realisations) == 0:
        print('No realisations were found while loading ENS-CORE ! Aborting loading...')
        return -1

    g = None
    irealisation = 0
    for file in realisations:
        with open(file) as f:
            # Read parameters
            ntimes, lmax = [int(x) for x in f.readline().split()]
            times = np.zeros((ntimes,))
            if g is None:
                g = np.zeros((len(realisations), ntimes, 2*lmax*(lmax+2)))

            for i in range(ntimes):
                times[i] = float(f.readline())
                k = 0
                while k < 2*lmax*(lmax+2):
                    line = f.readline()
                    temp = [float(x) for x in line.split()]
                    g[irealisation, i, k:k+len(temp)] = temp
                    k += len(temp)
        irealisation += 1

    if keepRealisations:
        # Move realisation axis to last place to have data of form [ntimes, ncoef, nreal] (originally [nreal, ntimes, ncoef])
        formatted_g = np.moveaxis(g, 0, -1)
        dataModel.addMeasure("U", "U", lmax, "km/yr", formatted_g, times=times)
    else:
        dataModel.addMeasure("U", "U", lmax, "km/yr", np.mean(g, axis=0), np.std(g, axis=0), times)
    return 0
