# Python modules
from __future__ import division
import copy


# 3rd party modules
import wx
import numpy as np

# Our modules
import constants
import dialog_visualize_resolution
import auto_gui.visualize as visualize
import vespa.common.util.ppm as util_ppm
import vespa.common.wx_gravy.util as common_wx_util

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


class TabVisualize(visualize.VisualizeUI):

    def __init__(self, parent, db, experiment, etab, prefs):

        visualize.VisualizeUI.__init__(self, parent)

        self.db = db
        self.experiment = experiment
        self.etab = etab
        self._prefs = prefs

        # Grab key events so I can look for Ctrl/Cmd+A ==> select all
        self.ListPlotMetabolites.Bind(wx.EVT_KEY_DOWN, self.on_key_down)


    def populate_metabolite_list(self):
        """Clears & repopulates the list of metabs."""
        self.ListPlotMetabolites.Clear()
        metabolites = [self.db.fetch_metabolite(metabolite.id) \
                                for metabolite in self.experiment.metabolites]

        names = [metabolite.name for metabolite in metabolites]
        self.ListPlotMetabolites.SetItems(names)


    # EVENT HANDLER Redefinitions -----------------------------------

    def on_key_down(self, event):
        if common_wx_util.is_select_all(event):
            names = [metabolite.name for metabolite in self.etab.experiment.metabolites]
            for item in names:
                self.ListPlotMetabolites.SetStringSelection(item)
            self.etab.plot_canvas(reset_history=True)
            self.etab.plot_integral()
        else:
            # Don't eat the keystroke! If we eat it, users can't use the
            # keyboard to move around in the list or select items.
            event.Skip()


    def on_display_mode(self, event):
        self.etab.plot_canvas(reset_history=True)
        self.etab.plot_integral()

    def on_xaxis_max(self, event):
        self.update_widget_ranges()
        xmax = self.FloatXaxisMax.GetValue()
        xmin = self.FloatXaxisMin.GetValue()
        if self._prefs.xaxis_hertz:
            freq1d = self.etab.freq1d
            xmax = util_ppm.pts2hz(util_ppm.ppm2pts(xmax,freq1d),freq1d)
            xmin = util_ppm.pts2hz(util_ppm.ppm2pts(xmin,freq1d),freq1d)
        self.etab.plot1d_axes.set_xlim((xmax,xmin))
        self.etab.plot1d.canvas.draw()

    def on_xaxis_min(self, event):
        self.update_widget_ranges()
        xmax = self.FloatXaxisMax.GetValue()
        xmin = self.FloatXaxisMin.GetValue()
        if self._prefs.xaxis_hertz:
            freq1d = self.etab.freq1d
            xmax = util_ppm.pts2hz(util_ppm.ppm2pts(xmax,freq1d),freq1d)
            xmin = util_ppm.pts2hz(util_ppm.ppm2pts(xmin,freq1d),freq1d)
        self.etab.plot1d_axes.set_xlim((xmax,xmin))
        self.etab.plot1d.canvas.draw()

    def on_cursor_max(self, event):
        self.update_widget_ranges()
        xmax = self.FloatCursorMax.GetValue()
        xmin = self.FloatCursorMin.GetValue()
        if self._prefs.xaxis_hertz:
            freq1d = self.etab.freq1d
            xmax = util_ppm.pts2hz(util_ppm.ppm2pts(xmax,freq1d),freq1d)
            xmin = util_ppm.pts2hz(util_ppm.ppm2pts(xmin,freq1d),freq1d)
        if self.etab.plot1d.refs != None:
            self.etab.plot1d.refs.set_span(xmin,xmax)
            self.etab.plot1d.canvas.draw()

    def on_cursor_min(self, event):
        self.update_widget_ranges()
        xmax = self.FloatCursorMax.GetValue()
        xmin = self.FloatCursorMin.GetValue()
        if self._prefs.xaxis_hertz:
            freq1d = self.etab.freq1d
            xmax = util_ppm.pts2hz(util_ppm.ppm2pts(xmax,freq1d),freq1d)
            xmin = util_ppm.pts2hz(util_ppm.ppm2pts(xmin,freq1d),freq1d)
        if self.etab.plot1d.refs != None:
            self.etab.plot1d.refs.set_span(xmin,xmax)
            self.etab.plot1d.canvas.draw()


    def on_index(self, event, dim):
         # This pseudo event handler is called by the on_indexN() event
         # handlers (below)
        index = event.GetEventObject().GetValue() - 1
        control = getattr(self, "LabelIndex%dValue" % dim)
        # Under Windows/wx 3.x, SetRange() has a side effect of firing one of these events with
        # index == -1 which raises an IndexError if we don't discard/ignore it.
        if index != -1:
            control.SetLabel(str(self.experiment.dims[dim - 1][index]))
        self.etab.plot_canvas()
        self.etab.plot_integral()

    def on_index1(self, event):
        self.on_index(event, 1)

    def on_index2(self, event):
        self.on_index(event, 2)

    def on_index3(self, event):
        self.on_index(event, 3)

    def on_metabolites(self, event):
        self.etab.plot_canvas(reset_history=True)
        self.etab.plot_integral()
        self.etab.plot_contour()

    def on_sum_plots(self, event):
        self.etab.plot_canvas(reset_history=True)

    def on_grayscale(self, event):
        checked = event.GetEventObject().IsChecked()
        self._prefs.contour_grayscale = checked
        self.etab.plot_contour(recalc=False)

    def on_contour_levels(self, event):
        self._prefs.contour_levels = event.GetEventObject().GetValue()
        self.etab.plot_contour(recalc=False)

    def on_contour_mode(self, event):
        index = event.GetEventObject().GetCurrentSelection()

        # Contour plots involve two dimensions, and at least one of the
        # dims must have a length > 1. The code below verifies that that's
        # true. If it's not, we attempt to find and select a contour plot
        # that's valid.
        dim_lengths = [len(dim) for dim in self.experiment.dims]
        if index == 0:
            if (dim_lengths[0] == 1) and (dim_lengths[1] == 1):
                if (dim_lengths[2] != 1):
                    index = 1
                else:
                    self.etab.plot_contour(reset=True)
                    return
        elif index == 1:
            if (dim_lengths[0] == 1) and (dim_lengths[2] == 1):
                if (dim_lengths[1] != 1):
                    index = 0
                else:
                    self.etab.plot_contour(reset=True)
                    return
        elif index == 2:
            if (dim_lengths[1] == 1) and (dim_lengths[2] == 1):
                if (dim_lengths[0] != 1):
                    index = 0
                else:
                    self.etab.plot_contour(reset=True)
                    return
        self._prefs.contour_mode = index
        event.GetEventObject().SetSelection(index)
        self.etab.plot_contour()

    def on_linewidth(self, event):
        self.etab.linewidth = event.GetEventObject().GetValue()
        self.etab.set_apodization()
        self.etab.plot_canvas()
        self.etab.plot_integral()

    def on_resolution(self, event):

        pts = self.etab.freq1d.dims[0]
        sw  = self.etab.freq1d.sw
        dialog = dialog_visualize_resolution.DialogVisualizeResolution(self, sw, pts)
        if dialog.ShowModal() == wx.ID_OK:

            sw  = dialog.sweep_width
            pts = int(dialog.points)

            self.etab.freq1d.sw   = sw
            self.etab.freq2d.sw   = sw
            self.etab.basis.sw    = sw

            self.etab.build_basis_functions(dim0=pts)
            self.update_widget_ranges()
            self.etab.set_apodization(dim0=pts)
            self.etab.plot_canvas(reset_history=True)
            self.etab.plot_integral()

        dialog.Destroy()


    def update_widget_ranges(self):
        self.etab.maxppm = util_ppm.pts2ppm(0, self.etab.freq1d)
        self.etab.minppm = util_ppm.pts2ppm(self.etab.freq1d.dims[0]-1, self.etab.freq1d)
        xaxmax = self.FloatXaxisMax.GetValue()
        xaxmin = self.FloatXaxisMin.GetValue()
        curmax = self.FloatCursorMax.GetValue()
        curmin = self.FloatCursorMin.GetValue()
        if xaxmax > self.etab.maxppm: xaxmax = self.etab.maxppm
        if xaxmin < self.etab.minppm: xaxmin = self.etab.minppm
        if curmax > self.etab.maxppm: curmax = self.etab.maxppm
        if curmin < self.etab.minppm: curmin = self.etab.minppm
        self.FloatXaxisMax.SetRange(self.etab.minppm, self.etab.maxppm)
        self.FloatXaxisMin.SetRange(self.etab.minppm, self.etab.maxppm)
        self.FloatCursorMax.SetRange(self.etab.minppm, self.etab.maxppm)
        self.FloatCursorMin.SetRange(self.etab.minppm, self.etab.maxppm)
        self.FloatXaxisMax.SetValue(xaxmax)
        self.FloatXaxisMin.SetValue(xaxmin)
        self.FloatCursorMax.SetValue(curmax)
        self.FloatCursorMin.SetValue(curmin)


    def on_ascii_display(self, event):

        self.etab.display_results_text()
