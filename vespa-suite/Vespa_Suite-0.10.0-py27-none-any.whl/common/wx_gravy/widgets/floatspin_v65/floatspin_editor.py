from __future__ import division

import wx

import common, misc
from edit_windows import ManagedBase
from tree import Tree
from widget_properties import *
import edit_widget
from floatspin_property import FloatSpinProperty
import vespa.common.wx_gravy.util as wx_util
if wx_util.is_wx_floatspin_ok():
    from wx.lib.agw.floatspin import FloatSpin, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY
else:
    from vespa.common.wx_gravy.widgets.floatspin.floatspin import FloatSpin, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY
    



class EditFloatSpin(edit_widget.EditWidget):

    events = ["EVT_FLOATSPIN",]

    def __init__(self, name, parent, id, label, sizer, pos,
                 property_window, show=True):
        """\
        Class to handle FloatSpin objects
        """
        self.style = 0
        self.extrastyle = FS_LEFT
        self.value = 0.0
        self.range = ( 0.0, 100.0)
        self.increment = 1.0
        self.digits = 0


        self.extrastyle_labels = ( "#section#Extra-Style", "FS_LEFT", "FS_RIGHT", "FS_CENTRE", "FS_READONLY" )
        self.extrastyle_pos = ( FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY  )


        self.style_labels = ('#section#Style', 'wxSP_ARROW_KEYS', 'wxSP_WRAP',
                        'wxTE_PROCESS_ENTER',
                        'wxTE_PROCESS_TAB', 'wxTE_MULTILINE', 'wxTE_PASSWORD',
                        'wxTE_READONLY', 'wxHSCROLL', 'wxTE_RICH',
                        'wxTE_RICH2', 'wxTE_AUTO_URL', 'wxTE_NOHIDESEL',
                        'wxTE_CENTRE', 'wxTE_RIGHT', 'wxTE_LINEWRAP',
                        'wxTE_WORDWRAP', 'wxNO_BORDER')
        self.style_pos = (wx.SP_ARROW_KEYS, wx.SP_WRAP,
                          wx.TE_PROCESS_ENTER, wx.TE_PROCESS_TAB,
                          wx.TE_MULTILINE,wx.TE_PASSWORD, wx.TE_READONLY,
                          wx.HSCROLL, wx.TE_RICH, wx.TE_RICH2, wx.TE_AUTO_URL,
                          wx.TE_NOHIDESEL, wx.TE_CENTRE, wx.TE_RIGHT,
                          wx.TE_LINEWRAP, wx.TE_WORDWRAP, wx.NO_BORDER) 

        edit_widget.EditWidget.__init__(self, name, 'FloatSpin', parent, id,
                                        label, sizer, pos,
                                        property_window, show=show)
    # -- Properties -----------------------------------------------------------


    def get_style(self):
        retval = [0] * len(self.style_pos)
        try:
            for i in range(len(self.style_pos)):
                if self.style & self.style_pos[i]:
                    retval[i] = 1
        except AttributeError:
            pass
        return retval

    def set_style(self, value):
        value = self.properties['style'].prepare_value(value)
        self.style = 0
        for v in range(len(value)):
            if value[v]:
                self.style |= self.style_pos[v]

    def get_style_widget(self):
        return CheckListProperty(self, 'style', None, self.style_labels) 


    def get_extrastyle(self):
        retval = [0] * len(self.extrastyle_pos)
        try:
            for i in range(len(self.extrastyle_pos)):
                if self.extrastyle & self.extrastyle_pos[i]:
                    retval[i] = 1
        except AttributeError:
            pass
        return retval

    def set_extrastyle(self, value):
        value = self.properties['extrastyle'].prepare_value(value)
        self.extrastyle = 0
        for v in range(len(value)):
            if value[v]:
                self.extrastyle |= self.extrastyle_pos[v]

    def get_extrastyle_widget(self):
        return CheckListProperty(self, 'extrastyle', None, self.extrastyle_labels)


    def get_range(self):
        # we cannot return self.range since this would become a "(0, 100)"
        # string, and we don't want the parens
        return "%s, %s" % self.range

    def set_range(self, val):
        try: min_v, max_v = map(float, val.split(','))
        except: self.properties['range'].set_value(self.get_range())
        else:
            self.range = (min_v, max_v)
            self.properties['value'].set_range(min_v, max_v)
            if self.widget: self.widget.SetRange(min_v, max_v)

    def get_range_widget(self):
        return TextProperty(self, 'range', None, can_disable=True)


    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = float(value) 

    def get_value_widget(self):            
        return FloatSpinProperty(self, 'value', None, can_disable=True)


    def get_increment(self):
        return self.increment

    def set_increment(self, increment):
        self.increment = float(increment)  

    def get_increment_widget(self):            
        return FloatSpinProperty(self, 'increment', None, can_disable=True)




    def get_digits(self):
        return self.digits

    def set_digits(self, digits):
        self.digits = int(digits)   
        
    def get_digits_widget(self):
        return SpinProperty(self, 'digits', None, can_disable=True)

        
    #--------------------------------------------------------------------------

    def create_widget(self):
        self.widget = FloatSpin(self.parent.widget, self.id, style=self.style, agwStyle=self.extrastyle)
        self.widget.SetValue(self.get_value())
        self.widget.SetIncrement(self.get_increment())
        self.widget.SetDigits(self.get_digits())
        
# end of class EditFloatSpin


def builder(parent, sizer, pos, number=[1]):
    """\
    factory function for EditFloatSpin objects.
    """
    label = edit_widget.increment_label('floatspin', number)
    floatSpinWin = EditFloatSpin(label, parent, wx.NewId(), misc._encode(label), sizer, pos, common.property_panel)
    edit_widget.add_widget_node(floatSpinWin, sizer, pos, option=1, flag=wx.EXPAND)


def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory to build EditFloatSpin objects from an xml file
    """
    label = edit_widget.get_label_from_xml(attrs)
    floatSpinWin = EditFloatSpin(label, parent, wx.NewId(), misc._encode(label), sizer, pos, common.property_panel, show=False)
    edit_widget.add_widget_node(floatSpinWin, sizer, pos, from_xml=True)
    return floatSpinWin


def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    import os
    return edit_widget.initialize(
        'EditFloatSpin', builder, xml_builder,
        os.path.join(os.path.dirname(__file__), 'floatspin.xpm'))
