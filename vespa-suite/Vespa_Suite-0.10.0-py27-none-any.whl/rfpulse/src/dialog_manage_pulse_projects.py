# Python modules
from __future__ import division
import os

# 3rd party modules
import wx

# Our modules
import auto_gui.manage_pulse_projects as manage_pulse_projects
import dialog_view_pulse_project
import vespa.common.util.time_ as util_time
import vespa.common.util.import_ as util_import
import vespa.common.util.export as util_export
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.util as common_wx_util
import vespa.common.dialog_export as dialog_export
import vespa.common.constants as common_constants

class DialogManagePulseProjects(manage_pulse_projects.MyDialog):
    """
    Displays the dialog for pulse_project managment (view, delete, import
    export, etc.). The parent param is for the parent window and may be
    None. The db param must be a Database instance.
    """
    def __init__(self, parent, db):
        if not parent:
            parent = wx.GetApp().GetTopWindow()

        manage_pulse_projects.MyDialog.__init__(self, parent)

        self.db = db
        
        # self.pulse_projects is a list of pulse_project preview objects; there's a 
        # 1:1 correspondence between items in this list and items in the
        # dialog's listbox.
        self.pulse_projects = ( )

        self.ListPulseProjects.InsertColumn(0, "Name")
        self.ListPulseProjects.InsertColumn(1, "Public", wx.LIST_FORMAT_CENTER)
        self.ListPulseProjects.InsertColumn(2, "Use Count", wx.LIST_FORMAT_CENTER)

        self.populate_pulse_projects()

        self.SetSize( (500, 400) )

        self.Layout()

        self.Center()

        # Grab key events so I can look for Ctrl/Cmd+A ==> select all
        self.ListPulseProjects.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        self.set_button_status()


    ##################    EVENT HANDLERS     ##################
    
    def on_key_down(self, event):
        if common_wx_util.is_select_all(event):
            common_wx_util.select_list_ctrl_items(self.ListPulseProjects)
            
            self.on_selection_changed()
            
        event.Skip()                    


    def on_view(self, event):
        pulse_projects = self.get_selected_pulse_projects()

        if len(pulse_projects):
            self.view_pulse_project(pulse_projects[0])


    def on_clone(self, event):
        pulse_projects = self.get_selected_pulse_projects()

        for pulse_project in pulse_projects:
            # Since this is just an pulse_project preview, I have to fetch the 
            # full pulse_project in order to clone it.
            original = self.db.fetch_pulse_project(pulse_project.id)

            # Create the clone
            new_pulse_project = original.clone()
            
            new_pulse_project.name = \
                        self.db.find_unique_name(new_pulse_project, "clone")
            
            # Append a comment marking the clone
            comment = "Cloned %s from %s (%s)\n" % \
                        (util_time.now(util_time.DISPLAY_TIMESTAMP_FORMAT),
                         original.id, original.name)
            if new_pulse_project.comment:
                new_pulse_project.comment += "\n" + comment
            else:
                new_pulse_project.comment = comment

            self.db.insert_pulse_project(new_pulse_project)

        if len(pulse_projects):
            self.populate_pulse_projects()


    def on_delete(self, event):
        trouble = self.get_selected_open_intersection()
        
        if trouble:
            msg = "The following %d project(s) are currently open. "    \
                  "Please close them before deleting them.\n\n%s"
            names = [project.name for project in trouble]
            msg = msg % (len(names), ", ".join(names))
                    
            common_dialogs.message(msg, "Delete Pulse Project(s)",
                                   common_dialogs.X_OK)
        else:
            pulse_projects = self.get_selected_pulse_projects()
        
            if pulse_projects:
                names = [pulse_project.name for pulse_project in pulse_projects]
                msg = "Are you sure you want to delete the following %d pulse_project(s)?\n\n%s"
                msg = msg % (len(names), ", ".join(names))
                if wx.YES == common_dialogs.message(msg,
                                                    "Delete pulse_project(s)",
                                                    common_dialogs.Q_YES_NO):
                    # Very important test here --
                    # We must not allow users to delete pulse projects that
                    # are referred to by pulse seqs. Since pulse seqs are 
                    # manipulated outside of this app (in Simulation), 
                    # changes to them can happen at any time. That's why we
                    # postpone this check until the last possible moment
                    # before deletion.
                    # Since the database isn't locked in between this check
                    # and the actual deletion, there's a window in which 
                    # a reference could be created before the deletion. 
                    # However this window is milliseconds wide and can't be
                    # exploited by a user clicking stuff with the mouse.
                    in_use = False
                    for pulse_project in pulse_projects:
                        if self.db.fetch_pulse_project_referrers(pulse_project.id):
                            in_use = True
                            break
                            
                    if in_use:
                        msg = "One or more of these project is in use "     \
                              "(referenced by a pulse sequence).\n\n"       \
                              "Pulse projects that are in use may not "     \
                              "be deleted."
                        common_dialogs.message(msg, "Delete Pulse Project(s)")
                    else:
                        # Hasta la vista!
                        ids = [pulse_project.id for pulse_project in pulse_projects]
                        self.db.delete_pulse_projects(ids)
                        self.populate_pulse_projects()
            else:
                common_dialogs.message("Please select one or more pulse projects to delete.")


    def on_import(self, event):
        filename = common_dialogs.pickfile("Select Import File")
        
        if filename:
            msg = ""
            try:
                importer = util_import.PulseProjectImporter(filename, self.db)
            except IOError:
                msg = """I can't read the file "%s".""" % filename
            except SyntaxError:
                msg = """The file "%s" isn't a valid Vespa export file.""" % filename
                
            if msg:
                common_dialogs.message(msg, style=common_dialogs.E_OK)
            else:
                # Time to rock and roll!
                wx.BeginBusyCursor()
                importer.go()
                wx.EndBusyCursor()

                self.populate_pulse_projects()
                
                msg = """RFPulse imported %d of %d pulse_project(s).
                         Would you like to see the import log?"""            
                msg = msg % (len(importer.imported), importer.found_count)
                if wx.YES == common_dialogs.message(msg, "Import Complete", 
                                                    common_dialogs.Q_YES_NO):
                    common_wx_util.display_file(importer.log_filename)


    def on_export(self, event):
        trouble = self.get_selected_open_intersection()
        
        if trouble:
            msg = "The following %d project(s) are currently open. "    \
                  "Please close them before exporting them.\n\n%s"
            names = [project.name for project in trouble]
            msg = msg % (len(names), ", ".join(names))
                    
            common_dialogs.message(msg, "Export Pulse Project(s)",
                                   common_dialogs.X_OK)
        else:
            pulse_projects = self.get_selected_pulse_projects()
        
            if pulse_projects:
                dialog = dialog_export.DialogExport(self)
                dialog.ShowModal()

                if dialog.export:
                    filename = dialog.filename
                    comment = dialog.comment
                    compress = dialog.compress
                    
                    wx.BeginBusyCursor()
                    # Remember that these are lightweight pulse_project preview 
                    # objects and not fully fledged pulse_project objects. I have to 
                    # load proper copies of the pulse_projects before invoking the 
                    # exporter.
                    pulse_projects = [self.db.fetch_pulse_project(pp.id) for pp
                                                                         in pulse_projects]
                    try:
                        util_export.export(filename, pulse_projects, self.db,
                                           comment, compress)
                    except IOError, (error_number, error_string):
                        msg = """Exporting to "%s" failed. The operating system message is below --\n\n""" % filename
                        msg += error_string
                        common_dialogs.message(msg, "Vespa Export", 
                                               common_dialogs.E_OK)
                
                    # Reload list in case any pulse_projects are newly public.
                    self.populate_pulse_projects()

                    wx.EndBusyCursor()
                #else:
                    # The user cancelled the export dialog.
                
                dialog.Destroy()

                self.ListPulseProjects.SetFocus()
            else:
                common_dialogs.message("Please select one or more pulse projects to export.")


    def on_close(self, event):
        self.Close()


    def on_selection_changed(self, event=None):
        # This function is sometimes called internally (rather than by wx)
        # in which case event is None. 
        self.set_button_status()


    def on_pulse_project_activated(self, event):
        if self.ButtonView.IsEnabled():
            pulse_projects = self.get_selected_pulse_projects()

            if len(pulse_projects):
                self.view_pulse_project(pulse_projects[0])


    ##################    Internal helper functions     ##################
    
    def get_selected_open_intersection(self):
        """Returns the intersection between the set of currently selected
        projects and the projects open in tabs. This is useful because some
        operations (e.g. delete) can't be performed when this set is not 
        empty.
        """
        open_pulse_projects = wx.GetApp().vespa.get_open_projects()
        
        selected_pulse_projects = self.get_selected_pulse_projects()
        
        # I can't use set() to construct the intersection because these might
        # be (and probably will be) different objects representing the same
        # pulse project.
        open_ids = [pulse_project.id for pulse_project in open_pulse_projects]
        
        return [pulse_project for pulse_project in selected_pulse_projects
                              if pulse_project.id in open_ids]
        
    
    def get_selected_pulse_projects(self):
        """Returns a (possibly empty) list of the currently selected
        pulse_projects.
        """
        indices = common_wx_util.get_selected_item_indices(self.ListPulseProjects)
        
        return [pulse_project for i, pulse_project in enumerate(self.pulse_projects)
                                                   if (i in indices)]
        

    def populate_pulse_projects(self):
        """Clears & repopulates the list of pulse_projects"""
        # Build a list of the ids of the currently selected items. I'll
        # use this after re-populating the list.
        selected = [pulse_project.id for pulse_project 
                                     in  self.get_selected_pulse_projects()]

        self.ListPulseProjects.DeleteAllItems()

        self.pulse_projects = self.db.fetch_pulse_project_previews()

        # Populate the listbox
        frozen_color = wx.Colour(*common_constants.FROZEN_COLOR)
        for i, pulse_project in enumerate(self.pulse_projects):
            self.ListPulseProjects.InsertItem(i, pulse_project.name)

            # Mark the public column if necessary
            public = "x" if pulse_project.is_public else " "
            self.ListPulseProjects.SetItem(i, 1, public)

            # Display referrer count if non-zero
            referrers = len(pulse_project.referrers)
            referrers = (str(referrers) if referrers else "")
            self.ListPulseProjects.SetItem(i, 2, referrers)

            if pulse_project.is_frozen:
                # Frozen!
                self.ListPulseProjects.SetItemBackgroundColour(i, frozen_color)

        self.ListPulseProjects.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.ListPulseProjects.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.ListPulseProjects.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)

        # Reselect all the items that were selected before, if possible.
        if self.pulse_projects:
            if selected:
                self.select_ids(selected)

            if not self.get_selected_pulse_projects():            
                # Nothing is selected, so I select the first item.
                common_wx_util.select_list_ctrl_items(self.ListPulseProjects, 0)

        self.ListPulseProjects.SetFocus()
        self.on_selection_changed()

    
    def select_ids(self, ids):
        """Attempts to select the list indices that correspond to the ids
        in the param. Any non-existent ids are ignored.
        """
        indices = [ ]
        
        indices = [i for i, pulse_project in enumerate(self.pulse_projects)
                                          if pulse_project.id in ids]
        
        common_wx_util.select_list_ctrl_items(self.ListPulseProjects, indices)
        
        if indices:
            self.ListPulseProjects.EnsureVisible(indices[0])
            
            
    def set_button_status(self):
        """Enables/disables buttons based on what is selected in the list"""
        pulse_projects = self.get_selected_pulse_projects()
        
        enable = (len(pulse_projects) == 1)
        self.ButtonView.Enable(enable)

        enable = bool(len(pulse_projects))
        self.ButtonClone.Enable(enable)
        self.ButtonDelete.Enable(enable)
        self.ButtonExport.Enable(enable)
        
        # Can't delete pulse projects that are in use
        if any([bool(pulse_project.referrers) for pulse_project 
                                              in pulse_projects]):
            self.ButtonDelete.Disable()


    def view_pulse_project(self, pulse_project):
        # Since this is just an pulse_project preview, I have to fetch the 
        # full pulse_project in order to display it properly.
        pulse_project = self.db.fetch_pulse_project(pulse_project.id)

        dialog = dialog_view_pulse_project.DialogViewPulseProject(self,
                                                                  pulse_project)
        
        dialog.ShowModal()
        
        dialog.Destroy()
