# Python modules
from __future__ import division
import math

# 3rd party modules
import wx


# Our modules
import constants
import tab_transform_base
import auto_gui.panel_hs_matpulse as panel_hs_matpulse
import vespa.common.util.misc as common_util_misc
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception
import vespa.common.constants as constants



class _PanelParameters(panel_hs_matpulse.PanelHsMatpulse):
    def __init__(self, parent, inner_notebook, tab):
                    
        panel_hs_matpulse.PanelHsMatpulse.__init__(self, parent)
               
        self._inner_notebook = inner_notebook
        self._parent_tab = tab
        
        self.initialize_controls()  

        self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focus)

        
    ##### Event Handlers ######################################################

    def on_child_focus(self, event):
        # When the focus changes we take the opportunity to update the
        # bandwidth & dwell time which influence one another (combined with
        # a number of other factors).
        self.recalculate_bandwidth_dwell_time()
        
        # It's important to call event.Skip() here because the base 
        # transformation tab also wants to see EVT_CHILD_FOCUS.
        event.Skip()


    def on_radio_bandwidth(self, event):
        self.RadioDwellTime.SetValue(False)
        self.TextDwellTime.Disable()
        self.TextBandwidth.Enable()

    def on_radio_dwell_time(self, event):
        self.RadioBandwidth.SetValue(False)
        self.TextBandwidth.Disable()
        self.TextDwellTime.Enable()

    
    ##### Internal helper functions  ##########################################


    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # Ensure that bandwidth/dwell time values are current.
        self.recalculate_bandwidth_dwell_time()
        
        d = { }
        
        d["total_rotation"]           = self.TextTotalRotation.GetValue().strip()
        d["time_steps"]               = self.TextTimeSteps.GetValue().strip()
        d["was_dwell_time_specified"] = self.RadioDwellTime.GetValue()
        d["was_bandwidth_specified"]  = self.RadioBandwidth.GetValue()
        d["dwell_time"]               = self.TextDwellTime.GetValue().strip()
        d["_bandwidth"]               = self.TextBandwidth.GetValue().strip()
        d["quality_cycles"]           = self.TextCycles.GetValue().strip()
        d["power_n"]                  = self.TextPowerN.GetValue().strip()
        d["sharpness_mu"]             = self.TextSharpnessMu.GetValue().strip()
        d["filter_type"]              = self.ComboBoxFilterType.GetValue()
        d["filter_application"]       = self.TextFilterApplication.GetValue()
        
        return d


    def initialize_controls(self):

        self.ComboBoxFilterType.Clear()        
        self.ComboBoxFilterType.AppendItems( \
                                [constants.FilterType.NO_SELECTION['display'],
                                 constants.FilterType.COSINE['display'],
                                 constants.FilterType.HAMMING['display']])         
                

    def recalculate_bandwidth_dwell_time(self):
        # Will try to interconvert: bandwidth <-> dwell_time
        # but if one of the values required is not valid
        # we will blow-it-off without warning, for now.

        # In validate_gui( ) we check to make sure that
        # the bandwidth/dwell_time are consistent with the
        # machine settings (minimum dwell and dwell increment)
        time_steps = self.TextTimeSteps.GetValue()
        if common_util_misc.is_intable(time_steps):
            time_points = int(time_steps)
        else:
            return
            
        was_dwell_time_specified = self.RadioDwellTime.GetValue()
                       
        if was_dwell_time_specified:
            dwell_time = self.TextDwellTime.GetValue()
            if common_util_misc.is_floatable(dwell_time):
                dtb = float(dwell_time)
            else:
                return
        else:
            bandwidth = self.TextBandwidth.GetValue()
            if common_util_misc.is_floatable(bandwidth):
                dtb = float(bandwidth)
            else:
                return
    
        cycles = self.TextCycles.GetValue()
        if common_util_misc.is_floatable(cycles):
            cycles = float(cycles)
        else:
            return
                    
        sharpness_mu = self.TextSharpnessMu.GetValue()
        if common_util_misc.is_floatable(sharpness_mu):
            sharpness_mu = float(sharpness_mu)
        else:
            return

        dtbn = self._parent_tab.transform.parameters.dwell_bandwidth_interconvert(dtb, 
                                                     sharpness_mu, cycles, time_points)
        
        if not was_dwell_time_specified:
            self.TextDwellTime.SetValue(str(dtbn))
        else:
            self.TextBandwidth.SetValue(str(dtbn))  

        
        
        
class TabCreateHyperbolicSecant(tab_transform_base.TabTransformBase):
    
    def __init__(self, inner_notebook, left_neighbor, pulse_project,
                 transform, is_new):

        tab_transform_base.TabTransformBase.__init__(self,
                                                     inner_notebook, 
                                                     left_neighbor, 
                                                     transform)
        
        self._inner_notebook = inner_notebook
        self._pulse_project  = pulse_project

        sizer_generic = self.LabelGenericPlaceholder.GetContainingSizer()
        parent_generic = self.LabelGenericPlaceholder.GetParent()
        self.LabelGenericPlaceholder.Destroy()
        
        self.params = _PanelParameters(parent_generic, inner_notebook, self)
        sizer_generic.Insert(0, self.params, 0, wx.EXPAND)
        sizer_generic.Fit(self.params)

        self.initialize_controls()   

        self.Layout()   
        self.Fit()
        self.Show(True)

        tab_transform_base.TabTransformBase.complete_init(self, is_new)

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

        d["was_bandwidth_specified"] = bool(d["was_bandwidth_specified"])
        
        for key in ("total_rotation", 
                    "dwell_time", 
                    "_bandwidth",
                    "quality_cycles", 
                    "sharpness_mu", 
                    "filter_application", ):
            d[key] = float(d[key])

        for key in ("time_steps", "power_n", ):
            d[key] = int(d[key])
            
        d["time_points"] = d["time_steps"]

        d["filter_type"] = constants.FilterType.get_type_for_value(d["filter_type"], 'display')
        
        return d      
  
  
    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # Get values from the parameters panel
        d = tab_transform_base.TabTransformBase.get_raw_gui_data(self)
        d.update(self.params.get_raw_gui_data())

        return d
        
        
    def initialize_controls(self):
        parameters = self.transform.parameters

        self.params.TextTotalRotation.SetValue(str(parameters.total_rotation))
        self.params.TextTimeSteps.SetValue(str(parameters.time_points))
        
        self.params.TextDwellTime.SetValue(str(parameters.dwell_time))
        # We infer the bandwidth from the dwell time.
        bandwidth = \
            self.transform.parameters.dwell_bandwidth_interconvert(parameters.dwell_time,
                                                   parameters.sharpness_mu,
                                                   parameters.quality_cycles,
                                                   parameters.time_points)
        self.params.TextBandwidth.SetValue(str(bandwidth))

        # Select and simulate a click on the appropriate dwell time/bandwidth
        # radio button 
        if parameters.was_bandwidth_specified:
            self.params.RadioBandwidth.SetValue(True)
            self.params.on_radio_bandwidth(self)                
        else:
            self.params.RadioDwellTime.SetValue(True)
            self.params.on_radio_dwell_time(self)            

        self.params.TextCycles.SetValue(str(parameters.quality_cycles))
        self.params.TextPowerN.SetValue(str(parameters.power_n))
        self.params.TextSharpnessMu.SetValue(str(parameters.sharpness_mu))        

        if parameters.filter_type:
            val = parameters.filter_type['display']
            self.params.ComboBoxFilterType.SetStringSelection(val)
        
        self.params.TextFilterApplication.SetValue(str(parameters.filter_application))          

        if self._pulse_project.is_frozen:
            # Frozen projects are mostly uneditable
            self.params.Disable()
            self.ButtonRun.Hide()
            

    def run(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        tab_transform_base.TabTransformBase.run(self)

        successful = True
        
        try:
            self.transform.create_pulse(self._pulse_project.machine_settings,
                                        self._pulse_project.master_parameters)     
        except pulse_func_exception.PulseFuncException, pfe:
            common_dialogs.message(pfe.message, "Error Generating Pulse", wx.ICON_ERROR | wx.OK)
            successful = False
            
        if successful:
            self._last_run.update(self.get_raw_gui_data())

            self.plot(update_profiles=True)
        
        return True


    def validate_gui(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        msg = ""

        if not common_util_misc.is_floatable(d["total_rotation"]):
            msg = """I don't understand the rotation "%s".""" % d["total_rotation"]

        if not msg:
            if not common_util_misc.is_intable(d["time_steps"]):
                msg = """I don't understand the time steps value "%s".""" % d["time_steps"]

        # Either one of dwell time or bandwidth must be specified. At present,
        # neither is selected by default, so we can't assume that if one 
        # is not selected, the other is.
        if not msg:
            if not d["was_dwell_time_specified"] and \
               not d["was_bandwidth_specified"]:
                msg = """Please specify a dwell time or bandwidth."""
            
        if not msg:
            if not common_util_misc.is_floatable(d["dwell_time"]):
                msg = """I don't understand the dwell time "%s".""" % d["dwell_time"]

        if not msg:
            if not common_util_misc.is_floatable(d["_bandwidth"]):
                msg = """I don't understand the bandwidth "%s".""" % d["_bandwidth"]

        if not msg:
            if not common_util_misc.is_floatable(d["quality_cycles"]):
                msg = """I don't understand the cycles value "%s".""" % d["quality_cycles"]

        if not msg:
            if not common_util_misc.is_intable(d["power_n"]):
                msg = """I don't understand the power(n) value "%s".""" % d["power_n"]

        if not msg:
            if not common_util_misc.is_floatable(d["sharpness_mu"]):
                msg = """I don't understand the sharpness(mu) value "%s".""" % d["sharpness_mu"]
                
        if not msg:
            if not common_util_misc.is_floatable(d["filter_application"]):
                msg = """I don't understand the filter application percentage "%s".""" % d["filter_application"]
                
        if not msg:
            # At this point we know all of the fields can be cooked. The rest
            # of the validation we have to do is on the cooked data, so we
            # grab it here.
            d = self.get_cooked_gui_data()

        if not msg:
            if (d["filter_application"] < 0) or (d["filter_application"] > 100):
                msg = """Please enter a filter application percentage between 0 and 100."""

        if not msg:
            # Make sure the dwell time is consistent with Machine Settings.
            # At this point we've already called recalculate_bandwidth_dwell_time()
            minimum_dwell   = self._pulse_project.machine_settings.min_dwell_time
            dwell_increment = self._pulse_project.machine_settings.dwell_time_increment
            
            # At this point, the variables d["xyz"] have already been converted to
            # their appropriate float, integer, etc., values.
            dwell_time = d["dwell_time"]
            
            # Get the remainder = (dwell_time-minimum_dwell)%dwell_increment,
            # and the integer number of dwell_increments,
            # nn = (dwell_time-minimum_dwell//dwell_increment,
            # as well as the minimum difference to a nearby dwell increment
            # i.e. the smallest distance (diff) between the dwell_time and
            # minimum_dwell+N*dwell_increment, where N is an integer.
            
            diff = 0
            if dwell_time > minimum_dwell:
                nn = 0
                temp = minimum_dwell
                while (temp + dwell_increment) <= dwell_time:
                    temp += dwell_increment
                    nn += 1
                    
                remainder = dwell_time - temp
                diff = remainder
                if diff > 0.5*dwell_increment:
                    diff = dwell_increment - remainder                
            
            if dwell_time < minimum_dwell or diff > 0.000001:            
                if  d["was_dwell_time_specified"]:
                    msg =  "dwell_time must be equal to the minimum dwell (%s) " + \
                             "plus and integer multiple of the dwell time increment (%s)"
                    msg = msg %(minimum_dwell, dwell_increment)
                else:
                    # If bandwidth was specified.
                    if dwell_time < minimum_dwell:
                        new_dwell_time = minimum_dwell
                    elif remainder >= 0.5*dwell_increment:
                        new_dwell_time = minimum_dwell + (nn+1)*dwell_increment
                    else:
                        new_dwell_time = minimum_dwell + nn*dwell_increment
                     
                    # Recalculate the bandwidth.
                    # Suggest a new dwell/bandwidth combination.   
                    sharpness_mu = d["sharpness_mu"]
                    cycles =  d["quality_cycles"] 
                    time_points = d["time_points"]
                    new_bandwidth = self.transform.parameters.dwell_bandwidth_interconvert(new_dwell_time, 
                                                                         sharpness_mu, cycles, time_points)

                    msg = "The bandwidth you specified yields a dwell time that is not " + \
                          "compatible with the machine settings.\nWe suggest the following:\n " + \
                          "\tbandwidth = %s \n\tdwell time = %s" %(new_bandwidth, new_dwell_time)

                    if wx.NO == common_dialogs.message(msg, None, common_dialogs.Q_YES_NO):
                        msg = "Please adjust your bandwidth to yield a dwell time that " + \
                              "is equal to the minimum dwell (%s) " + \
                              "plus and integer multiple of the dwell time increment (%s)"
                              
                        msg = msg %(minimum_dwell, dwell_increment)
                    else:
                        # No need to set them in the dictionary, d, as it will 
                        # be thrown away after this function call.
                        self.params.TextDwellTime.SetValue(str(new_dwell_time))
                        self.params.TextBandwidth.SetValue(str(new_bandwidth))
                        
                        # Force the window to update right away so that it 
                        # changes before the GUI freezes while running. 
                        self.params.TextDwellTime.Update()
                        self.params.TextBandwidth.Update()                        
                        
                        # Set this to be the empty message as our error condition
                        # is now cleared up.
                        msg = ""                          

        if not msg:
            # Warn if time_steps are greater than 1/4 of calc_resolution.
            # Unfortunately we have to reach into another tab to get this
            # because we want the value that's in the GUI which may or may
            # not match what's in the object.
            tab = self._inner_notebook.GetPage(0)
            calc_resolution = tab.TextCalcResolution.GetValue()
            
            if common_util_misc.is_intable(calc_resolution):
                calc_resolution = int(calc_resolution)

                if calc_resolution < (d["time_points"] * 4):
                    msg = "For best results, the calculation resolution "   \
                          "(currently %d) should be at least four times "   \
                          "wider than the number of time steps.\n\n"        \
                          "Do you want to continue with the current values?"
                          
                    msg = msg % calc_resolution
                          
                    if wx.NO == common_dialogs.message(msg, None, common_dialogs.Q_YES_NO):
                        msg = "Please adjust the calculation resolution or " \
                              "the number of time steps."
                    else:
                        msg = ""
            #else:
                # The calc resolution isn't valid. I don't think this case
                # can ever happen since that tab will be validated before
                # this one.

        if msg:
            self._inner_notebook.activate_tab(self)
            common_dialogs.message(msg)

        return not bool(msg)
        
