import os
import re
import numpy as np
from .default import giveMeasureTypeUnits


def getDataAndLmax(data, measureType):
    """ Returns the data and the lmax for the data and type of measure given.

    :param data: Array containing the measure data
    :type data: ndarray
    :param measureType: Type of the measure
    :type measureType: str
    :return: Data and the lmax computed from the data shape
    :rtype: ndarray, int
    """
    sizeData = np.where(data[0] != 0)[0].shape[0] - 1
    if measureType == "U":
        lmax = (-2+np.sqrt(4+4*sizeData/2))/2
        nk = int(lmax*(lmax+2))
        middle = int((data.shape[1] - 1)/2)
        data = data[:, np.r_[1:nk+1, middle+1:middle+nk+1]]
    else:
        lmax = (-2+np.sqrt(4+4*sizeData))/2
        nk = int(lmax*(lmax+2))
        data = data[:, 1:nk+1]
    # Check if computed lmax is int
    if not (int(lmax) == lmax):
        raise ValueError('[{}] File size ({}) is not multiple of lmax*(lmax + 2), lmax={}'.format(measureType, sizeData, lmax))

    return data, lmax


def load(dataDirectory, dataModel, keepRealisations):
    """ Loading function for pygeodyn files of ASCII format. Also adds the data to the dataModel.

    :param dataDirectory: Location of the pygeodyn files
    :type dataDirectory: os.path
    :param dataModel: Model in which to add the loaded measures
    :type dataModel: Model
    :param keepRealisations: If True, all realisations are kept in the data. Else, the data is averaged over the realisations
    :type keepRealisations: bool
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    points_to_cut = 1
    times = None

    valid_measures_names = ['DIFF', 'U', 'MF', 'SV', 'ER']
    state_type = 'Analysed' #'Computed'

    filelist = {}
    if keepRealisations:
        # Find all valid measures directories
        dirs_to_explore = [os.path.join(dataDirectory, x) for x in os.listdir(dataDirectory) if x in valid_measures_names]
        for realisation_dir in dirs_to_explore:
            for file in os.listdir(realisation_dir):
                matchfile = re.match('^'+state_type+'_Realisation(\d+)_(\w+)', file)
                if matchfile is not None:
                    irealisation = int(matchfile.group(1))
                    measureName = matchfile.group(2)
                    if measureName not in filelist:
                        filelist[measureName] = []
                    filelist[measureName].append([irealisation, os.path.join(realisation_dir, file)])

        # Check if realisation data was found
        if len(filelist) == 0:
            raise IOError('No realisation data was found in {}. Check the path or try to load the model with keepRealisation to False.'.format(dataDirectory))

        # Treat the filelist previously build by extracting the data and adding it to the model
        for measureName in filelist:
            measureData = None
            measureType, units = giveMeasureTypeUnits(measureName)

            for ireal, fileName in filelist[measureName]:
                print(ireal, " Reading", measureName, os.path.basename(fileName))

                # Reading realisation file
                sourceData = np.loadtxt(fileName)[points_to_cut:]

                # Extract times (once for all files)
                if times is None:
                    times = sourceData[:, 0]
                # Prevent from loading times that are not the same for all files
                if not np.allclose(times, sourceData[:, 0]):
                    print('[%s] Times are not the same in all files !', measureName)
                    return -1

                # Extract sourceData and the maximum sph. harm. coef lmax
                sourceData, lmax = getDataAndLmax(sourceData, measureType)
                if measureData is None:
                    # Initialise data to be of size [ntimes, ncoef, nrealisations]
                    measureData = np.zeros((sourceData.shape[0], sourceData.shape[1], len(filelist[measureName])))
                measureData[:, :, ireal] = sourceData

            # Add the data loaded to the model as measures
            dataModel.addMeasure(measureName, measureType, lmax, units,
                                 measureData, times=times)

    # Else read Mean+RMS for all values and add them to the model
    else:
        mean_dir = os.path.join(dataDirectory, 'Mean')
        rms_dir = os.path.join(dataDirectory, 'RMS')
        for file in os.listdir(mean_dir):
            matchfile = re.match('^'+state_type+'_mean_(\w+)', file)
            if matchfile is not None:
                measureName = matchfile.group(1)
                rms_file = os.path.join(rms_dir, state_type+'_rms_'+measureName+'.dat')
                mean_file = os.path.join(mean_dir, file)
                measureType, units = giveMeasureTypeUnits(measureName)

                # Reading measure file
                mean_data = np.loadtxt(mean_file)[points_to_cut:]
                rms_data = np.loadtxt(rms_file)[points_to_cut:]

                # Extract times
                times = mean_data[:, 0]

                mean_data, lmax = getDataAndLmax(mean_data, measureType)
                rms_data, lmax = getDataAndLmax(rms_data, measureType)

                dataModel.addMeasure(measureName, measureType, lmax, units,
                                     mean_data, rms_data, times)

    # Returns 0 if everything went well
    return 0
