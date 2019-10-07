# Python modules
from __future__ import division

# 3rd party modules
import wx

# Our modules
import vespa.common.wx_gravy.util as wx_util
if wx_util.is_wx_floatspin_ok():
    import wx.lib.agw.floatspin as floatspin
else:
    import vespa.common.wx_gravy.widgets.floatspin.floatspin as floatspin


class FloatSpinMultiplier(floatspin.FloatSpin):
    def __init__(self, *args, **keywords):
        
        floatspin.FloatSpin.__init__(self, *args, **keywords)
        
        self.multiplier = 1
        
        self.Bind(wx.EVT_SPIN_UP, self.on_spin_up)
        self.Bind(wx.EVT_SPIN_DOWN, self.on_spin_down)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_spin_wheel)

        
    __doc = """The smallest increment is based on the number of digits and
    ensures that a spin up/down event will change the number displayed, 
    even if only by 1 in the least significant decimal place.
    """
    def __get_minimum_increment(self): 
        return 1 / (10 ** self.GetDigits())
    def __set_minimum_increment(self, value): 
        raise AttributeError

    minimum_increment = property(__get_minimum_increment, __set_minimum_increment)
    
    
    def _calculate_increment(self, increase = True):
        value = abs(self.GetValue())
                
        if self.multiplier == 1:
            # When the multiplier is 1 (the default), the increment works out
            # to be zero. In that case this control behaves like a normal 
            # spin control with increment = 1
            increment = 1 if increase else -1
        else:
            multiplier = self.multiplier if increase else (1 / self.multiplier)
            
            increment = (value * multiplier) - value
            
        return max(abs(increment), self.minimum_increment)
    
    
    def on_spin_up(self, event):
        increment = self._calculate_increment()
        
        floatspin.FloatSpin.SetIncrement(self, increment)

        floatspin.FloatSpin.OnSpinUp(self, event)


    def on_spin_down(self, event):
        increment = self._calculate_increment(False)
        
        floatspin.FloatSpin.SetIncrement(self, increment)

        floatspin.FloatSpin.OnSpinDown(self, event)


    def on_spin_wheel(self, event):
        increment = self._calculate_increment(event.GetWheelRotation() > 0)
        
        floatspin.FloatSpin.SetIncrement(self, increment)

        floatspin.FloatSpin.OnMouseWheel(self, event)

