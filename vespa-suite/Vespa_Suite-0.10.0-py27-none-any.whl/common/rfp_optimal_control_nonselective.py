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
import vespa.common.pulse_funcs.optimal_control_nonselective as ocn
import vespa.common.rfp_ocn_state as rfp_ocn_state
import vespa.common.util.xml_ as util_xml
from vespa.common.constants import Deflate


class OCNParameterDefaults(object):
    """
    Default values for the constructor of Optimal 
    Control (non-selective) Parameters
    """
    PULSE_TYPE = constants.UsageType.EXCITE
    
    # PHASE_TYPE is coalesced or non_coalesced/Linear
    PHASE_TYPE = constants.PhaseType.COALESCED    
    # If non_coalesced, we assume they want linear subtype
    # with a user supplied gradient_refocusing_value.
    GRADIENT_REFOCUSING_VALUE = 0.515
    
    TIP_ANGLE = 90.0
    # BANDWIDTH is in kHz
    BANDWIDTH = 1.0 
    STEP_SIZE_MULTIPLIER = 0.5
    STEP_SIZE_MODIFICATION = constants.StepSizeModification.AVERAGE
    EXCITE_BAND_POINTS = 41
    B1_IMMUNITY_RANGE = 20.0
    STEPS = 5
    # B1_MAXIMUM is in microtesla.
    B1_MAXIMUM = 25.0 
    LIMIT_SAR = False
    SAR_FACTOR = 0.5
    ERROR_INCREASE_TOLERANCE = 1e-4
    MAX_ITERATION_CHECK = True
    MAX_ITERATIONS = 50
    RESIDUAL_ERROR_CHECK = False
    # RESIDUAL_ERROR_TOLERANCE is a percent in the GUI, so 0.08 here ==> 8.0 
    # in the GUI. We use this default because it takes ~5-10 minutes to run 
    # which is similar to our other default values. 
    RESIDUAL_ERROR_TOLERANCE = 0.08
    DIFFERENTIAL_ERROR_CHECK = False
    # DIFFERENTIAL_ERROR_TOLERANCE is a % of a % in the GUI, so 0.00000001
    # here is 0.00000001 * (100 * 100) = .0001 in the GUI.
    # We use this default because it takes ~5-10 minutes to run 
    # which is similar to our other default values. 
    DIFFERENTIAL_ERROR_TOLERANCE = 0.00000001
    HALT_IF_ERROR_INCREASING = False
    HALT_ON_MAX_TIME = True
    # MAX_TIME is in minutes
    MAX_TIME = 5 
    ENFORCE_SYMMETRY = True
    
    
class OCNParameters(object):
    """Parameters for Non-Selective Optimal Control"""
    # The XML_VERSION enables us to change the XML output format in the future 
    XML_VERSION = "1.0.0"

    def __init__(self, attributes=None):

        # Variables as defined on wiki:
        # http://scion.duhs.duke.edu/vespa/rfpulse/wiki/OptimalControl
        
        self.pulse_type = OCNParameterDefaults.PULSE_TYPE
        # Note: If phase_type is LINEAR, we assume they want
        # a linear sub-type of non-coalesced phase type
        # with the gradient_refocusing_value given.
        self.phase_type = OCNParameterDefaults.PHASE_TYPE
        self.gradient_refocusing_value = OCNParameterDefaults.GRADIENT_REFOCUSING_VALUE
        self.tip_angle = OCNParameterDefaults.TIP_ANGLE
        self.bandwidth = OCNParameterDefaults.BANDWIDTH
        self.step_size_multiplier = OCNParameterDefaults.STEP_SIZE_MULTIPLIER
        self.step_size_modification = OCNParameterDefaults.STEP_SIZE_MODIFICATION
        self.excite_band_points = OCNParameterDefaults.EXCITE_BAND_POINTS
        self.b1_immunity_range = OCNParameterDefaults.B1_IMMUNITY_RANGE
        self.steps = OCNParameterDefaults.STEPS
        self.b1_maximum = OCNParameterDefaults.B1_MAXIMUM
        self.limit_sar = OCNParameterDefaults.LIMIT_SAR
        self.sar_factor = OCNParameterDefaults.SAR_FACTOR
        self.error_increase_tolerance = OCNParameterDefaults.ERROR_INCREASE_TOLERANCE
        self.max_iteration_check = OCNParameterDefaults.MAX_ITERATION_CHECK
        self.max_iterations = OCNParameterDefaults.MAX_ITERATIONS
        self.residual_error_check = OCNParameterDefaults.RESIDUAL_ERROR_CHECK
        self.residual_error_tolerance = OCNParameterDefaults.RESIDUAL_ERROR_TOLERANCE
        self.differential_error_check = OCNParameterDefaults.DIFFERENTIAL_ERROR_CHECK
        self.differential_error_tolerance = OCNParameterDefaults.DIFFERENTIAL_ERROR_TOLERANCE
        self.halt_if_error_increasing = OCNParameterDefaults.HALT_IF_ERROR_INCREASING
        self.halt_on_max_time = OCNParameterDefaults.HALT_ON_MAX_TIME
        self.max_time = OCNParameterDefaults.MAX_TIME
        self.enforce_symmetry = OCNParameterDefaults.ENFORCE_SYMMETRY

        if attributes:
            self.inflate(attributes)


    def deflate(self, flavor=Deflate.ETREE):
        if flavor == Deflate.ETREE:
            # e = parameters_element
            e = ElementTree.Element("parameters",
                                      {"version" : self.XML_VERSION})
                        
            # Handles ints, floats, and booleans
            for attribute in ("gradient_refocusing_value", "enforce_symmetry",
                              "tip_angle", "bandwidth",
                              "step_size_multiplier", "excite_band_points", 
                              "b1_immunity_range", "steps", 
                              "b1_maximum", "limit_sar", "sar_factor", 
                              "error_increase_tolerance", "max_iteration_check", 
                              "max_iterations", "residual_error_check", 
                              "residual_error_tolerance", 
                              "differential_error_check", 
                              "differential_error_tolerance", "max_time", 
                              "halt_if_error_increasing", "halt_on_max_time"):
                value = getattr(self, attribute)
                util_xml.TextSubElement(e, attribute, value)

            # Handle attributes that are dictionaries: 
            util_xml.TextSubElement(e, "pulse_type", self.pulse_type["db"])
            util_xml.TextSubElement(e, "phase_type", self.phase_type["db"])
            util_xml.TextSubElement(e, "step_size_modification", 
                                    self.step_size_modification["db"])

            return e
        
        elif flavor == Deflate.DICTIONARY:
            return copy.copy(self.__dict__)


    def inflate(self, source):
        if hasattr(source, "makeelement"):
            # Quacks like an ElementTree.Element
            #
            for attribute in ("enforce_symmetry", "limit_sar",
                              "max_iteration_check", "residual_error_check",
                              "differential_error_check", 
                              "halt_if_error_increasing", "halt_on_max_time"):
                setattr(self, attribute, 
                        util_xml.BOOLEANS[source.findtext(attribute)])
            
            for attribute in ("excite_band_points", "steps", "max_iterations"):
                setattr(self, attribute, int(source.findtext(attribute)))

            for attribute in ("gradient_refocusing_value", "tip_angle", 
                              "bandwidth", "step_size_multiplier", "max_time",
                              "b1_immunity_range", 
                              "b1_maximum", "sar_factor", 
                              "error_increase_tolerance",  
                              "residual_error_tolerance", 
                              "differential_error_tolerance"):
                value = float(source.findtext(attribute))
                setattr(self, attribute, value)
            
            # Attributes that are dictionaries: 

            self.pulse_type = source.findtext("pulse_type")
            self.pulse_type = \
                constants.UsageType.get_type_for_value(self.pulse_type, "db")

            self.phase_type = source.findtext("phase_type")
            self.phase_type = \
                constants.PhaseType.get_type_for_value(self.phase_type, "db")
                
            self.step_size_modification = source.findtext("step_size_modification")
            self.step_size_modification = \
                constants.StepSizeModification.get_type_for_value(self.step_size_modification, "db")            
            
        elif hasattr(source, "keys"):
            # Quacks like a dict
            for key in source.keys():
                if hasattr(self, key):
                    setattr(self, key, source[key])
                        
                        
class OCNTransformation(rfp_transformation.Transformation):
    
    def __init__(self, attributes=None):
        rfp_transformation.Transformation.__init__(self, constants.TransformationType.OCN)
                                      
        if attributes:
            self.inflate(attributes)
        
    def run_oc(self, machine_settings, master_parameters, prev_result, 
               is_initial_step):
        # Put previous result into a Result() object
        
        self.result  = copy.deepcopy(prev_result)
        
        b1 = np.array(self.result.rf.waveform)        
            
        ocn_params = ocn.OCNParams()
        
        # Convert UI parameters into calculational code parameters.
            
        ocn_params.pdwell = self.result.dwell_time
        ocn_params.pulspts = len(b1)
        
        ocn_params.pulselength = self.result.rf.waveform_x_axis[ocn_params.pulspts-1] * 1000
        ocn_params.pulselength = ocn_params.pulselength + ocn_params.pdwell/1000
        # or...
        # set(handles.Pulslength,'String', num2str(mpgdtmu/1000*length(mpgb1))) ;
                
        ocn_params.tip = self.parameters.tip_angle
        
        # Phase type options are coalesced, non-coalesced, and linear.
        # LINEAR is a special subtype of NON-COALESCED. If the user selects 
        # non-coalesced, the code does not worry about the phase when looking 
        # for the best fit solution.
        ocn_params.phase_type = self.parameters.phase_type
        
        ocn_params.linfact = self.parameters.gradient_refocusing_value
        
        ocn_params.dectol = self.parameters.error_increase_tolerance
        ocn_params.passband = self.parameters.bandwidth
        ocn_params.bmax =  self.parameters.b1_maximum
        ocn_params.steps = self.parameters.steps
        ocn_params.pbparm = self.parameters.excite_band_points
        ocn_params.brange = self.parameters.b1_immunity_range
        ocn_params.pulse_type = self.parameters.pulse_type      
        
        ocn_params.halt_max_iterations = self.parameters.max_iteration_check
        ocn_params.max_iterations = self.parameters.max_iterations
        ocn_params.halt_differential_error = self.parameters.differential_error_check
        ocn_params.differential_error_tolerance = self.parameters.differential_error_tolerance
        ocn_params.halt_residual_error = self.parameters.residual_error_check
        ocn_params.residual_error_tolerance = self.parameters.residual_error_tolerance        
        ocn_params.halt_increasing_error = self.parameters.halt_if_error_increasing
        ocn_params.halt_max_time = self.parameters.halt_on_max_time
        ocn_params.max_time = self.parameters.max_time * constants.MINUTES_TO_SECONDS
        
        ocn_params.limit_sar = self.parameters.limit_sar
        ocn_params.sar_factor = self.parameters.sar_factor
         
        ocn_params.step_size_modification = self.parameters.step_size_modification
        
        ocn_params.step_size = self.parameters.step_size_multiplier       
        
        # NOTE: According to Jerry this is only available for Spin-Echo Pulses.
        ocn_params.enforce_symmetry = self.parameters.enforce_symmetry
        
        ocn_params.initial_calculation = is_initial_step
        if is_initial_step:
            # If it's the first run, the previous state does not exist
            # so use a clean fresh object initialized to zeros.
            self.result.ocn_state = rfp_ocn_state.OCNState()
        #else:
            # We continue using the existing self.result.ocn_state.
            
        # Calculate the optimized result.
        y = ocn.oc_nonselective_calc(b1, ocn_params, self.result.ocn_state)
        
        self.result.rf.waveform = y.tolist()                              
        
        # Generate new frequency profiles here, using the Bloch equations.
        self.result.update_profiles(master_parameters.calc_resolution)  
    

    def deflate(self, flavor=Deflate.ETREE):
        # I start by getting my base class to deflate itself, then I append
        # the values specific to this class.
        base = rfp_transformation.Transformation.deflate(self, flavor)
        if flavor == Deflate.ETREE:
            # At present we have nothing to add
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
