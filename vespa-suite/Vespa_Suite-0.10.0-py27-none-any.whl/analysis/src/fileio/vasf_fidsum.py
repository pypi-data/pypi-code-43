# Python modules
from __future__ import division

# 3rd party modules

# Our modules
import vespa.analysis.src.fileio.vasf as vasf 
import vespa.common.mrs_data_raw_fidsum as mrs_data_raw_fidsum

from vespa.common.constants import Deflate
from vespa.analysis.src.fileio.util_exceptions import OpenFileAttributeMismatchError


class RawReaderVasfFidsum(vasf.RawReaderVasf):
    def __init__(self):
        """
        Reads multiple Siemens DICOMs file into an DataRawFidsum object.

        It implements the interface defined by raw_reader.RawReader (q.v.).
        """

        vasf.RawReaderVasf.__init__(self)
        
        
    def read_raw(self, filename, ignore_data=False, *args, **kwargs):
        # Call my base class read_raw()
        raw = vasf.RawReaderVasf.read_raw(self, filename, ignore_data)

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
