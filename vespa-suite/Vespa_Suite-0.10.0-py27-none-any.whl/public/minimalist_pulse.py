# Python modules
from __future__ import division

# 3rd party modules

# Vespa modules
import vespa.common.pulse_funcs.util as pulse_funcs_util


class MinimalistPulse(object):
    """Describes the pulse that's passed as part of a simulation description.
    
    This class implements __str__() so it's easy to print a nicely formatted
    version of it.
    """
    def __init__(self):
        # The name of the pulse project that generated this pulse
        self.name = ""
        
        # The dwell time in microseconds
        self.dwell_time = 0.0
        
        # The waveform as a list of complex floats (microTesla). 
        self.rf_waveform = []
        self.rf_xaxis = []

        # The gradient as a list of floats 
        self.gradient = []
        self.grad_xaxis = []


    @property
    def duration(self):
        """Returns the pulse's duration in milliseconds"""
        return pulse_funcs_util.calculate_duration(len(self.rf_waveform), self.dwell_time)


    @property
    def waveform(self):
        """Returns rf_waveform to maintain back compatiblity"""
        return self.rf_waveform


    @property
    def waveform_real(self):
        """Returns a list containing the real portion of the waveform"""
        return [c.real for c in self.rf_waveform]


    @property
    def waveform_imag(self):
        """Returns a list containing the imaginary portion of the rf_waveform"""
        return [c.imag for c in self.rf_waveform]


    def __str__(self):
        return self.__unicode__().encode("utf-8")


    def __unicode__(self):
        lines = [ ]
        lines.append("--- Pulse ---")
        lines.append("Name: %s" % self.name)
        lines.append("Dwell time (uSecs): %f" % self.dwell_time)
        lines.append("Waveform: %d points" % len(self.rf_waveform))
        
        return u'\n'.join(lines)
        
