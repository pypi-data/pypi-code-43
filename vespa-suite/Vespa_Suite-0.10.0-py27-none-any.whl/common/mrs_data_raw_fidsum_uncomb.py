# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.common.mrs_data_raw as mrs_data_raw
from vespa.common.constants import Deflate

class DataRawFidsumUncomb(mrs_data_raw.DataRaw):
    """
    A subclass of mrs_data_raw.DataRaw that behaves exactly the same as its 
    base class. It exists so that we can differentiate it from other raw data 
    that has both coil and individual fid data in its raw array.
    
    """
    # This is the version of this object's XML output format. 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        mrs_data_raw.DataRaw.__init__(self, attributes)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # Make my base class do its deflate work
            e = mrs_data_raw.DataRaw.deflate(self, flavor)

            # Alter the tag name & XML version info   
            e.tag = "raw_fidsum_uncomb"
            e.set("version", self.XML_VERSION)

            # If this class had any custom attributes, I'd add them here.

            return e

        elif flavor == Deflate.DICTIONARY:
            return self.__dict__.copy()
