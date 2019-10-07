# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import vespa.analysis.src.constants as constants
import vespa.analysis.src.mrs_dataset as mrs_dataset
import auto_gui.dataset_browser as dataset_browser
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.util as wx_util

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


class DialogDatasetBrowser(dataset_browser.MyDialog):
    """
    Opens a dialog that allows the user to select a dataset from all of the
    datasets open in tabs in Analysis.

    After the dialog closes, the dialog's dataset attribute contains the 
    selected dataset, or None if the user hits cancel.
    
    The datasets param passed to __init__() should be a dict of dataset
    names (tab names) mapping to datasets.
    """

    def __init__(self, datasets, parent=None, omit_self=None):
        if not parent:
            parent = wx.GetApp().GetTopWindow()

        dataset_browser.MyDialog.__init__(self, parent)

        _sort_datasets = [(name,datasets[name]) for name in sorted(datasets.keys())]
        
        if omit_self and isinstance(omit_self, mrs_dataset.Dataset):
            _all_datasets  = [item for item in _sort_datasets if item[1].id != omit_self.id]
        else:
            _all_datasets = _sort_datasets
        
        # self._all_datasets is where I stash the dict of all available 
        # datasets from which the user can choose.
        # self.dataset contains the dataset that the user choose and
        # is only relevant as this dialog closes.
        self._all_datasets = _all_datasets
        self.dataset = None

        # We add the Open & Cancel buttons dynamically so that they're in  
        # the right order under OS X, GTK, Windows, etc.
        self.ButtonOK, _ = wx_util.add_ok_cancel(self, 
                                                 self.LabelOkCancelPlaceholder, 
                                                 self.on_ok)
        self._populate_list()

        wx_util.set_font_to_monospace(self.Listbox)
        
        self.SetSize( (700, 350) )

        self.Layout()

        self.Center()

        self.Listbox.SetFocus()


    ########################    Event Handlers    #################


    def on_list_double_click(self, event):
        self.on_ok()
        

    def on_list_selection(self, event):
        # Enable OK if something selected.
        self.ButtonOK.Enable( (len(self.Listbox.GetSelections()) > 0) )


    def on_ok(self, event=None):
        # This handler is sometimes called programmatically, in which case
        # event is None.
        i = self.Listbox.GetSelection()
        
        # It shouldn't be possible to click OK without something selected, 
        # but just in case...
        if i != wx.NOT_FOUND:
            self.dataset = self.Listbox.GetClientData(i)
                                                       
        self.Close()


    ########################    "Private" Methods    #################
        
    def _populate_list(self):
        wx.SetCursor(wx.HOURGLASS_CURSOR)

        # Reset controls
        self.ButtonOK.Enable(False)
        self.Listbox.Clear()
        
        # FIXME PS - the dataset sorting code doesn't work as intended. The 
        # problem is that "Dataset10" sorts *before* "Dataset9". That can
        # be fixed but alphabetical probably isn't the best sort order 
        # anyway. A better choice would be to mimic the order of the tabs
        # as they're open in the notebook, but that will require some
        # help from NotebookDatasets.
        
        # Each list item is [tab name]: [data source] where the data source is
        # the first listed in the dataset. 
        # name_length is the length of the shortest tab name (e.g. "Dataset4")
        # plus a bit of padding. When constructing the listbox entries, I
        # right justify each dataset name so that they line up regardless of
        # how many characters are in the name, e.g. --
        #     Dataset1: blah blah blah 
        #    Dataset52: blah blah blah 
        #   Dataset999: blah blah blah 
        name_length = 0 
        for item in self._all_datasets:
            dataset = item[1]
            name    = item[0]
            if not name_length:
                # name_length isn't yet calculated -- do so now.
                name_length = len(name) + 2

            source = dataset.blocks["raw"].data_source
            s = "%s: %s" % (name.rjust(name_length), source)            
            self.Listbox.Append(s)
            
            self.Listbox.SetClientData((self.Listbox.GetCount() - 1), dataset)

#         for name in sorted(self._all_datasets.keys()):
#             dataset = self._all_datasets[name]
# 
#             if not name_length:
#                 # name_length isn't yet calculated -- do so now.
#                 name_length = len(name) + 2
# 
#             source = dataset.blocks["raw"].data_source
#             s = "%s: %s" % (name.rjust(name_length), source)            
#             self.Listbox.Append(s)
#             
#             self.Listbox.SetClientData((self.Listbox.GetCount() - 1), dataset)
            
        wx.SetCursor(wx.NullCursor)

