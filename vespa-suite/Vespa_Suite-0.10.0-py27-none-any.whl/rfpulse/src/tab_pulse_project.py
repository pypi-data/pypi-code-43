# Python modules
from __future__ import division
import os


# 3rd party modules
import wx
import wx.aui as aui
import wx.lib.agw.aui as aui        # NB. wx.aui version throws odd wxWidgets exception on Close/Exit


# Our modules
import constants
import tab_basic_info
import tab_create_slr
import tab_create_hs
import tab_create_gaussian
import tab_create_randomized
import tab_create_import
import tab_transform_interpolate_rescale
import tab_transform_root_reflect
import tab_transform_optimal_control_nonselective
import util_rfpulse_config
import dialog_optional_message
import util as rfpulse_util
import vespa.common.util.misc as util_misc
import vespa.common.util.time_ as util_time
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.notebooks as vespa_notebooks
import vespa.common.rfp_transformation_factory as rfp_transformation_factory
import vespa.common.rfp_machine_settings as rfp_machine_settings
import vespa.common.rfp_pulse_project as rfp_pulse_project
from vespa.common.constants import TransformationType


BASIC_INFO_TAB_TITLE = "Basic Info"

# _OPTIMAL_CONTROL_TAB_TITLE is the base part of the title on OC tabs. The
# full title also contains a number. See _update_oc_tab_labels().
_OPTIMAL_CONTROL_TAB_TITLE = "OC(NS)"

# _OUT_OF_SYNC_SYMBOL is the text added to the tab label when it's not in sync
# (i.e. has been edited since last run).
_OUT_OF_SYNC_SYMBOL = " * "


def _find_run_button(window):
    # Given a window (usually a tab), will walk through the tree of children
    # looking for a button with the text "Run". If it can't find such a 
    # button, it returns None.
    #
    # This function is recursive.
    run_button = None

    subwindows = [ ]
    for kid in window.GetChildren():
        if hasattr(kid, "GetChildren"):
            # This kid has kids of its own that we might need to check
            subwindows.append(kid)

        if hasattr(kid, "GetLabel") and isinstance(kid, wx.Button):
            # Looks like a button...
            if kid.GetLabel() == "Run":
                # It is a button, and it's the one we're looking for.
                run_button = kid
           
    # As long as we haven't found our target yet and there's still kids to
    # traverse, we keep looking.
    while (not bool(run_button)) and bool(subwindows):
        run_button = _find_run_button(subwindows.pop())
        
    return run_button



class TabPulseProject(vespa_notebooks.VespaAuiNotebook):
    """
    This is both a notebook and a tab. It's a tab in the main a.k.a.
    outer notebook. It's also a notebook that represents an RFPulse as a
    series of tabs. There are zero or more instances of these classes in
    existence at one time -- one for each pulse project that the user has
    opened.
    
    """
    def __init__(self, main_frame, db, pulse_project=None):
        
        style = aui.AUI_NB_SCROLL_BUTTONS       |       \
                aui.AUI_NB_CLOSE_ON_ACTIVE_TAB  |       \
                aui.AUI_NB_BOTTOM               |       \
                aui.AUI_NB_MIDDLE_CLICK_CLOSE   |       \
                wx.NO_BORDER

        vespa_notebooks.VespaAuiNotebook.__init__(self, main_frame, style)

        self._db = db
        
        # _last_save tracks the ids of the tabs that were open when this
        # project was last saved. Individual tabs know who their left 
        # neighbors are and will notice if it changes. However if the 
        # last (rightmost) tab/transformation in a series is deleted, the 
        # tab to the left won't notice. It's up to the project notebook to 
        # notice that change, and this is how we do it.
        # Note that the ids that this list stores are the values returned
        # by Python's id() function. Those values aren't useful for much, 
        # but they work just fine for comparing against themselves.
        self._last_save = [ ]
        
        if pulse_project:
            # The user opened an existing pulse project from the DB or 
            # copied an open project.
            is_new = False
            self.pulse_project = pulse_project
            
            # If I can't find this in the database, then this project was
            # copied from another project. That matters, see below.
            is_saved = self._db.exists_pulse_project_in_database(pulse_project.id)
        else:
            # This is a new project
            is_new = True
            self.pulse_project = rfp_pulse_project.PulseProject()
            self.pulse_project.id = util_misc.uuid()
            self.pulse_project.created = util_time.now()
    
            # New projects get the default machine settings.
            default_template = self._db.fetch_default_machine_settings_template()
            self.pulse_project.machine_settings = \
                    rfp_machine_settings.settings_from_template(default_template)

        # Create the user interface.
        self.add_tab(None, is_new) 
        for transformation in self.pulse_project.transformations:
            self.add_tab(transformation, is_new)
            
        if is_new or is_saved:
            # The project is brand new or if I've opened an existing project
            # from the database. I save the state of the tabs. This, along
            # with the individual tabs saving their GUI state, means the
            # user can hit close right away and not be bugged about
            # unsaved changes. 
            self._set_last_save()
        # else:
            # The only way a project could be not new and yet unsaved is if
            # it's been copied from another project. In that case, we want
            # the user to be prompted if they attempt to close without saving.
            # Doing nothing here (i.e. not setting self._last_save) does
            # the trick.
            
        # Show the basic info tab
        self.activate_tab(index=0)
        
        # Set the focus to the name textbox on Basic Info. For some reason,
        # the focus winds up in la-la land unless we allow things to settle
        # down before calling SetFocus(), hence the use of CallAfter() here.
        # On GTK, even this trick is not sufficient. Not sure what else to do!
        wx.CallAfter(self.tabs[0].TextName.SetFocus)

        self.update_sync_status()

        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_page_changed)
        
        

    @property
    def create_transformation_added(self):
        """True if the project contains a create transformation, False 
        otherwise"""
        type_ = TransformationType.NONE
        
        if self.pulse_project.transformations:
            type_ = self.pulse_project.transformations[0].type
            
        return type_ in TransformationType.CREATE_TYPES


    @property
    def is_saved(self):
        return all([tab.is_saved for tab in self.tabs]) and \
               (self._last_save == [id(tab) for tab in self.tabs])


    @property
    def is_synced(self):
        return all([tab.is_synced for tab in self.tabs])


    #=======================================================
    #
    #           Event handlers start here 
    #                 (alphabetized)
    #
    #=======================================================

    def on_activation(self):
        # This is a faux event handler. wx doesn't call it directly. It's 
        # a notification from my parent (the experiment notebook) to let
        # me know that this tab has become the current one.
        if self.active_tab:
            self.active_tab.on_activation()


    def on_menu_view_option(self, event): 
        if self.active_tab:
            self.active_tab.on_menu_view_option(event) 


    def on_menu_view_output(self, event):
        if self.active_tab:
            self.active_tab.on_menu_view_output(event)

             
    def on_output(self, event):
        
        #FIXME - can output arrays to text file using NUMPY.SAVETEXT function
        
        event_id = event.GetId()
        msg = ""
        
        if event_id == self.ids.OUTPUT_1D_STACK_TO_PNG:
            filename = common_dialogs.pickfile("Select PNG Filename", new_file=True)
            if filename:
                filename = os.path.splitext(filename)[0]+'.png'
                figure = self.canvas.figure
            # Chopped out stuff... from Simulation code.
        elif event_id == self.ids.OUTPUT_INTEGRAL_TO_PDF:
            filename = common_dialogs.pickfile("Select PDF Filename", new_file=True)
            if filename:
                filename = os.path.splitext(filename)[0]+'.pdf'
                figure = self.integral.figure


        if filename:
            try:
                figure.savefig( filename,
                                dpi=300, 
                                facecolor='w', 
                                edgecolor='w',
                                orientation='portrait', 
                                papertype='letter', 
                                format=None,
                                transparent=False)
            except IOError:
                msg = """I can't write the file "%s".""" % filename
            
        if msg:
            common_dialogs.message(msg, style=common_dialogs.E_OK)  


    def on_page_changed(self, event):
        # we may be on a new transformation tab, we need to update the
        # settings in the View Menu
        self.active_tab.on_activation()
        # If a user changes an input field and then moves to another tab,
        # I won't get the child focus event upon which RFPulse normally 
        # relies to notice a change in sync status. To ensure the status
        # is current, we update it when a tab becomes active.
        self.update_sync_status()
        

    def on_page_close(self, event):
        tab_index = self.GetSelection()
        
        veto = False
        
        msg = ""
        
        if self.pulse_project.is_frozen:
            msg = "This project is frozen. You can't delete "   \
                  "transformations from it."
                 
        if not msg:
            if tab_index == 0:
                msg = "You can't remove the Basic Info tab from a pulse project."

        if not msg:
            if tab_index == 1 and self.GetPageCount() > 2:
                msg = "Sorry, you can't delete the project's create "       \
                      "transformation when there are transformations "      \
                      "downstream."

        if msg:
            common_dialogs.message(msg, "Remove Transformation")
            veto = True
        else:
            msg = "Are you sure you want to delete this transformation?"
            
            if tab_index != (len(self.tabs) - 1):
                # This isn't the last tab, so there are downstream tabs.
                msg += "\n\nResults in the downstream tabs will be discarded."
            if wx.NO == common_dialogs.message(msg, "Remove Transformation",
                                               common_dialogs.Q_YES_NO):
                veto = True

        if veto:
            event.Veto()
        else:
            # Buh-bye!
            # Remember that indices into the list of transformations are one
            # smaller than the indices into the list of tabs (because of
            # create info), so I have to adjust the tab_index here.
            oc_tab_deleted = \
                rfpulse_util.is_oc(self.pulse_project.transformations[tab_index - 1])

            self.pulse_project.delete_transformation(tab_index - 1)
            # Whack the results in the downstream tabs.
            for tab in self.tabs[tab_index:]:
                tab.clear_result()

            if oc_tab_deleted:
                # An OC tab was deleted, so I need to update the labels on 
                # those tabs. The renumbering can't happen correctly until
                # the tab is actually gone which won't happen until wx
                # processes this on_page_close() call, so we use CallAfter()
                # to update the OC tab labels once the tab is really gone. 
                wx.CallAfter(self._update_oc_tab_labels)


    #=======================================================
    #
    #     Internal & shared helper methods start here 
    #                 (alphabetized)
    #
    #=======================================================
    def _is_discard_results_ok(self):
        # Shows the "are you sure you want to discard downstream results?"
        # message box (if the user hasn't already disabled it) and returns
        # the user's choice. 
        discard_ok = True
        
        # This is an optional message which means the user might have 
        # disabled its display. Here we check that.
        config = util_rfpulse_config.Config()
        if "warn_when_discarding_results" in config["general"]:
            warn_when_discarding_results = \
                config["general"].as_bool("warn_when_discarding_results")
        else:
            warn_when_discarding_results = True
            
        if warn_when_discarding_results:
            msg = "Results in the downstream tabs will be discarded.\n\n"   \
                  "Are you sure you want to continue?"
            dialog = dialog_optional_message.DialogOptionalMessage(self, msg)
            answer = dialog.ShowModal()
        
            if dialog.dont_show_again:
                # Turn this off so we won't squawk next time
                config["general"]["warn_when_discarding_results"] = False
                config.write()
            dialog.Destroy()
        
            if answer != wx.OK:
                discard_ok = False
                
        return discard_ok


    def _set_last_save(self):
        # See __init__ for documentation of _last_save.
        self._last_save = [id(tab) for tab in self.tabs]


    def add_tab(self, transformation, is_new):
        """Adds a tab representing the transformation."""
        
        if not transformation:
            tab = tab_basic_info.TabBasicInfo(self, self._db, self.pulse_project)
            self.AddPage(tab, BASIC_INFO_TAB_TITLE)
        else:
            # Adding root reflect is conditional
            if transformation.type == TransformationType.ROOT_REFLECTION:
                # we have -1 points here because time_points is the number of 
                # pulse steps +1 in order to plot correctly. Thus here we 
                # subtract one.
                npts = self.pulse_project.transformations[0].parameters.time_points - 1
                if  npts > constants.MAX_ROOT_REFLECT_POINTS:
                    title = "RFPulse - Add Transformation"
                    msg = "The Root Reflect transformation algorithm is " + \
                          "only stable for pulses of 64 points or less. " + \
                          "Please reduce the number of points in your "   + \
                          "pulse to use this transformation."
                    common_dialogs.message(msg, title)
                    return

            # We use dictionary dispatch to avoid a lengthy if..elif...elif            
            # Each dict key points to a 2-tuple (tab constructor, tab label).
            dispatcher = { 
                TransformationType.CREATE_SLR["db"] : 
                    (tab_create_slr.TabCreateSlr, " SLR "),
                TransformationType.CREATE_GAUSSIAN["db"] : 
                    (tab_create_gaussian.TabCreateGaussian, "Gaussian"),                      
                TransformationType.CREATE_RANDOMIZED["db"] : 
                    (tab_create_randomized.TabCreateRandomized, "Randomized"),
                TransformationType.CREATE_HYPERBOLIC_SECANT["db"] : 
                    (tab_create_hs.TabCreateHyperbolicSecant, "Hyperbolic"),
                TransformationType.CREATE_IMPORT["db"] : 
                    (tab_create_import.TabCreateImport, "Import"),                    
                TransformationType.INTERPOLATE_RESCALE["db"] : 
                    (tab_transform_interpolate_rescale.TabTransformInterpolateRescale,
                     " I.R. "),
                TransformationType.ROOT_REFLECTION["db"] : 
                    (tab_transform_root_reflect.TabTransformRootReflect,
                     "Root Reflect"),
                TransformationType.OCN["db"] : 
                    (tab_transform_optimal_control_nonselective.TabTransformOCN,
                     _OPTIMAL_CONTROL_TAB_TITLE),
                         }
        
            constructor, label = dispatcher[transformation.type["db"]]
            
            # We need to pass the left neighbor to the ctor. Since new tabs
            # are always appended (rather than inserted midstream), the left
            # neighbor of an about-to-be-added tab is the last one currently
            # in the list.
            tab = constructor(self, self.tabs[-1], self.pulse_project,
                              transformation, is_new)
            self.AddPage(tab, label, False)  
            
            if rfpulse_util.is_oc(transformation):
                self._update_oc_tab_labels()    

        # Make the new tab active.
        self.activate_tab(tab)


    def add_transformation(self, transform_type, transform=None):
        """
        Appends a transformation & tab to the end of the list. In some cases,
        adding the transformation is refused (e.g. if the user wants to add
        a create transformation and there's already one in the project).
        """
        msg = ''
        if transform_type in TransformationType.CREATE_TYPES:
            if self.create_transformation_added:
                msg = 'There is already a create transformation in this project.'
        else:
            if not self.create_transformation_added:
                msg = 'Please add a create transformation before adding other transformations.'
        
        if not msg:
            if self.pulse_project.is_frozen:
                msg = "This project is frozen. You can't add transformations to it."
        
        if msg:
            common_dialogs.message(msg)
            return
        
        if not transform:
            transform = rfp_transformation_factory.create_transformation(transform_type)

        # append to end of list.
        self.pulse_project.transformations.append(transform)
        self.add_tab(transform, True)

        
    def close(self):
        """Asks the user if it is OK to close the project. Returns False
        if the user rejects the close (i.e. hits "cancel" on the "OK to 
        close?" message box), True otherwise. If there are no changes,
        the user is not prompted at all (and True is returned).
        """
        if not self.is_saved:
            name = self.pulse_project.name
            if name:
                name = '"%s"' % name

            msg = "The project %s has unsaved changes. RFPulse is about "   \
                  "to discard those changes." % name
            answer = common_dialogs.message(msg, None, 
                                    wx.ICON_INFORMATION | wx.OK | wx.CANCEL)
        else:
            # No need to bug the user; everything is up to date.
            answer = wx.OK

        return (answer == wx.OK)
            

    def get_left_neighbor(self, tab):
        """Returns the tab param's left neighbor, or None if there is no 
        left neighbor."""
        i = self.get_tab_index(tab) - 1
        return None if i < 0 else self.tabs[i]
        
        
    def get_current_calc_resolution(self):
        # Allows other tabs to reach into Info (first) tab to get this
        # because we want the value that's in the GUI which may or may
        # not match what's in the object.
        tab = self.GetPage(0)
        calc_resolution = tab.TextCalcResolution.GetValue()
        return int(calc_resolution)


    def run(self, calling_tab=None):
        # Set the focus to the run button if possible. This is a fix for 
        # RFPulse bug 19:
        # http://scion.duhs.duke.edu/vespa/rfpulse/ticket/19
        run_button = _find_run_button(self.active_tab)
        if run_button:
            run_button.SetFocus()
        
        self.update_sync_status()

        if calling_tab:
            # We only run up to & including the tab on which run was clicked, 
            # so I truncate the list of tabs there. 
            i = 0
            for tab in self.tabs:
                i += 1
                if tab.GetId() == calling_tab.GetId():
                    break
        else:
            # Run all tabs
            i = len(self.tabs)
    
        tabs = self.tabs[:i]
        right_neighbors = self.tabs[i:]
    
        # Furthermore, we only run tabs that are out of sync. Note that 
        # tabs which have no result are always out of sync.
        tabs = [tab for tab in tabs if not tab.is_synced]

        if tabs:
            # First I have to ensure that each tab's input is valid
            gui_is_valid = True
            for tab in tabs:
                if not tab.validate_gui():
                    gui_is_valid = False
                    break
                
            if gui_is_valid:
                if right_neighbors:
                    # The next hurdle is that right neighbors are about to 
                    # have their results destroyed, and the user has to 
                    # confirm that that's OK.
                    run_approved = self._is_discard_results_ok()
                else:
                    # There are no right neighbors, so no results are going
                    # to get destroyed.
                    run_approved = True

                if run_approved:
                    # Trash the downstream results.
                    for tab in right_neighbors:
                        tab.clear_result()
                        
                    # Next I have to move the data from the GUI into the 
                    # objects.
                    for tab in tabs:
                        tab.accept_gui_data()
                
                    # Run 'em.
                    wx.SetCursor(wx.HOURGLASS_CURSOR)
                    for tab in tabs:
                        if not tab.run():
                            break

                    self.update_sync_status()
                
                    if not calling_tab:
                        # If no calling tab was specified, we ran everything
                        # up to and including the last tab. As a courtesy, 
                        # we make the last tab active. 
                        self.activate_tab(index=len(self.tabs) - 1)

                wx.SetCursor(wx.NullCursor)
        else:
            common_dialogs.message("These results are already up to date.")


    def save(self, save_as=False):
        self.update_sync_status()
        
        if not save_as and self.is_saved:
            # nothing to do
            save = False
        else:
            # If save_as == True, we always save. 
            save = True
            
        if save:
            # The GUI has to be valid in order for us to save.
            for i, tab in enumerate(self.tabs):
                valid = tab.validate_gui() if i else tab.validate_gui(True)

                if not valid:
                    save = False
                    break
            
        if save:
            # All tabs are valid
            
            # The subsequent code cares about whether or not tabs are in 
            # sync, but only the transformation tabs. We ignore the basic 
            # info tab.
            sync_status = [tab.is_synced for tab in self.tabs[1:]]
            
            if not all(sync_status):
                # At least one transformation tab is not in sync which means
                # the results are invalid. We don't save invalid results,
                # so we give the user the option to halt the save. To help 
                # them decide, we provide a list of tabs that aren't in sync.
                indices = [ ]
                for i, is_synced in enumerate(sync_status):
                    if not is_synced:
                        # The list of indices will be used in a message to
                        # the user. Unlike the list from which we're counting,
                        # the user sees the basic info tab in addition to the
                        # transformation tabs, and they also start counting 
                        # from 1 rather than 0. We add 2 to each index to
                        # so that it will make sense to the user.
                        indices.append(str(i + 2))

                # I convert indices from a list into a message fragment
                if len(indices) == 1:
                    indices = ("tab %s" % indices[0])
                    that_or_those = "that tab"
                else:
                    indices = "tabs " + ", ".join(indices[:-1]) + \
                              " and %s" % indices[-1:][0]
                    that_or_those = "those tabs"

                msg = "The results of %s are not current, so results "      \
                      "from %s will not be saved.\n\n"                      \
                      "Do you want to continue with the save?"                      
                msg %= (indices, that_or_those)
                          
                if wx.NO == common_dialogs.message(msg, "Save", common_dialogs.Q_YES_NO):
                    save = False

        if save and not save_as:
            referrers = self._db.fetch_pulse_project_referrers(self.pulse_project.id)
            referrers = [referrer[1] + '\n' for referrer in referrers]
            if referrers:
                save = False
                
                msg = "This project is now in use by the following pulse "  \
                      "sequences and cannot be altered -- \n\n"             \
                      "%s\n\n"                                              \
                      "Please change the project's name and select "        \
                      "'Save As' instead of save."
                msg %= "* ".join(referrers)
                common_dialogs.message(msg, "Save")
            
        if save:
            # Move the values from the GUI into the objects
            for tab in self.tabs:
                tab.accept_gui_data()

            if save_as:
                exists = False
            else:
                exists = self._db.exists_pulse_project_in_database(self.pulse_project.id)

            if not exists:
                # This is a new project.
                # Check to ensure that the name is unique. This has to
                # be done here where we control the event loop, and 
                # just before the project is written to the database. 
                # That's the only way we can guarantee the database
                # isn't modified before we get a chance to write our
                # uniquely-named project.
                if self._db.count_pulse_projects(name=self.pulse_project.name):
                    self.activate_tab(index=0)
                    msg = """Another project is already named "%s". """ \
                          """Please enter a unique name."""
                    msg = msg % self.pulse_project.name
                    common_dialogs.message(msg, "Save")
                    save = False
            
        if save:
            if save_as:
                # Give this project a new UUID and make it private.
                self.pulse_project.id = util_misc.uuid()
                self.pulse_project.is_public = False
            
            # Figure out which results should be skipped.
            skip_these = [tab.transform.result for tab in self.tabs[1:]
                                               if not tab.is_synced]

            if exists:
                self._db.replace_pulse_project(self.pulse_project, skip_these)
            else:
                self._db.insert_pulse_project(self.pulse_project, skip_these)
                
            self.tabs[0].update_uuid()
            
            # Now that the save is done, I & all of my tabs take note
            # of the state of the GUI so we know what the last save state
            # looks like.
            self._set_last_save()
            for tab in self.tabs:
                tab.on_save()


    def _update_oc_tab_labels(self):
        # OC tab labels are relatively complicated. Each has a number in the
        # form major.minor, where major corresponds to a given set of OC tabs
        # and minor represents a specific tab inside a set. In order to keep
        # the renumbering code sane, this relabels every OC tab it finds
        # and then calls update_sync_status() to fix any sync status info
        # it may have trashed.
        major = 0
        minor = 1
        for tab in self.tabs[1:]:
            if rfpulse_util.is_oc(tab):
                if minor == 1:
                    # This is a new set of OC tabs.
                    major += 1
                label = _OPTIMAL_CONTROL_TAB_TITLE + (" - %d.%d" % (major, minor))
                self.SetPageText(self.get_tab_index(tab), label)
                minor += 1
            else:
                minor = 1
                
        self.update_sync_status()


    def update_sync_status(self, tab=None):
        """Forces the notebook to update the sync status indicator on the
        tab labels. If a tab is passed, then updating starts with that tab
        and proceeds to the right. If no tab is passed, updating starts at
        the first tab (basic info).
        """
        # Get the index of the tab that changed
        i = self.get_tab_index(tab) if tab else 0
        # For this tab & each tab to the right, update the sync status
        # indicator
        for tab in self.tabs[i:]:
            tab_index = self.get_tab_index(tab)
            label = self.GetPageText(tab_index)
            if tab.is_synced:
                if label.startswith(_OUT_OF_SYNC_SYMBOL):
                    # Remove the edit symbol
                    label = label[len(_OUT_OF_SYNC_SYMBOL):]
                #else:
                    # label is already correct
            else:
                # not synced
                if not label.startswith(_OUT_OF_SYNC_SYMBOL):
                    # Add the edit symbol
                    label = _OUT_OF_SYNC_SYMBOL + label
                #else:
                    # label is already correct

            self.SetPageText(tab_index, label)
            
            # As a courtesy, I also let the tabs themselves know that sync
            # status may have changed. Most tabs don't care but at least
            # one kind does (optimal control).
            if hasattr(tab, "update_sync_status"):
                tab.update_sync_status()
                

