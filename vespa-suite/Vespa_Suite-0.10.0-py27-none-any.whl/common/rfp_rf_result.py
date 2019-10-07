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
#import vespa.common.bloch_call as bloch_call
#import vespa.common.rfp_opcon_state as rfp_opcon_state
import vespa.common.constants as constants
import vespa.common.pulse_funcs.grad_refocus as grad_refocus
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception

import vespa.common.pulse_funcs.bloch_lib_hargreaves as bloch_lib_h


PI = np.pi



class RfResults(object):
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

        created     - A DateTime object representing the creation time.
        
        rf_waveform - list, complex numbers, units in microTesla
        rf_xaxis    - list, floats, units of time in seconds

        gradient    - list, complex numbers, units in microTesla
        grad_xaxis  - list, floats, units of time in seconds
        
        Note. display should be in milliseconds
        
        """
        self.created = util_time.now()
        
        # RF Waveform 
        self.rf_waveform = None     # [mT]  was rf.waveform
        self.rf_xaxis    = None     # [sec] was rf.waveform_x_axis

        # Gradient Waveform 
        self.gradient    = None     # [mT/m] was gradient.gradient_waveform
        self.grad_xaxis  = None     # [sec]  was gradient.time_points
 
        # Waveform and x-axis unit temporary results

        self.mz         = None  # bloch results for M starting out relaxed
        self.mxy        = None  # bloch results for M start in transverse plane
        self.xaxis      = None
        
        self.mz_ext    = None
        self.mxy_ext   = None
        self.xaxis_ext = None
        
        self.b1immunity = None
        self.last_b1immunity = None
                
        # Gradient Refocusing fractional Value
        self.grad_refocus_fraction = 0.0

        self.refocused_profile = None
        
        # An rfp_opcon_state.OpConState object. - need to create this object if used
        self.opcon_state = None
   
        # Explicit test for None necessary here. See:
        # http://scion.duhs.duke.edu/vespa/project/ticket/35
        if attributes is not None:
            self.inflate(attributes)


    @property
    def dwell_time(self):
        "Returns the dwell_time in microseconds"
        if len(self.rf_xaxis) > 1:
            return 1000000 * (self.rf_xaxis[1] - self.rf_xaxis[0])
        else:
            return 0.0

      
    def gradient_refocusing(self, val=None):
        # This function calls a routine that may throw an exception of type
        #  pulse_func_exception.PulseFuncException
        
        profile, ax = self.get_profile(constants.UsageType.EXCITE)
        
        ax = ax * 1000.0
        
        length = len(self.rf_xaxis)
        mpgpulms = 1000.0*(self.rf_xaxis[length-1]) + self.dwell_time/1000.0
        
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


    def update_profiles(self, outputs):  
        """
        Recalculate the profile(s) using the Bloch equation
        
        Results are stored as mT and mT/m, Hargreaves lib requires G and G/cm
        - mT -> G = x10
        - mT/m -> G/cm = 10/100 = 0.1
        
        """
        igamma = outputs['gyromagnetic_nuclei']
        gamma = constants.GAMMA_VALUES[igamma]  # this is in MHz/T -> 2pi * 100 to Hz/gauss
        gamma = 2.0 * PI * 100.0 * gamma
        
        resolution         = outputs['calc_resolution']
        bloch_range_value  = outputs['bloch_range_value']
        bloch_range_units  = outputs['bloch_range_units']
        bloch_offset_value = outputs['bloch_offset_value']
        
        if self.rf_waveform is not None:
            b1     = self.rf_waveform * 10.0    # convert mT to G
            if self.gradient is None:         
                g = np.ones(len(b1))            # this is 1.0 G/cm as default
            else: 
                g = self.gradient * 0.1         # convert mT/m to G/cm
            dwell  = self.dwell_time
            npts   = resolution
            khz2mm = 1.0
            
            # Array for spatial values 
            # - nyquist times +/- resolution range
            # - Convert to cm for display
            
            if bloch_range_units == 'cm':
                nq = bloch_range_value
            else:   
                # units are in kHz
                # convert to cm using GAMMA and gradient strength
                ig = (np.nonzero(g))[0][0]     # first non-zero gradient value
                nq = bloch_range_value / (4.2576 * g[ig])
                
            x     = nq*np.arange(-npts/2,npts/2)/float(npts/2)
            xaxis = x.copy() 
            xx    = 4.0*x.copy()      # For extended range
        
            # this all used to be in bloch_call.py
        
            t  = np.arange(1,len(b1)+1)*dwell*0.000001  # time axis in [sec]
            f  = np.array([bloch_offset_value,])                       # on resonance
            
            # b1 needs to be Gauss for Hargreaves library, hence the x10
             
            mx1, my1, mz1 = bloch_lib_h.bloch(b1,g,t,None,None,f,x, mode=0, gamma=gamma)     # no decays
            mx2, my2, mz2 = bloch_lib_h.bloch(b1,g,t,None,None,f,x, mode=0,do_mxy=True, gamma=gamma)     # no decays
            mx3, my3, mz3 = bloch_lib_h.bloch(b1,g,t,None,None,f,xx,mode=0, gamma=gamma)     # no decays
            mx4, my4, mz4 = bloch_lib_h.bloch(b1,g,t,None,None,f,xx,mode=0,do_mxy=True, gamma=gamma)     # no decays

            self.mz      = np.hstack((mx1,my1,mz1))
            self.mxy     = np.hstack((mx2,my2,mz2))
            self.mz_ext  = np.hstack((mx3,my3,mz3))
            self.mxy_ext = np.hstack((mx4,my4,mz4))

            self.xaxis     = xaxis          
            self.xaxis_ext = xaxis.copy() * 4              


    def get_profile(self, use_type, extended=False, absolute=False):
        """
        We can display results for extended or standard width x-range, and
        for four usage types = Excite, Inversion, Saturation, SpinEcho.
        
        This is a total of 8 profiles we can extract from our RF complex
        waveform. 
        
        This method lets user specify which one to return. Note. all of these
        plots are already pre-calculated, we are just choosing which to show.
        
        """
        if use_type == constants.UsageType.EXCITE     or \
           use_type == constants.UsageType.INVERSION  or \
           use_type == constants.UsageType.SATURATION:
            
            if extended:
                y = self.mz_ext
                x = self.xaxis_ext
            else:
                y = self.mz
                x = self.xaxis
                
        elif use_type == constants.UsageType.SPIN_ECHO:
            
            if extended:
                y = self.mxy_ext
                x = self.xaxis_ext
            else:
                y = self.mxy
                x = self.xaxis

        if use_type == constants.UsageType.EXCITE:            
            yout = y[:,0] + 1j*y[:,1]
        elif use_type == constants.UsageType.SATURATION:
            yout = y[:,2] + 0j
        elif use_type == constants.UsageType.INVERSION:
            yout = -y[:,2] + 0j
        elif use_type == constants.UsageType.SPIN_ECHO:
            yout = y[:,0] - 1j*y[:,1]
        
        if absolute:
            yout = np.abs(yout)       

        return (yout, x)


    def get_gradient(self):
        
        if self.gradient is None: 
            x = self.rf_xaxis
            y = np.copy(x)*0.0
        else:
            x = self.grad_xaxis
            y = self.gradient
            
        return (y,x)


    def update_b1_immunity(self, outputs):
        """
        Recalculate the matrix of B1 immunity using the Bloch equation
        
        """
        if self.rf_waveform is not None: 

            pulse_type    =   int(outputs["pulse_type"])
            freq_center   = float(outputs["freq_center"])
            freq_range    = float(outputs["freq_range"])   # in +/- Hz
            freq_steps    =   int(outputs["freq_steps"])
            b1_strength   = float(outputs["b1_strength"])
            b1_range      = float(outputs["b1_range"])     # in +/- uT
            b1_steps      =   int(outputs["b1_steps"])
            magn_vector   =   int(outputs["magn_vector"])
            ref_b1_limits = float(outputs["ref_b1_limits"])
            
            if self.last_b1immunity is not None:
                if self.last_b1immunity["pulse_type"]    == outputs["pulse_type"]  and  \
                   self.last_b1immunity["freq_center"]   == outputs["freq_center"] and  \
                   self.last_b1immunity["freq_range"]    == outputs["freq_range"]  and  \
                   self.last_b1immunity["freq_steps"]    == outputs["freq_steps"]  and  \
                   self.last_b1immunity["b1_strength"]   == outputs["b1_strength"] and  \
                   self.last_b1immunity["b1_range"]      == outputs["b1_range"]    and  \
                   self.last_b1immunity["b1_steps"]      == outputs["b1_steps"]:
                    # all params are the same, we don't need to run bloch sims
                    return
            
            b1 = self.rf_waveform.copy()    
            if self.gradient is None:         
                g = np.ones(len(b1))        # this is 1.0 G/cm as default
            else: 
                g = self.gradient * 0.1     # convert mT/m to G/cm
            dwell  = self.dwell_time

            # units are in kHz - convert to cm using GAMMA and gradient strength
            fctr = freq_center / (4.2576 * g[0])
            frng = freq_range  / (4.2576 * g[0])

            x = np.linspace(fctr-frng, fctr+frng, freq_steps)
            f = [0.0,]  
            t = np.arange(1,len(b1)+1)*dwell*0.000001  # time axis in [sec]
            
            b1max    = np.max(np.abs(b1)) * 1000    # mT to uT
            bcenter  = b1_strength
            brange   = b1_strength * (b1_range / 100.0)
            bstr     = (b1_strength - brange) / b1max
            bend     = (b1_strength + brange) / b1max
            b1scales = np.linspace(bstr, bend, b1_steps)
            
            resx = []
            resy = []
            resz = []
            
            if pulse_type == 3:     # spin-echo simulation
                do_mxy = True
            else:                   # excite, inversion, saturation simulation
                do_mxy = False
            
            for b1scale in b1scales: 
                
                # b1 needs to be Gauss for Hargreaves library
                b1in = b1.copy() * b1scale * 10.0  # mT to G

                mx1, my1, mz1 = bloch_lib_h.bloch(b1in,g,t,None,None,f,x, mode=0, do_mxy=do_mxy)     # no decays

                resx.append(mx1)
                resy.append(my1)
                resz.append(mz1)

            resx = np.array(resx)
            resy = np.array(resy)
            resz = np.array(resz)

            self.b1immunity = np.concatenate((resx,resy,resz), axis=2)
            
            self.last_b1immunity = outputs



    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            
            e = ElementTree.Element("result", {"version" : self.XML_VERSION})
            
            util_xml.TextSubElement(e, "created", self.created)
            
            item = util_xml.numeric_list_to_element(self.rf_waveform, complex, "rf_waveform")
            e.append(item)

            item = util_xml.numeric_list_to_element(self.rf_xaxis, float, "rf_xaxis")
            e.append(item)

            if self.gradient is not None:
                item = util_xml.numeric_list_to_element(self.gradient, float, "gradient")
                e.append(item)

            if self.grad_xaxis is not None:
                item = util_xml.numeric_list_to_element(self.grad_xaxis, float, "grad_xaxis")
                e.append(item)

#             if self.opcon_state:
#                 e.append(self.opcon_state.deflate(flavor))
                
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
            
            e = source.find("rf_waveform")
            if e is not None:
                item = util_xml.element_to_numeric_list(e)
                self.rf_waveform = np.array(item)

            e = source.find("rf_xaxis")
            if e is not None:
                item = util_xml.element_to_numeric_list(e)
                self.rf_xaxis = np.array(item)
                
            e = source.find("gradient")
            if e is not None:
                item = util_xml.element_to_numeric_list(e)
                self.gradient = np.array(item)

            e = source.find("grad_xaxis")
            if e is not None:
                item = util_xml.element_to_numeric_list(e)
                self.grad_xaxis = np.array(item)

#            e = source.find("opcon_state")
#            if e is not None:
#                self.opcon_state = rfp_opcon_state.OpConState(e)  # FIXME - bjs need to create this object
                
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])

            if "rf" in source:
                self.rf = source["rf"]




            
           
                    
                    