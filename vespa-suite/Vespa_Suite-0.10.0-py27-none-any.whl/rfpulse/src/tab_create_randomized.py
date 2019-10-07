# Python modules
from __future__ import division


# 3rd party modules
import wx


# Our modules
import auto_gui.panel_randomized as panel_randomized
import tab_transform_base
import vespa.common.util.misc as common_util_misc
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.pulse_funcs.pulse_func_exception as pulse_func_exception
import vespa.common.pulse_funcs.util as pulse_funcs_util
import vespa.common.constants as common_constants


class _PanelParameters(panel_randomized.PanelRandomized):
    def __init__(self, parent, inner_notebook):

        panel_randomized.PanelRandomized.__init__(self, parent)

        self._inner_notebook = inner_notebook

        self.initialize_controls()


    ##### Internal helper functions  ##########################################

    def enable_separation_controls(self, enable):
        self.LabelSeparation.Enable(enable)
        self.TextSeparation.Enable(enable)
        self.LabelSeparationKhz.Enable(enable)


    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = { }
        d["time_steps"] = self.TextTimeSteps.GetValue().strip()
        d["duration"] = self.TextDuration.GetValue().strip()

        return d


    def initialize_controls(self):
        pass


class TabCreateRandomized(tab_transform_base.TabTransformBase):

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

        self.params.TextTimeSteps.SetValue(str(parameters.time_points))
        self.params.TextDuration.SetValue(str(parameters.duration))

        if self._pulse_project.is_frozen:
            # Frozen projects are mostly uneditable
            self.params.Disable()
            self.ButtonRun.Hide()


    def get_cooked_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        for key in ("duration", ):
            d[key] = float(d[key])

        d["time_points"] = int(d["time_steps"])

        return d


    def get_raw_gui_data(self):
        """ See documentation here:
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

        if not msg:
            if not common_util_misc.is_intable(d["time_steps"]):
                msg = """I don't understand the time steps value "%s".""" % d["time_steps"]

        if not msg:
            if not common_util_misc.is_floatable(d["duration"]):
                msg = """I don't understand the duration "%s".""" % d["duration"]

        if not msg:
            # At this point we know all of the fields can be cooked. The rest
            # of the validation we have to do is on the cooked data, so we
            # grab it here.
            d = self.get_cooked_gui_data()

        if not msg:
            duration = pulse_funcs_util.check_and_suggest_duration(
                        d["time_points"], d["duration"],
                        self._pulse_project.machine_settings.min_dwell_time,
                        self._pulse_project.machine_settings.dwell_time_increment,
                        )

            if duration != d["duration"]:
                msg = "The duration should be %s to accommodate your "      \
                      "time steps and machine settings (minimum dwell "     \
                      "time and dwell time increment). Would you like "     \
                      "to change the duration to %s?"
                s = ("%f" % duration).strip("0")
                msg = msg % (s, s)

                if wx.YES == common_dialogs.message(msg, None,
                                                    common_dialogs.Q_YES_NO):
                    msg = ""
                    self.params.TextDuration.SetValue(str(duration))
                    # I force the window to update right away so that it
                    # changes before the GUI freezes while running.
                    self.params.TextDuration.Update()
                else:
                    msg = "Please change the duration or number of time steps."

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

        if msg:
            self._inner_notebook.activate_tab(self)
            common_dialogs.message(msg)

        return not bool(msg)

