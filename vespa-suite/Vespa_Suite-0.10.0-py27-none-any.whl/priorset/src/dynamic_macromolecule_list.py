# Python modules
from __future__ import division


# 3rd party modules
import wx


# Our modules
import vespa.common.util.ppm as util_ppm
import vespa.common.wx_gravy.util as wx_util


from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY
from vespa.common.wx_gravy.widgets.floatspin_multiplier.floatspin_multiplier_base import FloatSpinMultiplier



##### Dynamic Metabolite List Class ###########################################

class DynamicMacromoleculeList(object):

    def __init__(self, grid_parent, tab, GridSizer, priorset):
        
        self.tab         = tab
        self.grid_parent = grid_parent
        self.priorset    = priorset
        self.list_lines  = []

        hpp         = priorset.hpp
        dim0        = priorset.dims[0]
        resppm      = priorset.resppm
        frequency   = priorset.frequency
        self.minppm = util_ppm.pts2ppm(dim0, priorset)
        self.maxppm = util_ppm.pts2ppm(   0, priorset)

        # We follow the wx CamelCaps naming convention for this wx object.
        self.GridSizer = GridSizer

        self.set_new_values()


    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    
    def __unicode__(self):
        lines = [ ]
        vals = self.get_values()
        for i,line in enumerate(vals):
            check = str(line['checkbox'])
            ppm   = "{:.4f}".format(str(line['ppm']))
            area  = "{:.4f}".format(str(line['area']))
            width = "{:.4f}".format(str(line['width']))

            lines.append("Line "+str(i)+", Check = "+check+", PPM = "+ppm+", Area = "+area+", Width [Hz] = "+width)

        # __unicode__() must return a Unicode object. In practice the code
        # above always generates Unicode, but we ensure it here.
        return u'\n'.join(lines)    


    def set_new_values(self):

        # Set up default values from priorset
        self.checks = self.priorset.mmol_flags
        self.ppms   = self.priorset.mmol_ppms
        self.areas  = self.priorset.mmol_areas
        self.widths = self.priorset.mmol_widths

        self.remove_all_rows()

        for check, ppm, area, width in \
            zip(self.checks, self.ppms, self.areas, self.widths):
            self.add_row(check, ppm, area, width)
        
    
    def add_row(self, _check, _ppm, _area, _width):
        """Adds a row to the end of the list."""

        # create widgets to go into the line
        list_line = { }

        checkbox = wx.CheckBox(self.grid_parent, -1, '')
        
        ppm   = FloatSpin(self.grid_parent, agwStyle=FS_LEFT)
        area  = FloatSpin(self.grid_parent, agwStyle=FS_LEFT)
        width = FloatSpin(self.grid_parent, agwStyle=FS_LEFT)
        
        # keep a copy of panel and widgets to access later
        line = { "checkbox":checkbox, "ppm":ppm, "area":area, "width":width}

        # Add the controls to the grid sizer
        self.GridSizer.Add(line["checkbox"], 0, wx.ALIGN_CENTER_VERTICAL)
        for key in ("ppm","area","width"):
            self.GridSizer.Add(line[key], 0, wx.ALIGN_CENTER_VERTICAL)

        # Configure the controls I just created

        checkbox.SetValue(_check)

        # All of the floatspins have the same size. 
        floatspin_size = wx.Size(90, -1)

        # Note. On these Spin and FloatSpin widgets, if the value you want to
        #    set is outside the wxGlade standard range, you should make the 
        #    call to reset the range first and then set the value you want.
        ppm.SetDigits(3)
        ppm.SetIncrement(0.05)
        ppm.SetRange(self.minppm,self.maxppm)
        ppm.SetValue(_ppm)
        ppm.SetMinSize(floatspin_size) 

        area.SetDigits(5)
        area.SetIncrement(0.05)
        area.SetRange(0.00001,10000.0)
        area.SetValue(_area)
        area.SetMinSize(floatspin_size) 

        width.SetDigits(3)
        width.SetIncrement(5.0)
        width.SetRange(0.00001,10000.0)
        width.SetValue(_width)
        width.SetMinSize(floatspin_size) 

        self.list_lines.append(line)

        self.grid_parent.Bind(wx.EVT_CHECKBOX, self.update_macromolecules, checkbox)
        self.grid_parent.Bind(EVT_FLOATSPIN,   self.update_macromolecules, ppm)
        self.grid_parent.Bind(EVT_FLOATSPIN,   self.update_macromolecules, area)
        self.grid_parent.Bind(EVT_FLOATSPIN,   self.update_macromolecules, width)

        self.tab.Layout()
        self.tab.PanelBaselineSignals.Layout()
        
        
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
            
        self.GridSizer.Layout()
        self.tab.PanelBaselineSignals.Layout()


    def remove_all_rows(self):
        self.select_all()
        self.remove_checked_rows()

        
    def get_values(self):
        return [self.get_line_values(line) for line in self.list_lines]


    def get_line_values(self, line):
        # Returns a dict containing  values of the controls in the line.
        return { "checkbox"   : line["checkbox"].GetValue(),
                 "ppm"        : line["ppm"].GetValue(),
                 "area"       : line["area"].GetValue(),
                 "width"      : line["width"].GetValue()
               }

    def select_all(self):
        for line in self.list_lines:
            line["checkbox"].SetValue(True)


    def deselect_all(self):
        for line in self.list_lines:
            line["checkbox"].SetValue(False)


    def update_macromolecules(self, event):
        self.tab.on_dynamic_macromolecule_list(None)
   
   
    def get_macromolecule_settings(self):
        
        checks  = []
        ppms    = []
        areas   = []
        widths  = []
        
        vals = self.get_values()

        for i,line in enumerate(vals):
            if line['checkbox']:
                checks.append(True)
            else:
                checks.append(False)
            ppms.append(line['ppm'])   
            areas.append(line['area'])
            widths.append(line['width'])

        return checks, ppms, areas, widths

    
