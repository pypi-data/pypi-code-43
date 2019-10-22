import numpy as np
import scipy.io


def load(dataDirectory, dataModel, keepRealisations=False):
    """ Loading function for mid-path model. Also adds the data to the dataModel.

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
    print("Loading mid-path data !!")

    str_dir_file = dataDirectory + "/time_midpath.mat"
    print(str_dir_file)
    tmp = scipy.io.loadmat(str_dir_file, squeeze_me=True, struct_as_record=False)  # read matlab 6 binary file into dictionary

    times = tmp["time"].T
    times = np.ascontiguousarray(times)

    nt = times.shape[0]

    print("read MF mid-path data...")
    # Reading MF @ CMB in NS units
    str_dir_file = dataDirectory + "/gnm_midpath.mat"
    tmp = scipy.io.loadmat(str_dir_file, squeeze_me=True,
                           struct_as_record=False)  # read matlab 6 binary file into dictionary
    gnmE = tmp["gnm"]
    gnmE = np.ascontiguousarray(gnmE)
    #    gnmE = np.loadtxt(os.path.join(dataDirectory,"gnm_midpath.dat"))

    print("... mid-path gnm data read !!")

    # detect lmax
    lmax = (-2 + np.sqrt(4 + 4 * gnmE.shape[1])) / 2
    print("lmax=", lmax)
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to lmax*(lmax+2)" % gnmE.shape[1])
    else:
        lmax = int(lmax)

    n = lmax * (lmax + 2)

    data = gnmE * 10 ** 9  # scale to nT ??
    dataModel.addMeasure("MF", "MF", lmax, "nT", data, times=times)

    # now deals with tnm, snm
    str_dir_file = dataDirectory + "/snm_midpath.mat"
    tmp = scipy.io.loadmat(str_dir_file, squeeze_me=True, struct_as_record=False)  # read matlab 6 binary file into dictionary
    snm = tmp["snm"]
    snm = np.ascontiguousarray(snm)

    str_dir_file = dataDirectory + "/tnm_midpath.mat"
    tmp = scipy.io.loadmat(str_dir_file, squeeze_me=True, struct_as_record=False)  # read matlab 6 binary file into dictionary
    tnm = tmp["tnm"]
    tnm = np.ascontiguousarray(tnm)

    print("... mid-path tnm+snm data read !!")

    data = np.concatenate((tnm, snm), axis=1)
    print(data.shape)

    # detect lmax
    lmax = (-2 + np.sqrt(4 + 4 * (data.shape[1]) / 2)) / 2
    if int(lmax) != lmax:
        raise ValueError("Data length %i does not correspond to 2*lmax*(lmax+2)" % data.shape[1])
    else:
        lmax = int(lmax)

    data = data * 10 ** 0  # scale to km/yr ??
    dataModel.addMeasure("U", "U", lmax, "km/yr", data, times=times)

    return 0
