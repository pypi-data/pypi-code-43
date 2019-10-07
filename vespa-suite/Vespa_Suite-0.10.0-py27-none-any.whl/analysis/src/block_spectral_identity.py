# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import vespa.analysis.src.chain_spectral_identity as chain_spectral_identity
import vespa.analysis.src.block as block
from vespa.common.constants import Deflate



class _Settings(object):
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        pass


    @property
    def zero_fill_multiplier(self):
        return 1

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



class BlockSpectralIdentity(block.Block):
    """This is a lightweight placeholder class for the spectral block.""" 

    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    
    def __init__(self, attributes=None):
        block.Block.__init__(self, attributes)

        self.set = _Settings(attributes)

        self.data = None


    ##### Standard Methods and Properties #####################################

    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]

        lines.append("----------- BlockSpectralIdentity Object ------------")
        lines.append("Nothing here")

        return u'\n'.join(lines)


    def create_chain(self, dataset):
        self.chain = chain_spectral_identity.ChainSpectralIdentity(dataset, self)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("block_spectral_identity",
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
            
            self.set = _Settings(source.find("settings"))

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if key == "set":
                    setattr(self, key, source[key])

