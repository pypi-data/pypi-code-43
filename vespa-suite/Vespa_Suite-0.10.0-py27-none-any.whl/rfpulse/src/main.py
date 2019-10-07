#!/usr/bin/env python

# Python modules
from __future__ import division
import os
import webbrowser

# 3rd party modules
import wx
import wx.adv as wx_adv
import wx.lib.agw.aui as aui        # NB. wx.aui version throws odd wxWidgets exception on Close/Exit


# Our modules
# We import vespa.common.wx_gravy.plot_panel here even though we don't use it
# in this module. It needs to be the first Vespa import to avoid matplotlib 
# sensitivity to import order. 
# See http://scion.duhs.duke.edu/vespa/project/ticket/26
import vespa.common.wx_gravy.plot_panel
import util_db
import util_menu
import notebook_pulse_projects
import dialog_third_party_export
import dialog_manage_pulse_projects
import dialog_manage_transform_kernels
import dialog_manage_machine_settings
import util_rfpulse_config as rf_config
import vespa.common.images as images
import vespa.common.util.init as util_init
import vespa.common.util.misc as util_misc
import vespa.common.util.config as util_config
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.util as wx_util
import vespa.common.dialog_pulse_project_browser as dialog_pulse_project_browser

from vespa.common.constants import TransformationType


#----------------------------------------------------------------------


class Main(wx.Frame):

    def __init__(self, db, position, size):
        
        self._left, self._top = position
        self._width, self._height = size
        
        style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX |           \
                wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.RESIZE_BORDER |   \
                wx.CLIP_CHILDREN

        wx.Frame.__init__(self, None, wx.ID_ANY, "RFPulse",
                          (self._left, self._top),
                          (self._width, self._height), style)

        self.db = db
        self.pulse_project_notebook = None
        
        # GUI Creation ----------------------------------------------
        
        aui_manager = aui.AuiManager()
        aui_manager.SetManagedWindow(self)
        # We don't use this reference to the AUI manager outside of this 
        # code, but if we don't keep a ref to it then Python will garbage
        # collect it and the AUI manager will die which usually results in 
        # a segfault. So here we create a reference that we don't use. 
        self.__aui_manager = aui_manager

        self.SetIcon(images.Mondrian.GetIcon())

        self.statusbar = self.CreateStatusBar(4, 0)
        self.statusbar.SetStatusText("Ready")
        
        # I make the status bar globally available because multiple places
        # in the app want to use it.
        wx.GetApp().vespa.statusbar = self.statusbar

        util_menu.bar = util_menu.RFPulseMenuBar(self)
        self.SetMenuBar(util_menu.bar)


        self.build_panes(aui_manager)
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
        
    def build_panes(self, aui_manager):

        self.pulse_project_notebook = notebook_pulse_projects.NotebookPulseProjects(self, self.db)

        # create center pane
        aui_manager.AddPane(self.pulse_project_notebook, 
                            aui.AuiPaneInfo().
                            Name("pulse projects").
                            CenterPane().
                            PaneBorder(False))

        # "commit" all changes made to AuiManager
        aui_manager.Update()


    ##############                                    ############
    ##############      Event handlers are below      ############
    ##############       in alphabetical order        ############
    ##############                                    ############

    def on_erase_background(self, event):
        event.Skip()


    def on_self_close(self, event):
        if self.pulse_project_notebook.close_all():
            # Save my coordinates
            config = rf_config.Config()

            config.set_window_coordinates("main", self._left, self._top, 
                                          self._width, self._height)
            config.write()
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

    ############    Pulse Project menu

    def on_new_pulse_project(self, event):
        wx.SetCursor(wx.HOURGLASS_CURSOR)
        self.pulse_project_notebook.add_pulse_project_tab()
        wx.SetCursor(wx.NullCursor)


    def on_open_pulse_project(self, event):

        dialog = dialog_pulse_project_browser.DialogPulseProjectBrowser(self, self.db)
        dialog.ShowModal()
        if dialog.selected_pulse_project_id:
            wx.SetCursor(wx.HOURGLASS_CURSOR)
            pulse_project = self.db.fetch_pulse_project(dialog.selected_pulse_project_id)
            # Make sure the results are current
            pulse_project.update_results()
            self.pulse_project_notebook.add_pulse_project_tab(pulse_project)
            wx.SetCursor(wx.NullCursor)


    def on_run_pulse_project(self, event):
        if self.pulse_project_notebook.active_tab:
            self.pulse_project_notebook.active_tab.run()


    def on_save_pulse_project(self, event):
        self.pulse_project_notebook.save_pulse_project()


    def on_save_as_pulse_project(self, event):
        self.pulse_project_notebook.save_as_pulse_project()


    def on_close_pulse_project(self, event):
        self.pulse_project_notebook.close_pulse_project()


    def on_copy_pulse_project_tab(self, event):
        wx.SetCursor(wx.HOURGLASS_CURSOR)
        self.Freeze()
        self.pulse_project_notebook.copy_tab()
        self.Thaw()
        wx.SetCursor(wx.NullCursor)


    def on_third_party_export(self, event):
        tab = self.pulse_project_notebook.active_tab
        
        if tab:
            if tab.is_synced:
                # All of the tabs in the pulse project are in sync.
                export = True
            else:
                # At least one tab is not in sync. Give the user the option
                # to halt the export. 
                msg = "You have edited this project since it was "      \
                      "last opened or run. RFPulse can only export "    \
                      "the project as it was when it was last opened "  \
                      "or run.\n\n"                                     \
                      "Do you want to continue with the export?"
          
                export = (wx.YES == common_dialogs.message(msg, "Continue Export", 
                                                           common_dialogs.Q_YES_NO))

            if export:       
                pulse     = tab.pulse_project.get_pulse()       # returns MinimalistPulse obj
                bandwidth = tab.pulse_project.get_bandwidth()   # in kHz
                tip_angle = tab.pulse_project.get_tip_angle()   # in degrees
                
                if pulse:
                    dialog = dialog_third_party_export.DialogThirdPartyExport(self, 
                                                              tab.pulse_project.id,
                                                              pulse, bandwidth, tip_angle)
                    dialog.ShowModal()
                else:
                    msg = """This pulse project doesn't have a final """    \
                          """pulse. You can only use export completed """   \
                          """pulse projects to third party formats."""
                    common_dialogs.message(msg)
        #else:
            # Ignore the menu click -- Only the welcome tab is open
        


    ############    Management  menu

    def on_manage_pulse_projects(self, event):
        dialog = dialog_manage_pulse_projects.DialogManagePulseProjects(self, self.db)
        dialog.ShowModal()

    def on_manage_machine_settings_templates(self, event):
        dialog = dialog_manage_machine_settings.DialogManageMachineSettings(self, self.db)
        dialog.ShowModal()

    ############    Transforms menu

    def on_create_slr(self, event):
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.CREATE_SLR)
        self.Thaw()
        
    def on_create_hyperbolic_secant(self, event):
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.CREATE_HYPERBOLIC_SECANT)
        self.Thaw()
        
    def on_create_gaussian(self, event):        
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.CREATE_GAUSSIAN)
        self.Thaw()
                
    def on_create_randomized(self, event):        
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.CREATE_RANDOMIZED)
        self.Thaw()
        
    def on_create_import(self, event):        
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.CREATE_IMPORT)
        self.Thaw()
    
    def on_ir(self, event):
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.INTERPOLATE_RESCALE)
        self.Thaw()
        
    def on_optimal_control_nonselective(self, event):
        self.Freeze()
        self.pulse_project_notebook.add_transformation(TransformationType.OCN)
        self.Thaw()

    ############    View  menu
    # View options affect only the experiment tab and so it's up to the
    # experiment notebook to react to them.
            
    def on_menu_view_option(self, event):    
        self.pulse_project_notebook.on_menu_view_option(event)

    def on_menu_view_output(self, event):
        self.pulse_project_notebook.on_menu_view_output(event)

    ############    Help menu

    def on_user_manual(self, event):
        path = util_misc.get_vespa_install_directory()
        path = os.path.join(path, "docs", "rfpulse_user_manual.pdf")
        wx_util.display_file(path)

    def on_rfpulse_help_online(self, event):
        webbrowser.open("http://scion.duhs.duke.edu/vespa/rfpulse", 1)

    def on_vespa_help_online(self, event):
        webbrowser.open("http://scion.duhs.duke.edu/vespa", 1)

    def on_about(self, event):
        info = wx_adv.AboutDialogInfo()
        info.SetVersion(util_misc.get_vespa_version())
        info.SetCopyright("Copyright 2010, Duke University and the United States Department of Veterans Affairs. All rights reserved.")
        info.SetDescription("RFPulse is an advanced toolkit for generating RF pulses for MR simulations.")
        info.SetWebSite("http://scion.duhs.duke.edu/vespa/")
        wx_adv.AboutBox(info)


    def on_show_inspection_tool(self, event):
        wx_util.show_wx_inspector(self)





#--------------------------------------------------------------------

if __name__ == "__main__":
    app, db_filename = util_init.init_app("RFPulse")

    db = util_db.Database(db_filename)

    # All my other settings are in rfpulse.ini
    config = rf_config.Config()
    
    position, size = config.get_window_coordinates("main")
    frame = Main(db, position, size)
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()

