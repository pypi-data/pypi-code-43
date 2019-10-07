# Python modules
from __future__ import division
import copy

# 3rd party modules
import wx

# Our modules
import util
import tab_transform_base
import auto_gui.ocn as ocn
import vespa.common.constants as constants
import vespa.common.util.misc as common_util_misc
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception


class _PanelParameters(ocn.PanelOptimalControlNonselect):
    def __init__(self, parent_base, transform_tab):
        
        ocn.PanelOptimalControlNonselect.__init__(self, parent_base)
        
        self.transform_tab = transform_tab 
        
        if transform_tab.transform.result:
            ocn_state = transform_tab.transform.result.ocn_state 
        else:
            ocn_state = None

        self.update_suspend_stats(ocn_state)
        
    ###################    Public methods 
    
    def get_raw_gui_data(self):
        """ See documentation for get_raw_gui_data here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = { }

        d["pulse_type"] = self.ComboOptimizePulseType.GetValue()
        d["phase_type"] = self.ComboPhaseType.GetValue()
        d["gradient_refocusing_value"] = self.FloatLinearFactor.GetValue()
        d["tip_angle"] = self.FloatTipAngle.GetValue()
        d["bandwidth"] = self.FloatBandwidth.GetValue()
        d["step_size_multiplier"] = self.FloatStepSizeMultiplier.GetValue()
        d["step_size_modification"] = self.ComboStepSizeModification.GetValue()
        d["excite_band_points"] = self.SpinExciteBandPoints.GetValue()
        d["b1_immunity_range"] = self.FloatB1ImmunityRange.GetValue()
        d["steps"] = self.SpinRangeSteps.GetValue()
        d["b1_maximum"] = self.FloatLimitB1Max.GetValue()
        d["limit_sar"] = self.CheckLimitSar.GetValue()
        d["sar_factor"] = self.FloatLimitSarFactor.GetValue()
        d["error_increase_tolerance"] = self.FloatErrorIncreaseTolerance.GetValue()
        d["enforce_symmetry"] = self.CheckSymmetrize.GetValue()           

        # Limit controls
        d["max_iteration_check"] = self.CheckMaxIterations.GetValue()
        d["max_iterations"] = self.SpinMaxIterationNumber.GetValue()
        d["residual_error_check"] = self.CheckResidualError.GetValue()
        d["residual_error_tolerance"] = self.FloatResidualError.GetValue()
        d["differential_error_check"] = self.CheckDifferentialError.GetValue()
        d["differential_error_tolerance"] = self.FloatDifferentialError.GetValue() 
        d["halt_if_error_increasing"] = self.CheckHaltErrorIncreasing.GetValue()
        d["halt_on_max_time"] = self.CheckLimitByTime.GetValue()
        d["max_time"] = self.SpinCtrlTimeLimit.GetValue()        
        
        return d
        
        
    def update_suspend_stats(self, suspend_stats=None):
        if suspend_stats:
            iterations = "%d" % suspend_stats.iterations
            # In the GUI, we express these error values as a % and %% 
            # respectively.
            residual_error = suspend_stats.residual_error * 100
            residual_error = "%.8f%%" % residual_error
            differential_error = suspend_stats.differential_error * (100 * 100)
            differential_error = "%.8f%%%%" % differential_error
            # elapsed time in the GUI is given in minutes but suspend_stats
            # measures it in seconds.
            run_time = "%.2f" % (suspend_stats.run_time / 60)
        else:
            iterations = ""
            residual_error = ""
            differential_error = ""
            run_time = ""
            
        self.LabelActualIterations.SetLabel(iterations)
        self.LabelActualResidualError.SetLabel(residual_error)
        self.LabelActualDifferentialError.SetLabel(differential_error)
        self.LabelActualTimeElapsed.SetLabel(run_time)
        
        
                                               
    ##### Event Handlers ######################################################
            
    def on_selchange_pulse_type(self, event=None):

        value = self.ComboOptimizePulseType.GetValue()
        
        # Update values in ComboPhaseType, based on this value. e.g....
        self.ComboPhaseType.Clear()
        if value == constants.UsageType.EXCITE['display']:
            # NOTE: We will be doing something a little odd here, in that we are 
            # adding two different types, a PhaseType and a NonCoalescedPhaseSubtype.
            # These are the values (and meanings) of the entries in Matpulse.
            self.ComboPhaseType.SetItems([constants.PhaseType.COALESCED['display'], \
                                      constants.PhaseType.NON_COALESCED['display'], \
                                    constants.NonCoalescedPhaseSubtype.LINEAR['display']])
            self.ComboPhaseType.SetStringSelection(constants.PhaseType.COALESCED['display'])
            self.CheckSymmetrize.Disable()
        elif value == constants.UsageType.SATURATION['display']:
            self.ComboPhaseType.SetItems([constants.PhaseType.NON_COALESCED['display'],])
            self.ComboPhaseType.SetStringSelection(constants.PhaseType.NON_COALESCED['display'])            
            self.CheckSymmetrize.Disable()            
        elif value == constants.UsageType.INVERSION['display']:
            self.ComboPhaseType.SetItems([constants.PhaseType.COALESCED['display'],])
            self.ComboPhaseType.SetStringSelection(constants.PhaseType.COALESCED['display'])                
            self.CheckSymmetrize.Disable()     
        elif value == constants.UsageType.SPIN_ECHO['display']:
            self.ComboPhaseType.SetItems([constants.PhaseType.COALESCED['display'],])
            self.ComboPhaseType.SetStringSelection(constants.PhaseType.COALESCED['display'])                
            self.CheckSymmetrize.Enable()        
            
        self.on_selchange_phase_type()         

    def on_selchange_phase_type(self, event=None):
                
        value = self.ComboPhaseType.GetValue()
        if value == constants.NonCoalescedPhaseSubtype.LINEAR['display']:
            self.FloatLinearFactor.Enable()
        else:
            self.FloatLinearFactor.Disable()

    def on_range_steps_changed(self, enent=None):
        
        if self.SpinRangeSteps.GetValue() <= 0:
            self.FloatB1ImmunityRange.Disable()
        else:    
            self.FloatB1ImmunityRange.Enable()
        
    def on_check_sar(self, event=None):
        
        if self.CheckLimitSar.GetValue():
            self.FloatLimitSarFactor.Enable()
        else:
            self.FloatLimitSarFactor.Disable()
    
    def on_check_max_iterations(self, event=None):
        
        if self.CheckMaxIterations.GetValue():
            self.SpinMaxIterationNumber.Enable()
        else:
            self.SpinMaxIterationNumber.Disable()
    
    def on_check_residual_error(self, event=None):

        if self.CheckResidualError.GetValue():
            self.FloatResidualError.Enable()
        else:
            self.FloatResidualError.Disable()
    
    def on_check_differential_error(self, event=None):

        if self.CheckDifferentialError.GetValue():
            self.FloatDifferentialError.Enable()
        else:
            self.FloatDifferentialError.Disable()
            
    def on_check_limit_time(self, event=None):
        self.SpinCtrlTimeLimit.Enable(self.CheckLimitByTime.GetValue())
                        
    
    def on_continue_run(self, event=None):
        # Basically implement the fun functionality with the values
        # that are already in the object...
        self.transform_tab.continue_run()



class TabTransformOCN(tab_transform_base.TabTransformBase):
    
    def __init__(self, inner_notebook, left_neighbor, pulse_project, 
                 transform, is_new):

        tab_transform_base.TabTransformBase.__init__(self,
                                                               inner_notebook, 
                                                               left_neighbor, 
                                                               transform)

        self._inner_notebook = inner_notebook
        self._pulse_project = pulse_project

        sizer       = self.LabelAlgorithmPlaceholder.GetContainingSizer()
        parent_base = self.LabelAlgorithmPlaceholder.GetParent()
        self.LabelAlgorithmPlaceholder.Destroy()

        self.oc_panel = _PanelParameters(parent_base, self)

        self.initialize_controls()
        
        # insert the transform panel into the TabTransformBase template
        sizer.Insert(0, self.oc_panel, 1, wx.EXPAND, 0)     

        self.plot(relim_flag=True)
        
        self.Layout()   
        self.Fit()
        self.Show(True)
        
        tab_transform_base.TabTransformBase.complete_init(self, is_new)



    def continue_run(self):
        self.Freeze()
        transform = copy.deepcopy(self.transform)
        transform.result = None
        self._inner_notebook.add_transformation(constants.TransformationType.OCN,
                                                transform)
        self.Thaw()        
        
    ##### Event Handlers ######################################################
        

    def on_run(self, event):        
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        self._inner_notebook.run(self)


    ##### Internal helper functions  ##########################################
        
    def get_cooked_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        d["pulse_type"] = constants.UsageType.get_type_for_value(d["pulse_type"], 'display')
        d["step_size_modification"] = constants.StepSizeModification.get_type_for_value( \
                                                            d["step_size_modification"], 'display')
        
        if d["phase_type"] == constants.PhaseType.COALESCED['display']:
            d["phase_type"] = constants.PhaseType.COALESCED
        elif d["phase_type"] == constants.PhaseType.NON_COALESCED['display']:
            d["phase_type"] = constants.PhaseType.NON_COALESCED
        else:
            d["phase_type"] = constants.NonCoalescedPhaseSubtype.LINEAR
            
        # In the GUI, these are expressed as a % and %%, respectively. Here
        # we convert them to raw numbers.
        d["residual_error_tolerance"] /= 100
        d["differential_error_tolerance"] /= (100 * 100)
        
        return d


    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = tab_transform_base.TabTransformBase.get_raw_gui_data(self)
        d.update(self.oc_panel.get_raw_gui_data())

        return d
 
 
    def initialize_controls(self):

        # :FIXME: Add some form of "Advanced Control" with additional inputs...
        # e.g. for "Enforce Symmetry" 

        # Initializing to default values
        
        self.oc_panel.ComboOptimizePulseType.Clear()
        self.oc_panel.ComboOptimizePulseType.SetItems([constants.UsageType.EXCITE['display'],
                                               constants.UsageType.SATURATION['display'],
                                               constants.UsageType.INVERSION['display'], 
                                               constants.UsageType.SPIN_ECHO['display']])
        self.oc_panel.ComboOptimizePulseType.SetStringSelection(self.transform.parameters.pulse_type['display'])
        
   
        self.oc_panel.ComboPhaseType.Clear()
        self.oc_panel.ComboPhaseType.SetItems([constants.PhaseType.COALESCED['display'], 
                                           constants.PhaseType.NON_COALESCED['display'], 
                                    constants.NonCoalescedPhaseSubtype.LINEAR['display']])        
        self.oc_panel.ComboPhaseType.SetStringSelection(self.transform.parameters.phase_type['display'])


        # :FIXME: Add more like this to this initialization - for handling limits.
        self.oc_panel.FloatTipAngle.SetValue(self.transform.parameters.tip_angle)
        self.oc_panel.FloatTipAngle.SetDigits(1)
        self.oc_panel.FloatTipAngle.SetIncrement(0.5)
        self.oc_panel.FloatTipAngle.SetRange(0,1000000)

        self.oc_panel.FloatLinearFactor.SetValue(self.transform.parameters.gradient_refocusing_value)
        self.oc_panel.FloatLinearFactor.SetDigits(3)
        self.oc_panel.FloatLinearFactor.SetIncrement(0.001)
        self.oc_panel.FloatLinearFactor.SetRange(0,100)
                
        self.oc_panel.SpinExciteBandPoints.SetValue(self.transform.parameters.excite_band_points)
        
        self.oc_panel.FloatBandwidth.SetValue(self.transform.parameters.bandwidth)
        self.oc_panel.FloatBandwidth.SetDigits(2)
        self.oc_panel.FloatBandwidth.SetIncrement(0.01)
        self.oc_panel.FloatBandwidth.SetRange(0,1000000)
                
        self.oc_panel.FloatB1ImmunityRange.SetValue(self.transform.parameters.b1_immunity_range)
        self.oc_panel.FloatB1ImmunityRange.SetDigits(1)
        self.oc_panel.FloatB1ImmunityRange.SetIncrement(0.5)
        self.oc_panel.FloatB1ImmunityRange.SetRange(0,100)        
        
        self.oc_panel.SpinRangeSteps.SetValue(self.transform.parameters.steps)
        
        self.oc_panel.ComboStepSizeModification.SetItems([constants.StepSizeModification.AVERAGE['display'], \
                                                     constants.StepSizeModification.FIXED['display'], \
                                                     constants.StepSizeModification.COMPUTE['display']])
        self.oc_panel.ComboStepSizeModification.SetStringSelection(self.transform.parameters.step_size_modification['display'])
        
        self.oc_panel.FloatStepSizeMultiplier.SetValue(self.transform.parameters.step_size_multiplier)
        self.oc_panel.FloatStepSizeMultiplier.SetDigits(2)
        self.oc_panel.FloatStepSizeMultiplier.SetIncrement(0.01)
        self.oc_panel.FloatStepSizeMultiplier.SetRange(0,1000)         
        
        self.oc_panel.FloatLimitB1Max.SetValue(self.transform.parameters.b1_maximum)
        self.oc_panel.FloatLimitB1Max.SetDigits(2)
        self.oc_panel.FloatLimitB1Max.SetIncrement(0.25)
        self.oc_panel.FloatLimitB1Max.SetRange(0,1000000)   
                
        self.oc_panel.FloatErrorIncreaseTolerance.SetValue(self.transform.parameters.error_increase_tolerance)
        self.oc_panel.FloatErrorIncreaseTolerance.SetDigits(8)
        self.oc_panel.FloatErrorIncreaseTolerance.SetIncrement(0.000001)
        self.oc_panel.FloatErrorIncreaseTolerance.SetRange(0,10)         
        
        self.oc_panel.CheckLimitSar.SetValue(self.transform.parameters.limit_sar)
        self.oc_panel.FloatLimitSarFactor.SetValue(self.transform.parameters.sar_factor)
        self.oc_panel.FloatLimitSarFactor.SetDigits(2)
        self.oc_panel.FloatLimitSarFactor.SetIncrement(0.01)
        self.oc_panel.FloatLimitSarFactor.SetRange(0,10)         
        
        self.oc_panel.CheckMaxIterations.SetValue(self.transform.parameters.max_iteration_check)
        self.oc_panel.SpinMaxIterationNumber.SetValue(self.transform.parameters.max_iterations)

        self.oc_panel.CheckResidualError.SetValue(self.transform.parameters.residual_error_check)
        # We express this as a %
        self.oc_panel.FloatResidualError.SetValue(self.transform.parameters.residual_error_tolerance * 100)
        self.oc_panel.FloatResidualError.SetDigits(3)
        self.oc_panel.FloatResidualError.SetIncrement(0.01)
        self.oc_panel.FloatResidualError.SetRange(0,100) 
                
        self.oc_panel.CheckDifferentialError.SetValue(self.transform.parameters.differential_error_check)
        # We express this as a % of a %
        self.oc_panel.FloatDifferentialError.SetValue(self.transform.parameters.differential_error_tolerance * (100 * 100))
        self.oc_panel.FloatDifferentialError.SetDigits(6)
        self.oc_panel.FloatDifferentialError.SetIncrement(0.000001)
        self.oc_panel.FloatDifferentialError.SetRange(0,100) 
           
        self.oc_panel.CheckHaltErrorIncreasing.SetValue(self.transform.parameters.halt_if_error_increasing)        

        self.oc_panel.CheckLimitByTime.SetValue(self.transform.parameters.halt_on_max_time)
        self.oc_panel.SpinCtrlTimeLimit.SetValue(self.transform.parameters.max_time)
        # Time limit ranges from 1 minute to 1 week
        self.oc_panel.SpinCtrlTimeLimit.SetRange(1, 10080) 
                
        self.oc_panel.CheckSymmetrize.SetValue(self.transform.parameters.enforce_symmetry)   
                
        self.oc_panel.on_selchange_pulse_type()                
        self.oc_panel.on_selchange_phase_type()
        self.oc_panel.on_check_sar()
        self.oc_panel.on_check_max_iterations()
        self.oc_panel.on_check_residual_error()
        self.oc_panel.on_check_differential_error()
        self.oc_panel.on_range_steps_changed()
        self.oc_panel.on_check_limit_time()
        
        # Continue is only available once a result is present
        enable = bool(self.transform) and bool(self.transform.result)
        self.oc_panel.ButtonContinue.Enable(enable)
        
        if self._pulse_project.is_frozen:
            # Frozen projects are mostly uneditable
            self.oc_panel.Disable()
            self.oc_panel.ButtonContinue.Hide()
            self.ButtonRun.Hide()


    def run(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        tab_transform_base.TabTransformBase.run(self)      
        
        # Pass in the result of the last transformation
        # as the initial conditions of this transformation.
        
        previous_result = self._pulse_project.get_previous_result(self.transform)
        
        successful = True
        
        left_neighbor = self._inner_notebook.get_left_neighbor(self)
        initial_step = not util.is_oc(left_neighbor)
        
        try:
            self.transform.run_oc(self._pulse_project.machine_settings, 
                                  self._pulse_project.master_parameters,
                                  previous_result, initial_step)
        except pulse_func_exception.PulseFuncException, pfe:
            common_dialogs.message(pfe.message, "Error in Optimization", wx.ICON_ERROR | wx.OK)
            successful = False        
        
        if successful:
            self._last_run.update(self.get_raw_gui_data())
            self.plot(update_profiles=True)
            self.oc_panel.update_suspend_stats(self.transform.result.ocn_state)

            self.oc_panel.ButtonContinue.Enable()
        else:
            self.oc_panel.ButtonContinue.Disable()
        
        return successful


    def update_sync_status(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # The continue button is only enabled if the transform has results
        # and the tab is in sync. Of course it is also disabled when the
        # project is frozen. Last but not least, it's disabled if this is 
        # not the last tab in the project. 
        enable = (bool(self.transform)                      and \
                  bool(self.transform.result)               and \
                  bool(self.is_synced)                      and \
                  bool(not self._pulse_project.is_frozen)   and \
                  (self._inner_notebook.tabs[-1] == self)
                 )
        self.oc_panel.ButtonContinue.Enable(enable)


    def validate_gui(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        msg = ""

        # Check raw input
        # Currently no checks since using spin controls on floats and ints.

        if not msg:
            # Raw stuff all checks out OK, now cook the data and make sure
            # that looks good.
            d = self.get_cooked_gui_data()
            
            
            # Check cooked input.

            if not msg:
                if d["gradient_refocusing_value"] <= 0.0:
                    msg = "The gradient refocusing value must be greater than zero."

            if not msg:
                if d["tip_angle"] <= 0.0:
                    msg = "The tip angle must be greater than zero."

            if not msg:
                if d["bandwidth"] <= 0.0:
                    msg = "The bandwidth must be greater than zero."

            if not msg:
                if d["step_size_multiplier"] <= 0.0:
                    msg = "The step size multiplier must be greater than zero."

            if not msg:
                if d["b1_immunity_range"] <= 0.0:
                    msg = "The B1 immunity range must be greater than zero."
                    
            if not msg:
                if d["b1_maximum"] <= 0.0:
                    msg = "The B1 maximum must be greater than zero."

            if not msg:
                if d["sar_factor"] <= 0.0:
                    msg = "The SAR factor must be greater than zero."
                    
            if not msg:
                if d["error_increase_tolerance"] <= 0.0:
                    msg = "The error increase tolerance must be greater than zero."

            if not msg:
                stop_checkboxes = ("max_iteration_check", 
                                    "residual_error_check",
                                    "differential_error_check",
                                    "halt_if_error_increasing",
                                    "halt_on_max_time",
                                   )
                                    
                if not any([d[name] for name in stop_checkboxes]):
                    msg = "Please select at least one suspension criterion."

        if msg:
            self._inner_notebook.activate_tab(self)
            common_dialogs.message(msg)

        return not bool(msg)
        
