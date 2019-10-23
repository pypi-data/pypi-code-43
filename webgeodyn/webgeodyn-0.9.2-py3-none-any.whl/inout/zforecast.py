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


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for zForecast files. Also adds the data to the dataModel.

    :param dataDirectory: Location of the zForecast files
    :type dataDirectory: os.path
    :param dataModel: Model in which to add the loaded measures
    :type dataModel: Model
    :param keepRealisations: If True, all realisations are kept in the data. Else, the data is averaged over the realisations
    :type keepRealisations: bool
    :return: 0 if everything went well, -1 otherwise
    :rtype: int
    """
    firstpoint = 3  # CUT FIRST 3 points
    times = None

    filelist = {}
    for file in os.listdir(dataDirectory):
        # If realisations are kept, only build a filelist that will be treated afterwards
        if keepRealisations:
            matchfile = re.match('^ZReal_Forecast_Analysis_(.*)_(.*).dat$', file)
            if matchfile is not None:
                measureName = matchfile.group(1)
                irealisation = int(matchfile.group(2))-1
                if measureName not in filelist:
                    filelist[measureName] = []
                filelist[measureName].append([irealisation, file])

        # Else read Mean+RMS for all values and add them to the model
        else:
            matchfile = re.match('^ZForecast_Analysis_(.*).dat$', file)
            if matchfile is not None:
                measureName = matchfile.group(1)
                datafile = os.path.join(dataDirectory, file)
                rms_datafile = os.path.join(dataDirectory, "ZRMS_" + measureName + "_Analysis.dat")
                measureType, units = giveMeasureTypeUnits(measureName)

                # Reading measure file
                sourceData = np.loadtxt(datafile)[firstpoint:]
                sourceDataRMS = np.loadtxt(rms_datafile)[firstpoint:]

                # Extract times (once for all files)
                if times is None:
                    print("Ignoring first %i points" % firstpoint)
                    times = sourceData[:, 0]
                    itimes_analysis = np.arange((302-firstpoint) % 3, times.shape[0], 3)
                    times_analysis = times[itimes_analysis]
                    print("Found %i analysis time steps from %f to %f" % (times_analysis.shape[0],
                                                                          times_analysis[0], times_analysis[-1]))

                # Prevent from loading times that are not the same for all files
                if not np.allclose(times, sourceData[:, 0]) or not np.allclose(times, sourceDataRMS[:, 0]):
                    print('[%s] Times are not the same in all files', measureName)
                    return -1

                sourceData, lmax = getDataAndLmax(sourceData, measureType)
                sourceDataRMS, lmax = getDataAndLmax(sourceDataRMS, measureType)

                rmsdata = np.zeros((sourceDataRMS[itimes_analysis].shape[0],
                                    sourceDataRMS[itimes_analysis].shape[1], 2))
                rmsdata[:, :, 1] = sourceDataRMS[itimes_analysis]
                rmsdata[:, :, 0] = sourceDataRMS[itimes_analysis-1]

                dataModel.addMeasure(measureName, measureType, lmax, units,
                                     sourceData[itimes_analysis], rmsdata, times_analysis)

    # Treat the filelist previously build by extracting the data and adding it to the model
    if keepRealisations:
        for measureName in filelist:
            measureData = None
            measureType, units = giveMeasureTypeUnits(measureName)

            for ireal, fileName in filelist[measureName]:
                print(ireal, " Reading", measureName, fileName)
                datafile = os.path.join(dataDirectory, fileName)

                # Reading realisation file
                sourceData = np.loadtxt(datafile)[firstpoint:]

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

    # Returns 0 if everything went well
    return 0
