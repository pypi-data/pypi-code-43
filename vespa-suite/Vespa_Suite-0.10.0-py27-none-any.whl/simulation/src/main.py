#!/usr/bin/env python

# Python modules
from __future__ import division
import os
import webbrowser
import struct

# 3rd party modules
import wx
import wx.adv as wx_adv
import wx.lib.agw.aui as aui        # NB. wx.aui version throws odd wxWidgets exception on Close/Exit


# Our modules
import constants
import util_menu
import util_simulation_config
import util_db
import aui_subclass
import notebook_experiments
import dialog_manage_metabolites
import dialog_manage_pulse_sequences
import dialog_manage_experiments
import dialog_mixed_metabolite_output as dialog_mixout

import vespa.common.util.init as util_init
import vespa.common.util.time_ as util_time
import vespa.common.util.misc as util_misc
import vespa.common.images as images
import vespa.common.constants as common_constants
import vespa.common.mrs_experiment as mrs_experiment
import vespa.common.mrs_pulse_sequence as mrs_pulse_sequence
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.util as wx_util
import vespa.common.dialog_experiment_browser as dialog_experiment_browser

#----------------------------------------------------------------------




class Main(wx.Frame):

    def __init__(self, db, position, size):
        self._left, self._top = position
        self._width, self._height = size

        style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX |           \
                wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER |   \
                wx.CLIP_CHILDREN

        wx.Frame.__init__(self, None, wx.ID_ANY, "Simulation",
                          (self._left, self._top),
                          (self._width, self._height), style)

        self.db = db

        # GUI Creation ----------------------------------------------

        self.experiment_notebook = None

        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)

        self.SetIcon(images.Mondrian.GetIcon())

        self.statusbar = self.CreateStatusBar(4, 0)
        self.statusbar.SetStatusText("Ready")

        util_menu.bar = util_menu.SimulationMenuBar(self)
        self.SetMenuBar(util_menu.bar)

        self.build_panes()
        self.bind_events()

    ##############                                    ############
    ##############     Internal helpers are below     ############
    ##############       in alphabetical order        ############
    ##############                                    ############

    def bind_events(self):
        self.Bind(wx.EVT_CLOSE, self.on_self_close)
        self.Bind(wx.EVT_SIZE, self.on_self_coordinate_change)
        self.Bind(wx.EVT_MOVE, self.on_self_coordinate_change)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase_background)


    def build_panes(self):
        self.experiment_notebook = notebook_experiments.NotebookExperiments(self, self.db)

        # create center pane
        self._mgr.AddPane(self.experiment_notebook,
                          aui.AuiPaneInfo().
                          Name("experiments").
                          CenterPane().
                          PaneBorder(False))

        # "commit" all changes made to AuiManager
        self._mgr.Update()


    ##############                                    ############
    ##############      Event handlers are below      ############
    ##############       in alphabetical order        ############
    ##############                                    ############

    def on_erase_background(self, event):
        event.Skip()


    def on_self_close(self, event):
        if self.experiment_notebook.close_all_experiment_tabs():
        
            # Since this is the main window, closing "self" means closing the app.
            # I trap this so I can save my coordinates
            config = util_simulation_config.Config()

            config.set_window_coordinates("main", self._left, self._top,
                                          self._width, self._height)
            config.write()
            
            self._mgr.UnInit()      # needed to avoid wx._core.wxAssertionError: C++ assertion "GetEventHandler() == this" failed at ..\..\src\common\wincmn.cpp 
            self.Destroy()


    def on_self_coordinate_change(self, event):
        # This is invoked for move & size events
        if self.IsMaximized() or self.IsIconized():
            # Bah, forget about this. Recording coordinates doesn't make sense
            # when the window is maximized or minimized. This is only a
            # concern on Windows; GTK and OS X don't produce move or size
            # events when a window is minimized or maximized.
            pass
        else:
            if event.GetEventType() == wx.wxEVT_MOVE:
                self._left, self._top = self.GetPosition()
            else:
                # This is a size event
                self._width, self._height = self.GetSize()


    ##############                                    ############
    ##############       Menu handlers are below      ############
    ##############       in the order they appear     ############
    ##############             on the menu            ############
    ##############                                    ############

    ############    Experiment menu

    def on_new_experiment(self, event):
        experiment = mrs_experiment.Experiment()
        experiment.id = util_misc.uuid()
        # Set last-used defaults
        experiment.b0      = wx.GetApp().vespa.b0
        experiment.isotope = wx.GetApp().vespa.isotope

        self.experiment_notebook.add_experiment_tab(experiment, True)


    def on_copy_tab(self, event):
        self.experiment_notebook.copy_tab()

    def on_add_sub_tab(self, event):
        self.experiment_notebook.add_sub_tab()

    def on_open_experiment(self, event):
        dialog = dialog_experiment_browser.DialogExperimentBrowser(self, self.db)

        dialog.ShowModal()

        if dialog.selected_experiment_id:
            # If this experiment is already open, just activate its tab.
            experiments = wx.GetApp().vespa.get_open_experiments()

            ids = [experiment.id for experiment in experiments]

            if dialog.selected_experiment_id in ids:
                # It's already open
                self.experiment_notebook.activate_experiment_tab(dialog.selected_experiment_id)
            else:
                # It's not open. Create a new tab for it.
                experiment = self.db.fetch_experiment(dialog.selected_experiment_id)
                self.experiment_notebook.add_experiment_tab(experiment, False)
        #else:
            # User hit cancel


    def on_save_experiment(self, event):
        if self.experiment_notebook:
            if self.experiment_notebook.active_tab:
                self.experiment_notebook.active_tab.save_experiment()


    def on_close_experiment(self, event):
        if self.experiment_notebook:
            self.experiment_notebook.close_experiment_tab()

    def on_menu_third_analysis_prior(self, event):
        self.on_manage_mixed_output(constants.ThirdPartyExportTypes.ANALYSIS_PRIOR)

    def on_menu_third_midas_prior(self, event):
        self.on_manage_mixed_output(constants.ThirdPartyExportTypes.MIDAS_PRIOR)

    def on_menu_third_lcmodel(self, event):
        self.on_manage_mixed_output(constants.ThirdPartyExportTypes.LCMODEL)

    def on_menu_third_jmrui_text(self, event):
        self.on_manage_mixed_output(constants.ThirdPartyExportTypes.JMRUI)

    def on_menu_third_gava_text(self, event):
        self.on_manage_mixed_output(constants.ThirdPartyExportTypes.GAVA)

    def on_manage_mixed_output(self, format):
        if self.experiment_notebook:
            tab = self.experiment_notebook.active_tab
            if tab:
                msg = ''
                if tab.setup.is_new:
                    # (self.is_new == True) ==> nothing important in self.last_save
                    if not tab.setup.last_run:
                        # OK, the expt has not been run at least once which is 
                        # a necessary precondition for saving third party 
                        # output.
                        msg = "Please run this experiment before saving 3rd party output."
                if msg:
                    common_dialogs.message(msg, None, common_dialogs.I_OK)
                else:
                    dialog = dialog_mixout.DialogMixedMetaboliteOutput(self, 
                                             tab.experiment, tab.freq1d, format)
                    dialog.ShowModal()
        


    ############    View  menu
    # View options affect only the experiment tab and so it's up to the
    # experiment notebook to react to them.

    def on_menu_view_option(self, event):
        self.experiment_notebook.on_menu_view_option(event)

    def on_menu_view_output(self, event):
        self.experiment_notebook.on_menu_view_output(event)

    ############    Management  menu

    def on_manage_experiments(self, event):
        dialog = dialog_manage_experiments.DialogManageExperiments(self, self.db)
        dialog.ShowModal()


    def on_manage_metabolites(self, event):
        dialog = dialog_manage_metabolites.DialogManageMetabolites(self, self.db)
        dialog.ShowModal()


    def on_manage_pulse_sequences(self, event):
        dialog = dialog_manage_pulse_sequences.DialogManagePulseSequences(self, self.db)
        dialog.ShowModal()
        


    ############    Help menu

    def on_user_manual(self, event):
        path = util_misc.get_vespa_install_directory()
        path = os.path.join(path, "docs", "simulation_user_manual.pdf")
        wx_util.display_file(path)


    def on_simulation_help_online(self, event):
        webbrowser.open("http://scion.duhs.duke.edu/vespa/simulation", 1)


    def on_vespa_help_online(self, event):
        webbrowser.open("http://scion.duhs.duke.edu/vespa", 1)


    def on_about(self, event):
        bit = str(8 * struct.calcsize('P')) + '-bit Python'
        info = wx_adv.AboutDialogInfo()
        info.SetVersion(util_misc.get_vespa_version())
        info.SetCopyright("Copyright 2010, Duke University. All rights reserved.")
        info.SetDescription("Simulation is an advanced spectral simulation and analysis environment. Running on "+bit)
        info.SetWebSite("http://scion.duhs.duke.edu/vespa/")
        wx_adv.AboutBox(info)


    def on_show_inspection_tool(self, event):
        wx_util.show_wx_inspector(self)



#--------------------------------------------------------------------

if __name__ == "__main__":
    app, db_path = util_init.init_app("Simulation")

    db = util_db.Database(db_path, True)

    # My settings are in simulation.ini
    config = util_simulation_config.Config()

    app.vespa.isotope = config["general"]["default_isotope"]
    app.vespa.b0 = float(config["general"]["default_b0"])

    position, size = config.get_window_coordinates("main")
    frame = Main(db, position, size)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()

    # Once we exit the main loop, there's a couple of "last used" values
    # that we want to save.
    config = util_simulation_config.Config()

    config["general"]["default_isotope"] = app.vespa.isotope
    config["general"]["default_b0"]      = app.vespa.b0

    config.write()
