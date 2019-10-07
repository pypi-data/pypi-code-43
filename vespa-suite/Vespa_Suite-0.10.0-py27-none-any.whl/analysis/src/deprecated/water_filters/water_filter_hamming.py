# Python imports
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party imports
import numpy as np

# Vespa imports
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import water_filters.water_filter as water_filter
import functors.functor as functor
import time_series_extrapolate as ts_extrap
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc

from vespa.common.constants import Deflate


class FilterConstants(object):
    
    LENGTH_MIN = 1
    LENGTH_MAX = 99
    LENGTH_DEFAULT = 11

    EXTRAPOLATION_ALL = ['None', 'Linear', 'AR Model']
    EXTRAPOLATION_DEFAULT = EXTRAPOLATION_ALL[0]

    EXTRAPOLATION_POINTS_MIN = 1
    EXTRAPOLATION_POINTS_MAX = 1000
    EXTRAPOLATION_POINTS_DEFAULT = 10


def _create_panel(parent, tab, filter_):
    # These imports are inline so that wx doesn't get imported unless we
    # receive an explicit request for a GUI object.
    import panel_water_filter_hamming
    
    return panel_water_filter_hamming.PanelWaterFilterHamming(parent, tab, filter_)


class WaterFilterHamming(water_filter.WaterFilter):
    
    XML_VERSION = "1.0.0"

    ID = "32fb31c6-20d2-47bb-9275-402ad8afa71d"

    DISPLAY_NAME = 'Hamming - water filter'


    def __init__(self, attributes=None):
        self.length                     = FilterConstants.LENGTH_DEFAULT
        self.extrapolation_method       = FilterConstants.EXTRAPOLATION_DEFAULT
        self.extrapolation_point_count  = FilterConstants.EXTRAPOLATION_POINTS_DEFAULT

        self.functor = _FunctWaterFilterHamming()

        self._panel = None
        
        if attributes is not None:
            self.inflate(attributes)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("----------- WaterFilterHamming ---------------")
        lines.append("length                    : " + unicode(self.length))
        lines.append("extrapolation_method      : " + unicode(self.extrapolation_method))
        lines.append("extrapolation_point_count : " + unicode(self.extrapolation_point_count))

        # __unicode__() must return a Unicode object. In practice the code
        # above always generates Unicode, but we ensure it here.
        lines =  u'\n'.join(lines)

        return lines


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # Get my base class to deflate itself
            e = water_filter.WaterFilter.deflate(self, flavor)
            
            # handle the things that are specific to this class.
            util_xml.TextSubElement(e, "length", self.length)
            util_xml.TextSubElement(e, "extrapolation_method", self.extrapolation_method)
            util_xml.TextSubElement(e, "extrapolation_point_count", self.extrapolation_point_count)

            return e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            # Get my base class to inflate itself
            e = water_filter.WaterFilter.inflate(self, source)
            
            # Now inflate the things specific to this class
            self.extrapolation_method = source.findtext("extrapolation_method")

            for name in ("length", 'extrapolation_point_count' ):
                setattr(self, name, int(source.findtext(name)))

        elif hasattr(source, "keys"):
            raise NotImplementedError


    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # self._panel is only created as needed. 
        if not self._panel:
            self._panel = _create_panel(parent, tab, self)
            
        return self._panel
        



class _FunctWaterFilterHamming(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):

        self.length                     = FilterConstants.LENGTH_DEFAULT
        self.extrapolation_method       = FilterConstants.EXTRAPOLATION_DEFAULT
        self.extrapolation_point_count  = FilterConstants.EXTRAPOLATION_POINTS_DEFAULT

        self.attribs = ("length",
                        "extrapolation_method", 
                        "extrapolation_point_count")
        

    ##### Standard Methods and Properties #####################################

    
    def update(self, other):    
        filter_ = other.water_handler.active
        for attr in self.attribs:
            util_misc.safe_attribute_set(filter_, self, attr) 
            

    def algorithm(self, chain):
        
        filter_length = self.length
        extrapolation_method = self.extrapolation_method
        extrapolation_point_count = self.extrapolation_point_count
        
        water_time = 0

        # get Hamming filter
        hamming_filter = np.hamming(filter_length + 1)[0:filter_length]

        # normalize
        hamming_filter = hamming_filter / sum(hamming_filter)

        # Convolution function is always high-pass, so get water function
        water_time = np.convolve(chain.data, hamming_filter, 1)

        if extrapolation_method == 'Linear':
            k2 = (filter_length - 1) // 2
            x  = np.arange(k2)

            # Get slope of linear fit
            slope = np.polyfit(x, water_time[k2:k2+k2], 1)[0]

            for j in range(int(k2)):
                water_time[j] = water_time[k2] + ((k2 - j) * slope)

        elif extrapolation_method == 'AR Model':
            k = (filter_length - 1) // 2
            p = extrapolation_point_count

            rwdata = ts_extrap.time_series_forecast(water_time[k:].real, p, k, backcast=True)
            iwdata = ts_extrap.time_series_forecast(water_time[k:].imag, p, k, backcast=True)

            # will return NaN if constant function !
            if not np.isfinite(rwdata[0]):
                rwdata = np.zeros(k,float)+water_time[k].real
                #rwdata = replicate(water_time[k].real, k)
            if not np.isfinite(iwdata[0]):
                iwdata = np.zeros(k,float)+water_time[k].imag
                #iwdata = replicate(water_time[k].imag, k)

            water_time[0:k] = rwdata + 1j * iwdata

        # Return the time data with the water estimate subtracted

        chain.data = chain.data - water_time       
  
