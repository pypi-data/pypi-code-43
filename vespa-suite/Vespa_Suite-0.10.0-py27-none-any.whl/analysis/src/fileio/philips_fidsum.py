"""
Routines for reading a Philips .spar/.sdat formats and returning an 
DataRawFidsum object populated with the file's data.
"""

# Python modules
from __future__ import division
import os.path

# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.util.misc as util_misc
import vespa.common.mrs_data_raw_fidsum as mrs_data_raw_fidsum
import vespa.common.configobj as configobj
import vespa.common.util.fileio as util_fileio
import vespa.analysis.src.fileio.util_philips as fileio_util_philips
import vespa.analysis.src.fileio.raw_reader as raw_reader 

import vespa.analysis.src.fileio.util_exceptions as util_exceptions

# data is complex64 per Philips documentation for SDAT
NUMPY_DATA_TYPE = np.complex64
# BYTES_PER_ELEMENT expresses how many bytes each element occupies. You
# shouldn't need to change this definition.
BYTES_PER_ELEMENT = np.zeros(1, dtype=NUMPY_DATA_TYPE).nbytes


def get_filename_pair(filename):
    """
    Given the name of a SPAR data file (e.g. /home/me/foo.sdat) or
    parameters file (e.g. c:/stuff/xyz.spar), returns a tuple of
    (parameters_filename, data_filename). It doesn't matter if the
    filename is a fully qualified path or not.

    This is a little shaky on case sensitive file systems since I assume
    that the file extensions are either all upper or all lower case. If, for
    instance, the data file is foo.sdat and the param file is FOO.SPAR, this
    code won't generate the correct name.
    """
    # filenames are the same except for the last three letters.
    parameters_filename = data_filename = filename[:-3]

    if filename[-1:].isupper():
        data_filename += 'DAT'
        parameters_filename += 'PAR'
    else:
        data_filename += 'dat'
        parameters_filename += 'par'

    return (parameters_filename, data_filename)




class RawReaderPhilipsFidsum(raw_reader.RawReader):
    def __init__(self):
        raw_reader.RawReader.__init__(self)
        
        # The sample files given to us all had uppercase extensions, so my guess
        # is that all Philips files are created this way. The GTK file open 
        # dialog takes case sensitivity seriously and won't show foo.SPAR if we
        # use a filetype filter of '*.spar'. Hence we specify both upper and
        # lower case extensions.
        self.filetype_filter = "Spectra (*.spar)|*.spar;*.SPAR"
        self.multiple = True
        

    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        """
        Given the name of a .spar or .sdat file, returns a DataRawFidSum object
        populated with the parameters and data represented by the file pair.

        When ignore_data is True, this function only reads the parameters file
        which can be much faster than reading both params & data.
        """
        parameters_filename, data_filename = get_filename_pair(filename)
        
        if not os.path.isfile(parameters_filename):
            raise util_exceptions.FileNotFoundError, \
                  "I can't find the parameters file '%s'" % parameters_filename

        if not ignore_data and not os.path.isfile(data_filename):
            raise util_exceptions.FileNotFoundError, \
                  "I can't find the data file '%s'" % data_filename
        
        # Read the SPAR file and extract the stuff I need.
        header = open(parameters_filename, "rb").read()

        d = _extract_parameters(header)

        d["data_source"] = filename

        # Read data, too, if the caller wants me to do so.
        dims = d["dims"]
        shape = dims[::-1]
        del d["dims"]

        if ignore_data:
            # Create zero data
            datas = [np.zeros(shape, NUMPY_DATA_TYPE)]
        else:
            datas = _read_data(data_filename, dims[0], d["rows"])

        # Create a DataRawFidsum out of the first set of data in the list.
        d["data"] = datas[0]
        raw = mrs_data_raw_fidsum.DataRawFidsum(d)
        # Concatenate the remainder onto the first.
        for data in datas[1:]:
            data.shape = shape

            d["data"] = data

            raw.concatenate(mrs_data_raw_fidsum.DataRawFidsum(d))

        return raw
    
    
####################    Internal functions start here     ###############

def _read_data(filename, npoints, nfids):
    """Given a filename, the number of points in each FID and the number of
    FIDs, reads the data from the file and returns a list of numpy arrays.
    
    The list will contain nfids arrays; the arrays will be 1D arrays with 
    npoints elements.
    """
    f = open(filename, "rb")

    datas = [ ]

    while nfids:
        data = f.read(npoints * BYTES_PER_ELEMENT)

        data = _decode_raw(data)

        data = np.fromiter(data, NUMPY_DATA_TYPE)
        data = np.conjugate(data)

        datas.append(data)

        nfids -= 1

    return datas


def _decode_raw(data):
    """
    Given a string of data in raw format, returns an iterable (tuple or list) 
    of Python complexes.
    """
    data = fileio_util_philips.vax_to_ieee_single_float(data)

    # Complex numbers are written as pairs of floats (or doubles). Here
    # I knit the (real, imaginary) pairs back into complex numbers.
    data = util_fileio.collapse_complexes(data)

    return data
    
    
def _extract_parameters(header):
    """
    Given the contents of a SPAR file as a string, extracts a few specific
    parameters and returns a flat dict containing those parameters and their 
    value. 
    The returned dict is appropriate for passing to DataRaw.inflate().
    """
    d = { }

    header = util_misc.normalize_newlines(header)

    # A copy of this goes into the dict.
    d["header"] = header

    # The header is in a proprietary format that we can massage into something
    # that looks enough like an INI file to make ConfigObj accept it. I'm 
    # not sure it's a great idea to abuse ConfigObj this way, but it seems
    # to work.
    header = header.split("\n")

    # The proprietary format uses exclamation points to indicate comments
    header = [line.replace('!', '#',   1) for line in header]

    # The proprietary format uses colon as the key/value delimiter.
    header = [line.replace(':', ' = ', 1) for line in header]

    header = configobj.ConfigObj(header)

    # Vespa stores frequency in MHz
    d["frequency"]      = float(header["synthesizer_frequency"])/1000000.0
    d["sw"]             = float(header["sample_frequency"])
    
    d["dims"]           = mrs_data_raw_fidsum.DataRawFidsum.DEFAULT_DIMS
    d["dims"][0]        = int(header["samples"])
    d["dims"][1]        = int(header["dim2_pnts"])
    d["dims"][2]        = int(header["dim3_pnts"])
    d["dims"][3]        = 1 # FIXME bjs is there a third spatial dim?

    d["rows"]           = int(header["rows"])

    d["nucleus"]        = header["nucleus"]
    d["seqte"]          = float(header["echo_time"])
    if header["nucleus"] == '1H':
        d["midppm"]     = constants.DEFAULT_PROTON_CENTER_PPM
    else:
        d["midppm"]     = constants.DEFAULT_XNUCLEI_CENTER_PPM
    d["slice_thickness"] = float(header["cc_size"])
    # FIXME bjs find a value for flip angle?
    # FIXME slice_orientation_pitch and slice_orientation_roll available?

    return d    
    
