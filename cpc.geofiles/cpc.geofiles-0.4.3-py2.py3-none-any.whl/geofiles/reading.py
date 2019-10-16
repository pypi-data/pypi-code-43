"""
Contains methods for reading gridded data.
"""

# Built-ins
import subprocess
import uuid
import os
import shutil

# Third-party
import numpy as np

# This package
from .exceptions import ReadingError


def read_grib(file, grib_type, grib_var, grib_level, geogrid, yrev=False, grep_fhr=None,
              debug=False, wgrib2_new_grid=False):
    """
    Reads a record from a grib file

    Uses wgrib for grib1 files, and wgrib2 for grib2 files. For grib1 files, the record in
    question is written to a temporary binary file, the data is read in, and the file is removed.
    wgrib2 has the ability to write the record to STDIN, so no temporary file is necessary to
    read in a record from a grib2 file.

    ### Parameters

    - file (string): name of the grib file to read from
    - grib_type (string): type of grib file ('grib1', 'grib2')
    - variable (string): name of the variable in the grib record (ex. TMP, UGRD, etc.)
    - level (string): name of the level (ex. '2 m above ground', '850 mb', etc.)
    - geogrid (Geogrid): Geogrid the data should be placed on
    - yrev (optional): option to flip the data in the y-direction (eg. ECMWF grib files)
    - grep_fhr (optional): fhr to grep grib file for - this is useful for gribs that may for some
      reason have duplicate records for a given variable but with different fhrs. This way you
      can get the record for the correct fhr.

    ### Returns

    - (array_like): a data array containing the appropriate grib record

    ### Raises

    - ReadingError: if wgrib has a problem reading the grib and/or writing the temp file
    - ReadingError: if no grib record is found
    """
    # Make sure grib file exists first
    if not os.path.isfile(file):
        raise ReadingError('Grib file not found', file)
    # Generate a temporary file name
    temp_file = str(uuid.uuid4()) + '.bin'
    # Set the grep_fhr string
    if grep_fhr:
        grep_fhr_str = grep_fhr
    else:
        grep_fhr_str = '.*'
    # Set the name of the wgrib program to call
    if grib_type == 'grib1':
        # Make sure wgrib is installed
        if not shutil.which('wgrib'):
            raise ReadingError('wgrib not installed')
        wgrib_call = 'wgrib "{}" | grep ":{}:" | grep ":{}:" | grep -P "{}" | wgrib ' \
                     '-i "{}" -nh -bin -o "{}"'.format(file, grib_var, grib_level,
                                                       grep_fhr_str, file, temp_file)
    elif grib_type == 'grib2':
        # Make sure wgrib2 is installed
        if not shutil.which('wgrib2'):
            raise ReadingError('wgrib2 not installed')
        # Note that the binary data is written to stdout
        if wgrib2_new_grid and grib_var in ['UGRD', 'VGRD']:
            grib_file = 'temp.grb2'
            wgrib_extra_before = (
                f'wgrib2 -match "GRD:10 m" {file} -new_grid_winds earth -new_grid ncep grid 3 '
                f'{grib_file} > /dev/null ;')
        else:
            wgrib_extra_before = ''
            grib_file = file
        wgrib_call = (
            f'{wgrib_extra_before} '
            f'wgrib2 "{grib_file}" -match "{grib_var}" -match "{grib_level}" -match '
            f'"{grep_fhr_str}" '
            f'-end -order we:sn -no_header -inv /dev/null -bin - ')
    else:
        raise ReadingError(__name__ + ' requires grib_type to be grib1 or grib2')
    if debug:
        print('wgrib command: {}'.format(wgrib_call))
    # Generate a wgrib call
    try:
        if grib_type == 'grib1':
            output = subprocess.call(wgrib_call, shell=True, stderr=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL)
        else:
            proc = subprocess.Popen(wgrib_call, shell=True, stderr=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE)
    except Exception as e:
        if grib_type == 'grib1':
            os.remove(temp_file)
        raise ReadingError('Couldn\'t read {} file: {}'.format(grib_type, str(e)))
    # Read in the binary data
    if grib_type == 'grib1':
        data = np.fromfile(temp_file, dtype=np.float32)
    else:
        data = np.frombuffer(bytearray(proc.stdout.read()), dtype='float32')
    if data.size == 0:
        raise ReadingError('No grib record found')
    # Delete the temporary file
    if grib_type == 'grib1':
        os.remove(temp_file)
    try:
        os.remove('temp.grb2', )
    except:
        pass
    # Flip the data in the y-dimension (if necessary)
    if yrev:
        # Reshape into 2 dimensions
        try:
            data = np.reshape(data, (geogrid.num_y, geogrid.num_x))
        except AttributeError:
            raise ValueError('The yrev parameter requires that the geogrid parameter be defined')
        # Flip
        data = np.flipud(data)
        # Reshape back into 1 dimension
        data = np.reshape(data, data.size)
    # Return data
    return data
