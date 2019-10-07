# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import ecc_filters.ecc_simple as ecc_simple
import ecc_filters.ecc_klose as ecc_klose
import ecc_filters.ecc_quality as ecc_quality
import ecc_filters.ecc_quecc as ecc_quecc
import ecc_filters.ecc_traf as ecc_traf

from vespa.common.constants import Deflate

_ALL_FILTER_CLASSES = [ 
                       ecc_simple.EccSimple,
                       ecc_klose.EccKlose,
                       ecc_quality.EccQuality,
                       ecc_quecc.EccQuecc,
                       ecc_traf.EccTraf,
                      ]



class EccHandler(object):
    """
    This is a class to help organize the various ecc filters that 
    can be selected during spectral processing. 
    """
    
    XML_VERSION = "1.0.0"
    
    def __init__(self):
        self._active_id = ''
        
        self._filters = { }
        
        self._preset_save_raw = None
        self._preset_save_dataset = None
        self._preset_save_dataset_id = None
        self._preset_save_filename = ""
        
        # Instantiate each filter
        for klass in _ALL_FILTER_CLASSES:
            self._filters[klass.ID] = klass()


    ##############      Properties      ##############

    @property
    def active(self):
        """Returns the active filter, or None if no filter is active"""
        return self._filters.get(self._active_id, None)


    @property
    def names_and_ids(self):
        """Returns a list of 2-tuples of (name, id) sorted by name. There's 
        one tuple in the list for each filter. 
        """
        names = [filter_.DISPLAY_NAME for filter_ in self._filters.values()]
            
        return sorted(zip(names, self._filters.keys()))

    @property
    def active_id(self):
        """Returns the active filter id, which is '' if no filter is active"""
        return self._active_id

    ##############      Methods      ##############

    def activate(self, id_):
        """Activates the filter with the given id. If the id is None or "",
        no filter is active (i.e. this object's .active property returns 
        None).
        
        If the id refers to a filter that this handler doesn't know about,
        it raises a ValueError.
        """
        if id_ and (id_ not in self._filters):
            raise ValueError, "No ECC filter with id '%s'" % id_
            
        self._active_id = id_


    def algorithm(self, chain):
        """Executes the active filter's functor's algorithm. If no filter is 
        active, this is a no-op.
        """
        if self.active:
            self.active.functor.algorithm(chain)


    def destroy_guis(self):
        """Destroys any GUI elements (panels) associated with this 
        handler's filters. This should be called before this handler is
        deleted to ensure cleanup of any wx objects that were created by
        the filters.
        
        In a perfect world, we'd implement this code in __del__ so this 
        function wouldn't need to be called explicitly. However, there are
        enough scary admonitions against using __del__ that I'm afraid to
        rely on it.
        """
        for filter_ in self._filters.values():
            if filter_._panel:
                filter_._panel.Destroy()


    def update(self, other):
        """Forces the active filter to update. If no filter is active,
        this is a no-op.
        """
        if self.active:
            self.active.functor.update(other)
            
    def configure_as_preset(self, val):
        """
        Here we copy dataset-specific attribute values into temporary
        values at the handler level. Then we set these attributes to None/Null
        values to handle the call to deflate them into a 'preset' file. After
        this, we need to call this method again with val=False to copy the
        original values back to the ecc object. Note that we must also set the
        temporary storage attributes to Null values to allow for proper garbage
        handling if necessary.
        
        """
        if val == True:
            if self.active:
                self._preset_save_raw = self.active.ecc_raw
                self._preset_save_dataset = self.active.ecc_dataset
                self._preset_save_dataset_id = self.active.ecc_dataset_id
                self.active.ecc_raw = None
                self.active.ecc_dataset = None
                self.active.ecc_dataset_id = None
                if self.active._panel:
                    self._preset_save_filename = self.active._panel._filename
                    self.active._panel._filename = ""
        else:
            if self.active:
                self.active.ecc_raw = self._preset_save_raw
                self.active.ecc_dataset = self._preset_save_dataset
                self.active.ecc_dataset_id = self._preset_save_dataset_id
                self._preset_save_raw = None
                self._preset_save_dataset = None
                self._preset_save_dataset_id = None
                if self.active._panel:
                    self.active._panel._filename = self._preset_save_filename
                    self._preset_save_filename = ""
        
        
        
        
