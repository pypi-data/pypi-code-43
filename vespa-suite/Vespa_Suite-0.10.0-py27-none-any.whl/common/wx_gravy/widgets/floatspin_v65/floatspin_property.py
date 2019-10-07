from __future__ import division

import wx

# misc is a wxGlade thing
import misc

from widget_properties import Property
from widget_properties import _activator
from widget_properties import _mangle
from widget_properties import _label_initial_width
import vespa.common.wx_gravy.util as wx_util

if wx_util.is_wx_floatspin_ok():
    from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN
else:
    from vespa.common.wx_gravy.widgets.floatspin.floatspin import FloatSpin, EVT_FLOATSPIN
    

class FloatSpinProperty(Property, _activator):
    """\
    Properties associated to a float spin control.
    """
    def __init__(self, owner, name, parent=None, can_disable=False,
                 r=None, enabled=False):
        # r = range of the spin (min, max)
        Property.__init__(self, owner, name, parent)
        self.can_disable = can_disable
        _activator.__init__(self)
        if can_disable: self.toggle_active(enabled)
        self.val_range = r
        self.panel = None
        if parent is not None: self.display(parent)
        self.val = owner[name][0]()

    def display(self, parent):
        """\
        Actually builds the spin control to set the value of the property
        interactively
        """
        self.id = wx.NewId()
        if self.val_range is None: self.val_range = (0, 1000)
        label = wx.StaticText(parent, -1, _mangle(self.name), size=(_label_initial_width, -1))
        label.SetToolTip(wx.ToolTip(_mangle(self.name)))
        if self.can_disable:
            self._enabler = wx.CheckBox(parent, self.id+1, '', size=(1, -1))
        self.spin = FloatSpin(parent, self.id, increment=0.001, min_val=self.val_range[0], max_val=self.val_range[1])
        val = float(self.owner[self.name][0]())
        if not val:
            self.spin.SetValue(1) # needed for GTK to display a '0'
        self.spin.SetValue(val) #int(self.owner[self.name][0]()))
        if self.can_disable:
            wx.EVT_CHECKBOX(self._enabler, self.id+1,
                         lambda event: self.toggle_active(event.IsChecked()))
            self.spin.Enable(self.is_active())
            self._enabler.SetValue(self.is_active())
            self._target = self.spin
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(label, 2, wx.ALL|wx.ALIGN_CENTER, 3)
        if getattr(self, '_enabler', None) is not None:
            sizer.Add(self._enabler, 1, wx.ALL|wx.ALIGN_CENTER, 3)
            option = 4
        else:
            option = 5
        sizer.Add(self.spin, option, wx.ALL|wx.ALIGN_CENTER, 3)
        self.panel = sizer
        self.bind_event(self.on_change_val)

    def OnFloatSpin(self, event):
        self.on_change_val(event)

    def bind_event(self, function):
        def func_2(event):
            if self.is_active():
                misc.wxCallAfter(function, event)
            event.Skip()
        wx.EVT_KILL_FOCUS(self.spin, func_2)
        self.spin.Bind( EVT_FLOATSPIN, self.OnFloatSpin)
        if wx.Platform == '__WXMAC__':
            wx.EVT_TEXT(self.spin, self.spin.GetId(), func_2)
            wx.EVT_SPINCTRL(self.spin, self.spin.GetId(), func_2)

    def get_value(self):
        try: return self.spin.GetValue()
        except AttributeError: return self.val

    def set_value(self, value):
        self.val = float(value)
        try: self.spin.SetValue(float(value))
        except AttributeError: pass

    def set_range(self, min_v, max_v):
        self.val_range = (min_v, max_v)
        try: self.spin.SetRange(min_v, max_v)
        except AttributeError: pass

    def write(self, outfile, tabs):
        if self.is_active(): 
            Property.write(self, outfile, tabs)

 
