# Python modules
from __future__ import division

# 3rd party modules
import xml.etree.cElementTree as ElementTree

# Our modules
import water_filters.water_filter_fir as water_filter_fir
import water_filters.water_filter_hamming as water_filter_hamming
import water_filters.water_filter_hlsvd as water_filter_hlsvd

from vespa.common.constants import Deflate


_ALL_FILTER_CLASSES = [ water_filter_fir.WaterFilterFir,
                        water_filter_hamming.WaterFilterHamming,
                        water_filter_hlsvd.WaterFilterHlsvd]



class WaterFilterHandler(object):
    """
    This is a class to help organize the various water filters that 
    can be selected during spectral processing. 
    """
    
    XML_VERSION = "1.0.0"
    
    def __init__(self):
        self._active_id = ''
        self._filters = { }

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


    ##############      Methods      ##############

    def activate(self, id_):
        """Activates the filter with the given id. If the id is None or "",
        no filter is active (i.e. this object's .active property returns 
        None).
        
        If the id refers to a filter that this handler doesn't know about,
        it raises a ValueError.
        """
        if id_ and (id_ not in self._filters):
            raise ValueError, "No water filter with id '%s'" % id_
            
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

