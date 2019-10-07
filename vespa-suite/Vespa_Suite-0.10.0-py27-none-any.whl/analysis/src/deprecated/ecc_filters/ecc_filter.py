# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports

# Vespa imports
from vespa.common.constants import Deflate


class EccFilter(object):
    """This is a base class for ECC filters. It does a little work, but not
    a lot. The child classes are expected to do most of the work. 
    
    This mainly exists to codify the interface that all ECC filters must
    make available.
    
    """
    # Each instance of this class needs the following class-level attributes:
    #    - XML_VERSION, e.g. "1.0.0" for versioning the XML output 
    #      generated herein.
    #    - ID, e.g. "8dfdfb60-9247-41a7-ae05-aee7a4a1c05d" - The UUID
    #      for this version of this filter.
    #    - DISPLAY_NAME, e.g. 'My ECC Filter' - This is the text that will 
    #      display in the GUI in the list of ECC filters from which to choose.

    def __init__(self, attributes=None):
        self.ecc_raw = None
        self.ecc_dataset = None
        self.ecc_dataset_id = None

        self.functor = None
        
        self._panel = None
        
        self._gui_data = None

        if attributes is not None:
            self.inflate(attributes)


    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # Subclasses of this class will probably want to populate
        # self._panel the first time this is called.
        return self._panel
        

    def get_associated_datasets(self, is_main_dataset=True):
        """
        Returns a list of datasets associated with this object
        
        The 'is_main_dataset' flag allows the method to know if it is the top
        level dataset gathering associated datasets, or some dataset that is
        only associated with the top dataset. This is used to stop circular
        logic conditions where one or more datasets refer to each other.

        """
        # Subclasses of this class will probably want to return something here. 
        return [ ]
            

    def deflate(self, flavor=Deflate.ETREE):
        # Subclasses of this class should call this base class method first 
        # and append to what it returns.
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("ecc_filter",
                                      { "version" : self.XML_VERSION,
                                        "id" : self.ID})

            # Filters are only identified in the XML by UUID which is 
            # not so human-friendly, so we add a comment that contains 
            # the filter name.
            comment = "This is the %s ECC filter" % self.DISPLAY_NAME 
            e.append(ElementTree.Comment(comment))

            if self._panel:
                e.append(self._panel.deflate(flavor))

            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        # Subclasses of this class should call this base class method first 
        # and continue with inflating their custom elements (if any) 
        # thereafter.
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            self._gui_data = source.find("gui_data")

        elif hasattr(source, "keys"):
            raise NotImplementedError


