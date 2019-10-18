""""Module to generate .h files with structure arrays"""

import numpy as np
from scipy import constants as sc


def write_header_string(array, name):
    # Write the array strings.
    tosave = 'const static double %s[%d] = {' % (name, len(array))
    for val in array:
        tosave += '%.3e, ' % val
    tosave = tosave[:-2] + '};\n'
    return tosave


def make_3d_header(path, name=None):
    """Write a LIME header for a 3D model."""

    if not type(path) is str:
        raise TypeError("Must be a path to a model.")
    if '.npy' in path:
        data = np.load(path)
    else:
        data = np.loadtxt(path)

    # Input array should have format: data.shape = (ntheta, params, ncells),
    # where ncells = nrvals x nzvals, as in the 2D case. The params are:
    #
    #   0 - radius [au]
    #   1 - altitude [au]
    #   2 - density [g / cm^3]
    #   3 - gas temperature [K]
    #   4 - molecular abundance [wrt n(H2)]

    if data.ndim == 2:
        print("Found 2D model.")
        make_2d_header(path, name)
        return
    if not all([data.shape[1] <= d for d in data.shape]):
        raise ValueError("Wrong array shape.")

    # Note that density must be converted to LIME units [n(H2) / m^3].

    data[:, 2] /= 2.37 * sc.m_p * 1e9

    # Make sure that each column has a cell at the midplane: z = 0.

    for aslice in data:
        for r in np.unique(aslice[0]):
            idx = aslice[1][aslice[0] == r].argmin()
            aslice[1][idx] = 0.0

    # Write the array names.

    arrnames = ['c1arr', 'c2arr', 'c3arr', 'dens', 'temp', 'abund']
    hstring = ''
    for i, array in enumerate(data):
        hstring += write_header_string(array, arrnames[i])

    return data


def make_2d_header(
        path, name=None,
        density_already_in_cm3=False, abundance_already_relative=True,
        isotope=1,
        # dust2gas=False,
):
    """Write the header file."""

    # Check to find the dimension of the input array. If arr.ndim == 2 then we
    # assume that there is no azimuthal dependence. Otherwise, we write a two
    # dimensional array for LIME.

    if not isinstance(path, str):
        raise TypeError("Must be path to chemical model.")
    if path.endswith('.npy'):
        data = np.load(path)
    elif path.endswith('.out'):
        data = np.loadtxt(path, skiprows=3).T
    else:
        data = np.loadtxt(path).T
    print(data)
    # data = np.array([param[data[2] > 0] for param in data])
    print(data.shape)
    if data.shape[0] > data.shape[1]:
        data = data.T

    # Check that the arrays are correctly sized.
    # If it is the 8 parameter value, remove the average grainsize.

    if data.shape[0] == 7:
        datalong = True
    elif data.shape[0] == 8:
        data = np.vstack([data[:5], data[6:]])
        datalong = True
    elif data.shape[0] == 5:
        datalong = False
    else:
        raise ValueError("Must be either a 5 or 7 or 8 column file.")

    # Make the conversions to LIME appropriate units:
    # Main collider density (H2) is in [m^-3].
    # Relative abundance is with respect to the main collider density.
    # Temperatures are all in [K].

    with np.errstate(divide='ignore'):
        if not density_already_in_cm3:
            print("Converting H2 density to cm-3 from g/cm-3")
            data[2] /= 2.37 * sc.m_p * 1e3
        if not abundance_already_relative:
            print("Converting species abundance to relative")
            data[-1] = data[-1] / data[2]
        data[2] *= 1e6
        if isotope != 1.:
            print(f"Multiply abundances by {isotope}")
            data[-1] *= isotope
        if datalong:
            data[5] = np.where(data[5] != 0.0, 1. / data[5], 100.)
        data = np.where(~np.isfinite(data), 0.0, data)

    # Make sure that each column has a cell at the midplane: z = 0.

    for r in np.unique(data[0]):
        idx = data[1][data[0] == r].argmin()
        data[1][idx] = 0.0

    # Make sure these are the same as in the template file.
    # Note that we skip the average grainsize array.

    if datalong:
        arrnames = ['c1arr', 'c2arr', 'dens', 'temp', 'dtemp',
                    'gastodust', 'abund']
    else:
        arrnames = ['c1arr', 'c2arr', 'dens', 'temp', 'abund']

    # Write the arrays and output to file.

    hstring = ''
    for i, array in enumerate(data):
        hstring += write_header_string(array, arrnames[i])

    if name is None:
        name = path.split('/')[-1]
        i = -1
        while name[i] != '.':
            i -= 1
            if i == 0:
                i = len(name)
                break
        name = name[:i]
    elif name[-2:] == '.h':
        name = name[:-2]

    with open('%s.h' % name, 'w') as hfile:
        hfile.write('%s' % hstring)
    print("Written to '%s.h'." % name)

    return

#
# def make_2d_header_from_astropy_table(data):
#     """Write the header file."""
#
#     # Make the conversions to LIME appropriate units:
#     # Main collider density (H2) is in [m^-3].
#     # Relative abundance is with respect to the main collider density.
#     # Temperatures are all in [K].
#
#     # Make sure that each column has a cell at the midplane: z = 0.
#
#     for r in np.unique(data["Radius"]):
#         idx = data[1][data[0] == r].argmin()
#         data[1][idx] = 0.0
#
#     # Make sure these are the same as in the template file.
#     # Note that we skip the average grainsize array.
#
#     if datalong:
#         arrnames = ['c1arr', 'c2arr', 'dens', 'temp', 'dtemp',
#                     'gastodust', 'abund']
#     else:
#         arrnames = ['c1arr', 'c2arr', 'dens', 'temp', 'abund']
#
#     # Write the arrays and output to file.
#
#     hstring = ''
#     for i, array in enumerate(data):
#         hstring += write_header_string(array, arrnames[i])
#
#     if name is None:
#         name = path.split('/')[-1]
#         i = -1
#         while name[i] != '.':
#             i -= 1
#             if i == 0:
#                 i = len(name)
#                 break
#         name = name[:i]
#     elif name[-2:] == '.h':
#         name = name[:-2]
#
#     with open('%s.h' % name, 'w') as hfile:
#         hfile.write('%s' % hstring)
#     print("Written to '%s.h'." % name)
