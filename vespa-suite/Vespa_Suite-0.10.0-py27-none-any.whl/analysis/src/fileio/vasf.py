"""
Routines for reading a VASF format .rsp/.rsd file pair and returning an 
DataRaw object populated with the files' data.

It doesn't support reading the other two VASF formats (.sid/.sip and 
.mid/.mip) nor does it support writing to any VASF format. 

In other words, there are three formats (.rsp/.rsd, .sid/.sip and .mid/.mip)
and two features to offer for each (read/write) for a total of six possible
features for this module to offer. Of those, it only offers one. At present,
there's no plans to change this.
"""

# Python modules
from __future__ import division
import struct
import os.path
import re
import exceptions

# 3rd party modules
import numpy

# Our modules
import vespa.common.constants as constants
import vespa.common.util.misc as util_misc
import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.configobj as configobj
import vespa.common.util.fileio as util_fileio
import vespa.analysis.src.fileio.raw_reader as raw_reader 
import vespa.analysis.src.fileio.util_parameters as util_parameters

import vespa.analysis.src.fileio.util_exceptions as util_exceptions



def get_filename_pair(filename):
    """
    Given the name of a VASF data file (e.g. /home/me/foo.rsd) or
    parameters file (e.g. c:/stuff/xyz.mip), returns a tuple of
    (parameters_filename, data_filename). It doesn't matter if the
    filename is a fully qualified path or not.

    This is a little shaky on case sensitive file systems since I assume
    that the file extensions are either all upper or all lower case. If, for
    instance, the data file is foo.rsd and the param file is FOO.RSP, this
    code won't generate the correct name.
    """
    # filenames are the same except for the last letter.
    parameters_filename = data_filename = filename[:-1]

    if filename[-1:].isupper():
        data_filename += 'D'
        parameters_filename += 'P'
    else:
        data_filename += 'd'
        parameters_filename += 'p'

    return (parameters_filename, data_filename)


class RawReaderVasf(raw_reader.RawReader):
    def __init__(self):
        raw_reader.RawReader.__init__(self)
        
        self.filetype_filter = "Spectra (*.rsd)|*.rsd;"
        self.multiple = True
        
        
    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        """
        Given the name of a .rsp or .rsd file, returns an DataRaw object
        populated with the parameters and data represented by the file pair.

        When ignore_data is True, this function only reads the parameters file
        which can be much faster than reading both params & data.
        
        This function does not make use of kwarg['open_dataset'] keyword
    
        Note that raw data that's not in XDR format lacks metadata and
        therefore might not be read correctly. First of all, for non-XDR data
        the number of bytes occupied by a type (e.g. float) varies from
        platform to platform especially across 32- and 64-bit systems. When
        forced to guess, we use the type size for the current platform.

        Second, raw data carries no information on endianness. I think all the 
        platforms where Vespa is likely to run are little endian so this isn't
        a big concern. Again, XDR-ed data is entirely immune from this.
        """
        parameters_filename, data_filename = get_filename_pair(filename)

        if not os.path.isfile(parameters_filename):
            raise util_exceptions.FileNotFoundError, \
                  "I can't find the parameters file '%s'" % parameters_filename

        if not ignore_data and not os.path.isfile(data_filename):
            raise util_exceptions.FileNotFoundError, \
                  "I can't find the data file '%s'" % data_filename

        # Read the RSP file and extract the stuff I need.
        header = open(parameters_filename, "rb").read()
    
        d = _map_parameters(header)
    
        d["header"]   = header
        d["data_source"] = filename

        # Read data, too, if the caller wants me to do so.
        shape = d["dims"][::-1]
        del d["dims"]
        
        data_type = constants.DataTypes.any_type_to_numpy(d["data_type"])
        if ignore_data:
            # Create zero data
            data = numpy.zeros(shape, data_type)
        else:
            data = _read_data(data_filename, data_type, d["is_xdr"])
            data.shape = shape

        d["data"] = data

        return mrs_data_raw.DataRaw(d)



####################    Internal functions start here     ###############

def _read_data(filename, data_type, is_xdr=True):
    """
    Reads data from a VASF file and returns it in a numpy array. Note that
    the array is unshaped (one dimensional).
    """
    data_type = constants.DataTypes.any_type_to_internal(data_type)

    data = open(filename, "rb").read()

    # Calculate # of elements by dividing the data length by the
    # number of bytes in the given type.
    element_count = len(data) // constants.DataTypes.XDR_TYPE_SIZES[data_type]

    if is_xdr:
        data = util_fileio.decode_xdr(data, data_type, element_count)
    else:
        # The size of raw data's elements might differ from XDR's definition
        # in which case element_count will be off and this code will break.
        # There's not much we can do about that -- it's the nature of raw 
        # data to be sensitive to things like compiler settings and chip
        # architectures.
        data = _decode_raw(data, data_type, element_count)

    data_type = constants.DataTypes.any_type_to_numpy(data_type)
    data = numpy.fromiter(data, data_type)

    return data


def _decode_raw(data, data_type, element_count):
    """
    Given a string of data in raw format and a data type, returns
    an iterable (tuple or list) of Python objects representing the decoded
    data. data_type must be one of the data types defined in 
    vespa.common.constants.DataTypes.ALL.

    element_count is the number of elements expected in the data.
    
    See caveats about raw data in the read_raw() docstring.
    """
    if data_type == constants.DataTypes.COMPLEX64:
        format = "ff"
    elif data_type == constants.DataTypes.COMPLEX128:
        format = "dd"
    elif data_type == constants.DataTypes.FLOAT64:
        format = "d"
    elif data_type == constants.DataTypes.FLOAT32:
        format = "f"
    elif data_type == constants.DataTypes.INT32:
        format = "l"
    elif data_type == constants.DataTypes.BYTE:
        format = "B"
    else:
        raise ValueError, "Unknown data type '%s'" % data_type

    try:
        data = struct.unpack(format * element_count, data)
    except struct.error:
        raise util_fileio.UnreadableDataError,                            \
              "Unexpected input encountered while reading raw data"

    if constants.DataTypes.is_complex(data_type):
        # Complex numbers are written as pairs of floats (or doubles). Here
        # I knit the (real, imaginary) pairs back into complex numbers.
        data = util_fileio.collapse_complexes(data)

    return data


def _map_parameters(header):
    """Given the text of a .rsp file, extracts a subset of the parameters
    therein and returns a dict suitable for passing to mrs_data_raw.DataRaw().
    """
    # ConfigObj() accepts several types of constructor inputs, one of which
    # is a list of strings (representing the lines of a file). This is handy
    # because it gives me a chance to translate the header a little before 
    # handing it to ConfigObj. The translation is necessary because many of 
    # our files use the semicolon (;) as a comment delimiter while ConfigObj 
    # accepts only the hash mark (#) as a comment delimiter.
    # Just say "no" to non-standard file formats!
    header = util_misc.normalize_newlines(header)
    header = header.split("\n")
    # The list comprehension below replaces the first semicolon of every line
    # with a hash (if it finds one at all).
    header = [line.replace(';', '#', 1) for line in header]

    header = configobj.ConfigObj(header)

    return util_parameters.map_parameters(header['FILE INFORMATION'],
                                          header['IDENTIFICATION INFORMATION'],
                                          header['MEASUREMENT INFORMATION'],
                                          header['DATA INFORMATION']
                                         )
