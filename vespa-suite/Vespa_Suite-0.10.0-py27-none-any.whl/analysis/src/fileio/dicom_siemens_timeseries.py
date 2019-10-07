# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.analysis.src.fileio.dicom_siemens as dicom_siemens  
import vespa.common.mrs_data_raw_timeseries as mrs_data_raw_timeseries

from vespa.common.constants import Deflate
from vespa.analysis.src.fileio.util_exceptions import OpenFileAttributeMismatchError



class RawReaderDicomSiemensTimeseries(dicom_siemens.RawReaderDicomSiemens):
    def __init__(self):
        """
        Reads multiple Siemens DICOMs file into an DataRawTimeseries object.

        It implements the interface defined by raw_reader.RawReader (q.v.).
        """

        dicom_siemens.RawReaderDicomSiemens.__init__(self)


    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        # Call my base class read_raw()
        raw = dicom_siemens.RawReaderDicomSiemens.read_raw(self, filename, 
                                                           ignore_data, 
                                                           kwargs['open_dataset'])

        # Change that DataRaw object into a DataRawTimeseries
        d = raw.deflate(Deflate.DICTIONARY)

        return mrs_data_raw_timeseries.DataRawTimeseries(d)


        
    def _check_dimensionality(self, open_dataset):
        # If there's already data open, the attributes of the currently open
        # dataset(s) must match those of what we're trying to open.
        raw = self.raws[0]

        if (1 == max(open_dataset.raw_dims[1:])) and (raw.sw == open_dataset.sw):
            # All is well!
            pass
        else:
            raise OpenFileAttributeMismatchError
