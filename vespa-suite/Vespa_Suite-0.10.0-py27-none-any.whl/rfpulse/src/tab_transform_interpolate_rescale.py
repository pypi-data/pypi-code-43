# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import tab_transform_base
import auto_gui.panel_interpolate_rescale as panel_interpolate_rescale
import vespa.common.util.misc as common_util_misc
import vespa.common.wx_gravy.common_dialogs as common_dialogs



class _PanelParameters(panel_interpolate_rescale.Panel_InterpolateRescale):
    def __init__(self, parent):
        
        panel_interpolate_rescale.Panel_InterpolateRescale.__init__(self, parent)
        
        # These two controls will be hidden for now
        # but may be enabled post-beta.
        self.LabelInterpolation.Hide()
        self.TextInterpolation.Hide()
        
        self.on_checked_interpolate()
        self.on_checked_rescaling()                 
                          
                          
    ##### Event Handlers ######################################################
                          
    def on_checked_interpolate(self, event=None):
        # This is sometimes called internally; in that case event is None
        enable = self.CheckInterpolate.GetValue()
        
        self.LabelOldDwell.Enable(enable)
        self.LabelCurrentDwellTime.Enable(enable)
        self.LabelOldMs.Enable(enable)     

        self.LabelDwell.Enable(enable)
        self.TextDwellTime.Enable(enable)    
        self.LabelNewMs.Enable(enable)
             
             
        # These two controls will be hidden for now
        # but may be enabled post-beta.
        self.LabelInterpolation.Hide()
        self.TextInterpolation.Hide()    
    
    def on_checked_rescaling(self, event=None):
        # This is sometimes called internally; in that case event is None
        enable = self.CheckRescaling.GetValue()
        self.LabelAngle.Enable(enable)
        self.TextAngle.Enable(enable)
        
    ##### Internal helper functions  ##########################################
        
    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = { }

        d["do_interpolate"] = self.CheckInterpolate.GetValue()
        d["interpolation_factor"] = self.TextInterpolation.GetValue().strip()
        d["new_dwell_time"] = self.TextDwellTime.GetValue().strip()
        d["do_rescaling"] = self.CheckRescaling.GetValue()
        d["angle"] = self.TextAngle.GetValue().strip()
        
        return d
        
        
class TabTransformInterpolateRescale(tab_transform_base.TabTransformBase):
    
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

        self.interpolate_rescale_panel = _PanelParameters(parent_base)

        self.initialize_controls()
        
        # insert the transform panel into the TabTransformBase template
        sizer.Insert(0, self.interpolate_rescale_panel, 1, wx.EXPAND, 0)     

        self.plot(relim_flag=True)
        
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
        
        for key in ("new_dwell_time", "angle", ):
            d[key] = float(d[key])

        for key in ("interpolation_factor", ):
            d[key] = int(d[key])
        
        return d


    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = tab_transform_base.TabTransformBase.get_raw_gui_data(self)
        d.update(self.interpolate_rescale_panel.get_raw_gui_data())

        return d
 
 
    def initialize_controls(self):
        # Interpolate
        self.interpolate_rescale_panel.CheckInterpolate.SetValue(self.transform.parameters.do_interpolate)  
        self.interpolate_rescale_panel.TextInterpolation.SetValue(str(self.transform.parameters.interpolation_factor))
        
        self.update_current_dwell_time()  
             
        #FIXME - bjs, at some point it would be nice to come up with a way to
        #  set the new dwell = current dwell if this is a new IR tab being set
        #  up. However, that creates three states for new dwell 1) no prior
        #  results (set to 32.0) 2) has prior results but is a new tab (set to
        #  current dwell) and 3) is a saved project tab and has a previous 
        #  value that may not be equal to 32 or the previous results dwell time
        new_dwell_time = self.transform.parameters.new_dwell_time        
        self.interpolate_rescale_panel.TextDwellTime.SetValue(str(new_dwell_time))

        # Scaling
        self.interpolate_rescale_panel.CheckRescaling.SetValue(self.transform.parameters.do_rescaling)
        self.interpolate_rescale_panel.TextAngle.SetValue(str(self.transform.parameters.angle))

        # Interpolate Rescale flags
        self.interpolate_rescale_panel.on_checked_interpolate()
        self.interpolate_rescale_panel.on_checked_rescaling() 
        
        if self._pulse_project.is_frozen:
            # Frozen projects are mostly uneditable
            self.interpolate_rescale_panel.Disable()
            self.ButtonRun.Hide()


    def run(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        tab_transform_base.TabTransformBase.run(self)  # currently 'pass'
        
        self.update_current_dwell_time()        
        
        # Pass in the result of the last transformation
        # as the initial conditions of this transformation.
        
        previous_result = self._pulse_project.get_previous_result(self.transform)
        self.transform.apply_interpolate_rescale(self._pulse_project.machine_settings, 
                                                 self._pulse_project.master_parameters,
                                                 previous_result)     

        self._last_run.update(self.get_raw_gui_data())
        
        self.plot(update_profiles=True)
        
        return True


    def update_current_dwell_time(self):
        previous_results = self._pulse_project.get_previous_result(self.transform) 
        if previous_results:
            current_dwell_time = previous_results.dwell_time
        else:
            current_dwell_time = 0.0
        self.interpolate_rescale_panel.LabelCurrentDwellTime.SetLabel(str(current_dwell_time))


    def validate_gui(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        msg = ""

        # Check raw input

        # At least one of the boxes has to be checked.
        if not d["do_interpolate"] and not d["do_rescaling"]:
            msg = "Please choose at least one of interpolation or rescaling."

        if not msg:
            if not common_util_misc.is_intable(d["interpolation_factor"]):
                msg = """I don't understand the interpolation factor "%s".""" % d["interpolation_factor"]

        if not msg:
            if not common_util_misc.is_floatable(d["new_dwell_time"]):
                msg = """I don't understand the dwell time "%s".""" % d["new_dwell_time"]

        if not msg:
            if not common_util_misc.is_floatable(d["angle"]):
                msg = """I don't understand the angle "%s".""" % d["angle"]

        if not msg:
            # Raw stuff all checks out OK, now cook the data and make sure
            # that looks good.
            d = self.get_cooked_gui_data()
            
            if d["interpolation_factor"] <= 0:
                msg = """The interpolation factor must be greater than zero."""
                
        if not msg:
            if d["new_dwell_time"] <= 0:
                msg = """The new dwell time must be greater than zero."""
            else:
                new_dwell = d["new_dwell_time"]
    
                minimum_dwell = self._pulse_project.machine_settings.min_dwell_time
                dwell_increment = self._pulse_project.machine_settings.dwell_time_increment
                
                if new_dwell < minimum_dwell:
                    msg = "The new dwell time (%s) is less than the "       \
                          "minimum allowed dwell time (%s)"                 \
                                                  % (new_dwell, minimum_dwell)
                else:
                    remainder = (new_dwell-minimum_dwell) % dwell_increment
                    diff = remainder
                    if diff > 0.5*dwell_increment:
                        diff = dwell_increment - remainder
                        
                    if diff > 0.000001:
                        msg = "The new dwell time (%s) minus the minimum "  \
                              "dwell time (%s) is not an integral number "  \
                              "of dwell time increments (%s)."              \
                                  % (new_dwell, minimum_dwell, dwell_increment)                

        if msg:
            self._inner_notebook.activate_tab(self)
            common_dialogs.message(msg)

        return not bool(msg)
        
