# Python modules
from __future__ import division
import xml.etree.cElementTree as ElementTree

# 3rd party modules
import numpy as np

# Our modules
from vespa.common.constants import Deflate
import vespa.common.util.xml_ as util_xml

# _RESIDUAL_ERROR_HISTORY_LENGTH is the number of iterations over which
# an OCNState object tracks residual error. This affects the values of
# the attributes residual_error_differences and residual_error_comparisons 
# which in turn affect when the suspend criteria for differential error
# and increasing error are met.
# Jerry's MatPulse code tracks residual errors for 4 iterations.
_RESIDUAL_ERROR_HISTORY_LENGTH = 4



class OCNState(object):
    """An object that represent the state of an optimization. This can be
    the final output of the OC run or it can be the starting point from which
    another round of optimization begins.
    """
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):
        # The next six variables track the state of the optimization. They're
        # the potentially final output of the OC run, and they're also the
        # current state from which optimization resumes when a user clicks
        # the "Continue in New Tab" button.
        self.multiplier = 0.0
        self.deltab1 = np.array([], dtype=np.complex)
        # residual_errors contains a history of residual errors (scalar 
        # floats) for the past N iterations where 
        # N = _RESIDUAL_ERROR_HISTORY_LENGTH. The most recent error is the
        # first item in the list; the last item in the list is the oldest.
        # The list never grows or shrinks; it always has the same number 
        # of items.
        # In Jerry's code original MatPulse code, these correspond to 
        # smerror, smerrorold, smerrorolder, and smerroroldest.         
        self.residual_errors = [0.0] * _RESIDUAL_ERROR_HISTORY_LENGTH

        # The next 8 attributes explain why the OC stopped (suspended, paused,
        # whatever you want to call it).
        self.met_max_iterations = False
        self.met_residual_error = False
        self.met_differential_error = False
        self.met_max_time = False
        self.met_increasing_error = False

        self.run_time = 0.0
        self.iterations = 0
        self.decreases = 0

        if attributes:
            self.inflate(attributes)
            
    @property
    def residual_error(self):
        return self.residual_errors[0]
    
    @property
    def differential_error(self):
        return self.residual_errors[1] - self.residual_errors[0]
        
    @property
    def residual_error_differences(self):
        """Returns a list of floats containing each residual error term 
        subtracted from the next youngest residual error term. In other words,
        a list of residual_errors[i + 1] - residual_errors[i] for each element
        in residual_errors.
        
        Since the youngest element in the residual_errors list has no younger
        item to compare to, the list returned by this function has length
        (_RESIDUAL_ERROR_HISTORY_LENGTH - 1).
        """
        f = lambda i: self.residual_errors[i + 1] - self.residual_errors[i]
        return [f(i) for i in range(len(self.residual_errors) - 1)]
        
    @property        
    def residual_error_comparisons(self):
        """Returns a list containing the boolean result each residual error
        term compared to the next oldest residual error term. In other words,
        a list of residual_errors[i] > residual_errors[i + 1] for each element
        in residual_errors.
        
        Since the last element in the residual_errors list has no next
        older item to compare to, the list returned by this function
        has length (_RESIDUAL_ERROR_HISTORY_LENGTH - 1).
        """
        f = lambda i: self.residual_errors[i] > self.residual_errors[i + 1]
        return [f(i) for i in range(len(self.residual_errors) - 1)]
        
        
    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("--- OC State ---")
        
        lines.append("multiplier: %f" % self.multiplier) 
        lines.append("deltab1: %s" % self.deltab1)
        lines.append("residual_errors: %s" % self.residual_errors) 
        lines.append("met_max_iterations: %s" % self.met_max_iterations) 
        lines.append("met_residual_error: %s" % self.met_residual_error) 
        lines.append("met_differential_error: %s" % self.met_differential_error) 
        lines.append("met_max_time: %s" % self.met_max_time) 
        lines.append("met_increasing_error: %s" % self.met_increasing_error) 

        lines.append("run_time: %f" % self.run_time) 
        lines.append("iterations: %d" % self.iterations) 
        lines.append("decreases: %d" % self.decreases) 
        lines.append("residual_error: %f" % self.residual_error) 
        lines.append("differential_error: %f" % self.differential_error) 

        return u'\n'.join(lines)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # o_e = ocn_state_element
            o_e = ElementTree.Element("ocn_state",
                                      {"version" : self.XML_VERSION})

            for attribute in ("multiplier", 
                              "met_max_iterations", 
                              "met_residual_error",
                              "met_differential_error",
                              "met_max_time", 
                              "met_increasing_error",
                              "run_time", "iterations", "decreases",):
                util_xml.TextSubElement(o_e, attribute, getattr(self, attribute))
                
            for value in self.residual_errors:
                util_xml.TextSubElement(o_e, "residual_error", value)

            e = util_xml.numpy_array_to_element(self.deltab1, "deltab1")
            o_e.append(e)

            return o_e

        elif flavor == Deflate.DICTIONARY:
            raise NotImplementedError


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element

            for attribute in ("multiplier", "run_time", ):
                setattr(self, attribute, float(source.findtext(attribute)))

            for attribute in ("multiplier", "run_time", ):
                setattr(self, attribute, float(source.findtext(attribute)))

            self.residual_errors = [float(element.text) 
                                        for element 
                                        in source.findall("residual_error")]

            for attribute in ("iterations", "decreases", ):
                setattr(self, attribute, int(source.findtext(attribute)))

            for attribute in ("met_max_iterations", 
                              "met_residual_error",
                              "met_differential_error",
                              "met_max_time", 
                              "met_increasing_error", ):
                setattr(self, attribute, 
                        util_xml.BOOLEANS[source.findtext(attribute)])

            self.deltab1 = source.find("deltab1")
            self.deltab1 = util_xml.element_to_numpy_array(self.deltab1)
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])

            

