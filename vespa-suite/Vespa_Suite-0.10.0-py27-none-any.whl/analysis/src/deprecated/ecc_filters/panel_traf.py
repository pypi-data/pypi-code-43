# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports


# Vespa imports
import util_ecc
import auto_gui.ecc_traf as ecc_traf
from vespa.common.constants import Deflate
import vespa.common.util.xml_ as util_xml



class PanelTraf(ecc_traf.EccTrafUI):

    def __init__(self, parent, tab, attributes):
    
        ecc_traf.EccTrafUI.__init__(self, parent)

        self._tab = tab
        self._filename = ""
        
        if attributes is not None:
            self.inflate(attributes)
        
        self.initialize_controls()
        self.populate_controls()


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            e = ElementTree.Element("gui_data")
            
            util_xml.TextSubElement(e, "filename", self._filename)
                                        
            return e
        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            filename = source.findtext("filename")
            if filename is not None:
                self._filename = filename
        elif hasattr(source, "keys"):
            raise NotImplementedError


    def initialize_controls(self):
        """ 
        This methods goes through the widgets and sets up certain sizes
        and constraints for those widgets. This method does not set the 
        value of any widget except insofar that it is outside a min/max
        range as those are being set up. 

        Use populate_controls() to set the values of the widgets from
        a data object.

        """
        pass


    def populate_controls(self):
        """ 
        Populates the widgets with relevant values from the data object. 
        It's meant to be called when a new data object is loaded.
    
        This function trusts that the data object it is given doesn't violate
        any rules. Whatever is in the data object gets slapped into the 
        controls, no questions asked. 
    
        This function is, however, smart enough to enable and disable 
        other widgets depending on settings.

        """
        self.TextEccFilename.SetValue(self._filename)
           

    ##### Event Handlers ###############################################
                      
    def on_browse(self, event):
        # Allows the user to select an ECC dataset. ecc_dataset.local
        ecc_dataset = util_ecc.select_ecc_dataset(self._tab.top.datasets)
    
        if ecc_dataset:
            block = ecc_dataset.blocks["raw"]
            raw_data  = block.data.copy() * 0
            dims = ecc_dataset.raw_dims
            for k in range(dims[3]):
                for j in range(dims[2]):
                    for i in range(dims[1]):
                        dat = block.data[k,j,i,:].copy() / block.data[k,j,i,0]
                        raw_data[k,j,i,:] = dat
                    
            filter_ = self._tab.block.set.ecc_handler.active
            filter_.ecc_dataset = ecc_dataset
            filter_.ecc_raw     = raw_data
            self._filename = block.data_source
            self.TextEccFilename.SetValue(block.data_source)
            self._tab.process_and_plot()
