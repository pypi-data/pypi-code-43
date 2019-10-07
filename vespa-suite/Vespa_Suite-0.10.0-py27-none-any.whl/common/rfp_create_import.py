# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree
import cmath


# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.util.xml_ as util_xml
import vespa.common.util.misc as util_misc
import vespa.common.rfp_transformation as trans
import vespa.common.rfp_result as rfp_result
import vespa.common.pulse_funcs.read_pulse as read_pulse
from vespa.common.constants import Deflate


class CreateImportParameterDefaults(object):
    FILE_PATH = ""
    COMMENT = ""
    FILE_FORMAT = constants.ImportFileFormat.AMPLITUDE_PHASE_DEGREES
    DWELL_TIME = 100
    USE_MAX_INTENSITY = False
    MAX_INTENSITY = 10.0
    SCALE_FACTOR = 1.0
    IS_PHASE_DEGREES = True
    



class CreateImportPulseParameters(object):
    """
    Holds the data needed for the "creation" of a Pulse by importing from a text file.
    """
    # The XML_VERSION enables us to change the XML output format in the future
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        # File path
        self.file_path = CreateImportParameterDefaults.FILE_PATH
        
        # Comment field
        self.comment = CreateImportParameterDefaults.COMMENT        
                
        # File format for input data.
        self.file_format = CreateImportParameterDefaults.FILE_FORMAT
        
        # Dwell time
        self.dwell_time = CreateImportParameterDefaults.DWELL_TIME
        
        self.use_max_intensity = CreateImportParameterDefaults.USE_MAX_INTENSITY
        
        # Dwell time
        self.max_intensity = CreateImportParameterDefaults.MAX_INTENSITY        

        self.scale_factor = CreateImportParameterDefaults.SCALE_FACTOR

        self.is_phase_degrees  = CreateImportParameterDefaults.IS_PHASE_DEGREES

        if attributes is not None:
            self.inflate(attributes)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # e = parameters_element
            e = ElementTree.Element("parameters",
                                      {"version" : self.XML_VERSION})

            for attribute in ("file_path", "dwell_time", "comment", \
                              "use_max_intensity", "max_intensity", \
                              "scale_factor", "is_phase_degrees"):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))
            
            util_xml.TextSubElement(e, "file_format", self.file_format["db"])

            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            for attribute in ("dwell_time", "max_intensity", "scale_factor"):
                setattr(self, attribute, float(source.findtext(attribute)))
                
            self.use_max_intensity = \
                        util_xml.BOOLEANS[source.findtext("use_max_intensity")]                

            temp = source.findtext("is_phase_degrees")
            if temp is not None:
                self.is_phase_degrees = util_xml.BOOLEANS[temp]

            self.file_format = source.findtext("file_format")
            self.file_format = \
                constants.ImportFileFormat.get_type_for_value(self.file_format, "db")

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


class CreateImportPulseTransformation(trans.Transformation):
    """Used to create a pulse by importing a text file"""

    def __init__(self, attributes=None):
        trans.Transformation.__init__(self,
                                      constants.TransformationType.CREATE_IMPORT)

        if attributes:
            self.inflate(attributes)


    def create_pulse(self, machine_settings, master_parameters):
        
        """
        Import the file, and convert to real, imaginary format,
        and then updates the profiles.
        """
        if not self.parameters.file_path:
            return 
        
        rf_y = read_pulse.read_pulse(self.parameters.file_path, 
                                     self.parameters.use_max_intensity,
                                     self.parameters.max_intensity, 
                                     self.parameters.scale_factor,
                                     self.parameters.file_format,
                                     self.parameters.is_phase_degrees)
        
        dwell_time = self.parameters.dwell_time/1000000

        rf_x = [i * dwell_time for i in range(len(rf_y))]

        rf = rfp_result.Waveform({"waveform"        : rf_y.tolist(),
                                  "waveform_x_axis" : rf_x})

        self.result = rfp_result.Result({"rf" : rf})

        # Generate new frequency profiles here, using the Bloch equations.
        self.result.update_profiles(master_parameters.calc_resolution)

        return self.result


    def deflate(self, flavor=Deflate.ETREE):
        # Start by getting the base class to deflate itself, then append
        # the values specific to this class.
        base = trans.Transformation.deflate(self, flavor)
        if flavor == Deflate.ETREE:
            # At present I have nothing to add
            pass
        elif flavor == Deflate.DICTIONARY:
            base.update(self.__dict__)

        return base

    def inflate(self, source):
        # Start by getting my base class to inflate itself, then read
        # the values specific to this class.
        base = trans.Transformation.inflate(self, source)

        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            # At present I have nothing to add
            pass
        elif hasattr(source, "keys"):
            # Quacks like a dict
            raise NotImplementedError
    