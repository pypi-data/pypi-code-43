"""
Routines for reading a Siemens *.rda format and returning an 
DataRaw object populated with the file's data.
"""

# Python modules
from __future__ import division
import struct

# 3rd party modules
import numpy

# Our modules
import vespa.common.constants as constants
import vespa.common.util.misc as util_misc
import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.configobj as configobj
import vespa.common.util.fileio as util_fileio
import vespa.analysis.src.fileio.raw_reader as raw_reader 


# data_type is complex128 per Siemens documentation
NUMPY_DATA_TYPE = numpy.complex128


class RawReaderSiemensRda(raw_reader.RawReader):
    def __init__(self):
        raw_reader.RawReader.__init__(self)
        
        self.filetype_filter = "Spectra (*.rda)|*.rda"
        self.multiple = True
        

    def read_raw(self, filename, ignore_data=False): 
        """
        Given the name of a .rda file, returns an DataRaw object
        populated with the parameters and data represented by the file pair.

        When ignore_data is True, this function only reads the parameters file
        which might be faster than reading both params & data.
        """
        # Read the RDA file and extract the stuff I need.
        header = open(filename, "rb").read()
    
        d, data = _extract_parameters(header)
        d["data_source"] = filename

        # Read data, too, if the caller wants me to do so.
        shape = d["dims"][::-1]
        del d["dims"]
        if ignore_data:
            # Create zero data.
            data = numpy.zeros(shape, NUMPY_DATA_TYPE)
        else:
            data = _parse_data(data)

            data.shape = shape

        d["data"] = data

        return mrs_data_raw.DataRaw(d)
    
    
####################    Internal functions start here     ###############

def _parse_data(data):
    """
    Reads data from a R file and returns it in a numpy array. Note that
    the array is unshaped (one dimensional).
    """
    data = _decode_raw(data)

    return numpy.fromiter(data, NUMPY_DATA_TYPE)


def _decode_raw(data):
    """
    Given a string of data in raw format, returns an iterable (tuple or list) 
    of Python complexes representing the decoded data.
    """
    # data_type is COMPLEX_DOUBLE (a.k.a. complex128) by Siemens documentation
    
    format = "dd"

    element_count = len(data) // struct.calcsize(format)
    
    try:
        data = struct.unpack(format * element_count, data)
    except struct.error:
        raise util_fileio.UnreadableDataError,                            \
              "Unexpected input encountered while reading raw data"

    # Complex numbers are written as pairs of floats (or doubles). Here
    # I knit the (real, imaginary) pairs back into complex numbers.
    data = util_fileio.collapse_complexes(data)

    return data
    
    
def _extract_parameters(header):
    """
    Given the contents of an RDA file as a string, extracts a few specific
    parameters and returns a flat dict containing those parameters and their 
    value. 
    The returned dict is appropriate for passing to DataRaw.inflate().
    """
    
    # The header starts life here as a string. I convert it to a ConfigObj.

    # Now we find the start/end of the header section based on the standard
    # ">>> Begin of header <<<" and ">>> End of header <<<" marker lines

    istr = header.find(">>> Begin of header <<<")
    iend = header.find(">>> End of header <<<")
    
    head_only = header[istr+25:iend]    # save this to return to user
    data = header[iend+23:]
    
    # ConfigObj() accepts several types of constructor inputs, one of which
    # is a list of strings (representing the lines of a file). This is handy
    # because it gives me a chance to translate the header a little before 
    # handing it to ConfigObj. 
    # Just say "no" to non-standard file formats!
    
    head = util_misc.normalize_newlines(head_only)   
    head = head.split("\n")
    
    # The list comprehension below replaces the first semicolon of every line
    # with a hash (if it finds one at all).
    head = [line.replace(':', ' = ', 1) for line in head]

    hdr = configobj.ConfigObj(head)

    # There's some subtle code below. Some of the dict elements that we
    # construct in the code below are lists (e.g. dims) with optional 
    # elements. For instance, it's possible that "measure_size_spectral" 
    # isn't present, in which case dim[0] won't get set.
    #
    # This brings up a problem: given that the list of dims is being 
    # created here and that it's imperative that objects define their own
    # defaults, how do we allow the object to initialize that list of dims?
    #
    # We do so by making the list defaults a public part of the class,
    # e.g. DataRaw.DEFAULT_DIMS. This allows the definition of the 
    # default to remain in the class where it belongs while this code can 
    # still use it and overwrite only the list elements it finds defined
    # in the .rsp file.
    d = { }

    d["frequency"]      = float(hdr["MRFrequency"]) 
    d["sw"]             = 1.0/(float(hdr["DwellTime"])*0.000001)
    
    d["dims"]           = mrs_data_raw.DataRaw.DEFAULT_DIMS
    d["dims"][0]        = int(hdr["VectorSize"])
    d["dims"][1]        = int(hdr["CSIMatrixSize[0]"])
    d["dims"][2]        = int(hdr["CSIMatrixSize[1]"])
    d["dims"][3]        = int(hdr["CSIMatrixSize[2]"])

    d["nucleus"]                = hdr["Nucleus"]
    d["seqte"]                  = float(hdr["TE"])
    if hdr["Nucleus"] == '1H':
        d["midppm"]             = constants.DEFAULT_PROTON_CENTER_PPM
    else:
        d["midppm"]             = constants.DEFAULT_XNUCLEI_CENTER_PPM
    d["echopeak"]               = mrs_data_raw.DataRaw.DEFAULT_ECHOPEAK
    d["flip_angle"]             = float(hdr["FlipAngle"])
    d["slice_thickness"]        = float(hdr["SliceThickness"])
    d["slice_orientation_pitch"]= '' # maybe not available
    d["slice_orientation_roll"] = '' # maybe not available

    d["image_position"] = mrs_data_raw.DataRaw.DEFAULT_IMAGE_POSITION
    d["image_position"][0] = float(hdr["VOIPositionSag"])
    d["image_position"][1] = float(hdr["VOIPositionCor"])
    d["image_position"][2] = float(hdr["VOIPositionTra"])

    d["image_dimension"] = mrs_data_raw.DataRaw.DEFAULT_IMAGE_DIMENSION
    d["image_dimension"][0] = float(hdr["FoVHeight"])
    d["image_dimension"][1] = float(hdr["FoVWidth"])
    d["image_dimension"][2] = float(hdr["FoV3D"])

    d["image_orient_col"] = mrs_data_raw.DataRaw.DEFAULT_IMAGE_ORIENTATION_COLUMN
    d["image_orient_col"][0] = float(hdr["ColumnVector[0]"])
    d["image_orient_col"][1] = float(hdr["ColumnVector[1]"])
    d["image_orient_col"][2] = float(hdr["ColumnVector[2]"])

    d["image_orient_row"] = mrs_data_raw.DataRaw.DEFAULT_IMAGE_ORIENTATION_ROW
    d["image_orient_row"][0] = float(hdr["VOINormalSag"]) # may need to  be RowVector[0]
    d["image_orient_row"][1] = float(hdr["VOINormalCor"]) #  etc, but values in RSP file
    d["image_orient_row"][2] = float(hdr["VOINormalTra"]) #  matched to VOINormalXxx

    d["header"] = head_only

    return d,data    
    
    



#------------------------------------------------------------

def _test():

    fname = "C:\\Users\\bsoher\\code\\repository_svn\\sample_data\\siemens_rda_export\\SVS_SE_30\\svs_se_3T.rda"

    r = read_raw(fname)
    
    bob = 10


if __name__ == '__main__':
    _test()    