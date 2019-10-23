import os
import numpy as np
import glob


def load(dataDirectory, dataModel, keepRealisations=False):
    """
    Loading function for the archeomagnetic models (COVARCH et COVLAKE). Also adds the data to the dataModel.

    :param dataDirectory: directory where the data is located
    :type dataDirectory: str (path)
    :param dataModel: Model to which the data should be added
    :type dataModel: Model
    :param keepRealisations: indicating if realisations should be kept or averaged
    :type keepRealisations: bool (default: False)
    :return: 0 if everything went well, -1 if inconsistency in dates
    :rtype: int
    """
    mean_file_name = glob.glob(os.path.join(dataDirectory, 'Mean_*'))[0]
    rms_file_name = glob.glob(os.path.join(dataDirectory, 'RMS_*'))[0]

    # Read metadata from mean file
    mean_file = open(mean_file_name)
    # Skip first line
    mean_file.readline()
    # Read second line that contain metadata
    meta_data = mean_file.readline().split()
    mean_file.close()

    Lb = int(meta_data[0])
    nb_dates = int(meta_data[1])
    dates = np.array(meta_data[2:], dtype=float)

    # Check consistency
    if len(dates) != nb_dates:
        print('Got a number of dates ({}) different than what was announced in the header ({}) !'.format(len(dates), nb_dates))
        return -1

    # Create magnetic field quantities
    measure_name = "MF"
    units = "nT"
    Nb = Lb * (Lb + 2)

    # Raw data is succession of coeffs grouped 4 by line
    # Everything is read and then reshaped to get the proper coef by date
    if keepRealisations:
        real_folder = os.path.join(dataDirectory, 'ensemble')
        real_files = glob.glob(os.path.join(real_folder, 'real_*'))
        nb_reals = len(real_files)

        # Storing array for realisation data
        real_data = np.zeros((nb_dates, Nb, nb_reals))

        for file in real_files:
            i_real = int(file.split('_')[-1]) - 1
            raw_data = np.genfromtxt(file, skip_header=2, dtype=np.float64)
            reshaped_data = np.reshape(raw_data, (nb_dates, Nb), order='C')
            real_data[:, :, i_real] = reshaped_data

        dataModel.addMeasure(measure_name, measure_name, Lb, units, real_data, times=dates)

    else:
        raw_mean_data = np.genfromtxt(mean_file_name, skip_header=2)
        mean_data = np.reshape(raw_mean_data, (nb_dates, Nb), order='C')

        raw_rms_data = np.genfromtxt(rms_file_name, skip_header=2)
        rms_data = np.reshape(raw_rms_data, (nb_dates, Nb), order='C')

        dataModel.addMeasure(measure_name, measure_name, Lb, units, mean_data, rms_data, dates)

    return 0
