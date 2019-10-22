#-*- coding: utf-8 -*-
import glob
import h5py
import os
import numpy as np
from .default import giveMeasureTypeUnits


def load(dataDirectory, dataModel, keepRealisations):
    """ Loading function for pygeodyn files of hdf5 format. Also adds the data to the dataModel.

    :param dataDirectory: Location of the pygeodyn files
    :type dataDirectory: os.path
    :param dataModel: Model in which to add the loaded measures
    :type dataModel: Model
    :param keepRealisations: If True, all realisationsr are kept in the data. Else, the data is averaged over the realisations
    :type keepRealisations: bool
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    firstpoint = 3

    measures_to_load = ['MF', 'SV', 'ER', 'U']

    hdf5_files = glob.glob(os.path.join(dataDirectory, '*.hdf5'))
    if len(hdf5_files) == 0:
        raise IOError('No hdf5 file was found in {} !'.format(dataDirectory))
    # Assuming that the file to read is the first one
    hdf_filename = hdf5_files[0]
    print('Reading:', hdf_filename)

    with h5py.File(hdf_filename) as hdf_file:
        computed_data = hdf_file['computed']

        times = np.array(computed_data['times'])[firstpoint:]

        for measureName, measureData in computed_data.items():
            if measureName not in measures_to_load:
                continue
            else:
                measureType, units = giveMeasureTypeUnits(measureName)

                # Move realisation axis to last place to have data of form [ntimes, ncoef, nreal] (originally [nreal, ntimes, ncoef])
                # Remove firstpoints
                formattedData = np.moveaxis(measureData, 0, -1)[firstpoint:]

                if measureName == 'MF':
                    lmax = hdf_file.attrs['Lb']
                elif measureName == 'U':
                    lmax = hdf_file.attrs['Lu']
                else:
                    lmax = hdf_file.attrs['Lsv']

                if keepRealisations:
                    dataModel.addMeasure(measureName, measureType, lmax, units,
                                         formattedData, times=times)
                else:
                    meanData = formattedData.mean(axis=2)
                    rmsData = formattedData.std(axis=2)
                    dataModel.addMeasure(measureName, measureType, lmax, units,
                                         meanData, rmsData, times)

    # Returns 0 if everything went well
    return 0
