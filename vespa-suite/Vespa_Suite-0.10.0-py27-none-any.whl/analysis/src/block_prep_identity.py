# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.analysis.src.chain_prep_identity as chain_prep_identity
import vespa.analysis.src.block as block
from vespa.common.constants import Deflate




class Settings(object):
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        pass


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("settings", 
                                    {"version" : self.XML_VERSION})
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



class BlockPrepIdentity(block.Block):
    """This is a lightweight placeholder class for the prep block.""" 

    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        block.Block.__init__(self, attributes)

        self.set = Settings(attributes)
        
        self.data = None


    ##### Standard Methods and Properties #####################################

#    @property
#    def data(self):
#        # This is read only and should be specifically sub-classed in 
#        #  derived classes in order to be declared read/write
#        return self.source_data


    @property
    def dims(self):
        """Data dimensions in a list, e.g. [1024, 5, 1, 1]. It's read only."""
        # Note that self.data.shape is a tuple. Dims must be a list.
        if self.data is not None:
            return list(self.data.shape[::-1])
        else:
            return None


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]

        lines.append("----------- BlockPrepIdentity ------------")
        lines.append("No printable data ")

        return u'\n'.join(lines)


    def create_chain(self, dataset):
        self.chain = chain_prep_identity.ChainPrepIdentity(dataset, self)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("block_prep_identity",
                                    { "id" : self.id,
                                      "version" : self.XML_VERSION})
            
            e.append(self.set.deflate())
            
            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        # Now I inflate the attribs that are specific to this class
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            self.set = Settings(source.find("settings"))

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if key == "set":
                    setattr(self, key, source[key])


        


