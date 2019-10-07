# Python modules
from __future__ import division
import copy

# 3rd party modules
import wx
import numpy as np

# Our modules
import vespa.analysis.src.mrs_dataset as mrs_dataset
import vespa.analysis.src.constants as constants
import vespa.analysis.src.prefs as prefs_module
import vespa.analysis.src.plot_panel_user_prior as plot_panel_user_prior
#import dynamic_list_user_prior
import vespa.common.util.misc as util_misc
import vespa.common.wx_gravy.util as wx_util
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import auto_gui.dialog_user_prior as dialog_user_prior
import vespa.common.util.ppm as util_ppm
from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY
from vespa.common.wx_gravy.widgets.floatspin_multiplier.floatspin_multiplier_base import FloatSpinMultiplier


# _NEW_LINE_DEFAULTS are the default values used when the user adds a line.
_NEW_LINE_DEFAULTS = [True, 4.7, 1.0, 0.0, 5.0, 1.0, 1.0, 1.0, 1.0] 


def _paired_event(obj_min, obj_max):
        val_min = obj_min.GetValue()
        val_max = obj_max.GetValue()
        pmin = min(val_min, val_max)
        pmax = max(val_min, val_max)
        obj_min.SetValue(pmin)
        obj_max.SetValue(pmax)
        return pmin, pmax


class DialogUserPrior(dialog_user_prior.MyDialog):
    """Displays user prior info and allows the user to edit it. Returns True
    if the user changed settings, False otherwise. Changes are written to the
    dataset by this dialog, so the return code is informative only. The caller
    doesn't need to react to it (except perhaps to update the GUI).
    """
    def __init__(self, parent, dataset):
        dialog_user_prior.MyDialog.__init__(self, parent)

        self._dataset = dataset

        # As the user alters widget values in this dialog, it writes them
        # directly to the UserPrior object in the dataset. If the user hits
        # cancel on this dialog, we want to be able to restore the original
        # UserPrior settings, so we make a copy of the object here.
        self._original_user_prior = copy.deepcopy(dataset.user_prior)

        # self._lines caches the result of self._update_spectrum().
        self._lines = None

        # The plot panel expects a Prefs object, but those kinds of objects are
        # pretty intimately tied with the View menu. From this modal dialog, 
        # the View menu is inaccessible. Instead we cobble together a Prefs
        # object with some hardcoded values. There's no way for the user to
        # change them and they're not written anywhere when the dialog exits.
        # You can have any preferences you want, as long as they're ours!
        class _UserPriorPrefs(prefs_module.AnalysisPrefs):
            def __init__(self):
                self.bgcolor = "white"
                self.line_color_imaginary = "red"
                self.line_color_magnitude = "purple"
                self.line_color_real = "black"
                self.zero_line_color = "goldenrod"
                self.zero_line_style = "solid"
                self.line_width = 1.0
                self.line_color_individual = "green"
                self.line_color_summed = "black"
                self.zero_line_bottom = False
                self.zero_line_middle = True
                self.zero_line_top = False
                self.zero_line_show = True
                self.xaxis_ppm = True
                self.xaxis_hertz = False
                self.xaxis_show = True

        self._prefs = _UserPriorPrefs()


        # We add the Open & Cancel buttons dynamically so that they're in the
        # right order under OS X, GTK, Windows, etc.
        self.ButtonOpen, self.ButtonCancel = \
            wx_util.add_ok_cancel(self, self.LabelOKCancelPlaceholder,
                                  self.on_ok, self.on_cancel)

        self.SetSize( (1000, 600) )

        self.Layout()
        
        self.Center()

        # Plotting is disabled during some of init. That's because the plot
        # isn't ready to plot, but the population of some controls 
        # (e.g. dynamic list) fires their respective change event which 
        # triggers a call to plot(). This is a Windows-specific bug.
        # In any case, skipping some calls to plot() will speed things up. =)
        self._plotting_enabled = False
        
        self._initialize_controls()
        self._populate_controls()

        self._plotting_enabled = True

        # The plot panel needs to init the scale to a sane value after data has
        # been passed to the view. _scale_intialized tracks whether or not this
        # has happened. It's intialized to False, set to True once the scale 
        # is intialized and never changes thereafter. 
        self._scale_intialized = False
        self._update_spectrum()

        # Set up the canvas
        self._plot()

        # Sash position is normally stored in self._prefs (see above); here
        # we just hardcode it.
        wx.CallAfter(self.WindowSplitter.SetSashPosition, 500, True)



    #################     Event Handlers   ##################

    def on_ok(self, event):
        # Nothing to do here since changes were written to the dataset as
        # they happened. 
        self.EndModal(True)


    def on_cancel(self, event):
        # Restore original settings before exiting.
        self._dataset.user_prior = self._original_user_prior

        self.EndModal(False)


    #################     Internal Helpers    ##################
    def _initialize_controls(self):
        """ 
        This methods goes through the widgets and sets up certain sizes
        and constraints for those widgets. This method does not set the 
        value of any widget except insofar that it is outside a min/max
        range as those are being set up. 
        
        Use populate_controls() to set the values of the widgets from
        a data object.
        """

        # calculate a few useful values
        
        dim0, dim1, dim2, dim3 = self._dataset.spectral_dims
        sw      = self._dataset.sw
        maxppm  = util_ppm.pts2ppm(0, self._dataset)
        minppm  = util_ppm.pts2ppm(dim0-1, self._dataset)
        ppmlim  = (minppm, maxppm)
        dim0lim = (0, dim0 - 1)
        
        
        # The many spin controls on various tabs need configuration of 
        # their size, # of digits displayed, increment and min/max. 
        wx_util.configure_spin(self.FloatAutoB0RangeStart,     70, 3, 0.1, ppmlim)
        wx_util.configure_spin(self.FloatAutoB0RangeEnd,       70, 3, 0.1, ppmlim)
        wx_util.configure_spin(self.FloatAutoPhase0RangeStart, 70, 3, 0.1, ppmlim)
        wx_util.configure_spin(self.FloatAutoPhase0RangeEnd,   70, 3, 0.1, ppmlim)
        wx_util.configure_spin(self.FloatAutoPhase1RangeStart, 70, 3, 0.1, ppmlim)
        wx_util.configure_spin(self.FloatAutoPhase1RangeEnd,   70, 3, 0.1, ppmlim)
        wx_util.configure_spin(self.FloatAutoPhase1Pivot,      70, 3, 0.1, ppmlim)

        self.view = \
               plot_panel_user_prior.PlotPanelUserPrior(self.PanelView, 
                                                        naxes=2,
                                                        reversex=True,
                                                        zoom='span', 
                                                        reference=True,
                                                        middle=True,
                                                        do_zoom_select_event=True,
                                                        do_zoom_motion_event=True,
                                                        do_refs_select_event=True,
                                                        do_refs_motion_event=True,
                                                        do_middle_select_event=False,
                                                        do_middle_motion_event=False,
                                                        do_scroll_event=True,
                                                        props_zoom=dict(alpha=0.2, facecolor='yellow'),
                                                        props_cursor=dict(alpha=0.2, facecolor='gray'), 
                                                        xscale_bump=0.0,
                                                        yscale_bump=0.05,
                                                        data = [],
                                                        prefs=self._prefs, 
                                                        dataset=self._dataset,
                                                        )
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelView.SetSizer(sizer)
        self.view.Fit()    


        #------------------------------------------------------------
        # set up dynamic list
        
        # The list grid sizer is marked so we can find it at run-time
        self.LinesGridSizer = self.LabelPriorLinesPlaceholder.GetContainingSizer()
        parent = self.LabelPriorLinesPlaceholder.GetParent()
        self.LabelPriorLinesPlaceholder.Destroy()
       
        # Add headings to the first row of the grid sizer.
        self.LinesGridSizer.Clear()
        self.LinesGridSizer.SetRows(1)
        headings = (None, "Peak Center\n[ppm]", "Peak Area", 
                    "Peak Phase\n[deg]", "Linewidth\n[Hz]")
        
        for heading in headings:
            if heading:
                label = wx.StaticText(parent, label=heading, style=wx.ALIGN_CENTRE)
                self.LinesGridSizer.Add(label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
            else:
                self.LinesGridSizer.AddSpacer( 1 )

        self._dynamic_user_prior_list = DynamicList1(self.PanelLines,
                                                     self.PanelPrior,
                                                     self.LinesGridSizer,
                                                     self._dataset,
                                                     self.on_dynamic_user_prior_list)


    def _populate_controls(self):
        """ 
        Populates the widgets with relevant values from the data object. 
        It's meant to be called when a new data object is loaded.
        
        This function trusts that the data object it is given doesn't violate
        any rules. Whatever is in the data object gets slapped into the 
        controls, no questions asked. 
        
        This function is, however, smart enough to enable and disable 
        other widgets depending on settings.
        """
        dataset = self._dataset

        #------------------------------------------------------------
        # set up Basic widgets
        user_prior = self._dataset.user_prior
        
        self.FloatAutoB0RangeStart.SetValue(    user_prior.auto_b0_range_start)
        self.FloatAutoB0RangeEnd.SetValue(      user_prior.auto_b0_range_end)
        self.FloatAutoPhase0RangeStart.SetValue(user_prior.auto_phase0_range_start)
        self.FloatAutoPhase0RangeEnd.SetValue(  user_prior.auto_phase0_range_end)
        self.FloatAutoPhase1RangeStart.SetValue(user_prior.auto_phase1_range_start)
        self.FloatAutoPhase1RangeEnd.SetValue(  user_prior.auto_phase1_range_end)
        self.FloatAutoPhase1Pivot.SetValue(     user_prior.auto_phase1_pivot)

        # we do not match old settings to any new ones in this widget
        self._dynamic_user_prior_list.set_new_values()
        lines = self._dynamic_user_prior_list.lines
        user_prior.spectrum.set_values(lines)
        

    def _plot(self):

        if self._plotting_enabled:

            # Get auto_prior spectral arrays (indiv and summed)
            lines = np.array(self._lines)
            line_sum = self._dataset.user_prior.spectrum.summed
            
            data1 = {'data' : lines, 
                     'line_color_real'      : self._prefs.line_color_individual,
                     'line_color_imaginary' : self._prefs.line_color_individual,
                     'line_color_magnitude' : self._prefs.line_color_individual }
            
            data2 = {'data' : line_sum,
                     'line_color_real'      : self._prefs.line_color_summed,
                     'line_color_imaginary' : self._prefs.line_color_summed,
                     'line_color_magnitude' : self._prefs.line_color_summed }
    
            data = [[data1], [data2]]
            self.view.set_data(data)
            self.view.update(set_scale=not self._scale_intialized)
    
            if not self._scale_intialized:
                self._scale_intialized = True
    
            # Calculate the new area after phasing
            area, rms = self.view.calculate_area()
            area = area[1]
            rms = rms[1]


    def _update_spectrum(self):
        # updates my cached version of the spectrum. calculate_spectrum() is
        # a little expensive so I don't want to call it more often than
        # I need to.
        self._lines = self._dataset.user_prior.spectrum.calculate_spectrum(self._dataset)


##############################    Event Handlers


########  Handlers for line controls
    def on_add_line(self, event):
        self._dynamic_user_prior_list.add_row(_NEW_LINE_DEFAULTS, update=True)
        # The call above fires on_dynamic_user_prior_list() so I don't need
        # to do anything else here.


    def on_delete_line(self, event): 
        self._dynamic_user_prior_list.remove_checked_rows()
        # The call above fires on_dynamic_user_prior_list() so I don't need
        # to do anything else here.


    def on_restore_defaults(self, event): 
        self._dataset.user_prior.spectrum.reset_to_default()
        self._dynamic_user_prior_list.set_new_values()
        self.on_dynamic_user_prior_list()


    def on_dynamic_user_prior_list(self, event=None):
        # This is a fudged event called from the actual event that occurs 
        # inside the dynamic list class but its also invoked programmatically
        # (i.e. by our code, not by wx). In the latter case, event is None.

        # This setup will allow up to call plot() or whatever without too 
        # much complexity. 
        lines = self._dynamic_user_prior_list.lines
        self._dataset.user_prior.spectrum.set_values(lines)
        self._update_spectrum()

        self._plot()


####### Handlers for algorithm params controls
    def on_auto_b0_range_start(self, event): 
        min_, max_ = _paired_event(self.FloatAutoB0RangeStart,
                                 self.FloatAutoB0RangeEnd)
        self._dataset.user_prior.auto_b0_range_start = min_
        self._dataset.user_prior.auto_b0_range_end = max_
        self._plot()


    def on_auto_b0_range_end(self, event): 
        min_, max_ = _paired_event(self.FloatAutoB0RangeStart,
                                 self.FloatAutoB0RangeEnd)
        self._dataset.user_prior.auto_b0_range_start = min_
        self._dataset.user_prior.auto_b0_range_end = max_
        self._plot()


    def on_auto_phase0_range_start(self, event):
        min_, max_ = _paired_event(self.FloatAutoPhase0RangeStart,
                                 self.FloatAutoPhase0RangeEnd)
        self._dataset.user_prior.auto_phase0_range_start = min_
        self._dataset.user_prior.auto_phase0_range_end = max_
        self._plot()
        

    def on_auto_phase0_range_end(self, event): 
        min_, max_ = _paired_event(self.FloatAutoPhase0RangeStart,
                                 self.FloatAutoPhase0RangeEnd)
        self._dataset.user_prior.auto_phase0_range_start = min_
        self._dataset.user_prior.auto_phase0_range_end = max_
        self._plot()
        

    def on_auto_phase1_range_start(self, event): 
        min_, max_ = _paired_event(self.FloatAutoPhase1RangeStart,
                                 self.FloatAutoPhase1RangeEnd)
        self._dataset.user_prior.auto_phase1_range_start = min_ 
        self._dataset.user_prior.auto_phase1_range_end = max_
        self._plot()


    def on_auto_phase1_range_end(self, event): 
        min_, max_ = _paired_event(self.FloatAutoPhase1RangeStart,
                                 self.FloatAutoPhase1RangeEnd)
        self._dataset.user_prior.auto_phase1_range_start = min_
        self._dataset.user_prior.auto_phase1_range_end = max_
        self._plot()
        

    def on_auto_phase1_pivot(self, event): 
        val = event.GetEventObject().GetValue()
        self._dataset.user_prior.auto_phase1_pivot = val
        self._plot()


#---------------------------------------------------------------------------------------------------

class DynamicList1(object):

    def __init__(self, PanelLines, PanelPrior, GridSizer, dataset, external_event_handler):
        
        self._dataset = dataset
        self._PanelLines = PanelLines
        self._PanelPrior = PanelPrior
        
        self.external_event_handler = external_event_handler
        
        # We follow the wx CamelCaps naming convention for this wx object.
        self._GridSizer = GridSizer
                
        self._list_lines = []


    @property
    def lines(self):
        return [self._get_line_values(line) for line in self._list_lines]

        
    def set_new_values(self, previous=None):
        if not previous:
            previous = self._dataset.user_prior.spectrum.get_rows()
            
        self.select_all()
        self.remove_checked_rows()

        for row_vals in previous:
            self.add_row(row_vals)

    
    def add_row(self, row_vals, update=False):
        '''
        Adds a row to the end of the list. 
        
        '''
        maxppm = util_ppm.pts2ppm(0, self._dataset)
        minppm = util_ppm.pts2ppm(self._dataset.spectral_dims[0]-1, self._dataset)

        self._GridSizer.SetRows(self._GridSizer.GetRows() + 1)

        # create widgets to go into the line
        list_line = { }

        checkbox = wx.CheckBox(self._PanelLines)
        
        value_ppm    = FloatSpin(self._PanelLines, agwStyle=FS_LEFT)
        value_area   = FloatSpin(self._PanelLines, agwStyle=FS_LEFT)
        value_phase  = FloatSpin(self._PanelLines, agwStyle=FS_LEFT)
        value_lwhz   = FloatSpin(self._PanelLines, agwStyle=FS_LEFT)
        
        # keep a copy of panel and widgets to access later
        line = { "check"        : checkbox, 
                 "value_ppm"    : value_ppm, 
                 "value_area"   : value_area, 
                 "value_phase"  : value_phase,
                 "value_lwhz"   : value_lwhz, 
               }

        # Add the controls to the grid sizer
        self._GridSizer.Add(line["check"], 0, wx.ALIGN_CENTER_VERTICAL)
        for key in ("value_ppm", "value_area", "value_phase", "value_lwhz"):
            self._GridSizer.Add(line[key], 0, wx.EXPAND)

        # Configure the controls I just created

        # All of the floatspins have the same size. 
        floatspin_size = wx.Size(70, -1)

        # Note. On these Spin and FloatSpin widgets, if the value you want to
        #    set is outside the wxGlade standard range, you should make the 
        #    call to reset the range first and then set the value you want.

        wx_util.configure_spin(value_ppm,  70, 2, 0.05,(minppm,maxppm))
        wx_util.configure_spin(value_area, 70, 3, 0.1, (0.001,100000.0))
        wx_util.configure_spin(value_phase,70, 1, 5.0, (-360,360))
        wx_util.configure_spin(value_lwhz, 70, 2, 1.0, (0.001,10000.0))

        checkbox.SetValue(row_vals[0])
        value_ppm.SetValue(row_vals[1])
        value_area.SetValue(row_vals[2])
        value_phase.SetValue(row_vals[3])
        value_lwhz.SetValue(row_vals[4])

        self._list_lines.append(line)

        # only need to update if a metabolite is added/removed from basis
        self._PanelLines.Bind(wx.EVT_CHECKBOX, self.event_handler, checkbox)
        self._PanelLines.Bind(EVT_FLOATSPIN, self.event_handler, value_ppm)
        self._PanelLines.Bind(EVT_FLOATSPIN, self.event_handler, value_area)
        self._PanelLines.Bind(EVT_FLOATSPIN, self.event_handler, value_phase)
        self._PanelLines.Bind(EVT_FLOATSPIN, self.event_handler, value_lwhz)

        self._PanelPrior.Layout()  

        if update:
            self.event_handler()
        
        
    def remove_checked_rows(self):
        # gather indices of all checked boxes
        checklist = []
        
        for i, line in enumerate(self._list_lines):
            if line["check"].GetValue():
                checklist.append(i)
        
        # remove in reverse order so we don't invalidate later
        # indices by removing the ones preceding them in the list
        checklist.reverse()
        
        for i in checklist:
            # Each line is a dict of controls + mixture info
            for item in self._list_lines[i].values():
                if hasattr(item, "Destroy"):
                    # It's a wx control
                    item.Destroy()
                
            del self._list_lines[i]
            
        # Reduce the # of rows in the grid sizer
        rows = self._GridSizer.GetRows()
        self._GridSizer.SetRows(rows - len(checklist))
        self._GridSizer.Layout()
        self._PanelPrior.Layout()        
        self.event_handler()


    def select_all(self):
        for line in self._list_lines:
            line["check"].SetValue(True)


    def deselect_all(self):
        for line in self._list_lines:
            line["check"].SetValue(False)
            
            
    def event_handler(self, event=None):
        self.external_event_handler(event)


################   Private Methods

    def _get_line_values(self, line):
        # Returns a dict containing  values of the controls in the line.
        return { "check"        : line["check"].GetValue(),
                 "value_ppm"    : line["value_ppm"].GetValue(),
                 "value_area"   : line["value_area"].GetValue(),
                 "value_phase"  : line["value_phase"].GetValue(),
                 "value_lwhz"   : line["value_lwhz"].GetValue(),
                 "limit_ppm"    : 0.0,
                 "limit_area"   : 0.0,
                 "limit_phase"  : 0.0,
                 "limit_lwhz"   : 0.0
               }






########################################################################
class MyForm(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self, dataset):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Testing the Dialog")
        panel = wx.Panel(self, wx.ID_ANY)
 
        self.statusbar = self.CreateStatusBar(4, 0)
        self.statusbar.SetStatusText("Ready")

        self.dataset = dataset
 
        # create the buttons and bindings
        DlgBtn = wx.Button(panel, label="Show Dialog")
        DlgBtn.Bind(wx.EVT_BUTTON, self.onDialog)
 
        # put the buttons in a sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(DlgBtn, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizer(sizer)
 
    #----------------------------------------------------------------------
    def onDialog(self, event):
        """
        Show the Dialog 
        """
        dialog = DialogUserPrior(self, self.dataset)
        
        code = dialog.ShowModal() 
        
        if code == wx.ID_OK:
            print "User hit OK"
        elif code == wx.CANCEL:
            print "User Cancelled"

        
        dialog.Destroy()
 

 
#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    
    dataset = mrs_dataset.Dataset()
    
    app = wx.App(False)
    frame = MyForm(dataset)
    frame.Show()
    app.MainLoop()