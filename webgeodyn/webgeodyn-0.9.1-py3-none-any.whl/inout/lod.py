#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import glob
import os
import numpy as np


def load(dataDirectory, dataModel, keepRealisations=True):
    """
    :param dataDirectory: location of the files to load
    :type dataDirectory: str
    :param dataModel: data model to which the loaded data are added
    :type dataModel: Model
    :param keepRealisations: indicates if realisations must be kept or not (not used)
    :type keepRealisations: bool
    :return: 0 if no errors are raised
    :rtype: int
    """

    dat_files = glob.glob(os.path.join(dataDirectory, '*.dat'))

    if len(dat_files) == 0:
        raise IOError("No .dat file was found in {}".format(dataDirectory))

    lod_data = np.genfromtxt(dat_files[0])

    dataModel.times = lod_data[:, 0]
    dataModel.notSH_measures['LOD'] = lod_data[:, 1]

    # If everything went fine
    return 0
