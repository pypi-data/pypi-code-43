# This file contains the routines for creating
# a pulse from first principles.

# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree


# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.pulse_funcs.slr_pulse as slr_pulse
import vespa.common.pulse_funcs.pulse_func_exception
import vespa.common.pulse_funcs.constants as pf_constants
import vespa.common.pulse_funcs.util as pulse_funcs_util
import vespa.common.rfp_transformation as trans
import vespa.common.rfp_result as rfp_result
import vespa.common.util.xml_ as util_xml
from vespa.common.constants import Deflate

class SLRParameterDefaults(object):
    """Default values for the constructor of SLRPulseParameters"""
    TIP_ANGLE           = 90.0
    TIME_POINTS         = 250
    DURATION            = 8.0
    BANDWIDTH           = 1.0
    SEPARATION          = 1.0 
    IS_SINGLE_BAND      = True
    NC_PHASE_SUBTYPE    = constants.NonCoalescedPhaseSubtype.LINEAR
    USE_REMEZ           = True
    PASS_RIPPLE         = 1.0
    REJECT_RIPPLE       = 1.0

# Tip angles are currently limited as shown below. Kim's paper has shown that 
# we can use tip angles outside of this range, but we haven't written the 
# code yet. Since it seems possible that our code will lift this limitation
# in the future, we're keeping the validity function and related message 
# next to one another to ensure that they stay in sync. 
TIP_ANGLE_RANGE_MESSAGE = "The tip angle must be 90, 180 or <= 30."

def is_tip_angle_valid(tip_angle):
    """True if tip angle in the range we know how to handle; False otherwise."""
    return (tip_angle == 90)                            or \
           (tip_angle == 180)                           or \
           ((tip_angle > 0) and (tip_angle <=30))


 
class SLRPulseParameters(object):
    """
    Holds the data needed for the creation of an SLR style RF pulse. 
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        # tip_angle is in degrees
        self.tip_angle    = SLRParameterDefaults.TIP_ANGLE
        
        # number of points:
        # In MATPULSE, there is an assumed point at value of zero.
        # Keep this implicit point at zero?  Any Machine effects?
        self.time_points  = SLRParameterDefaults.TIME_POINTS
        
        # duration is in milliseconds 
        self.duration     = SLRParameterDefaults.DURATION
        
        # bandwidth is in kHz
        self.bandwidth    = SLRParameterDefaults.BANDWIDTH
        
        # separation is in kHz and is used only for dual band pulses.
        self.separation   = SLRParameterDefaults.SEPARATION      
        
        self.is_single_band  = SLRParameterDefaults.IS_SINGLE_BAND
        
        # Subtype of non_coalesced: enum [min, max, other]
        self.nc_phase_subtype   = SLRParameterDefaults.NC_PHASE_SUBTYPE 
        
        self.use_remez = SLRParameterDefaults.USE_REMEZ
        
        # ripple values are percentages
        self.pass_ripple = SLRParameterDefaults.PASS_RIPPLE
        self.reject_ripple = SLRParameterDefaults.REJECT_RIPPLE        

        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)
        
    @property    
    def dwell_time(self):
        """Returns the dwell_time in microseconds."""
        return pulse_funcs_util.calculate_dwell_time(self.time_points, 
                                                     self.duration)
    
    
    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # e = parameters_element
            e = ElementTree.Element("parameters", 
                                      {"version" : self.XML_VERSION})
            
            for attribute in ("tip_angle", "time_points", "duration", 
                              "bandwidth", "separation", "is_single_band", ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))
            
            util_xml.TextSubElement(e, "nc_phase_subtype", self.nc_phase_subtype["db"])

            for attribute in ("use_remez", "pass_ripple", "reject_ripple", ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))

            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)

    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            for attribute in ("tip_angle", "duration", "bandwidth", 
                              "separation", ):
                setattr(self, attribute, float(source.findtext(attribute)))
                
            for attribute in ("time_points", ):
                setattr(self, attribute, int(source.findtext(attribute)))
            
            self.is_single_band = \
                        util_xml.BOOLEANS[source.findtext("is_single_band")]
            
            self.nc_phase_subtype = source.findtext("nc_phase_subtype")
            self.nc_phase_subtype = \
                constants.NonCoalescedPhaseSubtype.get_type_for_value(self.nc_phase_subtype, "db")
                
            self.use_remez = util_xml.BOOLEANS[source.findtext("use_remez")]
            self.pass_ripple = float(source.findtext("pass_ripple"))
            self.reject_ripple = float(source.findtext("reject_ripple"))
                            
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


class SLRPulseTransformation(trans.Transformation):
    """Used to Create an SLR (Shinnar-Le Roux) style pulse"""

    def __init__(self, attributes=None):
        trans.Transformation.__init__(self, 
                                      constants.TransformationType.CREATE_SLR)
        
        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)
                 

    def create_pulse(self, machine_settings, master_parameters):
        """
        Calculates the pulse waveform and then updates the profiles.
        Adjusts some parameters to be in the correct units before 
        the call to slr_pulse( ).
        
        Note: Be prepared to catch the exception,
        pulse_func_exception.PulseFuncException
        which may be raised by slr_pulse(), 
        but intentionally not caught here.
        """
        
        # Adopted from MPLPM.M        

        nct = self.parameters.nc_phase_subtype
        if nct == constants.NonCoalescedPhaseSubtype.MAX:
            # Max
            ptype = 2          
        elif nct == constants.NonCoalescedPhaseSubtype.MIN:
            # Min
            ptype = 3
        else:
            # linear (a.k.a. refocused)
            ptype = 1            

        # Pulse angle category (90, 180, shallow tip)
        if not is_tip_angle_valid(self.parameters.tip_angle):
            # ::FIXME:: Implement handling of non-standard tip angles, a la Kim's paper
            raise NotImplementedError(TIP_ANGLE_RANGE_MESSAGE)
         
        # Pulse bands (single band / dual band)g.
        if self.parameters.is_single_band:
            bandwidth = self.parameters.bandwidth
            separation = 0.0
        else:
            bandwidth = self.parameters.bandwidth
            separation = self.parameters.separation
            # NOTE: J.M. had some concern about these pulse types,
            # specifically about the "d.c." offset for the reject
            # band. This is something that could be explored in more 
            # detail.
            

        bandwidth_convention = 0
        if master_parameters.pulse_bandwidth_convention == constants.PulseConvention.MINIMUM:
            bandwidth_convention = 1
        elif master_parameters.pulse_bandwidth_convention == constants.PulseConvention.MAXIMUM:
            bandwidth_convention = 2

        # Call the SLR Pulse generating code.
        rf_y, rf_x, profiles = slr_pulse.slr_pulse(self.parameters.time_points, 
                                                     master_parameters.calc_resolution, 
                                                     self.parameters.dwell_time, 
                                                     self.parameters.duration,
                                                     self.parameters.tip_angle*np.pi/180.0,
                                                     self.parameters.pass_ripple,
                                                     self.parameters.reject_ripple,
                                                     ptype,                                                      
                                                     bandwidth, 
                                                     is_single_band=self.parameters.is_single_band,
                                                     separation=separation, 
                                                     use_remez=self.parameters.use_remez, 
                                                     n_zero_pad=machine_settings.zero_padding,
                                                     bandwidth_convention=bandwidth_convention)
         
                
        rf = rfp_result.Waveform({"waveform"        : rf_y.tolist(), 
                                  "waveform_x_axis" : rf_x})
        
        self.result = rfp_result.Result({"rf" : rf})
        
        # Generate new frequency profiles here, using the Bloch equations.
        self.result.update_profiles(master_parameters.calc_resolution)
       
        return self.result
    
    def convert_type_prof_to_freq(self, profile_type):
        if profile_type == pf_constants.ProfileType.M_XY:
            return constants.FreqProfileType.M_XY
        elif profile_type == pf_constants.ProfileType.M_X_MINUS_Y:
            return constants.FreqProfileType.M_X_MINUS_Y
        elif profile_type == pf_constants.ProfileType.M_Z:
            return constants.FreqProfileType.M_Z
        elif profile_type == pf_constants.ProfileType.M_MINUS_Z:
            return constants.FreqProfileType.M_MINUS_Z
        else:
            return constants.FreqProfileType.NONE

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
