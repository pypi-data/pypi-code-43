# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree
import math

# 3rd party modules
import numpy as np

# Our modules
from vespa.common.constants import Deflate
import vespa.common.util.xml_ as util_xml
import vespa.common.util.time_ as util_time
import vespa.common.util.fileio as util_fileio
import vespa.common.bloch_call as bloch_call
import vespa.common.rfp_ocn_state as rfp_ocn_state
import vespa.common.constants as constants
import vespa.common.pulse_funcs.grad_refocus as grad_refocus
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


class Result(object):
    """
    The result-set of a 'transformation' in the context of a synthesizing and
    modifying a radio frequency pulse, its gradient(s), and (raw) frequency 
    profile(s).
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        """
        The attributes param to init() should contain 
        
        rf       - A Waveform object
        
        gradient - A Gradient object containing the gradient 
                   that is in place during the rf waveform. May include
                   a single number or a time dependent array and optional 
                   carrier wave frequency modulation. Defaults to None
        
        created - A DateTime object representing the creation time.
        
        """
        self.created = util_time.now()
        
        # A Waveform object.
        self.rf = None

        # Gradient object 
        self.gradient = None
 
        # Waveform and x-axis unit temporary results

        self.mz    = None
        self.mxy   = None
        self.xaxis = None
        
        self.mz_ext    = None
        self.mxy_ext   = None
        self.xaxis_ext = None
                
        # Gradient Refocusing fractional Value
        self.grad_refocus_fraction = 0.0

        self.refocused_profile = None
        
        # An rfp_ocn_state.OCSNtate object.
        self.ocn_state = None
   
        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)


    @property
    def dwell_time(self):
        "Returns the dwell_time in microseconds"
        if len(self.rf.waveform_x_axis) > 1:
            return 1000000 * (self.rf.waveform_x_axis[1] - \
                              self.rf.waveform_x_axis[0])
        else:
            return 0.0


      
    def gradient_refocusing(self, val=None):
        # This function calls a routine that may throw an exception of type
        #  pulse_func_exception.PulseFuncException
        
        profile, ax = self.get_profile(constants.UsageType.EXCITE)
        
        length = len(self.rf.waveform_x_axis)
        mpgpulms = 1000.0*(self.rf.waveform_x_axis[length-1]) + self.dwell_time/1000.0
        
        if val is None:        
            try:
                val = grad_refocus.grad_refocus(ax, profile, mpgpulms)
            except pulse_func_exception.PulseFuncException:
                val = 0.5 
            pass
    
        ic = complex(0,1)
        
        self.grad_refocus_fraction = val
        self.refocused_profile = np.exp(ic*2.0*math.pi*val*ax*mpgpulms)*profile

        return val


    def update_profiles(self, resolution):
        """Recalculate the profile(s) using the Bloch equation"""
        if self.rf:
            rf_y = self.rf.waveform
            rf_x = self.rf.waveform_x_axis
            if len(rf_x) >= 2:
                # Convert dwell time into microseconds.
                dwell_time = (rf_x[1] - rf_x[0])*1000000.0
            else:
                return

            bout = bloch_call.calc_all_profiles(rf_y, dwell_time, resolution)

            self.mz        = bout[0]
            self.mxy       = bout[1]
            self.xaxis     = bout[2]
            self.mz_ext    = bout[3]
            self.mxy_ext   = bout[4]
            self.xaxis_ext = bout[5]     


    def get_profile(self, use_type, extended=False, absolute=False):
        """
        We can display results for extended or standard width x-range, and
        for four usage types = Excite, Inversion, Saturation, SpinEcho.
        
        This is a total of 8 profiles we can extract from our RF complex
        waveform. 
        
        This method lets user specify which one to return. Note. all of these
        plots are already pre-calculated, we are just choosing which to show.
        
        """

        if use_type == constants.UsageType.EXCITE or \
           use_type == constants.UsageType.INVERSION or \
           use_type == constants.UsageType.SATURATION:
            
            if extended == True:
                y = self.mz_ext
                x = self.xaxis_ext
            else:
                y = self.mz
                x = self.xaxis
                
        elif use_type == constants.UsageType.SPIN_ECHO:
            
            if extended == True:
                y = self.mxy_ext
                x = self.xaxis_ext
            else:
                y = self.mxy
                x = self.xaxis

        yout = np.zeros(len(y), np.complex128)        
        for i in range(len(y)):
            # FIXME - bjs, could change this to list comprehension?
            if use_type == constants.UsageType.EXCITE:            
                yout[i] = complex(y[i][0], y[i][1])
            elif use_type == constants.UsageType.SATURATION:
                yout[i] = complex(y[i][2], 0)
            elif use_type == constants.UsageType.INVERSION:
                yout[i] = complex(-y[i][2], 0)
            elif use_type == constants.UsageType.SPIN_ECHO:
                yout[i] = complex(y[i][0], -y[i][1])                 
        
        if absolute:
            yout = np.abs(yout)       

        return (yout, x)


    def get_gradient(self):
        
        if self.gradient is None: 
            x = self.rf.waveform_x_axis
            y = np.copy(x)*0.0
        elif self.gradient.gradient_waveform:
            x = self.gradient.time_points
            y = self.gradient.gradient_waveform
            
        return (y,x)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            
            e = ElementTree.Element("result", {"version" : self.XML_VERSION})
            
            util_xml.TextSubElement(e, "created", self.created)
            
            if self.rf:
                e.append(self.rf.deflate(flavor))

            if self.gradient:
                e.append(self.gradient.deflate(flavor))

            if self.ocn_state:
                e.append(self.ocn_state.deflate(flavor))
                
            return e
        
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            self.created = source.findtext("created")
            self.created = util_time.datetime_from_iso(self.created)
            
            # We need an explicit test for None below; casting to bool doesn't
            # work as expected. See "caution" at the end of this section:
            # http://docs.python.org/release/2.6.6/library/xml.etree.elementtree.html#the-element-interface
            
            e = source.find("rf_pulse")
            if e is not None:
                self.rf = Waveform(e)
                
            e = source.find("gradient")
            if e is not None:
                self.gradient = Gradient(e)

            e = source.find("ocn_state")
            if e is not None:
                self.ocn_state = rfp_ocn_state.OCNState(e)
                
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])

            if "rf" in source:
                self.rf = source["rf"]



class Waveform(object):   
    """
    A radio frequency pulse, suitable for an MRI machine.
    """ 
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        # List of complex numbers. units; microTesla
        self.waveform = [ ]
        # List of floats, units of time in seconds.
        # Note: display should be in milliSeconds.
        self.waveform_x_axis = [ ]
        
        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)
        
        
    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            
            e = ElementTree.Element("rf_pulse", {"version" : self.XML_VERSION})
            
            data_type = type(self.waveform[0]) if self.waveform else complex
            data_element = util_xml.numeric_list_to_element(self.waveform,
                                                            data_type,
                                                            "waveform")
            e.append(data_element)

            data_type = type(self.waveform_x_axis[0]) if self.waveform_x_axis else float
            data_element = util_xml.numeric_list_to_element(self.waveform_x_axis,
                                                            data_type,
                                                            "waveform_x_axis")
            e.append(data_element)
            
            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            self.waveform = source.find("waveform")
            self.waveform = util_xml.element_to_numeric_list(self.waveform)

            self.waveform_x_axis = source.find("waveform_x_axis")
            self.waveform_x_axis = \
                        util_xml.element_to_numeric_list(self.waveform_x_axis)

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])
                    
                    
class Gradient(object):
    """
    Magnetic Field Gradient applied before, during or after an 
    rf pulse for slice selection, phase selection, etc.
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        self.linear_gradient = 0.0       
        self.refocusing_gradient = 0.0   # (double) We will save refocusing gradient 
                                         # as a number; i.e. a % of gradient that 
                                         # needs to be inverted and applied.  
                                         # If a user want to do more than that, 
                                         # they will have to apply concatenation, 
                                         # etc....
        self.frequency_offset = 0.0
        
        self.time_points  = []  # Units of time; milliSeconds.        
        
        self.gradient_waveform     = []  # If exists, we have a "G2". 
                                           # units; milliTesla/Meter
                
        self.f2_frequency_waveform = []   # F2 - carrier frequency. 
                                            # units; kiloHertz (kHz).
                                            # ...to stay in same slice.
                                            # same x_axis as gradient.

        if attributes:
            self.inflate(attributes)
            

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # g_e = gradient_element
            g_e = ElementTree.Element("gradient",
                                      {"version" : self.XML_VERSION})

            for attribute in ("linear_gradient", "refocusing_gradient", 
                              "frequency_offset", ):
                util_xml.TextSubElement(g_e, attribute, getattr(self, attribute))
            
            # time_points is a list of floats, I think, but if there's data
            # in the list I'll infer the type from the data.
            data_type = util_fileio.get_data_type(self.time_points, float)
            data_element = \
                util_xml.numeric_list_to_element(self.time_points, data_type,
                                                 "time_points")                                    
            g_e.append(data_element)

            # gradient_waveform is a list of floats; see comment above.
            data_type = util_fileio.get_data_type(self.gradient_waveform, float)
            data_element = \
                util_xml.numeric_list_to_element(self.gradient_waveform,
                                                 data_type,
                                                 "gradient_waveform")                                    
            g_e.append(data_element)          

            # f2_frequency_waveform is a list of floats; see comment above.
            data_type = util_fileio.get_data_type(self.f2_frequency_waveform, float)
            data_element = \
                util_xml.numeric_list_to_element(self.f2_frequency_waveform,
                                                 data_type,
                                                 "f2_frequency_waveform")                                    
            g_e.append(data_element)          
            
            return g_e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):

        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            for attribute in ("linear_gradient", "refocusing_gradient", 
                              "frequency_offset", ):
                setattr(self, attribute, source.findtext(attribute))

            self.time_points = source.find("time_points")
            self.time_points = util_xml.element_to_numeric_list(self.time_points)
            
            self.gradient_waveform = source.find("gradient_waveform")
            self.gradient_waveform = \
                    util_xml.element_to_numeric_list(self.gradient_waveform)
            
            self.f2_frequency_waveform = source.find("f2_frequency_waveform")
            self.f2_frequency_waveform = \
                    util_xml.element_to_numeric_list(self.f2_frequency_waveform)

        elif hasattr(source, "keys"):
            # Quacks like a dict            
            self.linear_gradient = source["linear_gradient_value"]
            self.refocusing_gradient = source["refocused_gradient"]
            self.frequency_offset = source["frequency_offset"]
            
            
    def set_gradient_waveform(self, grad, time):
        assert(len(grad) == len(time))
        self.time_points = time
        self.gradient_waveform = grad
                
    def set_f2(self, freq):
        assert(self.time_points is not None)
        self.f2_frequency_waveform = freq[:len(self.time_points)]
            
    def clear_f2(self):
        f2_frequency_waveform = []
        
    def clear_gradient_waveform(self):
        self.time_points = []
        self.gradient_waveform = []
        f2_frequency_waveform = []                    
                    
                    