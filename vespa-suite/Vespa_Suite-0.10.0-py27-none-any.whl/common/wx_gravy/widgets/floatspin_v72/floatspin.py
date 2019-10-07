from __future__ import division
"""\
FloatSpin objects

@copyright: 2016-     Brian J. Soher
@license: MIT (see LICENSE.txt) - THIS PROGRAM COMES WITH NO WARRANTY
"""

import wx

from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY

from edit_windows import ManagedBase, EditStylesMixin
from tree import Tree
import common
import compat
import config
from widget_properties import *
from ordereddict import OrderedDict


class EditFloatSpin(ManagedBase, EditStylesMixin):
    """\
    Class to handle wxSpinCtrl objects
    """

    def __init__(self, name, parent, id, sizer, pos, property_window,
                 show=True):

        # Initialise parent classes
        ManagedBase.__init__(self, name, 'FloatSpin', parent, id, sizer, pos,
                             property_window, show=show)
        EditStylesMixin.__init__(self)

        self.extra_names = ['FS_LEFT', 'FS_RIGHT', 'FS_CENTRE', 'FS_READONLY']
        self.extra_pos   = ( FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY  )
        self.extra = FS_LEFT
        self.extra_dict = OrderedDict()
        self.extra_dict[_('Extra-style')] = self.extra_names
        
        # initialize instance variables
        self.value = 0.0
        self.range = (0.0, 100.0)  # Default values in wxSpinCtrl constructor.
        self.digits = 3
        self.increment = 1.0
        if config.preferences.default_border:
            self.border = config.preferences.default_border_size
            self.flag = wx.ALL

        # initialise properties remaining staff
        prop = self.properties
        self.access_functions['style'] = (self.get_style, self.set_style)
        self.access_functions['value'] = (self.get_value, self.set_value)
        self.access_functions['range'] = (self.get_range, self.set_range)
        self.access_functions['digits'] = (self.get_digits, self.set_digits)
        self.access_functions['increment'] = (self.get_increment, self.set_increment)
        self.access_functions['extrastyle'] = (self.get_extra, self.set_extra)
        prop['style']       = CheckListProperty(self, 'style', self.widget_writer)
        prop['range']       = TextProperty(self,  'range', None, can_disable=True, label=_("range"))
        prop['value']       = FloatProperty(self, 'value', None, can_disable=True, label=_("value"))
        prop['digits']       = SpinProperty(self,  'digits', None, can_disable=True, label=_("digits"))
        prop['increment']   = FloatProperty(self, 'increment', None, can_disable=True, label=_("increment"))
        prop['extrastyle']  = CheckListProperty(self, 'extrastyle', parent=None, styles=self.extra_dict)


    def create_widget(self):
        self.widget = FloatSpin(self.parent.widget, self.id, 
                                min_val=self.range[0], max_val=self.range[1],
                                value=self.value, increment=self.increment,
                                digits=self.digits)

    def create_properties(self):
        ManagedBase.create_properties(self)
        panel = wx.ScrolledWindow(self.notebook, -1, style=wx.TAB_TRAVERSAL)
        szr = wx.BoxSizer(wx.VERTICAL)
        prop = self.properties
        prop['range'].display(panel)
        prop['value'].display(panel)
        prop['digits'].display(panel)
        prop['increment'].display(panel)
        prop['extrastyle'].display(panel)
        prop['style'].display(panel)
        szr.Add(prop['range'].panel, 0, wx.EXPAND)
        szr.Add(prop['value'].panel, 0, wx.EXPAND)
        szr.Add(prop['digits'].panel, 0, wx.EXPAND)
        szr.Add(prop['increment'].panel, 0, wx.EXPAND)
        szr.Add(prop['extrastyle'].panel, 0, wx.EXPAND)
        szr.Add(prop['style'].panel, 0, wx.EXPAND)
        panel.SetAutoLayout(True)
        compat.SizerItem_SetSizer(panel, szr)
        szr.Fit(panel)
        self.notebook.AddPage(panel, 'Widget')


    def get_extra(self):
        retval = [0] * len(self.extra_pos)
        try:
            for i in range(len(self.extra_pos)):
                if self.extra & self.extra_pos[i]:
                    retval[i] = 1
        except AttributeError:
            pass
        return retval

    def set_extra(self, value):
        value = self.properties['extrastyle'].prepare_value(value)
        self.extra = 0
        for v in range(len(value)):
            if value[v]:
                self.extra |= self.extra_pos[v]

    def get_digits(self):
        return self.digits

    def set_digits(self, value):
        value = int(value)
        if self.digits != value:
            self.digits = value
            if self.widget:
                self.widget.SetValue(self.digits)
                
    def get_increment(self):
        return self.increment

    def set_increment(self, value):
        value = float(value)
        if self.increment != value:
            self.increment = value
            if self.widget:
                self.widget.SetValue(self.increment)                

    def get_range(self):
        # we cannot return self.range since this would become a "(0, 100)"
        # string, and we don't want the parents
        return "%s, %s" % self.range

    def set_range(self, val):
        try:
            min_v, max_v = map(float, val.split(','))
        except:
            self.properties['range'].set_value(self.get_range())
        else:
            self.range = (min_v, max_v)
            self.properties['value'].set_range(min_v, max_v)
            if self.widget:
                self.widget.SetRange(min_v, max_v)

    def get_value(self):
        return self.value

    def set_value(self, value):
        value = float(value)
        if self.value != value:
            self.value = value
            if self.widget:
                self.widget.SetValue(self.value)

# end of class EditFloatSpin


class _activator:
    """\
    A utility class which provides:
    - a method L{toggle_active()} to (de)activate a Property of a widget
    - a method L{toggle_blocked()} to (un)block enabler of a Property of a widget
    - a method L{prepare_activator()} to assign enabler and target with settings
    
    @ivar _enabler: CheckBox which provides the ability to Enable/Disable
                    the Property
    @type _enabler: CheckBox
    @ivar _target:  Object to enable/disable
    @type _target:  A single widget or a list of widgets
    """

    def __init__(self, target=None, enabler=None, omitter=None):
        """\
        @param target:  Object to Enable/Disable
        @type target:   A single widget or a list of widgets
        @param enabler: CheckBox which provides the ability to Enable/Disable
                        the Property
        @type enabler:  CheckBox
        """
        self._target = target
        self._enabler = enabler
        if self._enabler:
            self._blocked = self.is_blocked()
        else:
            self._blocked = False
        if self.is_blocked():
            self.toggle_active(False, False)
        elif self._target:
            self._active = self.is_active()
        else:
            self._active = True
        self.set_omitter(omitter)

    def toggle_active(self, active=None, refresh=True):
        """\
        Toggle the activation state
        """
        # active is not given when refreshing target and enabler
        if active and self.is_blocked():
            self._active = False  # blocked is always inactive
                                  # (security measure)
        elif active is not None:
            self._active = active
        if not self._target:
            return
        try:
            for target in self._target:
                target.Enable(self._active)
        except TypeError:
            self._target.Enable(self._active)
        if self._active and self._omitter:
            try:
                value = self.owner.access_functions[self.name][0]()
                self.owner.access_functions[self.name][1](value)
            except:
                pass
        if refresh:
            try:
                common.app_tree.app.saved = False
            except AttributeError:
                pass  # why does this happen on win at startup?
        try:
            self._enabler.SetValue(self._active)
        except AttributeError:
            pass

    def is_active(self):
        """\
        Return True for a non-blocked and enabled / active widget.
        """
        if self.is_blocked():
            return False
        if self._target:
            try:
                return self._target[0].IsEnabled()
            except TypeError:
                return self._target.IsEnabled()
        return self._active

    def toggle_blocked(self, blocked=None):
        """\
        Toggle the blocked state
        """
        if blocked is not None:
            self._blocked = blocked
        if self._enabler:
            self._enabler.Enable(not self._blocked)
        if self.is_blocked():  # deactivate blocked
            self.toggle_active(False, False)
        elif self._enabler:  # refresh activity of target and value of enabler
            self.toggle_active(refresh=False)
        elif not getattr(self, 'can_disable', None) and self._omitter:
            # enable blocked widget (that would be always active) without
            # _enabler
            if self.owner.get_property_blocking(self._omitter):
                self.toggle_active(True, False)

    def is_blocked(self):
        """\
        Return True for a non-enabled or blocked widget.
        """
        if self._enabler:
            return not self._enabler.IsEnabled()
        return self._blocked

    def prepare_activator(self, enabler=None, target=None):
        if target:
            self._target = target
            if enabler:
                self._enabler = enabler
        self.toggle_blocked()

    def set_omitter(self, omitter):
        self._omitter = omitter
        if omitter:
            self.owner.set_property_blocking(omitter, self.name)

    def remove_omitter(self):
        if self._omitter:
            self.owner.remove_property_blocking(self._omitter, self.name)

# end of class _activator


class FloatProperty(Property, _activator):
    """\
    Properties associated to a float spin control.
    """

    def __init__(self, owner, name, parent=None, can_disable=False,
                 r=None, enabled=False, immediate=False, label=None,
                 blocked=False, omitter=None):
        # r = range of the spin (min, max)
        Property.__init__(self, owner, name, parent, label=label)
        self.can_disable = can_disable
        self.immediate = immediate  # if true, changes to this property have an
                                    # immediate effect (instead of waiting the
                                    # focus change...)
        _activator.__init__(self, omitter=omitter)
        if can_disable:
            self.toggle_active(enabled)
            self.toggle_blocked(blocked)
        if r is not None:
            self.val_range = (r[0], max(r[0], r[1]))
        else:
            self.val_range = None
        self.panel = None
        self.val = owner[name][0]()
        if parent is not None:
            self.display(parent)

    def display(self, parent):
        """\
        Actually builds the spin control to set the value of the property
        interactively
        """
        if self.val_range is None:
            self.val_range = (0.0, 1000.0)
        lbl = getattr(self, 'label', None)
        if lbl is None:
            lbl = self._mangle(self.dispName)
        label = wx.lib.stattext.GenStaticText(
            parent, wx.ID_ANY, lbl, size=(config.label_initial_width, -1))
        self.spin = FloatSpin(parent, wx.ID_ANY, min_val=self.val_range[0], 
                              max_val=self.val_range[1])
        val = float(self.owner[self.name][0]())
        if not val:
            self.spin.SetValue(1)  # needed for GTK to display a '0'
        self.spin.SetValue(val)
        enabler = None
        if self.can_disable:
            enabler = wx.CheckBox(parent, wx.ID_ANY, '', size=(1, -1))
            enabler.Bind(wx.EVT_CHECKBOX,
                         lambda event: self.toggle_active(event.IsChecked()))
        self._tooltip_widgets = [label, self.spin, enabler]
        self.set_tooltip()
        self.prepare_activator(enabler, self.spin)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(label, 2, wx.ALL | wx.ALIGN_CENTER, 3)
        if getattr(self, '_enabler', None) is not None:
            sizer.Add(self._enabler, 1, wx.ALL | wx.ALIGN_CENTER, 3)
            option = 4
        else:
            option = 5
        sizer.Add(self.spin, option, wx.ALL | wx.ALIGN_CENTER, 3)
        self.panel = sizer
        self.bind_event(self.on_change_val)

    def bind_event(self, function):
        def func_2(event):
            if self.spin.IsBeingDeleted():
                return

            if self.is_active():
                function(event)
            event.Skip()
        #self.spin.Bind(wx.EVT_KILL_FOCUS, func_2)
        self.spin.Bind(EVT_FLOATSPIN, func_2)
        if wx.Platform == '__WXMAC__' or self.immediate:
            self.spin.Bind(wx.EVT_TEXT, func_2)
            self.spin.Bind(wx.EVT_FLOATSPIN, func_2)

    def get_value(self):
        try:
            return self.spin.GetValue()
        except AttributeError:
            return self.val

    def set_value(self, value):
        self.val = float(value)
        try:
            self.spin.SetValue(float(value))
        except AttributeError:
            pass

    def set_range(self, min_v, max_v):
        self.val_range = (min_v, max(min_v, max_v))
        try:
            self.spin.SetRange(min_v, max_v)
        except AttributeError:
            pass

    def write(self, outfile, tabs=0):
        if self.is_active():
            Property.write(self, outfile, tabs)

# end of class FloatProperty



def builder(parent, sizer, pos, number=[1]):
    """\
    factory function for EditFloatSpin objects.
    """
    name = 'float_spin_%d' % number[0]
    while common.app_tree.has_name(name):
        number[0] += 1
        name = 'float_spin_%d' % number[0]
    text = EditFloatSpin(name, parent, wx.NewId(), sizer, pos,
                        common.property_panel)
    node = Tree.Node(text)
    text.node = node
    text.show_widget(True)
    common.app_tree.insert(node, sizer.node, pos - 1)


def xml_builder(attrs, parent, sizer, sizeritem, pos=None):
    """\
    factory function to build EditFloatSpin objects from a XML file
    """
    from xml_parse import XmlParsingError
    try:
        name = attrs['name']
    except KeyError:
        raise XmlParsingError(_("'name' attribute missing"))
    if sizer is None or sizeritem is None:
        raise XmlParsingError(_("sizer or sizeritem object cannot be None"))
    text = EditFloatSpin(name, parent, wx.NewId(), sizer, pos,
                        common.property_panel)
    sizer.set_item(text.pos, option=sizeritem.option, flag=sizeritem.flag,
                   border=sizeritem.border)
    node = Tree.Node(text)
    text.node = node
    if pos is None:
        common.app_tree.add(node, sizer.node)
    else:
        common.app_tree.insert(node, sizer.node, pos - 1)
    return text


def initialize():
    """\
    initialization function for the module: returns a wxBitmapButton to be
    added to the main palette.
    """
    import os
    common.widgets['EditFloatSpin'] = builder
    common.widgets_from_xml['EditFloatSpin'] = xml_builder

    return common.make_object_button('EditFloatSpin', os.path.join(os.path.dirname(__file__), 'floatspin.xpm'))
