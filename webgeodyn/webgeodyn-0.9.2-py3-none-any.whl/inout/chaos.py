import os
import numpy as np
from scipy.interpolate import BSpline
import glob


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for CHAOS-6 model. Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged (not used)
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    # Custom lmax for displaying core field & secular variation (SV)
    lmax_custom = {"MF": 13, "SV": 16}
    dataDirectory = os.path.normpath(dataDirectory)
    chaos_files = glob.glob(os.path.join(dataDirectory, "CHAOS-6*_spline-coefficients.dat"))

    if len(chaos_files) == 0:
        raise IOError('No CHAOS-6 file was found in {}'.format(dataDirectory))

    # Take the most recent extension
    fname = sorted(chaos_files, reverse=True)[0]

    # Open the file and print the header
    f = open(fname)
    print(f.readline())

    # Read parameters
    lmax, nspl, jorder = [int(x) for x in f.readline().split()]
    print(lmax, nspl, jorder)

    # Read times
    knotstimes = np.zeros((nspl+jorder,))
    for i in range(nspl+jorder):
        knotstimes[i] = float(f.readline())

    # Read g spline coefficient values
    gt = np.zeros((lmax*(lmax+2), nspl))
    for i in range(nspl):
        for j in range(lmax*(lmax+2)):
            gt[j, i] = float(f.readline())

    f.close()
    # End of reading of the CHAOS file.

    times = np.copy(knotstimes[jorder-1:-(jorder-1)])
    ntimes = times.shape[0]
    g = np.zeros((ntimes, lmax*(lmax+2)))
    dg = np.zeros((ntimes, lmax*(lmax+2)))
    for j in range(lmax*(lmax+2)):
        # Build g and its derivative from splines
        spl = BSpline(knotstimes, gt[j, :], jorder-1)
        dspl = spl.derivative()
        g[:, j] = spl(times)
        dg[:, j] = dspl(times)

    # Add data for MF and SV up to the custom lmax
    lmax_b = lmax_custom["MF"]
    lmax_sv = lmax_custom["SV"]
    dataModel.addMeasure("MF lmax={}".format(lmax_b), "MF", lmax_b, "nT", g, times=times)
    dataModel.addMeasure("SV lmax={}".format(lmax_sv), "SV", lmax_sv, "nT/yr", dg, times=times)
    # Add data for MF and SV up to the lmax from CHAOS
    dataModel.addMeasure("MF", "MF", lmax, "nT", g, times=times)
    dataModel.addMeasure("SV", "SV", lmax, "nT/yr", dg, times=times)

    return 0
