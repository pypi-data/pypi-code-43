# This file contains the routines for creating
# a hyperbolic secant (HS) pulse.

# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree
import math

# 3rd party modules

# Our modules
import vespa.common.constants as constants
import vespa.common.pulse_funcs.analytic_pulse as analytic_pulse
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.util.xml_ as util_xml
from   vespa.common.constants import Deflate

import vespa.common.rfp_transformation as rfp_transformation
import vespa.common.rfp_result as rfp_result


class HSParameterDefaults(object):
    """Default values for the Hyperbolic Secant pulse"""

    TOTAL_ROTATION          = 1440.0
    TIME_POINTS             = 250
    WAS_BANDWIDTH_SPECIFIED = False
    DWELL_TIME              = 32.0
    QUALITY_CYCLES          = 6.0
    POWER_N                 = 1
    SHARPNESS_MU            = 4.0
    FILTER_TYPE             = constants.FilterType.NO_SELECTION
    FILTER_APPLICATION      = 0.0


class HyperbolicSecantPulseParameters(object):
    """
    An class that describes the data needed for the creation
    of a hyperbolic-secant pulse. 
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        # total_rotaion, in degrees
        self.total_rotation = HSParameterDefaults.TOTAL_ROTATION
        
        # number of points:
        # In MATPULSE, there is an assumed point at zero.
        # We are not making use of this assumption.
        self.time_points = HSParameterDefaults.TIME_POINTS
        
        # dwell_time is in microseconds (i.e. 10**-6 seconds)
        self.dwell_time = HSParameterDefaults.DWELL_TIME
        
        # The dwell time can be calculated from the bandwidth and vice 
        # versa. (See the function dwell_bandwidth_interconvert().)
        # Internally, only the dwell time is important so that's what
        # this class stores. However we allow the user to describe the params
        # in terms of bandwidth. This flag indicates whether or not they've
        # done that.
        self.was_bandwidth_specified = HSParameterDefaults.WAS_BANDWIDTH_SPECIFIED

        # quality(cycles) of the pulse.
        # This has to do with how the pulse is truncated
        # since all the HS functions have long tails. 
        self.quality_cycles = HSParameterDefaults.QUALITY_CYCLES
        
        # power_n is the exponent in the HSn function:
        # w1(tau) = w1max * sech(Beta * (tau**n))
        # where tau is 2t / (Tp - 1)
        # See J.K.Park, L. DelaBarra, and M. Garwood
        # Mag.Resonance in Medicine 55:846-857 (2006)
        self.power_n = HSParameterDefaults.POWER_N
        
        # sharpness_mu is used in the HS function as follows:
        # w1(t) = w1max * (sech(beta*t))**(1 + i*mu)
        # It impacts the shape of the pulse and it's sharpness.
        self.sharpness_mu = HSParameterDefaults.SHARPNESS_MU
        
        self.filter_type = HSParameterDefaults.FILTER_TYPE
        
        # a percentage - "how much" the filter is applied.
        self.filter_application = HSParameterDefaults.FILTER_APPLICATION

        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)  

    @property
    def bandwidth(self):
        return self.dwell_bandwidth_interconvert(self.dwell_time, 
                                                 self.sharpness_mu, 
                                                 self.quality_cycles, 
                                                 self.time_points)     

    @property
    def duration(self):
        return self.time_points * self.dwell_time / 1000.0 # in [ms]
    

    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # e = parameters_element
            e = ElementTree.Element("parameters", 
                                      {"version" : self.XML_VERSION})
            
            for attribute in ("total_rotation", "time_points", "dwell_time",
                              "quality_cycles", "power_n", 
                              "sharpness_mu", "filter_application", ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))
                
            util_xml.TextSubElement(e, "filter_type", self.filter_type["db"])

            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def dwell_bandwidth_interconvert(self, dtb, sharpness_mu, cycles, time_points):        
        # From MLLSWDC.M  and  MLLDWTC.M
        # e.g. mlldwell = mlltpf*mllnocv*1000/(mllnopv*mllswv) ;
        # Note: dwell_time in microseconds and bandwidth in kHz.
        multiplier = sharpness_mu/math.pi
        
        return multiplier * cycles * 1000 / (time_points * dtb)

    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            for attribute in ("total_rotation", "dwell_time",
                              "quality_cycles", "sharpness_mu", 
                              "filter_application", ):
                setattr(self, attribute, float(source.findtext(attribute)))

            for attribute in ("time_points", "power_n", ):
                setattr(self, attribute, int(source.findtext(attribute)))
            
            self.filter_type = source.findtext("filter_type")
            self.filter_type = \
                constants.FilterType.get_type_for_value(self.filter_type, "db")
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


class HyperbolicSecantPulseTransformation(rfp_transformation.Transformation):
    """ 
    Parameters for Hyperbolic Secant (aka Adiabatic) pulse generation.
    """    
    def __init__(self, attributes=None):
        rfp_transformation.Transformation.__init__(self,
                         constants.TransformationType.CREATE_HYPERBOLIC_SECANT)
        
        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)
        
            
    def create_pulse(self, machine_settings, master_parameters):
        
        # First, convert parameters to pulse_funcs values.
        # Second, call "the function" to generate our results.
        
        pulse_type = pf_constants.AnalyticType.HYPERBOLIC_SECANT        
        
        
        total_rotation = self.parameters.total_rotation
        time_points = self.parameters.time_points
        dwell_time = self.parameters.dwell_time
        cycles = self.parameters.quality_cycles
        n = self.parameters.power_n
        mu = self.parameters.sharpness_mu
        
        filter_type = self.parameters.filter_type
        if filter_type == constants.FilterType.COSINE:
            filter_type = pf_constants.ApodizationFilterType.COSINE
        elif filter_type == constants.FilterType.HAMMING:
            filter_type = pf_constants.ApodizationFilterType.HAMMING
        else:
            filter_type = None
        
        filter_application = self.parameters.filter_application      
        
        rf_y = analytic_pulse.hyperbolic_secant(time_points, cycles,
                                    filter_type, filter_application, 
                                    total_rotation, n, mu, dwell_time)
        
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
          

    def deflate(self, flavor=Deflate.ETREE):
        # I start by getting my base class to deflate itself, then I append
        # the values specific to this class.
        base = rfp_transformation.Transformation.deflate(self, flavor)
        if flavor == Deflate.ETREE:
            # At present I have nothing to add
            pass
        elif flavor == Deflate.DICTIONARY:
            base.update(self.__dict__)
            
        return base

    
    def inflate(self, source):
        # I start by getting my base class to inflate itself, then I read
        # the values specific to this class.
        base = rfp_transformation.Transformation.inflate(self, source)

        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            # At present I have nothing to add
            pass
        elif hasattr(source, "keys"):
            # Quacks like a dict
            raise NotImplementedError
