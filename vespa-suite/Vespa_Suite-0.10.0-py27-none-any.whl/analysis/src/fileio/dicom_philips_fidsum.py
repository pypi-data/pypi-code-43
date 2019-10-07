# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.analysis.src.fileio.dicom_philips as dicom_philips  
import vespa.common.mrs_data_raw_fidsum as mrs_data_raw_fidsum

from vespa.common.constants import Deflate
from vespa.analysis.src.fileio.util_exceptions import OpenFileAttributeMismatchError


class RawReaderDicomPhilipsFidsum(dicom_philips.RawReaderDicomPhilips):
    def __init__(self):
        """
        Reads multiple Philips DICOMs file into an DataRawFidsum object.
        It implements the interface defined by raw_reader.RawReader (q.v.).

        """
        dicom_philips.RawReaderDicomPhilips.__init__(self)


    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        """ Call my base class read_raw() """
        
        raw = dicom_philips.RawReaderDicomPhilips.read_raw(self, filename, 
                                                           ignore_data, 
                                                           kwargs['open_dataset'])

        # Change that DataRaw object into a DataRawFidsum, this is the trick
        # that turns this parser into a FidSum kind of thing
        
        d = raw.deflate(Deflate.DICTIONARY)

        return mrs_data_raw_fidsum.DataRawFidsum(d)


        
    def _check_dimensionality(self, open_dataset):
        """ if dataset already open, new dataset attributes must match """
        
        raw = self.raws[0]

        # FIXME - bjs, summed data sets have multiple files that are summed
        #  into one FID raw file. At this point, open_dataset will
        #  have a dimension 1 while the new set of concatenated raws will 
        #  have N files for a dimension. So for now we will just skip the
        #  comparison of the dims in here for summed data
        if (1 == max(open_dataset.raw_dims[1:])) and \
           (raw.sw == open_dataset.sw):
            # All is well!
            pass
        else:
            raise OpenFileAttributeMismatchError
