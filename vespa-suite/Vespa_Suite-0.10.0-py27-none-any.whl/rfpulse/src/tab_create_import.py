# Python modules
from __future__ import division
import time

# 3rd party modules
import wx
import numpy as np


# Our modules
import auto_gui.panel_import_pulse as panel_import_pulse
import tab_transform_base
import vespa.common.util.misc as common_util_misc
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.util as wx_util
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception
import vespa.common.pulse_funcs.read_pulse as read_pulse
import vespa.common.pulse_funcs.util as pulse_funcs_util


class _PanelParameters(panel_import_pulse.PanelImportPulse):
    def __init__(self, parent, inner_notebook):

        panel_import_pulse.PanelImportPulse.__init__(self, parent)

        self._inner_notebook = inner_notebook
        
        # If the user browses for a file and clicks OK on the browse dialog,
        # we want this tab to become out of sync even if the filename has
        # not changed. (We make the conservative assumption that the content
        # has changed even if the name hasn't.) An unchanged filename won't
        # show up as a change in the dict returned by get_raw_gui_data(), so
        # we use _file_selection_time behind the scenes to force a change in
        # the raw GUI data when a new filename is selected. We don't care
        # about the actual time stored in the attribute, just so long as
        # the value changes when a file is selected.
        self._file_selection_time = time.time()

        self.initialize_controls()
        
        wx.CallAfter(wx_util.wrap_label, self.LabelInstructions, self)
        
        self.Bind(wx.EVT_SIZE,  self.on_size)


    ##### Internal helper functions  ##########################################

    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = { }
        
        d["file_path"]         = self.StaticFilename.GetLabel().strip()
        d["comment"]           = self.TextComment.GetValue().strip()
        d["dwell_time"]        = self.TextDwellTime.GetValue().strip()
        d["use_max_intensity"] = self.radio_btn_max_intensity.GetValue()
        d["max_intensity"]     = self.TextMaxIntensity.GetValue().strip()
        d["scale_factor"]      = self.TextScaleFactor.GetValue().strip()    
        d["_file_selection_time"] = self._file_selection_time
        d["phase_units"]       = self.RadioPhaseValueUnits.GetSelection()

        return d


    def initialize_controls(self):
        pass

    ## Event Handlers ##
    
    def on_browse_button(self, event):
        dialog = wx.FileDialog(self)
        if wx.ID_OK == dialog.ShowModal():
            self.file_path = dialog.GetPath()
            self.StaticFilename.SetLabel(self.file_path)
            self._file_selection_time = time.time()
            self._inner_notebook.update_sync_status()
        
        
    def on_size(self, event):
        wx_util.wrap_label(self.LabelInstructions, self)
        event.Skip()


    def on_radio_max_intensity(self, event):
        self.radio_btn_max_intensity.SetValue(True)        
        self.radio_btn_scale_factor.SetValue(False)
        self.TextMaxIntensity.Enable()
        self.label_microtesla.Enable()
        self.TextScaleFactor.Disable()
        
        
    def on_radio_scale_factor(self, event):
        self.radio_btn_scale_factor.SetValue(True)        
        self.radio_btn_max_intensity.SetValue(False)
        self.TextMaxIntensity.Disable()
        self.label_microtesla.Disable()
        self.TextScaleFactor.Enable()        


class TabCreateImport(tab_transform_base.TabTransformBase):

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

        self.params = _PanelParameters(parent_generic, inner_notebook)
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

    def initialize_controls(self):

        parameters = self.transform.parameters

        self.params.StaticFilename.SetLabel(parameters.file_path)
        self.params.TextComment.SetValue(parameters.comment)
        self.params.TextDwellTime.SetValue(str(parameters.dwell_time))
        self.params.TextMaxIntensity.SetValue(str(parameters.max_intensity))
        self.params.TextScaleFactor.SetValue(str(parameters.scale_factor))        
        
        if parameters.use_max_intensity:
            self.params.on_radio_max_intensity(self)
        else:
            self.params.on_radio_scale_factor(self)      

        if self.transform.parameters.is_phase_degrees:
            self.params.RadioPhaseValueUnits.SetSelection(0)
        else:
            self.params.RadioPhaseValueUnits.SetSelection(1)

        
        if self._pulse_project.is_frozen:
            # Frozen projects are mostly uneditable
            self.params.Disable()
            self.ButtonRun.Hide()


    def get_cooked_gui_data(self):
        """ 
        See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        for key in ("dwell_time", "max_intensity","scale_factor"):
            d[key] = float(d[key])

        # d["phase_units"] is 0 (degrees) or 1 (radians)
        d["is_phase_degrees"] = (d["phase_units"] == 0)

        return d


    def get_raw_gui_data(self):
        """ 
        See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # Get values from the params panel
        d = tab_transform_base.TabTransformBase.get_raw_gui_data(self)
        d.update(self.params.get_raw_gui_data())

        return d


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

        return successful


    def validate_gui(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        msg = ""
        
        time_points = 0
        max_input_field = 0.0
        
        basic_info = self._inner_notebook.tabs[0].get_cooked_gui_data()
        machine_settings = basic_info["machine_settings"]
        max_b1_field = machine_settings.max_b1_field        
        # No check on comment field.
        # If the user does not enter anything, well that's their loss.
        
        if not msg:
            if not d["file_path"]:
                msg = """Please supply a file name."""
            else:
                try:
                    y = read_pulse.read_pulse(d["file_path"], use_max=False)
                    time_points = len(y)
                    max_input_field = np.max(np.abs(y))
                except pulse_func_exception.PulseFuncException, pfe:
                    msg = "Problem Reading File: " + pfe.message                                
                        
        if not msg:
            if not common_util_misc.is_floatable(d["dwell_time"]):
                msg = """I don't understand the dwell_time "%s".""" % d["dwell_time"]

        if not msg:
            if not common_util_misc.is_floatable(d["max_intensity"]):
                msg = """I don't understand the max intensity "%s".""" % d["max_intensity"]
                
        if not msg:
            if not common_util_misc.is_floatable(d["scale_factor"]):
                msg = """I don't understand the scale factor "%s".""" % d["scale_factor"]
                                
        if not msg:
            # At this point we know all of the fields can be cooked. The rest
            # of the validation we have to do is on the cooked data, so we
            # grab it here.
            d = self.get_cooked_gui_data()
            
            
        if not msg:
            if not d["dwell_time"] > 0.0:
                msg = """Dwell Time must be greater than zero"""
                
        if d["use_max_intensity"]:
            if not msg:
                if not d["max_intensity"] > 0.0:
                    msg = """Max Intensity must be greater than zero"""                
        else:    
            if not msg:
                if not d["scale_factor"] > 0.0:
                    msg = """Scale Factor must be greater than zero"""            
            
        if not msg:
            dwell_time = d["dwell_time"]
            dwell_time_increment = machine_settings.dwell_time_increment
            min_dwell_time = machine_settings.min_dwell_time
            
            msg = pulse_funcs_util.check_dwell_time(dwell_time, 
                                                    min_dwell_time,
                                                    dwell_time_increment)

        if not msg:
            if d["max_intensity"] > max_b1_field:
                msg = ("""Max intensity is greater than the max B1 field (%f)""" + \
                """ - as specified in machine settings. Please lower the Max Intensity, """ + \
                """or raise the max B1 field.""")  % max_b1_field
                
        if not msg:
            # 1000 to convert field strength in milliTesla to microTesla.
            max_pulse_strength = d["scale_factor"]*max_input_field*1000
            if max_pulse_strength > max_b1_field:
                msg = ("""The resulting max pulse strength (%f) is greater than the max B1 field (%f)""" + \
                """ - as specified in machine settings. Please lower the Scale Factor, """ + \
                """or raise the max B1 field.""")  % (max_pulse_strength, max_b1_field)

        if not msg:
            # Warn if time_steps are greater than 1/4 of calc_resolution.
            # Unfortunately we have to reach into another tab to get this
            # because we want the value that's in the GUI which may or may
            # not match what's in the object.
            calc_resolution = basic_info["calc_resolution"]
            
            if calc_resolution < (time_points * 4):
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

        if msg:
            self._inner_notebook.activate_tab(self)
            common_dialogs.message(msg)

        return not bool(msg)

