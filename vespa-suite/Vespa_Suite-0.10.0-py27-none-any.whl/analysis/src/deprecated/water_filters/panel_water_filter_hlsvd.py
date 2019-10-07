# Python imports
from __future__ import division

# 3rd party imports
import wx

# Vespa imports
import vespa.common.wx_gravy.util as wx_util
import auto_gui.water_hlsvd as water_hlsvd

from water_filter_hlsvd import FilterConstants


#-----------------------------------------------------------------------------

class PanelWaterFilterHlsvd(water_hlsvd.WaterHlsvdUI):
    
    def __init__(self, parent, tab, filter_):
        
        water_hlsvd.WaterHlsvdUI.__init__(self, parent)

        self._tab = tab
        self._filter = filter_
            
        self.initialize_controls()
        self.populate_controls()

        # We explicitly bind EVT_SPINCTRL *after* calling initialize_controls() 
        # in order to avoid SetRange side effects.
        # See http://trac.wxwidgets.org/ticket/14583
        self.Bind(wx.EVT_SPINCTRL, self.on_hlsvd_water_threshold, self.SpinThreshold)


    def initialize_controls(self):
        """ 
        This methods goes through the widgets and sets up certain sizes
        and constraints for those widgets. This method does not set the 
        value of any widget except insofar that it is outside a min/max
        range as those are being set up. 

        Use populate_controls() to set the values of the widgets from
        a data object.

        """
        wx_util.configure_spin(self.SpinThreshold, 60, None, None,
                               (FilterConstants.THRESH_MIN_HZ, 
                                FilterConstants.THRESH_MAX_HZ))


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
        self.SpinThreshold.SetValue(self._filter.threshold)
        self.CheckApplyThreshold.SetValue(self._filter.apply_as_water_filter)
               


                          
    ##### Event Handlers ###############################################
                          
   
    def on_hlsvd_water_threshold(self, event):
        self._filter.threshold = event.GetEventObject().GetValue()
        self._tab.process_and_plot()
    
    
    def on_hlsvd_apply_water_threshold(self, event):
        self._filter.apply_as_water_filter = event.GetEventObject().GetValue()
        self._tab.process_and_plot()




