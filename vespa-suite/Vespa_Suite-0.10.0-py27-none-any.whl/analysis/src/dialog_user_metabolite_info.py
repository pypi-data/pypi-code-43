# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import vespa.analysis.src.constants as constants
import auto_gui.dialog_user_metabolite_info as dialog_user_metabolite_info
import vespa.common.wx_gravy.util as wx_util

from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY


#------------------------------------------------------------------------------
# Note. GUI Architecture/Style
#
# Many of the GUI components in Vespa are designed using the WxGlade
# application to speed up development times. The GUI components are designed
# interactively and users can preview the resultant window/panel/dialog, but
# while event functions can be specified, only stub functions with those
# names are created. The WxGlade files (with *.wxg extensions) are stored in
# the 'wxglade' subdirectory. The ouput of their code generation are stored
# in the 'auto_gui' subdirectory.
#
# To used these GUI classes, each one is inherited into a unique 'vespa'
# class, where program specific initialization and other functionality are
# written.  Also, the original stub functions for widget event handlers are
# overloaded to provide program specific event handling.
#------------------------------------------------------------------------------


class DialogUserMetaboliteInfo(dialog_user_metabolite_info.MyDialog):
    """
    This dialog is used to organize user defined information about
    metabolites. This could be things like alternative spellings of
    metabolite names, literature values for concentration and an
    abbreviation for the full name of the metabolite.



    """
    def __init__(self, parent, dataset):
        if not parent:
            parent = wx.GetApp().GetTopWindow()

        dialog_user_metabolite_info.MyDialog.__init__(self, parent)

        self._dataset  = dataset
        self.parent    = parent

        #------------------------------
        # Initialize widget controls

        self._initialize_controls()

        self.Layout()
        self.Fit()

        self.SetSize( (580, 700) )

        self._improve_height()

        # Under Linux, the focus is elsewhere (?) unless I manually
        # set it to the list
        self.ButtonAddMetabolite.SetFocus()




    ##### Event Handlers ######################################################

    def on_select_all(self, event):
        self.dynamic_metinfo_list.select_all()

    def on_deselect_all(self, event):
        self.dynamic_metinfo_list.deselect_all()

    def on_add_metabolite(self, event):
        self.dynamic_metinfo_list.add_row()
        wx.CallAfter(self._improve_height)

    def on_remove_selected(self, event):
        self.dynamic_metinfo_list.remove_checked_rows()
        self.Layout()
        self.Refresh()


    def on_ok(self,event):
        # No changes made until user selects "OK" rather than "Cancel" so
        # here we update the metinfo object to reflect values in dialog

        # TODO, bjs, likely we need to do some error checking here for the
        # string widgets to ensure that there are no blank lines

        names, abbrs, spins, concs, t2 = self.dynamic_metinfo_list.get_values()

        metinfo = self._dataset.user_prior.metinfo

        metinfo.full_names     = names
        metinfo.abbreviations  = abbrs
        metinfo.spins          = spins
        metinfo.concentrations = concs
        metinfo.t2decays       = t2

        self.EndModal(True)


    def on_cancel(self, event):
        # Nothing to do here since changes are only written on "OK"
        self.EndModal(False)





    ##### Internal helper functions  ##########################################


    def _improve_height(self):
        # No matter what format the user chooses, we use a scrolled window to
        # contain the list of metabs because with a fixed-sized (non-scrolled)
        # panel, experiments that contain a lot of metabs (20+) can cause
        # this dialog to exceed the display height. However, the scrolled
        # window has its own problem: it doesn't size itself intelligently.
        # It always has the same (small) default height.
        #
        # So here we check to see if the scrolled window is actually scrolled;
        # i.e. it contains content that it can't completely display in its
        # current area. If so, we increase the dialog's height exactly
        # enough to allow the scrolled window to expand so that the user
        # doesn't have to scroll to see the contents.
        _, display_height = wx.GetDisplaySize()
        dialog_width, dialog_height = self.GetSize()

        # Compare virtual height with real height.
        # delta is how much bigger it needs to be to display all of its
        # content without scrolling.
        _, v_height = self.ScrolledWindowDynamicList.GetVirtualSize()
        _, r_height = self.ScrolledWindowDynamicList.GetClientSize()
        delta = v_height - r_height

        # max_delta is the max we can increase the dialog height before it
        # exceeds the display area. Note that wx reports the raw display
        # area without accounting for things like the Windows taskbar or the
        # OS X dock. Actual space available for use by applications may be
        # less. To account for this we subtract a fudge factor of 132 pixels.
        # This is pretty arbitrary, although on my Mac laptop the OS X dock
        # and the top menu occupy 132 pixels and the dock is huge relative
        # to the Windows taskbar and Gnome's similar thingies, so
        # hopefully this will be sufficient everywhere.
        max_delta = (display_height - dialog_height) - 132

        delta = min(delta, max_delta)

        if delta > 0:
            self.SetSize( (dialog_width, dialog_height + delta) )

        self.Center()


    def _initialize_controls(self):


        #----------------------------------------------------------------------
        # sets up other widgets in metabolite info dialog from values in the
        # metinfo object sent into the dialog initialization


        # The grid sizer for the metabs/mixed metabs list is marked with
        # a placeholder so that I can find it now (at runtime).
        placeholder = self.LabelMetaboliteListGridSizerPlaceholder
        self.MetaboliteGridSizer = placeholder.GetContainingSizer()
        parent = placeholder.GetParent()
        placeholder.Destroy()

        # Add headings to the first row of the grid sizer.
        self.MetaboliteGridSizer.Clear()
        self.MetaboliteGridSizer.SetRows(1)
        headings = (None, "Metabolite\nFull Name", "Abbreviation", "Number\nof Spins",
                    "Literature\nConcentration [mM]", "Literature\nT2 decay [ms]")

        for heading in headings:
            if heading:
                label = wx.StaticText(parent, label=heading, style=wx.ALIGN_CENTRE)
                self.MetaboliteGridSizer.Add(label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
            else:
                self.MetaboliteGridSizer.AddSpacer( 1 )

        # Columns 1 & 2 (the metab combobox and the metab abbreviation)
        # expand to fill whatever space is available.
        self.MetaboliteGridSizer.AddGrowableCol(1, 1)
        self.MetaboliteGridSizer.AddGrowableCol(2, 1)

        # Add widgets to dialog that wxGlade could not
        self.dynamic_metinfo_list = DynamicMetinfoList(self.ScrolledWindowDynamicList,
                                                       self.MetaboliteGridSizer,
                                                       self._dataset.user_prior.metinfo)

        # We add the OK & Cancel buttons dynamically so that they're in the
        # right order under OS X, GTK, Windows, etc.
        self.ButtonOk, self.ButtonCancel = \
                    wx_util.add_ok_cancel(self, self.LabelOkCancelPlaceholder,
                                          self.on_ok)











###############################################################################
##### Dynamic Output List Class ###############################################

class MetItem(object):
    def __init__(self, name='', abbr='', spins=1, conc=1.0, t2=250.0):

        self.name  = name
        self.abbr  = abbr
        self.spins = spins
        self.conc  = conc
        self.t2    = t2

class DynamicMetinfoList(object):

    def __init__(self, parent, metabolite_grid_sizer, metinfo):

        self.parent = parent

        # We follow the wx CamelCaps naming convention for this wx object.
        self.MetaboliteGridSizer = metabolite_grid_sizer

        self.new_index = 0
        self.list_lines = []
        self.items = []

        for i in range(len(metinfo.full_names)):
            item = MetItem( metinfo.full_names[i],
                            metinfo.abbreviations[i],
                            metinfo.spins[i],
                            metinfo.concentrations[i],
                            metinfo.t2decays[i])
            self.items.append(item)

        for item in self.items:
            self.add_row(item, notify_parent=False)
        self.parent.Layout()
        self.parent.Fit()


    def add_row(self, item=None, notify_parent=True):
        """
        Adds a row to the end of the list. Mixture, if given, should be
        a list of 2-tuples of (mixture name, scale).

        If notify_parent is True, the parent.Layout() and .Fit() are called after the row
        is added. Setting notify_parent=False when adding multiple rows (like during init)
        gives much better performance.
        """
        if item == None:
            self.new_index += 1
            name = 'new_entry'+str(self.new_index)
            abbr = 'new_abbr'+str(self.new_index)
            item = MetItem( name, abbr, 1, 1.0, 250.0 )
            self.items.append(item)

        # create widgets to go into the line
        check = wx.CheckBox(self.parent)
        name  = wx.TextCtrl(self.parent)
        abbr  = wx.TextCtrl(self.parent)
        # I want the text controls to expand horizontally as the dialog grows
        # so I set the wx.EXPAND flag on it when I add it to the sizer.
        # However, this also makes it expand vertically which makes it taller
        # than all of its neighbors.
        # To prevent that, I get its current height (before being added to the
        # sizer) and force that to be the max.
        _, height = abbr.GetSize()
        name.SetMaxSize( (-1, height) )
        abbr.SetMaxSize( (-1, height) )

        spins = wx.SpinCtrl(self.parent)
        conc  = FloatSpin(self.parent, agwStyle=FS_LEFT)
        t2    = FloatSpin(self.parent, agwStyle=FS_LEFT)

        # keep a copy of panel and widgets to access later
        line = { "checkbox"     : check,
                 "name"         : name,
                 "abbr"         : abbr,
                 "spins"        : spins,
                 "conc"         : conc,
                 "t2"           : t2,
               }

        # Add the controls to the grid sizer
        self.MetaboliteGridSizer.SetRows(self.MetaboliteGridSizer.GetRows()+1)

        self.MetaboliteGridSizer.Add(line["checkbox"], 0, wx.ALIGN_CENTER_VERTICAL)
        for key in ("name", "abbr", "spins", "conc", "t2"):
            self.MetaboliteGridSizer.Add(line[key], 0, wx.EXPAND)

        name.SetValue(item.name)
        abbr.SetValue(item.abbr)

        # Note. On these Spin and FloatSpin widgets, if the value you want to
        #    set is outside the wxGlade standard range, you should make the
        #    call to reset the range first and then set the value you want.
        spins.SetRange(1,20)
        spins.SetValue(item.spins)
        spins.SetMinSize(wx.Size(70, -1))

        conc.SetDigits(3)
        conc.SetIncrement(0.5)
        conc.SetRange(0.001,40000.0)
        conc.SetValue(item.conc)
        conc.SetMinSize(wx.Size(80, -1))

        t2.SetDigits(3)
        t2.SetIncrement(5.0)
        t2.SetRange(0.001,40000.0)
        t2.SetValue(item.t2)
        t2.SetMinSize(wx.Size(80, -1))


        self.list_lines.append(line)

        if notify_parent:
            # The dialog was resetting to the width of the four buttons after
            # adding a line. I do this trick to keep the width the same as
            # just before the Add button was selected.
            dialog_width, dialog_height = self.parent.GetSize()

            self.parent.Layout()
            self.parent.Fit()

            self.parent.SetSize((dialog_width, dialog_height))


    def remove_checked_rows(self):
        # gather indices of all checked boxes
        checklist = []

        for i, line in enumerate(self.list_lines):
            if line["checkbox"].GetValue():
                checklist.append(i)

        # remove in reverse order so we don't invalidate later
        # indices by removing the ones preceding them in the list
        checklist.reverse()

        for i in checklist:
            # Each line is a dict of controls + mixture info
            for item in self.list_lines[i].values():
                if hasattr(item, "Destroy"):
                    # It's a wx control
                    item.Destroy()

            del self.list_lines[i]

        # Reduce the # of rows in the grid sizer
        rows = self.MetaboliteGridSizer.GetRows()
        self.MetaboliteGridSizer.SetRows(rows - len(checklist))
        self.MetaboliteGridSizer.Layout()


    def get_values(self):
        items = [self.get_line_values(line) for line in self.list_lines]
        names = [item['name']  for item in items]
        abbrs = [item['abbr']  for item in items]
        spins = [item['spins'] for item in items]
        concs = [item['conc']  for item in items]
        t2    = [item['t2']    for item in items]

        return names, abbrs, spins, concs, t2


    def get_line_values(self, line):
        # Returns a dict containing the values of the controls in a line.
        return { "name"         : line["name"].GetValue(),
                 "abbr"         : line["abbr"].GetValue(),
                 "spins"        : line["spins"].GetValue(),
                 "conc"         : line["conc"].GetValue(),
                 "t2"           : line["t2"].GetValue(),
               }


    def select_all(self):
        for line in self.list_lines:
            line["checkbox"].SetValue(True)


    def deselect_all(self):
        for line in self.list_lines:
            line["checkbox"].SetValue(False)



