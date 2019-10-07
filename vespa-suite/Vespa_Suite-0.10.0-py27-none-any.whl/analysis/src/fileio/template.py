"""
This file is a template for those who want to implement a reader for 
a file format that Vespa doesn't know about. It contains plenty of comments 
to guide you.

Focus on the class method read_raw() which mainly asks you to populate a
Python dictionary with relevant metadata. If you can do that, you can get 
Vespa to understand your file format.

Don't neglect the rest of the file which contains other useful information.

You can also look at the other files in this directory for examples of real
implementations. The files dicom_siemens.py and siemens_rda.py are examples
of formats in which the metadata and data are in the same file. For examples
of formats where the data and metadata are in separate files, have a look at
philips_spar.py, varian.py and vasf.py.

Once you have finished creating a class to read your format's header and data,
Appendix B in the Analysis User Manual can tell you how to let the program know
that it should add this format to its data import options. The Analysis User 
Manual is available from Analysis's Help menu.
"""

# Python modules
from __future__ import division

# 3rd party modules
import numpy

# Our modules
import vespa.common.mrs_data_raw as mrs_data_raw
import fileio.raw_reader as raw_reader 

# NUMPY_DATA_TYPE describes the format of one element of your data. It's 
# useful to define it here since the module uses it in multiple places.
NUMPY_DATA_TYPE = numpy.float32
# BYTES_PER_ELEMENT expresses how many bytes each element occupies. You
# shouldn't need to change this definition.
BYTES_PER_ELEMENT = np.zeros(1, dtype=NUMPY_DATA_TYPE).nbytes


# Change the class name to something that makes sense to you. Our example
# reads the fictitious Acme format.
class RawReaderAcme(raw_reader.RawReader):
    # This inherits from raw_reader.RawReader (q.v.). The only methods you
    # need to implement are __init__() and read_raw(). You *may* want to 
    # override or supplement some of raw_reader.RawReader's other methods.

    def __init__(self):
        raw_reader.RawReader.__init__(self)
        
        # Set filetype_filter to the type of files you want to load.
        self.filetype_filter = "Acme (*.acme)|*.acme;"
        # Set multiple to False if users aren't allowed to open multiple 
        # files at once.
        self.multiple = True
        
        
    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        """
        Given the name of a .acme file, returns a DataRaw object
        populated with the parameters and data in the file.

        When ignore_data is True, this function only reads the parameters file
        which can be much faster than reading both params & data, depending
        on the file format.
        
        When there are datasets already open in Vespa-Analysis, they
        can be accessed through the kwarg['open_dataset'] attribute
        
        """
        # This function should create a Python dictionary and populate it with 
        # metadata (parameters) and the data. At the very end of the function, 
        # the dictionary is turned into a Vespa DataRaw object and
        # returned to the caller.
        #
        # This function will almost always return a single object that is a 
        # instance of DataRaw or one of its subclasses (like DataRawFidsum). 
        # In unusual cases (where a single file contains multiple datasets),
        # it will return a list of DataRaw instances (or subclasses).

        d = { }

        # All parameters are optional; Vespa will provide reasonable
        # defaults for any that are not supplied. The purpose of this function
        # is to allow you to read the parameters from a file, but you can 
        # hardcode them if you like. 
        # For instance:
        d["frequency"] = 127.9

        # Here are the parameters you're most likely to want to populate.

        # header: A text string containing all metadata. Vespa stores this 
        # but never reads it, so you can put anything you want in there. It's
        # free form.
        # 
        # data_source: A string describing where this data came from. It's
        # typically a filename, but it's free form so it could also be 
        # 'Study database' or 'Direct from scanner'. 
        # As with the header, what goes in here is entirely up to you.
        d["data_source"] = filename

        # sw: sweep width in Hertz as a float, e.g. 2000.0
        # frequency: frequency in MHz as a float, e.g 64.0
        # nucleus: string, e.g. '1H'. This is *not* free form. Common values
        #    that Vespa recognizes are 1H, 13C, and 31P. The complete list is
        #    in this file: 
        #    http://scion.duhs.duke.edu/vespa/project/browser/trunk/common/resources/isotopes.xml
        #    For instance:
        d["nucleus"] = "1H"
        # resppm: float, acquisition on-resonance value in PPM
        # midppm: float, current data middle point in PPM
        # echopeak: float [0.0 - 1.0], acquisition spectral echo peak as 
        #    a percentage of acquistion first dimension length.
        # seqte: float, sequence echo time (TE) in milliseconds

        # Last but not least, this function has to provide your data. The
        # data must have a shape which is typically a 4-tuple where the last
        # element is the number of points in the data. You might hardcode it,
        # infer it from the length of the data file, or read it from a 
        # parameters file.
        # The other values (dimensions) in the shape should be 1 if you're 
        # only reading one set of data at a time.
        # For instance:
        shape = (1, 1, 1, 2048)

        if ignore_data:
            # Create zero data
            data = numpy.zeros(shape, NUMPY_DATA_TYPE)
        else:
            data = _read_data(filename)
            data.shape = shape

        # This is typically the last thing that's added to the dictionary.
        d["data"] = data

        # Here's where the dictionary becomes a Vespa DataRaw object.
        return mrs_data_raw.DataRaw(d)



####################    Internal functions start here     ###############

def _read_data(filename):
    """
    Reads data from a .acme file and returns it in a numpy array. Note that
    the array is unshaped (one dimensional).
    """
    # It's up to you to write this function! An example for reading an 
    # extremely simple format is below. In this format, the data is written as
    # a series of 32-bit floats in native byte order. This is also reflected
    # in the NUMPY_DATA_TYPE definition at the top of this file.
    import struct

    data = open(filename, "rb").read()

    element_size = struct.calcsize('f')

    npoints = len(data) // BYTES_PER_ELEMENT

    data = struct.unpack('f' * npoints, data)

    data = numpy.array(data)

    return data


