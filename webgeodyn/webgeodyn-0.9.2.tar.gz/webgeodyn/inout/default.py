import os
import re
import numpy as np


def giveMeasureTypeUnits(measureName, measureType=None):
    """ Given a measure name, returns its units and its type.

    :param measureName: Name of the measure
    :type measureName: str
    :param measureType: Type of the measure (optional)
    :type measureType: str
    :return: A 2-tuple containing the type of the measure and the units
    :rtype: str,str
    """
    if measureType is None:
        if measureName == "ER" or measureName == "DIFF":
            measureType = "SV"
        else:
            measureType = measureName

    if measureType == "MF":
        units = "nT"
    elif measureType == "SV":
        units = "nT/yr"
    elif measureType == "U":
        units = "km/yr"
    elif measureType == "DIVHU":
        units = "/yr"
    else:
        print("Measure name not recognized for %s in giveMeasureTypeUnits. Setting units to nT.", measureName)
        units = "nT"

    return measureType, units


def load(dataDirectory, dataModel, keepRealisations=True):
    """ Loading function for default type.  Also adds the data to the dataModel.

    The files to load should have one of the following namepatterns :
    - 'MeasureType_iRealisation.dat' (e.g. MF_0001.dat [type should be 'MF' or 'SV' or 'U'])
    - 'MeasureName-MeasureType_iRealisation.dat' (e.g. ER-SV_0001.dat ; MagField-MF_0001.dat ; ... [type should be 'MF' or 'SV' or 'U'])

    In addition :
    - Time should be in "times.dat"
    - Units must be : nT, km, yr.

    :param dataDirectory: location of the files to load
    :type dataDirectory: str
    :param dataModel: data model to which the loaded data are added
    :type dataModel: Model
    :param keepRealisations: indicates if realisations must be kept or not (not used)
    :type keepRealisations: bool
    :return: 0 if no errors are raised
    :rtype: int
    """

    if os.path.isfile(os.path.join(dataDirectory, "times.dat")):
        times = np.loadtxt(os.path.join(dataDirectory, "times.dat"))
    else:
        raise ValueError("%s does not contain times.dat file, did you forget to specify dataFormat?" % dataDirectory)

    measures = {}
    for file in os.listdir(dataDirectory):
        print("[%s]" % file)
        matchfile = re.match('^(.*)_(.*).dat$', file)

        if matchfile is not None:
            if len(matchfile.group(1).split('-')) == 2:
                measureName, measureType = matchfile.group(1).split('-')
            else:
                measureName = matchfile.group(1).split('-')
                measureType = measureName
            irealisation = int(matchfile.group(2))-1
            print("   ", measureName, measureType, irealisation)

            if measureName not in measures:
                measures[measureName] = {"type": measureType, "filelist": []}
            measures[measureName]["filelist"].append([irealisation, file])

    if len(measures) == 0:
        raise ValueError("Unable to read %s as default format: no file matching *_*.dat" % dataDirectory)

    for measureName in measures:
        measureData = None
        measureType = measures[measureName]["type"]
        nrealisations = len(measures[measureName]["filelist"])
        measureType, units = giveMeasureTypeUnits(measureName, measureType)
        for ireal, fileName in measures[measureName]["filelist"]:
            # Reading realisation file
            sourceData = np.loadtxt(os.path.join(dataDirectory, fileName))

            # Compute lmax
            if measureType == 'U':
                lmax = (-2+np.sqrt(4+4*(sourceData.shape[1])/2))/2
            else:
                lmax = (-2+np.sqrt(4+4*sourceData.shape[1]))/2

            if int(lmax) != lmax:
                if measureType == 'U':
                    raise ValueError("Data length %i in file %s does not correspond to any 2*lmax*(lmax+2)" % (sourceData.shape[1], fileName))
                else:
                    raise ValueError("Data length %i in file %s does not correspond to any lmax*(lmax+2)" % (sourceData.shape[1], fileName))
            else:
                lmax = int(lmax)

            if times.shape[0] != sourceData.shape[0]:
                raise ValueError('times.dat file give %i times, %s file contains %i times' % (times.shape[0], fileName, sourceData.shape[0]))

            if measureData is not None:
                measureData[:, :, ireal] = sourceData
            else:
                if nrealisations > 1:
                    # Initialise data to be of size [ntimes, ncoef, nrealisations]
                    measureData = np.zeros((sourceData.shape[0], sourceData.shape[1], nrealisations))
                    measureData[:, :, ireal] = sourceData
                else:
                    measureData = sourceData

            dataModel.addMeasure(measureName, measureType, lmax, units, measureData, times=times)

    # If everything went fine
    return 0


def save(dataDirectory, dataModel, forceOverwrite=False):
    """ Saves the given model in .dat files.

    :param dataDirectory: location of the saving directory
    :type dataDirectory: str
    :param dataModel: data model to save
    :type dataModel: Model
    :param forceOverwrite: force the overwrite of existing files that bear the same name
    :type forceOverwrite: bool
    :return: 0 if no errors are raised
    :rtype: int

    """
    dataDirectory = os.path.realpath(dataDirectory)

    if not forceOverwrite:
        # Test the existence of all file names before starting to write
        if os.path.isfile(os.path.join(dataDirectory, "times.dat")):
            if not forceOverwrite:
                raise ValueError("%s already contains a times.dat file, please set forceOverwrite to True if you wish to overwrite it." % dataDirectory)
        for measureName in dataModel.measures:
            measure = dataModel.measures[measureName]
            measureType = measure.measureType
            if measure.has_realisations:
                for ireal in range(measure.data.shape[2]):
                    fileName = measureName + "-" + measureType + "_" + str(ireal+1).zfill(6) + ".dat"
                    if os.path.isfile(os.path.join(dataDirectory, fileName)):
                        raise ValueError("%s already contains a file named %s, please set forceOverwrite to True if you wish to overwrite it."
                                         % (dataDirectory, fileName))
            else:
                fileName = measureName + "-" + measureType + "_" + str(1).zfill(6) + ".dat"
                if os.path.isfile(os.path.join(dataDirectory, fileName)):
                    raise ValueError("%s already contains a file named %s, please set forceOverwrite to True if you wish to overwrite it."
                                     % (dataDirectory, fileName))

    # Write files
    os.makedirs(dataDirectory, exist_ok=True)
    print("Saving times to", os.path.join(dataDirectory, "times.dat"))
    np.savetxt(os.path.join(dataDirectory, "times.dat"), dataModel.times)
    for measureName in dataModel.measures:
        measure = dataModel.measures[measureName]
        measureType = measure.measureType
        print("Saving", measureName, "to",
              os.path.join(dataDirectory, measureName + "-" + measureType + "_######.dat"))
        if measure.has_realisations:
            for ireal in range(measure.data.shape[2]):
                fileName = os.path.join(dataDirectory, measureName + "-" + measureType + "_" + str(ireal+1).zfill(6) + ".dat")
                np.savetxt(fileName, measure.data[:, :, ireal])
        else:
            fileName = os.path.join(dataDirectory,measureName + "-" + measureType + "_" + str(1).zfill(6) + ".dat")
            np.savetxt(fileName, measure.data)

    # If everything went fine
    return 0
