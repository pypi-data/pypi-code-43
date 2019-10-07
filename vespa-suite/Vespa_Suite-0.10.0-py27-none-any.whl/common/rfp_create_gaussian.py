# This file contains the routines for creating
# a Gaussian pulse from first principles.

# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree


# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.pulse_funcs.analytic_pulse as analytic_pulse
import vespa.common.util.xml_ as util_xml
import vespa.common.pulse_funcs.pulse_func_exception
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.util as pulse_funcs_util
import vespa.common.rfp_transformation as trans
import vespa.common.rfp_result as rfp_result
from vespa.common.constants import Deflate

class GaussianParameterDefaults(object):
    """Default values for the constructor of SLRPulseParameters"""
    TIP_ANGLE               = 90.0
    TIME_POINTS             = 250
    DURATION                = 8.0
    BANDWIDTH               = 1.0
    FILTER_TYPE             = constants.FilterType.NO_SELECTION
    FILTER_APPLICATION      = 0.0

 
class GaussianPulseParameters(object):
    """
    Holds the data needed for the creation of a Gaussian Pulse. 
    """
    
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        # tip_angle is in degrees
        self.tip_angle    = GaussianParameterDefaults.TIP_ANGLE
        
        # number of points:
        self.time_points  = GaussianParameterDefaults.TIME_POINTS
        
        # duration is in milliseconds 
        self.duration     = GaussianParameterDefaults.DURATION
        
        # bandwidth is in kHz
        self.bandwidth    = GaussianParameterDefaults.BANDWIDTH
      
        self.filter_type  = GaussianParameterDefaults.FILTER_TYPE
        
        # a percentage - "how much" the filter is applied.
        self.filter_application = GaussianParameterDefaults.FILTER_APPLICATION      
        
      
        if attributes is not None:
            self.inflate(attributes)
        
    @property    
    def dwell_time(self):
        """Returns the dwell_time in microseconds."""
        return pulse_funcs_util.calculate_dwell_time(self.time_points, 
                                                     self.duration)
    
    
    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:

            e = ElementTree.Element("parameters", 
                                      {"version" : self.XML_VERSION})
            
            for attribute in ("tip_angle", 
                              "time_points", 
                              "duration", 
                              "bandwidth", 
                              "filter_application", ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))
            
            util_xml.TextSubElement(e, "filter_type", self.filter_type["db"])

            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)

    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            for attribute in ("tip_angle", 
                              "duration", 
                              "bandwidth", 
                              "filter_application", ):
                setattr(self, attribute, float(source.findtext(attribute)))
                
            for attribute in ("time_points", ):
                setattr(self, attribute, int(source.findtext(attribute)))
            
            self.filter_type = source.findtext("filter_type")
            self.filter_type = \
                constants.FilterType.get_type_for_value(self.filter_type, "db")
                            
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


class GaussianPulseTransformation(trans.Transformation):
    """Used to Create a Gaussian style pulse"""

    def __init__(self, attributes=None):
        trans.Transformation.__init__(self, 
                                      constants.TransformationType.CREATE_GAUSSIAN)

        if attributes:
            self.inflate(attributes)
                 

    def create_pulse(self, machine_settings, master_parameters):
        """
        Calculates the pulse waveform and then updates the profiles.
        Adjusts some parameters to be in the correct units before 
        the call to gaussian2( ).
        
        Note: Be prepared to catch the exception,
        pulse_func_exception.PulseFuncException
        which may be raised by gaussian2(), 
        but intentionally not caught here.
        """          

        filter_type = self.parameters.filter_type
        if filter_type == constants.FilterType.COSINE:
            filter_type = pf_constants.ApodizationFilterType.COSINE
        elif filter_type == constants.FilterType.HAMMING:
            filter_type = pf_constants.ApodizationFilterType.HAMMING
        else:
            filter_type = None
        
        filter_application = self.parameters.filter_application 

        dwell_time = self.parameters.dwell_time

        rf_y = analytic_pulse.gaussian3(self.parameters.time_points,
                                         dwell_time,
                                         self.parameters.bandwidth,
                                         filter_type, filter_application,
                                         self.parameters.tip_angle)   
        
        # Will only get the "y" component of the profile.
        # The x_axis we will have to generate locally.
        points = len(rf_y)
        rf_x = []        
        for ix in range(points):
            rf_x.append(ix*dwell_time/1000000.0)

        rf = rfp_result.Waveform({"waveform"        : rf_y.tolist(), 
                                  "waveform_x_axis" : rf_x})        
        
        self.result = rfp_result.Result({"rf" : rf})
        
        # Generate new frequency profiles here, using the Bloch equations.
        self.result.update_profiles(master_parameters.calc_resolution)
       
        return self.result
    

    def deflate(self, flavor=Deflate.ETREE):
        # I start by getting my base class to deflate itself, then I append
        # the values specific to this class.
        base = trans.Transformation.deflate(self, flavor)
        if flavor == Deflate.ETREE:
            # At present I have nothing to add
            pass
        elif flavor == Deflate.DICTIONARY:
            base.update(self.__dict__)
        
        return base

    def inflate(self, source):
        # I start by getting my base class to inflate itself, then I read
        # the values specific to this class.
        base = trans.Transformation.inflate(self, source)

        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            # At present I have nothing to add
            pass
        elif hasattr(source, "keys"):
            # Quacks like a dict
            raise NotImplementedError
