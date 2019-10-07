# Python modules
from __future__ import division
import copy
import xml.etree.cElementTree as ElementTree


# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.pulse_funcs.analytic_pulse as analytic_pulse
import vespa.common.pulse_funcs.util as pulse_funcs_util
import vespa.common.util.xml_ as util_xml
import vespa.common.rfp_transformation as trans
import vespa.common.rfp_result as rfp_result
from vespa.common.constants import Deflate


class RandomizedParameterDefaults(object):
    TIME_POINTS = 250
    DURATION    = 8.0



class RandomizedPulseParameters(object):
    """
    Holds the data needed for the creation of a Randomized Pulse.
    """
    # The XML_VERSION enables us to change the XML output format in the future
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        # number of points:
        self.time_points = RandomizedParameterDefaults.TIME_POINTS

        # duration is in milliseconds
        self.duration = RandomizedParameterDefaults.DURATION


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

            for attribute in ("time_points", "duration", ):
                util_xml.TextSubElement(e, attribute, getattr(self, attribute))

            return e
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            for attribute in ("duration", ):
                setattr(self, attribute, float(source.findtext(attribute)))

            for attribute in ("time_points", ):
                setattr(self, attribute, int(source.findtext(attribute)))

        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])


class RandomizedPulseTransformation(trans.Transformation):
    """Used to Create a Random pulse"""

    def __init__(self, attributes=None):
        trans.Transformation.__init__(self,
                                      constants.TransformationType.CREATE_RANDOMIZED)

        if attributes:
            self.inflate(attributes)


    def create_pulse(self, machine_settings, master_parameters):
        """
        Calculates the pulse waveform and then updates the profiles.
        """
        dwell_time = self.parameters.dwell_time

        rf_y = analytic_pulse.randomized(self.parameters.time_points)

        # The call to analytic_pulse.randomized() only returned the "y"
        # component of the profile. We generate the x_axis here.
        dwell_time /= 1000000.0
        rf_x = [i * dwell_time for i in range(len(rf_y))]

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
