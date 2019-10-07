# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.analysis.src.fileio.dicom_siemens as dicom_siemens  
import vespa.common.mrs_data_raw_fidsum as mrs_data_raw_fidsum

from vespa.common.constants import Deflate
from vespa.analysis.src.fileio.util_exceptions import OpenFileAttributeMismatchError


class RawReaderDicomSiemensFidsum(dicom_siemens.RawReaderDicomSiemens):
    def __init__(self):
        """
        Reads multiple Siemens DICOMs file into an DataRawFidsum object.

        It implements the interface defined by raw_reader.RawReader (q.v.).
        """

        dicom_siemens.RawReaderDicomSiemens.__init__(self)


    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        # Call my base class read_raw()
        raw = dicom_siemens.RawReaderDicomSiemens.read_raw(self, filename, 
                                                           ignore_data, 
                                                           kwargs['open_dataset'])

        # Change that DataRaw object into a DataRawFidsum
        d = raw.deflate(Deflate.DICTIONARY)

        return mrs_data_raw_fidsum.DataRawFidsum(d)


        
    def _check_dimensionality(self, open_dataset):
        # If there's already data open, the attributes of the currently open
        # dataset(s) must match those of what we're trying to open.
        raw = self.raws[0]

        # FIXME - bjs, summed data sets have multiple files that are summed
        #  into one FID raw file. At this point, open_dataset will
        #  have a dimension 1 while the new set of concatenated raws will 
        #  have N files for a dimension. So for now we will just skip the
        #  comparison of the dims in here for summed data
        if (1 == max(open_dataset.raw_dims[1:])) and \
           (raw.sw   == open_dataset.sw):
            # All is well!
            pass
        else:
            raise OpenFileAttributeMismatchError
