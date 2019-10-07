# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.analysis.src.chain_raw as chain_raw
import vespa.analysis.src.block as block
import vespa.common.mrs_data_raw as mrs_data_raw
import vespa.common.util.xml_ as util_xml
from vespa.common.constants import Deflate




class _Settings(object):
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        """
        Currently there are no input parameters set in this object. This may
        change in the future, or this object may serve as a base class for
        other "raw" types of data objects that need to do a bit of massaging
        of the data as it comes in (e.g. align and sum individual FIDs for 
        an SVS data set).
        
        """
        pass


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("settings", {"version" : self.XML_VERSION})
            return e
            
        elif flavor == Deflate.DICTIONARY:
            return self.__dict__.copy()


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            pass

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])



class BlockRaw(block.Block, mrs_data_raw.DataRaw):
    """ 
    This is a building block object that can be used to create a list of
    processing blocks. 
    
    This object represents the header(s) and raw data set(s) that comprise
    the first 'processing' block in the dataset.blocks list. It is sort of
    a special processing block in that it does no overt processing other 
    than the actual loading of the data into its self.data attribute.
    
    We sub-class from DataRaw base class to minimize recreation of any
    wheels, but to also leave us the flexibility of extending this class 
    in the future for any 'special children' types of data loading.
    
    In here we also package all the functionality needed to save and recall
    these values to/from an XML node.

    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        block.Block.__init__(self, attributes)
        mrs_data_raw.DataRaw.__init__(self, attributes)  

        self.set = _Settings(attributes)


    ##### Standard Methods and Properties #####################################

    @property
    def dims(self):
        """Data dimensions in a list, e.g. [1024, 5, 1, 1]. It's read only.
        The list is guaranteed to be a fresh, unique copy rather than a 
        reference to something inside this object.

        Returns None if no data is set.
        """
        # Note that self.data.shape is a tuple. Dims must be a list. The line
        # below assures that and also makes a copy of the dims.
        if self.data is not None:
            return list(self.data.shape[::-1])
        else:
            return None


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = mrs_data_raw.DataRaw.__unicode__(self).split('\n')

        # Replace the heading line
        lines[0] = "----------- DataRaw Object ------------"
        lines.append("No printable data ")

        return u'\n'.join(lines)


    def create_chain(self, dataset):
        self.chain = chain_raw.ChainRaw(dataset, self)


    def concatenate(self, new):
        # This is a method from DataRaw that's not supported here. 
        raise NotImplementedError


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            
            # Make my base class do its deflate work
            e = mrs_data_raw.DataRaw.deflate(self, flavor)
            
            # Alter the tag name & XML version info   
            e.tag = "block_raw"
            e.set("version", self.XML_VERSION)
            
            # Now I deflate the attribs that are specific to this class
            e.append(self.set.deflate())
            
            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):

        # Make my base class do its inflate work
        mrs_data_raw.DataRaw.inflate(self, source)

        # Now I inflate the attribs that are specific to this class
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            
            # Look for settings under the old name as well as the standard name.
            self.set = util_xml.find_settings(source, "block_raw_settings")
            self.set = _Settings(self.set)

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if key == "set":
                    setattr(self, key, source[key])


        


