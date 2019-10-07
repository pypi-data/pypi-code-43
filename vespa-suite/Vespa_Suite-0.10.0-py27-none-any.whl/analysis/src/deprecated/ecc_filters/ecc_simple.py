# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports
import numpy as np

# Vespa imports
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import ecc_filters.ecc_filter as ecc_filter
import functors.functor as functor
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc
from vespa.common.constants import Deflate


#----------------------------------------------------------
# Simple Eddy Current Correction

  
def _create_panel(parent, tab, attributes):
    # This import is inline so that wx doesn't get imported unless we
    # receive an explicit request for a GUI object.
    import panel_simple
    
    return panel_simple.PanelSimple(parent, tab, attributes)



class EccSimple(ecc_filter.EccFilter):
    
    XML_VERSION = "1.0.0"

    ID = "f0c8b367-db67-42f0-ac3b-cec146f9a315"

    DISPLAY_NAME = 'Simple'

    def __init__(self, attributes=None):
        ecc_filter.EccFilter.__init__(self, attributes)
        
        self.ecc_raw = None
        self.ecc_dataset = None

        # this id is only used to find the dataset in the top level list
        # after a viff file is opened
        self.ecc_dataset_id = None

        self.functor = _FunctEccSimple()

        self._panel = None
        
        self._gui_data = None

        if attributes is not None:
            self.inflate(attributes)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("------------ EccSimple ---------------------")
        lines =  u'\n'.join(lines)

        return lines


    def get_associated_datasets(self, is_main_dataset=True):
        """
        Returns a list of datasets associated with this object
        
        The 'is_main_dataset' flag allows the method to know if it is the top
        level dataset gathering associated datasets, or some dataset that is
        only associated with the top dataset. This is used to stop circular
        logic conditions where one or more datasets refer to each other.

        """

        # We don't want datasets being stored in VIFF files to collide with ids
        # in memory now, should they be loaded right back in again. So, in the 
        # dataset.deflate() method, the dataset.id is changed, deflated and 
        # then restored. Here we just return the unaltered list of associated
        # datasets
        
        if self.ecc_dataset:
            return [self.ecc_dataset]
        else:
            return []


    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # self._panel is only created as needed. 
        if not self._panel:
            self._panel = _create_panel(parent, tab, self._gui_data)
            
        return self._panel
        

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # Get my base class to deflate itself
            e = ecc_filter.EccFilter.deflate(self, flavor)
            
            if self.ecc_dataset:
                # handle the things that are specific to this class.

                # In the next line, we *have* to save the uuid values from the 
                # actual object rather than from the attribute above, in  
                # order for the associated dataset uuid to reflect the new id
                # that is given in the top level dataset. Associated datasets are
                # given new temporary uuid values so that if the main dataset is 
                # saved and immediately loaded back in, we do not get collisions
                # between the newly opened datasets and already existing ones.
                
                util_xml.TextSubElement(e, "ecc_dataset_id", self.ecc_dataset.id)

            if self.ecc_raw is not None:
                e.append(util_xml.numpy_array_to_element(self.ecc_raw, 'ecc_raw'))

            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            # Get my base class to inflate itself
            e = ecc_filter.EccFilter.inflate(self, source)

            # handle the things that are specific to this class.
            for name in ('ecc_dataset_id',):
                tmp = source.findtext(name)
                if tmp: 
                    setattr(self, name, tmp)

            ecc_raw = source.find("ecc_raw")
            if ecc_raw is not None:
                self.ecc_raw = util_xml.element_to_numpy_array(ecc_raw)

        elif hasattr(source, "keys"):
            raise NotImplementedError



class _FunctEccSimple(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):
        self.ecc_dataset = None
        self.ecc_raw = None
        

    ##### Standard Methods and Properties #####################################

    
    def update(self, other):   
        if other.ecc_handler.active: 
            self.ecc_dataset = other.ecc_handler.active.ecc_dataset
            self.ecc_raw = other.ecc_handler.active.ecc_raw

            

    def algorithm(self, chain):
        
        if self.ecc_dataset: 
            voxel = chain.voxel

            ecc = self.ecc_raw[voxel[2],voxel[1],voxel[0],:]
            
            thresh = 0.01
            index = ((abs(ecc) < thresh).nonzero())[0]
            if len(index) > 0:
                phase = np.angle(ecc[index])
                tom = (thresh * (ecc[index]/abs(ecc[index])) * np.exp(1j * phase)).astype('complex64')
                ecc[index] = tom
            
            chain.data  = chain.data / ecc    

     
