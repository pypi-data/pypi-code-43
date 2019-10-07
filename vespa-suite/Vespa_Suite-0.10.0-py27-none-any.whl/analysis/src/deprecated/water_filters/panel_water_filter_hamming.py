# Python imports
from __future__ import division

# 3rd party imports
import wx

# Vespa imports
import vespa.common.wx_gravy.util as wx_util
import auto_gui.water_hamming as water_hamming
from water_filter_fir import FilterConstants



#-----------------------------------------------------------------------------

class PanelWaterFilterHamming(water_hamming.WaterHammingUI):
    
    def __init__(self, parent, tab, filter_):
        
        water_hamming.WaterHammingUI.__init__(self, parent)

        self._tab = tab
        self._filter = filter_
            
        self.initialize_controls()
        self.populate_controls()

        # We explicitly bind EVT_SPINCTRL *after* calling initialize_controls() 
        # in order to avoid SetRange side effects.
        # See http://trac.wxwidgets.org/ticket/14583
        self.Bind(wx.EVT_SPINCTRL, self.on_water_length, self.SpinLength)
        self.Bind(wx.EVT_SPINCTRL, self.on_extrapolate_value, self.SpinExtrap)


    def initialize_controls(self):
        """ 
        This methods goes through the widgets and sets up certain sizes
        and constraints for those widgets. This method does not set the 
        value of any widget except insofar that it is outside a min/max
        range as those are being set up. 

        Use populate_controls() to set the values of the widgets from
        a data object.

        """
        # Here I set up the spin controls. Some are standard wxSpinCtrls and
        # some are floatspins (from wx.lib.agw.floatspin or wx_common).
        # For some of our variables, the default increment of +/-1 makes 
        # sense, but that's not true for all of them. 
        # These increments are arbitrary and expressed only once in the code
        # below. If you don't like them, feel free to change them.
        wx_util.configure_spin(self.SpinLength, 60, None, None,
                               (FilterConstants.LENGTH_MIN, 
                                FilterConstants.LENGTH_MAX))

        wx_util.configure_spin(self.SpinExtrap, 60, None, None,
                               (FilterConstants.EXTRAPOLATION_POINTS_MIN, 
                                FilterConstants.EXTRAPOLATION_POINTS_MAX))


    def populate_controls(self):
        """ 
        Populates the widgets with relevant values from the data object. 
        It's meant to be called when a new data object is loaded.
        
        This function trusts that the data object it is given doesn't violate
        any rules. Whatever is in the data object gets slapped into the 
        controls, no questions asked. 
        
        This function is, however, smart enough to enable and disable 
        other widgets depending on settings.

        """
        self.SpinLength.SetValue(self._filter.length)

        # Set values in Extrapolation Methods ComboBox.
        self.ComboExtrap.SetItems(FilterConstants.EXTRAPOLATION_ALL)
        if not self.ComboExtrap.SetStringSelection(self._filter.extrapolation_method):
            # Ooops, the string wasn't in the list.
            self.ComboExtrap.SetStringSelection(FilterConstants.EXTRAPOLATION_DEFAULT)
        
        self.SpinExtrap.SetValue(self._filter.extrapolation_point_count)
        self.SpinExtrap.Enable(self._filter.extrapolation_method == 'AR Model')
               


                          
    ##### Event Handlers ###############################################
                          
    def on_water_length(self, event):
        val = event.GetEventObject().GetValue()
        # FIXME PS - In IDL_Vespa, this value was required to always be odd 
        # so that the algorithm would have the same number of points to 
        # evaluate on either side of the "middle" of the window.
        # We're continuing this restriction although we don't know if it still
        # applies here because we're using different algorithms.    
        if not (val % 2):
            # I have to adjust the value to make it odd. I make sure that I 
            # adjust it in the direction of the user's change (i.e. make it
            # bigger or smaller).
            val += (1 if (val > self._filter.length) else -1)

        # Note that if I set the value to something out of range, the control 
        # will clip it for me.
        event.GetEventObject().SetValue(val)
        self._filter.length = val
        self._tab.process_and_plot()
    
    
    def on_extrapolate_method(self, event):
        val = event.GetEventObject().GetStringSelection()
        self.SpinExtrap.Enable(val == 'AR Model')
        self._filter.extrapolation_method = val
        self._tab.process_and_plot()
    
    
    def on_extrapolate_value(self, event):
        self._filter.extrapolation_point_count = event.GetEventObject().GetValue()
        self._tab.process_and_plot()




