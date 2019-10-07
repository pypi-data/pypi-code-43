# Python modules
from __future__ import division
import copy
import math
import cmath
import xml.etree.cElementTree as ElementTree


# 3rd party modules
import numpy as np

# Our modules
import vespa.common.constants as constants
import vespa.common.rfp_result as rfp_result
import vespa.common.rfp_transformation as rfp_transformation
import vespa.common.pulse_funcs.root_reflect as root_reflect
import vespa.common.util.xml_ as util_xml
from vespa.common.constants import Deflate


class RootReflectionParameters(object):
    """Parameters for performing root reflection"""
    def __init__(self, attributes=None):
                                      
        # If next flag is False, then we'll use 
        # the "A" and "B" polynomial roots.
        self.a_roots_only = True
        
        # +/- around the positive x-axis. In Radians.
        self.graph_angle = 0.785375     # 45 degree angle
        self.x_axis_start = 0.0
        
        self.aroots = []
        self.anorm = 1.0
        self.broots = []
        self.bnorm = 1.0
        
        # Set by the user interface or from the database
        # Which of the roots was flipped by the user.
        self.aroots_flipped = []
        self.broots_flipped = []
        
        # This is returned from the calculation routines.
        # We could remove our required zero's (if we have any)
        # but we will still be faced with the issue of any 
        # addition zero's that may be present.
        self.leading_zeros = 0
        self.trailing_zeros  = 0
        
        if attributes:
            self.inflate(attributes)
        
    def deflate(self):
        pass        
    
            
    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            pass
                
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])

        
class RootReflectionTransformation(rfp_transformation.Transformation):
    
    def __init__(self, attributes=None):
        rfp_transformation.Transformation.__init__(self, constants.TransformationType.ROOT_REFLECTION)
                                      
        if attributes:
            self.inflate(attributes)
        
    def apply_roots(self, machine_settings, master_parameters):
        # Take the roots, including those that were reflected, 
        # and generate the new results.
        
        ar = self.parameters.aroots.copy()
        br = self.parameters.broots.copy()
        
        for i in np.arange(len(ar)):
            if self.parameters.aroots_flipped[i] == True:
                ar[i] = self.reflected(ar[i])
                
        for i in np.arange(len(br)):
            if self.parameters.broots_flipped[i] == True:
                br[i] = self.reflected(br[i])                       
        
        rf_x = self.result.rf.waveform_x_axis
       
        maxb1 = machine_settings.max_b1_field
        dwell_time = self.result.dwell_time
        leadz = self.parameters.leading_zeros
        lagz = self.parameters.trailing_zeros
        length = len(rf_x) - leadz - lagz
      
        rf_y = root_reflect.roots_to_b1(ar, self.parameters.anorm,
                                        br, self.parameters.bnorm,
                                        length, maxb1, dwell_time,
                                        leadz, lagz)
        
        # These next two if statement are a bit of a hack
        # to compensate for the roots_to_b1 routine being 
        # a bit flaky.  
        # FIXME: Remove if possible
        # Note: Karl is currently trying to fix.
        if len(rf_y) > len(rf_x):
            endx = rf_x[-1]
            while len(rf_y) != len(rf_x):
                endx += dwell_time
                rf_x.append(endx)                
        if len(rf_y) < len(rf_x):
            rf_x = rf_x[0:len(rf_y)]

        
        rf = rfp_result.Waveform({"waveform"        : rf_y.tolist(), 
                                  "waveform_x_axis" : rf_x})
        
        self.result = rfp_result.Result({"rf" : rf})    
            
        self.result.update_profiles(master_parameters.calc_resolution)

                
    def get_roots(self, machine_settings, master_parameters, prev_result):
        # Take the previous rf waveform and put it into the root reflection routine.
        self.result  = copy.deepcopy(prev_result)
        input_waveform = np.array(self.result.rf.waveform)
        dwell = self.result.dwell_time
        resol = master_parameters.calc_resolution
        aroots,aplotroots,anorm,broots,bplotroots,bnorm,leadz,lagz = \
                           root_reflect.b1_to_roots(input_waveform,
                                                    dwell, 
                                                    0.5*math.pi)
        self.parameters.aroots = aroots
        self.parameters.broots = broots
        self.parameters.anorm = anorm
        self.parameters.bnorm = bnorm
        self.parameters.leading_zeros = leadz
        self.parameters.trailing_zeros  = lagz
        
        # These lines should create numpy array's filled 
        # with booleans, all initialized to False.
        self.parameters.aroots_flipped = list(False for a in self.parameters.aroots)
        self.parameters.broots_flipped = list(False for b in self.parameters.broots)

  
    def deflate(self, flavor=Deflate.ETREE):
        pass

    def inflate(self, source):
        pass

    def reflected(self, val_in):
        """ 
        Performs reflection of roots as described in
        'Numerical Recipes in C, 2nd Edition', 
        W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery,
        page 567, Cambridge University Press, 1992
        """
        # :FIXME: Do we need to handle values outside 
        # the unit circle and reflect them in?
        return 1/np.conjugate(val_in)
    
        # As it turns out we are not literally reflecting
        # across the unit circle, in the sense of being
        # equidistant from the unit cirle.

    
    def roots_within_angle(self):
        ''' 
        For the currently chosen angle (self.parameters.graph_angle) it returns 
        a list of booleans of the same size as the arrays, aroots and broots.
        
        The value is set to True if the corresponding root is within
        the specified angle of the positive x-axis, and False if it is not.
        '''
        roots_within_angle_a = []
        roots_within_angle_b = []
        
        for a in self.parameters.aroots:
            if math.acos(a.real/abs(a)) <= self.parameters.graph_angle:
                roots_within_angle_a.append(True)
            else:
                roots_within_angle_a.append(False)
                
        for b in self.parameters.broots:
            if math.acos(b.real/abs(b)) <= self.parameters.graph_angle:
                roots_within_angle_b.append(True)
            else:
                roots_within_angle_b.append(False)
                
        return (roots_within_angle_a, roots_within_angle_b)
    
        

    