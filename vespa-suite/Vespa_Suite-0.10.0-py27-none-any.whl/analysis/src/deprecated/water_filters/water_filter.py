# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports

# Vespa imports
from vespa.common.constants import Deflate


class WaterFilter(object):
    """This is a base class for water filters. It does a little work, but not
    a lot. The child classes are expected to do most of the work. 
    
    This mainly exists to codify the interface that all water filters must
    make available.
    
    """
    # Each instance of this class needs the following class-level attributes:
    #    - XML_VERSION, e.g. "1.0.0" for versioning the XML output 
    #      generated herein.
    #    - ID, e.g. "8dfdfb60-9247-41a7-ae05-aee7a4a1c05d" - The UUID
    #      for this version of this filter.
    #    - DISPLAY_NAME, e.g. 'My Water Filter' - This is the text that will 
    #      display in the GUI in the list of water filters from which to 
    #      choose.

    def __init__(self, attributes=None):
        self.functor = None
        
        self._panel = None
        
        self._gui_data = None

        if attributes is not None:
            self.inflate(attributes)

        
    @property
    def is_hlsvd(self):
        """True only for the HLSVD filter, False otherwise."""
        return False
        

    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # Subclasses of this class will probably want to populate
        # self._panel the first time this is called.
        return self._panel


    def deflate(self, flavor=Deflate.ETREE):
        # Subclasses of this class should call this base class method first 
        # and append to the element that it returns.
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("water_filter",
                                      { "version" : self.XML_VERSION,
                                        "id" : self.ID})
            # Filters are only identified in the XML by UUID which is 
            # not so human-friendly, so we add a comment that contains 
            # the filter name.
            comment = "This is the %s water filter" % self.DISPLAY_NAME 
            e.append(ElementTree.Comment(comment))

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


