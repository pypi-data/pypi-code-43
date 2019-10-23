#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os.path
import numpy as np


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for the CoreFlo-LL model (https://doi.org/10.1093/gji/ggy545).  Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged (not used)
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """

    # Reading measure U
    filename = os.path.join(dataDirectory, 'CoreFlo-LL.1_coeffs.dat')
    if not os.path.isfile(filename):
        print('{} does not contain a CoreFlo-LL file !'.format(filename))

    full_data = np.genfromtxt(filename, comments="#", delimiter=',')
    full_Nu = (full_data.shape[1] - 1)//2
    # Truncating at 18 for now
    Lu = 18
    Nu = Lu*(Lu+2)
    times = full_data[:, 0]
    toro_data = full_data[:, 1:Nu+1]
    polo_data = full_data[:, full_Nu+1:full_Nu+Nu+1]
    flow_data = np.concatenate((toro_data, polo_data), axis=1)

    dataModel.addMeasure("U", "U", Lu, "km/yr", flow_data, times=times)

    return 0
