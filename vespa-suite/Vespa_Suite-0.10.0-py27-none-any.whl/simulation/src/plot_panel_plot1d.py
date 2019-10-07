# Python modules
from __future__ import division

# 3rd party modules
import numpy as np

# Our modules
import vespa.common.util.ppm as util_ppm
import vespa.common.wx_gravy.plot_panel as plot_panel
import vespa.common.wx_gravy.util as wx_util
from wx.lib.agw.floatspin import FloatSpin, EVT_FLOATSPIN, FS_LEFT, FS_RIGHT, FS_CENTRE, FS_READONLY,  FixedPoint

        

class PlotPanelPlot1d(plot_panel.PlotPanel):
    
    def __init__(self, parent, tab, prefs, **kwargs):
        
        plot_panel.PlotPanel.__init__( self, parent, **kwargs )

        # parent is the containing panel for this plot_panel, it is used
        # in resize events, the tab attribute is the AUI Notebook tab
        # that contains this plot_panel

        self.parent = parent
        self.tab    = tab
        self._prefs = prefs
        self.count  = 0
        
        self.set_color( (255,255,255) )


    # EVENT FUNCTIONS -----------------------------------------------
    
    def on_motion(self, xdata, ydata, val, bounds, iaxis):
        if self._prefs.xaxis_hertz:
            hz  = xdata
            ppm = util_ppm.pts2ppm(util_ppm.hz2pts(xdata,self.tab.freq1d),self.tab.freq1d)
        else:
            ppm = xdata
            hz  = util_ppm.pts2hz(util_ppm.ppm2pts(xdata,self.tab.freq1d),self.tab.freq1d)
        
        # if in a stack plot, determine which plot we are in so we can
        # display the appropriate value from the val list
        ydiff = bounds[3]
        if ydiff == 0: ydiff = 1
        iplot = int(len(val) * (ydata / ydiff))
        iplot = np.clip(iplot, 0, len(val)-1)
        
        # show metabolite name label
        metabolite_label = ''
        if self.tab.plot_labels:
            mode = self.tab.control.ChoiceDisplayMode.GetCurrentSelection()
            if mode == 0:
                metabolite_label = self.tab.plot_labels[iplot]
            else:
                metabolite_label = self.tab.plot_labels[-1]
            if self.tab.control.CheckSumPlots.IsChecked():
                metabolite_label = "Summed Metabolites"
                
        self.tab.statusbar.SetStatusText(( "PPM = "  +str(ppm)  ), 0)
        self.tab.statusbar.SetStatusText(( "Hz = "   +str(hz)   ), 1)
        self.tab.statusbar.SetStatusText(( "Value = "+str(val[iplot])), 2)   
        self.tab.statusbar.SetStatusText(( metabolite_label  ), 3)
        
            
    def on_zoom_select(self, xmin, xmax, val, ymin, ymax, reset=False):
        if self._prefs.xaxis_hertz:
            xmax = util_ppm.pts2ppm(util_ppm.hz2pts(xmax,self.tab.freq1d),self.tab.freq1d)
            xmin = util_ppm.pts2ppm(util_ppm.hz2pts(xmin,self.tab.freq1d),self.tab.freq1d)
            xmax = np.clip(xmax, self.tab.minppm, self.tab.maxppm)
            xmin = np.clip(xmin, self.tab.minppm, self.tab.maxppm)
        self.tab.control.FloatXaxisMin.SetValue(xmin)
        self.tab.control.FloatXaxisMax.SetValue(xmax)


    def on_zoom_motion(self, xmin, xmax, val, ymin, ymax):
        if self._prefs.xaxis_hertz:
            xmax = util_ppm.pts2ppm(util_ppm.hz2pts(xmax,self.tab.freq1d),self.tab.freq1d) 
            xmin = util_ppm.pts2ppm(util_ppm.hz2pts(xmin,self.tab.freq1d),self.tab.freq1d)
            xmax = np.clip(xmax, self.tab.minppm, self.tab.maxppm)
            xmin = np.clip(xmin, self.tab.minppm, self.tab.maxppm)
        
        self.tab.control.FloatXaxisMax.SetValue(FixedPoint(str(xmax),10))
        self.tab.control.FloatXaxisMin.SetValue(FixedPoint(str(xmin),10))
        
        delta_ppm = xmax - xmin
        delta_hz  = delta_ppm * self.tab.freq1d.frequency
        self.tab.statusbar.SetStatusText(( "Delta PPM = "  +str(delta_ppm)), 0)
        self.tab.statusbar.SetStatusText(( "Delta Hz = "   +str(delta_hz) ), 1)
        self.tab.statusbar.SetStatusText(( " "+str(delta_hz) ), 2)
        
        
    def on_refs_select(self, xmin, xmax, val):
        
        if self._prefs.xaxis_hertz:
            xmax = util_ppm.pts2ppm(util_ppm.hz2pts(xmax,self.tab.freq1d),self.tab.freq1d)
            xmin = util_ppm.pts2ppm(util_ppm.hz2pts(xmin,self.tab.freq1d),self.tab.freq1d)
            xmax = np.clip(xmax, self.tab.minppm, self.tab.maxppm)
            xmin = np.clip(xmin, self.tab.minppm, self.tab.maxppm)
        self.tab.control.FloatCursorMax.SetValue(FixedPoint(str(xmax),10))
        self.tab.control.FloatCursorMin.SetValue(FixedPoint(str(xmin),10))
        self.tab.plot_integral()
        self.tab.plot_contour()
        self.count = 0

    def on_refs_motion(self, xmin, xmax, val):

        if self._prefs.xaxis_hertz:
            xmax = util_ppm.pts2ppm(util_ppm.hz2pts(xmax,self.tab.freq1d),self.tab.freq1d) 
            xmin = util_ppm.pts2ppm(util_ppm.hz2pts(xmin,self.tab.freq1d),self.tab.freq1d)
            xmax = np.clip(xmax, self.tab.minppm, self.tab.maxppm)
            xmin = np.clip(xmin, self.tab.minppm, self.tab.maxppm)
        
        self.tab.control.FloatCursorMax.SetValue(FixedPoint(str(xmax),10))
        self.tab.control.FloatCursorMin.SetValue(FixedPoint(str(xmin),10))
        
        delta_ppm = xmax - xmin
        delta_hz  = delta_ppm * self.tab.freq1d.frequency
        self.tab.statusbar.SetStatusText(( "Delta PPM = "  +str(delta_ppm)), 0)
        self.tab.statusbar.SetStatusText(( "Delta Hz = "   +str(delta_hz) ), 1)
        self.tab.statusbar.SetStatusText(( " " ), 2)
        self.count += 1
        if (self.count % 2) == 0:
            self.tab.plot_integral()


    
