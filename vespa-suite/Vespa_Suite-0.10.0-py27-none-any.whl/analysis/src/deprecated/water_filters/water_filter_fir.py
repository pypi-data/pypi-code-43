# Python imports
from __future__ import division

# 3rd party imports
import numpy as np
import scipy
import xml.etree.cElementTree as ElementTree

# Vespa imports
# These imports take advantage of the fact that Python adds analysis/src to
# sys.path when analysis/src/main.py is run.
import water_filters.water_filter as water_filter
import functors.functor as functor
import time_series_extrapolate as ts_extrap
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc

from vespa.common.constants import Deflate



#----------------------------------------------------------
# FIR (Finite Impulse Response) constants

class FilterConstants(object):
    
    LENGTH_MIN = 1
    LENGTH_MAX = 99
    LENGTH_DEFAULT = 11

    HALF_WIDTH_MIN = 0
    HALF_WIDTH_MAX = 500
    HALF_WIDTH_DEFAULT = 50
    HALF_WIDTH_STEP = 2

    RIPPLE_MIN = 0
    RIPPLE_MAX = 500
    RIPPLE_DEFAULT = 40
    RIPPLE_STEP = 2

    EXTRAPOLATION_ALL = ['None', 'Linear', 'AR Model']
    EXTRAPOLATION_DEFAULT = EXTRAPOLATION_ALL[0]

    EXTRAPOLATION_POINTS_MIN = 1
    EXTRAPOLATION_POINTS_MAX = 1000
    EXTRAPOLATION_POINTS_DEFAULT = 10




class WaterFilterFir(water_filter.WaterFilter):
    XML_VERSION = "1.0.0"

    ID = "58a41f52-38a0-46a2-bc4f-2e4a9a38d141"

    DISPLAY_NAME = 'FIR - water filter'

    def __init__(self, attributes=None):
        self.length                     = FilterConstants.LENGTH_DEFAULT
        self.half_width                 = FilterConstants.RIPPLE_DEFAULT
        self.ripple                     = FilterConstants.HALF_WIDTH_DEFAULT
        self.extrapolation_method       = FilterConstants.EXTRAPOLATION_DEFAULT
        self.extrapolation_point_count  = FilterConstants.EXTRAPOLATION_POINTS_DEFAULT

        self.functor = _FunctWaterFilterFir()

        self._panel = None
        
        if attributes is not None:
            self.inflate(attributes)


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("---------- WaterFilterFir -----------------")
        lines.append("length                    : " + unicode(self.length))
        lines.append("half_width                : " + unicode(self.half_width))
        lines.append("ripple                    : " + unicode(self.ripple))
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
            util_xml.TextSubElement(e, "half_width", self.half_width)
            util_xml.TextSubElement(e, "ripple", self.ripple)
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
            
            self.extrapolation_method = source.findtext("extrapolation_method")

            for name in ("length", 'extrapolation_point_count' ):
                setattr(self, name, int(source.findtext(name)))

            for name in ("half_width", 'ripple', ):
                setattr(self, name, float(source.findtext(name)))


        elif hasattr(source, "keys"):
            raise NotImplementedError


    def get_panel(self, parent, tab):
        """Returns the panel (GUI) associated with this filter"""
        # self._panel is only created as needed. 
        if not self._panel:
            self._panel = _create_panel(parent, tab, self)
            
        return self._panel


                          
class _FunctWaterFilterFir(functor.Functor):
    """ 
    This is a building block object that can be used to create a  
    processing chain for time domain to frequency domain spectral MRS 
    data processing.
    
    """
    
    def __init__(self):

        self.length                     = FilterConstants.LENGTH_DEFAULT
        self.half_width                 = FilterConstants.RIPPLE_DEFAULT
        self.ripple                     = FilterConstants.HALF_WIDTH_DEFAULT
        self.extrapolation_method       = FilterConstants.EXTRAPOLATION_DEFAULT
        self.extrapolation_point_count  = FilterConstants.EXTRAPOLATION_POINTS_DEFAULT

        self.attribs = ("length",
                        "half_width", 
                        "ripple", 
                        "extrapolation_method", 
                        "extrapolation_point_count")
        

    ##### Standard Methods and Properties #####################################

    
    def update(self, other):    
        filter_ = other.water_handler.active
        if filter_:
            for attr in self.attribs:
                util_misc.safe_attribute_set(filter_, self, attr) 
            
            

    def algorithm(self, chain):
        
        filter_length = self.length
        half_width = self.half_width
        ripple = self.ripple
        extrapolation_method = self.extrapolation_method
        extrapolation_point_count = self.extrapolation_point_count
        
        water_time = 0

        # Get filter cutoff in Hz in terms of Nyquist frequency,
        # 1/2T, where T is the time between data samples
        # Always do as lowpass, to simplify in removal part
        cutoff = 2 * half_width / chain.sw

        # FIR ripple is in db, and is converted to the approximate width
        # of the transition region (normalized so that 1 corresonds to pi)
        # for use in kaiser FIR filter design.
        width = (ripple - 8) / (2.285 * filter_length)

        # Approximate the digital_filter function with firwin
        # Differences are as high as 5% at width=0, and ~0% for larger widths
        h2o_filter = firwin(filter_length, cutoff, width)

        # normalize
        h2o_filter = h2o_filter / sum(h2o_filter)

        # convolution function is always high-pass, so get water function
        water_time = np.convolve(chain.data, h2o_filter, 1)
        
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
  
  

def _create_panel(parent, tab, filter_):
    # These imports are inline so that wx doesn't get imported unless we
    # receive an explicit request for a GUI object.
    import panel_water_filter_fir
    
    return panel_water_filter_fir.PanelWaterFilterFir(parent, tab, filter_)




#---------------------------------------------------------------------------
# The sinc() function in SciPy 0.8.0 (and probably older versions) causes 
# errors if the array contains zeros. This was fixed in SciPy 0.9.0. Since 
# we'd like to continue to support older versions of scipy, we use local 
# copies of sinc() and firwin() (which relies on sinc()) if the installed 
# scipy is < 0.9.0.

if scipy.__version__ >= "0.9.0":
    # It's safe to use the scipy versions of these
    sinc = scipy.sinc
    import scipy.signal
    firwin = scipy.signal.firwin
else:
    # If an older scipy is installed, I use my local versions
    def firwin(N, cutoff, width=None, window='hamming'):
        """
        FIR Filter Design using windowed ideal filter method.

        Parameters
        ----------
        N      -- order of filter (number of taps)
        cutoff -- cutoff frequency of filter (normalized so that 1 corresponds to
                  Nyquist or pi radians / sample)

        width  -- if width is not None, then assume it is the approximate width of
                  the transition region (normalized so that 1 corresonds to pi)
                  for use in kaiser FIR filter design.
        window -- desired window to use. See get_window for a list
                  of windows and required parameters.

        Returns
        -------
        h      -- coefficients of length N fir filter.

        """

        from scipy.signal.signaltools import get_window
        if isinstance(width,float):
            A = 2.285*N*width + 8
            if (A < 21): beta = 0.0
            elif (A <= 50): beta = 0.5842*(A-21)**0.4 + 0.07886*(A-21)
            else: beta = 0.1102*(A-8.7)
            window=('kaiser',beta)

        win = get_window(window,N,fftbins=1)
        alpha = N//2
        m = np.arange(0,N)
        h = win*sinc(cutoff*(m-alpha))
        return h / np.sum(h,axis=0)

    def sinc(x):
        """
        Returns sin(pi*x)/(pi*x) at all points of array x.

        """
        w = np.pi * np.asarray(x)
        # w might contain 0, and so temporarily turn off warnings
        # while calculating sin(w)/w.
        old_settings = np.seterr(all='ignore')
        s = np.sin(w) / w
        np.seterr(**old_settings)
        return np.where(x==0, 1.0, s)        



