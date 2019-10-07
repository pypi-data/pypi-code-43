# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree


# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.rfp_result as rfp_result
import vespa.common.rfp_transformation as rfp_transformation
import vespa.common.pulse_funcs.interpolate as interpolate
import vespa.common.pulse_funcs.sg_smooth as sgsmooth
import vespa.common.pulse_funcs.rescale as rescale
import vespa.common.util.xml_ as util_xml
from vespa.common.constants import Deflate


class InterpolateRescaleParameterDefaults(object):
    """Default values for the constructor of InterpolateRescalePulseParameters"""
    INTERPOLATION_FACTOR   = 1
    NEW_DWELL_TIME         = 32.0
    ON_RESONANCE_TIP       = 90.0

    
class InterpolateRescaleParameters(object):
    """Parameters for Interpolation and Re-Scaling"""
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        # Interpolation
        self.do_interpolate = False 
        self.interpolation_factor = InterpolateRescaleParameterDefaults.INTERPOLATION_FACTOR
        self.new_dwell_time = InterpolateRescaleParameterDefaults.NEW_DWELL_TIME     

        # Scaling
        self.do_rescaling = False
        self.angle = InterpolateRescaleParameterDefaults.ON_RESONANCE_TIP

        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # e = parameters_element
            e = ElementTree.Element("parameters",
                                      {"version" : self.XML_VERSION})
            
            for attribute in ("do_interpolate", "interpolation_factor", 
                              "new_dwell_time", "do_rescaling", "angle", ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))

            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            for attribute in ("do_interpolate", "do_rescaling"):
                setattr(self, attribute, 
                        util_xml.BOOLEANS[source.findtext(attribute)])
            
            for attribute in ("interpolation_factor", ):
                setattr(self, attribute, int(source.findtext(attribute)))
            
            for attribute in ("new_dwell_time", "angle"):
                setattr(self, attribute, float(source.findtext(attribute)))
                
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])
                        
                        
class InterpolateRescaleTransformation(rfp_transformation.Transformation):
    
    def __init__(self, attributes=None):
        rfp_transformation.Transformation.__init__(self, constants.TransformationType.INTERPOLATE_RESCALE)
                                      
        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)
        
    def apply_interpolate_rescale(self, machine_settings, master_parameters, prev_result):
        
        # put result into a Result() object; for now...
        #if not self.parameters.do_interpolate and \
        #not self.parameters.do_rescaling:        

        self.result  = copy.deepcopy(prev_result)
        
        if self.parameters.do_interpolate or self.parameters.do_rescaling:
        
            if self.parameters.do_interpolate:                
                y, x = interpolate.interpolate_dwell(self.result.rf.waveform,
                                        self.result.rf.waveform_x_axis,
                                        self.parameters.new_dwell_time/1000000)                
                
                rf = rfp_result.Waveform({"waveform"        : y.tolist(), 
                                          "waveform_x_axis" : x.tolist()})
                
                self.result = rfp_result.Result({"rf" : rf})

            if self.parameters.do_rescaling:
                y = rescale.rescale(np.array( self.result.rf.waveform),
                                              self.parameters.angle, 
                                              self.result.dwell_time)
                self.result.rf.waveform = y.tolist()      
                            
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
