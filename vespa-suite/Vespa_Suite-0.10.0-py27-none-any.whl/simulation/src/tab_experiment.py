# Python modules
from __future__ import division
import math
import os
import tempfile


# 3rd party modules
import wx
#import wx.aui as aui
import wx.lib.agw.aui as aui        # NB. wx.aui version throws odd wxWidgets exception on Close/Exit
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm

# Our modules
import prefs
import constants
import aui_subclass
import util_simulation_config
import util_menu
import tab_visualize
import tab_simulate
import plot_panel_plot1d
import plot_panel_integral
import plot_panel_contour
import mrs_data_basis
import build_basis_functions as bbf_module
import vespa.common.util.ppm as util_ppm
import vespa.common.util.generic_spectral as util_generic_spectral
import vespa.common.wx_gravy.util as wx_util
import vespa.common.constants as common_constants
import vespa.common.mrs_experiment as mrs_experiment
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.wx_gravy.notebooks as vespa_notebooks

PI = math.pi


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


class TabExperiment(vespa_notebooks.VespaAuiNotebook):

    def __init__(self, parent, top, db, experiment, is_new):
        style = wx.BORDER_NONE
        
        agw_style = aui.AUI_NB_TAB_SPLIT            |   \
                    aui.AUI_NB_TAB_MOVE             |   \
                    aui.AUI_NB_TAB_EXTERNAL_MOVE    |   \
                    aui.AUI_NB_BOTTOM 

        vespa_notebooks.VespaAuiNotebook.__init__(self, parent, style, agw_style)

        # global attributes

        self.top        = top
        self.parent     = parent
        self.db         = db
        self.experiment = experiment
        self.statusbar  = top.statusbar
        self.is_new     = is_new

        # Set up the experiment for plotting

        # plot attributes
        self._prefs = prefs.PrefsMain()

        # metabolite model attributes

        d = { "frequency" : self.experiment.b0 }
        self.basis  = mrs_data_basis.DataBasis(d)
        self.freq1d = mrs_data_basis.DataBasis(d)
        self.freq2d = mrs_data_basis.DataBasis(d)

        self.maxppm         = util_ppm.pts2ppm(0, self.freq1d)
        self.minppm         = util_ppm.pts2ppm(self.freq1d.dims[0]-1, self.freq1d)
        self.index1         = 0
        self.index2         = 0
        self.index3         = 0

        self.linewidth      = common_constants.DEFAULT_LINEWIDTH
        self.apodization    = None
        self.integral_data  = None
        self.plot_labels    = None

        if wx.GetApp().vespa.isotope == "1H":
            # should be 4.7
            self.midppm = common_constants.DEFAULT_PROTON_CENTER_PPM
        else:
            # should be 0.0
            self.midppm = common_constants.DEFAULT_XNUCLEI_CENTER_PPM

        self.build_tabs()
        self.update_plot_controls()
        self.build_basis_functions()
        self.plot_canvas()

        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy, self)


    #=======================================================
    #
    #           Event handlers start here
    #
    #=======================================================


    def on_activation(self):
        # This is a faux event handler. wx doesn't call it directly. It's
        # a notification from my parent (the experiment notebook) to let
        # me know that this tab has become the current one.

        # Force the View menu to match the current plot options.
        util_menu.bar.set_menu_from_state(self._prefs.menu_state)


    def on_destroy(self, event):
        self._prefs.save()


    def on_menu_view_option(self, event):

        reset_history = False
        plot_canvas = True
        plot_integral = False
        plot_contour  = False

        event_id = event.GetId()

        if self._prefs.handle_event(event_id):
            if event_id in (util_menu.ViewIds.INTEGRAL_XAXIS_SHOW,
                            util_menu.ViewIds.INTEGRAL_YAXIS_SHOW,
                            util_menu.ViewIds.CONTOUR_AXES_SHOW,
                            util_menu.ViewIds.INTEGRAL_PLOT_SHOW,
                            util_menu.ViewIds.CONTOUR_PLOT_SHOW,
                           ):
                # For these events, we don't need to bother replotting the
                # main plot.
                plot_canvas = False

            if event_id in (util_menu.ViewIds.XAXIS_PPM,
                            util_menu.ViewIds.XAXIS_HERTZ,
                           ):
                reset_history = True

            if event_id in (util_menu.ViewIds.DATA_TYPE_REAL,
                            util_menu.ViewIds.DATA_TYPE_IMAGINARY,
                            util_menu.ViewIds.DATA_TYPE_MAGNITUDE,
                            util_menu.ViewIds.LINE_SHAPE_GAUSSIAN,
                            util_menu.ViewIds.LINE_SHAPE_LORENTZIAN,
                            util_menu.ViewIds.INTEGRAL_PLOT_SHOW,
                            util_menu.ViewIds.INTEGRAL_XAXIS_SHOW,
                            util_menu.ViewIds.INTEGRAL_YAXIS_SHOW,
                           ):
                plot_integral = True

            if event_id in (util_menu.ViewIds.CONTOUR_PLOT_SHOW,
                            util_menu.ViewIds.CONTOUR_AXES_SHOW,
                           ):
                plot_contour = True

            if event_id in (util_menu.ViewIds.LINE_SHAPE_GAUSSIAN,
                            util_menu.ViewIds.LINE_SHAPE_LORENTZIAN,
                           ):
                self.set_apodization()

            if plot_canvas:
                self.plot_canvas(reset_history=reset_history)
            if plot_integral:
                self.plot_integral()
            if plot_contour:
                self.plot_contour()


    def on_menu_view_output(self, event):
        event_id = event.GetId()

        if event_id == util_menu.ViewIds.OUTPUT_TEXT_RESULTS:
            self.display_results_text()
        else:
            # "fands" is short for "formats and sources"
            fands = {
                util_menu.ViewIds.OUTPUT_1D_STACK_TO_PNG : ("PNG", self.plot1d),
                util_menu.ViewIds.OUTPUT_INTEGRAL_TO_PNG : ("PNG", self.integral),
                util_menu.ViewIds.OUTPUT_CONTOUR_TO_PNG  : ("PNG", self.contour),
                util_menu.ViewIds.OUTPUT_1D_STACK_TO_SVG : ("SVG", self.plot1d),
                util_menu.ViewIds.OUTPUT_INTEGRAL_TO_SVG : ("SVG", self.integral),
                util_menu.ViewIds.OUTPUT_CONTOUR_TO_SVG  : ("SVG", self.contour),
                util_menu.ViewIds.OUTPUT_1D_STACK_TO_EPS : ("EPS", self.plot1d),
                util_menu.ViewIds.OUTPUT_INTEGRAL_TO_EPS : ("EPS", self.integral),
                util_menu.ViewIds.OUTPUT_CONTOUR_TO_EPS  : ("EPS", self.contour),
                util_menu.ViewIds.OUTPUT_1D_STACK_TO_PDF : ("PDF", self.plot1d),
                util_menu.ViewIds.OUTPUT_INTEGRAL_TO_PDF : ("PDF", self.integral),
                util_menu.ViewIds.OUTPUT_CONTOUR_TO_PDF  : ("PDF", self.contour),
                      }

            format, source = fands[event_id]
            lformat = format.lower()
            filter_ = "%s files (*.%s)|*.%s" % (format, lformat, lformat)

            filename = common_dialogs.save_as("", filter_)

            if filename:
                msg = ''
                try:
                    source.figure.savefig(filename,
                                          dpi=300,
                                          facecolor='w',
                                          edgecolor='w',
                                          orientation='portrait',
                                          papertype='letter',
                                          format=None,
                                          transparent=False)
                except IOError:
                    msg = """I can't write the file "%s".""" % filename

                if msg:
                    common_dialogs.message(msg, style=common_dialogs.E_OK)


    #=======================================================
    #
    #           Internal methods start here
    #
    #=======================================================

    def build_tabs(self):
        """
        This is called once during init two build the visualize and
        simulate tabs. This code could just as well be inline in __init__().
        """

        visualize = wx.Panel(self, -1)
        simulate  = wx.Panel(self, -1)

        self.panel_plot1d   = wx.Panel(visualize, -1)
        self.panel_integral = wx.Panel(visualize, -1)
        self.panel_contour  = wx.Panel(visualize, -1)

        self.plot1d = plot_panel_plot1d.PlotPanelPlot1d(self.panel_plot1d,
                                                        self,
                                                        self._prefs,
                                                        naxes=1,
                                                        reversex=True,
                                                        zoom='span',
                                                        reference=True,
                                                        do_zoom_select_event=True,
                                                        do_zoom_motion_event=True,
                                                        do_refs_select_event=True,
                                                        do_refs_motion_event=True,
                                                        uses_collections=True,
                                                        props_zoom=dict(alpha=0.2, facecolor='yellow'),
                                                        props_cursor=dict(alpha=0.1, facecolor='gray') )

        self.integral = plot_panel_integral.PlotPanelIntegral(self.panel_integral,
                                                        self,
                                                        naxes=1,
                                                        reversex=False,
                                                        zoom='span',
                                                        reference=True,
                                                        middle = True,
                                                        do_zoom_select_event=False,
                                                        do_zoom_motion_event=True,
                                                        do_refs_select_event=False,
                                                        do_refs_motion_event=True,
                                                        do_middle_press_event=True,
                                                        props_zoom=dict(alpha=0.2, facecolor='yellow'),
                                                        props_cursor=dict(alpha=0.1, facecolor='gray') )

        self.contour = plot_panel_contour.PlotPanelContour(self.panel_contour,
                                                        self,
                                                        naxes=1,
                                                        reversex=False,
                                                        zoom='box',
                                                        reference=False,
                                                        middle = True,
                                                        do_zoom_select_event=False,
                                                        do_zoom_motion_event=True,
                                                        do_refs_select_event=False,
                                                        do_refs_motion_event=False,
                                                        do_middle_press_event=True,
                                                        props_zoom=dict(alpha=0.2, facecolor='yellow'),
                                                        props_cursor=dict(alpha=0.1, facecolor='gray') )

        # plot_panel objects need to be put into panels with sizers for their
        # resize functionality to work appropriately with a notebook page.

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.plot1d, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.panel_plot1d.SetSizer(sizer)
        self.plot1d.Fit()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.integral, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.panel_integral.SetSizer(sizer)
        self.integral.Fit()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.contour, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.panel_contour.SetSizer(sizer)
        self.contour.Fit()

        self.control = tab_visualize.TabVisualize(visualize, self.db,
                                                  self.experiment, self,
                                                  self._prefs)
        self.setup   = tab_simulate.TabSimulate(simulate, self.db,
                                                self.experiment, self,
                                                self.is_new)

        # Visualization Tab ------------------------
        visualize._mgr = aui_subclass.AUIManager(visualize)

        # We have four AUI-managed panes: control (the leftmost which contains
        # the textboxes, lists, floatspins, etc.) plot1d (the center, main
        # plot), integral and contour (the secondary plots on the right).
        # Sizing these panes has given us some trouble (see Simulation
        # ticket 6.) Unless we resort to trickery, plot1d occupies all
        # available real estate and the other panes only become visible if the
        # user moves the grippers.
        # We came up with a two-part hack to address that problem. Part One
        # is below. We create each AUI pane with the min size set to what
        # we want the initial size to be. Shortly after we set the min size
        # to (-1, -1) which allows the user to size them to nothing should
        # they desire.

        # The sizes we chose are 300 pixels for the control pane (makes it
        # completely visible on all 3 platforms), 200 for the secondary panes
        # (an arbitrary number) and the rest for the center pane.

        # Note that AuiPaneInfo.BestSize() "Sets the ideal size for the pane.
        # The docking manager will attempt to use this size as much as
        # possible when ***docking or floating the pane***." (emphasis mine)
        # In other words, BestSize() doesn't affect the initial size.
        visualize._mgr.AddPane(self.panel_plot1d,aui.AuiPaneInfo().
                                                    Name('plot1d').
                                                    MinSize( (-1, -1) ).
                                                    CenterPane())
        visualize._mgr.AddPane(self.control, aui.AuiPaneInfo().
                                                    Name('control').
                                                    MinSize( (350, -1) ).
                                                    CaptionVisible(False).
                                                    Gripper().Left().
                                                    CloseButton(False))
        visualize._mgr.AddPane(self.panel_integral, aui.AuiPaneInfo().
                                                    Name('integral').
                                                    MinSize( (200, -1) ).
                                                    CaptionVisible(False).
                                                    Gripper().Right().
                                                    CloseButton(False))
        visualize._mgr.AddPane(self.panel_contour, aui.AuiPaneInfo().
                                                    Name('contour').
                                                    MinSize( (200, -1) ).
                                                    CaptionVisible(False).
                                                    Gripper().Right().
                                                    CloseButton(False))

        visualize._mgr.Update()
        # Undo the MinSize() hack described above.
        visualize._mgr.GetPane("plot1d").MinSize( (-1, -1) )
        visualize._mgr.GetPane("control").MinSize( (-1, -1) )
        visualize._mgr.GetPane("integral").MinSize( (-1, -1) )
        visualize._mgr.GetPane("contour").MinSize( (-1, -1) )

        self.AddPage(visualize,"  Visualize  ",False)

        # Simulation Tab ------------------------
        simulate._mgr = aui_subclass.AUIManager(simulate)
        simulate._mgr.AddPane(self.setup, aui.AuiPaneInfo()
                                             .Name('setup')
                                             .CenterPane())
        simulate._mgr.Update()
        self.AddPage(simulate, "  Simulate  ", False)

        # plot1d initializations ----------
        xx = np.arange(self.freq1d.dims[0], dtype='float64')
        tt = xx / self.freq1d.sw
        self.apodization = util_generic_spectral.apodize(tt, self.linewidth, 'Gaussian')

        xx = util_ppm.pts2ppm(xx, self.freq1d)

        self.plot1d.figure.set_facecolor('white')
        self.plot1d.figure.subplots_adjust(left=0.0,right=0.999,
                                           bottom=0.001,top=1.0,
                                           wspace=0.0,hspace=0.01)
        self.plot1d_axes = self.plot1d.axes[0]
        self.plot1d_axes.set_facecolor(self._prefs.bgcolor)
        self.plot1d_axes.set_xlim(xx.max(),xx.min())

        self.integral.figure.set_facecolor('white')
        self.integral.figure.subplots_adjust(left=0.0,right=0.999,
                                             bottom=0.001,top=1.0,
                                             wspace=0.0,hspace=0.01)
        self.integral_axes = self.integral.axes[0]
        self.integral_axes.set_facecolor(self._prefs.bgcolor)
        self.integral_axes.set_xlim(0,1)

        self.contour.figure.set_facecolor('white')
        self.contour.figure.subplots_adjust(left=0.0,right=0.999,
                                            bottom=0.001,top=1.0,
                                            wspace=0.0,hspace=0.01)
        self.contour_axes = self.contour.axes[0]
        self.contour_axes.set_facecolor(self._prefs.bgcolor)
        self.contour_axes.set_xlim(0,1)
        self.contour_axes.set_ylim(0,1)


    #==================================================================
    #
    #       Shared/public methods start here
    #
    # In most (all?) cases these are only shared between this tab and
    # its two child tabs (Simulate & Visualize)
    #==================================================================

    def build_basis_functions(self, dim0=None):
        """
        Here we construct FID signals from the prior information from the
        experiment. These are rendered at the spectral resolution (number
        of points and sweep width) specified by the user. But, no line
        broadening is applied.

        By performing this recalculation for all metabolites under all
        conditions (ie. the FOR loops in the experiment) we are able to
        browse through the displayed spectra more quickly. However, for
        large numbers of simulations in an experiment, this recalculation
        can take a long time.

        We added the dim0 keyword here because when the user sets a new
        spectral resolution using the spectral dialog, we need to know
        what the new spectral dimension (aka. freq1d.dims[0]) value is,
        but since the basis functions have not yet been recalculated, we
        can not use the "dims" property to return a correct value from the
        data.shape attribute.  This keyword gets us around this conundrum.

        """
        if not self.experiment.metabolites:
            return

        if self.experiment.isotope == u'1H':
            self.freq1d.midppm     = common_constants.DEFAULT_PROTON_CENTER_PPM
            self.freq1d.resppm     = common_constants.DEFAULT_PROTON_CENTER_PPM
        else:
            self.freq1d.midppm     = common_constants.DEFAULT_XNUCLEI_CENTER_PPM
            self.freq1d.resppm     = common_constants.DEFAULT_XNUCLEI_CENTER_PPM

        # ensure that datasets and certain boundaries
        # reflect the experiment settings

        self.basis.frequency      = self.experiment.b0
        self.freq1d.frequency     = self.experiment.b0
        self.freq2d.frequency     = self.experiment.b0

        # can not use util_ppm methods because dims not properly set at this point
        if not dim0:
            dim0 = self.freq1d.dims[0]

        sw     = self.freq1d.sw
        freq   = self.freq1d.frequency
        midppm = self.freq1d.midppm
        resppm = self.freq1d.resppm
        self.maxppm = ( ((dim0/2) - (0)     ) * ((sw/dim0) / freq) ) + midppm
        self.minppm = ( ((dim0/2) - (dim0-1)) * ((sw/dim0) / freq) ) + midppm

        # if x-axis has changed, ensure bounds are appropriate
        axes = self.plot1d.axes[0]
        xmin = self.minppm
        xmax = self.maxppm
        x0, y0, x1, y1 = axes.dataLim.bounds
        # bjs - this was returning 'inf' values on init prior to any data being plotted
        #  not sure why it did not crash before. May need to put dummy data in on
        #  creation of the plot_panel
        axes.ignore_existing_data_limits = True
        if not all(np.isfinite([x0,y0,x1,y1])):
            axes.update_datalim([[xmin,0.0],[xmax,1.0]])
        else:
            axes.update_datalim([[xmin, y0],[xmax,y1+y0]])

        bx0, by0, bx1, by1 = axes.dataLim.bounds


        # We use a callback function to provide a progress indicator. However,
        # it only works under Linux/GTK.
        # See http://scion.duhs.duke.edu/vespa/simulation/ticket/35
        callback = self.build_basis_progress if ("__WXGTK__" in wx.PlatformInfo) else None
        self.basis.data = bbf_module.build_basis_functions(self.experiment,
                                                           dim0,
                                                           sw,
                                                           resppm,
                                                           callback)

        self.set_apodization()
        self.top.statusbar.SetStatusText(' ',0)


    def build_basis_progress(self):
        """
        Updates the status bar with build basis progress.
        Passed to and called by bbf_module.build_basis_functions().
        """
        _, progress = bbf_module.global_progress

        status = ("Basis functions %s complete...") % progress
        self.top.statusbar.SetStatusText(status)


    def close(self):
        return self.setup.close()


    def display_results_text(self):

        lines = unicode(self.experiment)
        lines += "\n\nSimulation Results\n" + "-" * 75 + "\n\n"

        lines += "\n".join([simulation.summary() for simulation
                                                 in self.experiment.simulations])

        wx_util.display_text_as_file(lines)


    def plot_canvas(self, reset_history=False):

        # check if any egregious issues with proceeding
        if not self.experiment.metabolites:
            return
        if self.basis.data is None:
            return

        # get indices of data to include
        imets = self.control.ListPlotMetabolites.GetSelections()
        # Under Windows & GTK, the list returned by GetSelections() is always
        # sorted smallest to largest. Under OS X, it's not sorted and might
        # be e.g. (2, 1, 0) or even (1, 0, 2). We sort it in order to ensure
        # consistent behavior.
        imets = sorted(imets)
        nmet  = len(imets)
        if nmet == 0:
            return

        self.plot_labels = [self.control.ListPlotMetabolites.GetString(i) for i in imets]
        self.plot_labels.reverse()
        index1 = self.control.SpinIndex1.GetValue()-1
        index2 = self.control.SpinIndex2.GetValue()-1
        index3 = self.control.SpinIndex3.GetValue()-1

        # check for display mode and fill data array
        mode = self.control.ChoiceDisplayMode.GetCurrentSelection()
        if mode == 0:
            b = self.basis.data[index3,index2,index1,imets,:]
        elif mode == 1:
            b = self.basis.data[index3,index2,:,imets[0],:]
        elif mode == 2:
            b = self.basis.data[index3,:,index1,imets[0],:]
        elif mode == 3:
            b = self.basis.data[:,index2,index1,imets[0],:]

        data = b.copy()
        data = data[::-1,:]

        if self.control.CheckSumPlots.IsChecked():
            data = data.sum(axis=0)
            data.shape = 1,data.shape[0]
            x00, y00, x11, y11 = self.plot1d_axes.dataLim.bounds

        npts = self.freq1d.dims[0]
        # transform into frequency domain and store
        if data.shape[0] == 1:
            data[:] = np.fft.fft(data[:] * self.apodization) / npts
        else:
            for i in range(data.shape[0]):
                data[i,:] = np.fft.fft(data[i,:] * self.apodization) / npts

        self.freq1d.data = data

        # select data type to plot - real, imaginary, magnitude
        if self._prefs.data_type_real:
            data = self.freq1d.data.real
            color = self._prefs.line_color_real
        elif self._prefs.data_type_imaginary:
            data = self.freq1d.data.imag
            color = self._prefs.line_color_imaginary
        elif self._prefs.data_type_magnitude:
            data = abs(self.freq1d.data)
            color = self._prefs.line_color_magnitude

        # check widget ranges if data has changed
        self.control.update_widget_ranges()

        # x-axis creation, zoom and cursor checks
        xx   = np.arange(self.freq1d.dims[0], dtype='float64')
        xmax = self.control.FloatXaxisMax.GetValue()
        xmin = self.control.FloatXaxisMin.GetValue()
        if self._prefs.xaxis_ppm:
            xx = util_ppm.pts2ppm(xx, self.freq1d)
        else:
            xx = util_ppm.pts2hz(xx, self.freq1d)
            xmax = util_ppm.pts2hz(util_ppm.ppm2pts(xmax,self.freq1d),self.freq1d)
            xmin = util_ppm.pts2hz(util_ppm.ppm2pts(xmin,self.freq1d),self.freq1d)
        xlim = (xmax, xmin)
        self.plot1d_axes.set_xlim(xlim)

        xmax = self.control.FloatCursorMax.GetValue()
        xmin = self.control.FloatCursorMin.GetValue()
        if self._prefs.xaxis_hertz:
            xmax = util_ppm.pts2hz(util_ppm.ppm2pts(xmax,self.freq1d),self.freq1d)
            xmin = util_ppm.pts2hz(util_ppm.ppm2pts(xmin,self.freq1d),self.freq1d)
        if self.plot1d.refs != None:
            self.plot1d.refs.set_span(xmin,xmax)


        # set up dynamic y-scaling based on min/max of data plotted
        ticklocs = []
        dmin = data.min()
        dmax = data.max()
        dr   = abs(dmax - dmin)
        dmin = dmin - dr*0.03   # space line collection vertically
        dmax = dmax + dr*0.03
        dr = dmax - dmin
        y0 = dmin
        y1 = dmin + data.shape[0] * dr

        # set up line collection requirements
        segs = []
        for i in range(data.shape[0]):
            segs.append(np.hstack((xx[:,np.newaxis], data[i,:,np.newaxis])))
            ticklocs.append(i*dr)
        offsets = np.zeros((data.shape[0],2), dtype=float)
        offsets[:,1] = ticklocs

        lines = mpl.collections.LineCollection(segs, offsets=offsets,
                                               linewidth=self._prefs.line_width)
        lines.set_color(color)

        self.plot1d_axes.cla()
        self.plot1d.refresh_cursors()
        self.plot1d_axes.add_collection(lines)
        self.plot1d_axes.set_yticks(ticklocs)

        if self._prefs.zero_line_show:
            for i in range(data.shape[0]):
                self.plot1d_axes.axhline(y = i*dr,
                                         color=self._prefs.zero_line_color,
                                         linestyle=self._prefs.zero_line_style,
                                         linewidth=self._prefs.line_width)

        # y-lim set needs to stay after zero_line or y-axis gets skewed
        self.plot1d_axes.set_ylim(y0, y1)
        x0, boundy0, x1, boundy1 = self.plot1d_axes.dataLim.bounds
        self.plot1d_axes.ignore_existing_data_limits = True
        self.plot1d_axes.update_datalim([[x0,y0],[x1+x0,y1]])


        mpl.artist.setp(self.integral_axes.axes.yaxis, visible=False)
        if self._prefs.xaxis_show:
            mpl.artist.setp(self.integral_axes.axes.xaxis, visible=True)
            self.plot1d.figure.subplots_adjust(left=0.0,right=0.999,
                                               bottom=0.05,top=1.0,
                                               wspace=0.0,hspace=0.0)
        else:
            mpl.artist.setp(self.integral_axes.axes.xaxis, visible=False)
            self.plot1d.figure.subplots_adjust(left=0.0,right=0.999,
                                               bottom=0.001,top=1.0,
                                               wspace=0.0,hspace=0.0)

        self.plot1d.canvas.draw()


    def plot_contour(self, reset=False, recalc=True):

        # check if any egregious issues with proceeding
        if not self._prefs.contour_plot_show:
            reset = True
        if reset:
            self.contour_axes.cla()
            self.contour.canvas.draw()
            return
        if self.basis.data is None:
            return

        if recalc:
            # get indices of data to include
            imets = self.control.ListPlotMetabolites.GetSelections()
            # Under Windows & GTK, the list returned by GetSelections() is
            # always sorted smallest to largest. Under OS X, it's not sorted
            # and might be e.g. (2, 1, 0) or even (1, 0, 2). We sort it in
            # order to ensure consistent behavior.
            imets = sorted(imets)
            nmet  = len(imets)
            if nmet == 0:
                return

            index1 = self.control.SpinIndex1.GetValue()-1
            index2 = self.control.SpinIndex2.GetValue()-1
            index3 = self.control.SpinIndex3.GetValue()-1

            # check for display mode and fill data array
            mode = self.control.ChoiceContourMode.GetCurrentSelection()
            if mode == 0:
                view = self.basis.data[index3,:,:,imets[0],:]   # data dims are X,Y
                xlen = len(self.experiment.dims[0])
                ylen = len(self.experiment.dims[1])
            elif mode == 1:
                view = self.basis.data[:,index2,:,imets[0],:]   # data dims are X,Z
                xlen = len(self.experiment.dims[0])
                ylen = len(self.experiment.dims[2])
            elif mode == 2:
                view = self.basis.data[:,:,index1,imets[0],:]   # data dims are Y,Z
                xlen = len(self.experiment.dims[1])
                ylen = len(self.experiment.dims[2])
            if xlen == 1 and ylen ==1:
                return
            view = view.copy()
            view.shape = xlen*ylen, self.basis.dims[0]

            # transform into frequency domain and store
            for i in range(view.shape[0]):
                view[i,:] = np.fft.fft(view[i,:] * self.apodization) / self.basis.dims[0]
        else:
            view = self.freq2d.data
            # check for display mode and fill data array
            mode = self.control.ChoiceContourMode.GetCurrentSelection()
            if mode == 0:
                xlen = len(self.experiment.dims[0])
                ylen = len(self.experiment.dims[1])
            elif mode == 1:
                xlen = len(self.experiment.dims[1])
                ylen = len(self.experiment.dims[2])
            elif mode == 2:
                xlen = len(self.experiment.dims[1])
                ylen = len(self.experiment.dims[2])
            if xlen == 1 and ylen ==1:
                return

        if reset:
            view = view * 0

        # save data so updates don't need recalculation
        self.freq2d.data = view

        # get locations for and plot cursors
        x0 = util_ppm.ppm2pts(self.control.FloatCursorMax.GetValue(), self.freq1d)
        x1 = util_ppm.ppm2pts(self.control.FloatCursorMin.GetValue(), self.freq1d)
        x0 = long(np.clip(x0, 0, self.freq1d.dims[0]-1))
        x1 = long(np.clip(x1, 1, self.freq1d.dims[0]-1))
        view = view[:,x0:x1]
        view = view.sum(axis=1)
        view.shape = xlen,ylen

        # select data type to plot - real, imaginary, magnitude
        if self._prefs.data_type_real:
            view = view.real
        elif self._prefs.data_type_imaginary:
            view = view.imag
        elif self._prefs.data_type_magnitude:
            view = abs(view)

        self.contour_axes.clear()

        if self._prefs.contour_axes_show:
            self.contour_axes.set_axis_on()
            self.contour.figure.subplots_adjust(left=0.07,right=0.95,
                                               bottom=0.07,top=0.95,
                                               wspace=0.0,hspace=0.0)
        else:
            self.contour_axes.set_axis_off()
            self.contour.figure.subplots_adjust(left=0.001,right=0.99,
                                               bottom=0.001,top=0.99,
                                               wspace=0.0,hspace=0.0)

        # if data is all the same, the contour plot fails, I think it
        # is because it can not decide where to put multiple level lines,
        # in this case, set an alert message and return
        self.statusbar.SetStatusText((''), 2)
        if abs((view.max()-view.min())/view.mean())<0.001:
             txt = "Contour can not plot constant areas"
             self.statusbar.SetStatusText((txt), 2)
             self.contour.canvas.draw()
             return

        # in some cases it is desirable to expand a 1D array out to pretend
        # that it is a 2d array, this code checks which dimension is len = 1
        # and expands the array into a square matrix for display
        if xlen == 1:
            y = np.ndarray(ylen*ylen,dtype='float')
            for i in np.arange(ylen):
                for j in np.arange(ylen):
                    y[j+i*ylen] = view[0,j]
            view = y
            view.shape = ylen,ylen
            xlen = ylen

        if ylen == 1:
            y = np.ndarray(xlen*xlen,dtype='float')
            for i in np.arange(xlen):
                for j in np.arange(xlen):
                    y[j+i*xlen] = view[j,0]
            view = y
            view.shape = xlen,xlen
            ylen = xlen

        # FIXME bjs - magic number multiplier to not get underflow exception
        # the 10000 multiplier below was necessary to avoid an odd
        # FloatPointError exception that was being throw for various
        # levels of contour.  With bigger values in view, it seems
        # to not occur. I should normalize this scaling using a
        # constant so as to be able to control it more easily, but
        # not today.

        levels = self.control.SpinContourLevels.GetValue()
        if self.control.CheckGrayscale.IsChecked():
            self.contour_axes.imshow(view, cmap=cm.gray, extent=(1,xlen,1,ylen), origin='lower')
        self.contour_axes.contour(view*10000, levels, extent=(1,xlen,1,ylen))
        self.contour.canvas.draw()

        self.contour.canvas.draw()  # np.max(view)


    def plot_integral(self, reset=False):

        # check if any egregious issues with proceeding
        if not self._prefs.integral_plot_show:
            return
        if self.freq1d.data is None:
            return

        # check that there are metabolites selected
        imets = self.control.ListPlotMetabolites.GetSelections()
        if len(imets) == 0:
            return

        # select data type to plot - real, imaginary, magnitude
        if self._prefs.data_type_real:
            view = self.freq1d.data.real
        elif self._prefs.data_type_imaginary:
            view = self.freq1d.data.imag
        elif self._prefs.data_type_magnitude:
            view = abs(self.freq1d.data)
        if len(view.shape)<2:
            return

        # check for display mode and fill x-axis
        mode = self.control.ChoiceDisplayMode.GetCurrentSelection()
        if mode == 0:
            return
        else:
            xx = np.array(self.experiment.dims[mode - 1])
        if len(xx)<2:
            return

        if self._prefs.xaxis_hertz:
            xx = xx * self.freq1d.frequency   # convert generally to Hz


        x0 = util_ppm.ppm2pts(self.control.FloatCursorMax.GetValue(), self.freq1d)
        x1 = util_ppm.ppm2pts(self.control.FloatCursorMin.GetValue(), self.freq1d)
        x0 = long(np.clip(x0, 0, self.freq1d.dims[0]-1))
        x1 = long(np.clip(x1, 1, self.freq1d.dims[0]-1))
        view = view[:,x0:x1]
        y = view.sum(axis=1)
        y = y[::-1]

        if reset:
            y = y * 0
            ymin = -1
            ymax = 1
        else:
            ymin = y.min() - (abs(y.min())*0.03)
            ymax = y.max() + (abs(y.max())*0.03)


        # this gets used during motion events
        self.integral_data = y

        self.integral_axes.clear()
        self.integral.refresh_cursors()
        self.integral_axes.plot(xx, y, linewidth=self._prefs.line_width)
        self.integral_axes.set_xlim(xx.min(), xx.max())
        self.integral_axes.set_ylim(ymin, ymax)

        if self._prefs.integral_xaxis_show:
            top    = 0.95
            bottom = 0.07
            mpl.artist.setp(self.integral_axes.axes.xaxis, visible=True)
        else:
            top    = 0.995
            bottom = 0.002
            mpl.artist.setp(self.integral_axes.axes.xaxis, visible=False)

        if self._prefs.integral_yaxis_show:
            right = 0.95
            left  = 0.15
            mpl.artist.setp(self.integral_axes.axes.yaxis, visible=True)
        else:
            right = 0.995
            left  = 0.002
            mpl.artist.setp(self.integral_axes.axes.yaxis, visible=False)

        self.integral.figure.subplots_adjust(left=left,right=right,
                                             bottom=bottom,top=top,
                                             wspace=0.0,hspace=0.0)
        self.integral.canvas.draw()


    def save_experiment(self):
        """Saves the experiment, if possible, and returns True. If the
        experiment can't be saved (because it contains invalid data, e.g.),
        returns False.

        This is quite similar to an event handler since it is called
        from main where it's invoked by a menu item.
        """
        return self.setup.save_experiment()


    def set_apodization(self, dim0=None):
        """
        We added the dim0 keyword here because when the user sets a new
        spectral resolution using the spectral dialog, we need to know
        what the new spectral dimension (aka. freq1d.dims[0]) value is,
        but since the basis functions have not yet been recalculated, we
        can not use the "dims" property to return a correct value from the
        data.shape attribute.  This keyword gets us around this conundrum.

        """
        if not dim0:
            dim0 = self.freq1d.dims[0]

        xx = np.arange(dim0, dtype='float64') / self.freq1d.sw
        type_ = 'Gaussian' if self._prefs.line_shape_gaussian else 'Lorentzian'
        self.apodization = util_generic_spectral.apodize(xx, self.linewidth, type_)


    def update_plot_controls(self):

        # This update routine is located on the Experiment_Tab level because
        # changes to the Simulate Tab can affect the Visualize Tab, but not
        # the other way around. So all Simulate functions are in the Simulate
        # module, but not all Visualize functions are in Visualize module.

        # update the Visualize tab controls

        self.control.Enable(True)
        expt = self.experiment

        # a few calculations

        npts  = self.freq1d.dims[0]
        sw    = self.freq1d.sw
        field = expt.b0
        hpp   = sw/npts

        self.maxppm = util_ppm.pts2ppm(0, self.freq1d)
        self.minppm = util_ppm.pts2ppm(npts-1, self.freq1d)

        # update Plot control

        # There are N+1 display modes, where N = the number of non-empty
        # dims in the experiment. "1D plot" is always an option.
        # Before repopulating this list of choices, we grab the current
        # selection so we can restore it if possible.
        selection = self.control.ChoiceDisplayMode.GetStringSelection()
        choices = ["1D Plot"]
        # The other options are a stack plot for each non-empty dim.
        choices += ["Stack Plot Index %d" % (i + 1) for i, dim
                                             in enumerate(self.experiment.dims)
                                             if dim != mrs_experiment.DEFAULT_LOOP]
        self.control.ChoiceDisplayMode.SetItems(choices)

        # Restore the selection if it's still in the combobox.
        selection = self.control.ChoiceDisplayMode.FindString(selection)
        if selection == wx.NOT_FOUND:
            selection = 0
        self.control.ChoiceDisplayMode.SetSelection(selection)

        # setting the Xaxis and Cursor ranges depends on the initial setup
        # of the Visualize panel to have urealistically large numbers in
        # these fields (ie. -999 to 999)

        xaxmax = self.control.FloatXaxisMax.GetValue()
        xaxmin = self.control.FloatXaxisMin.GetValue()
        curmax = self.control.FloatCursorMax.GetValue()
        curmin = self.control.FloatCursorMin.GetValue()

        if xaxmax > self.maxppm: xaxmax = self.maxppm
        if xaxmin > self.minppm: xaxmin = self.minppm
        if curmax > self.maxppm: curmax = self.maxppm
        if curmin > self.minppm: curmin = self.minppm

#        if self.plot_options.x_axis_type != PlotOptions.X_AXIS_PPM:
#
#            #FIXME - BJS found that the following holds
#            # ppm2hz != pts2hz(ppm2pts())
#            # hz2ppm != pts2ppm(hz2pts())
#            # Need to check original IDL code
#
#            xaxmax = util_ppm.pts2hz(util_ppm.ppm2pts(xaxmax,self.freq1d),self.freq1d)
#            xaxmin = util_ppm.pts2hz(util_ppm.ppm2pts(xaxmin,self.freq1d),self.freq1d)
#            curmax = util_ppm.pts2hz(util_ppm.ppm2pts(curmax,self.freq1d),self.freq1d)
#            curmin = util_ppm.pts2hz(util_ppm.ppm2pts(curmin,self.freq1d),self.freq1d)
#            maxppm = util_ppm.pts2hz(util_ppm.ppm2pts(self.maxppm,self.freq1d),self.freq1d)
#            minppm = util_ppm.pts2hz(util_ppm.ppm2pts(self.minppm,self.freq1d),self.freq1d)
#        else:
#            maxppm = self.maxppm
#            minppm = self.minppm
        maxppm = self.maxppm
        minppm = self.minppm

        self.control.FloatXaxisMax.SetValue(xaxmax)
        self.control.FloatXaxisMin.SetValue(xaxmin)
        self.control.FloatCursorMax.SetValue(curmax)
        self.control.FloatCursorMin.SetValue(curmin)
        self.control.FloatXaxisMax.SetRange(minppm, maxppm)
        self.control.FloatXaxisMin.SetRange(minppm, maxppm)
        self.control.FloatCursorMax.SetRange(minppm, maxppm)
        self.control.FloatCursorMin.SetRange(minppm, maxppm)

        for i in range(common_constants.RESULTS_SPACE_DIMENSIONS - 1):
            spin_control = getattr(self.control, "SpinIndex%d" % (i + 1))
            spin_control.SetRange(1, len(self.experiment.dims[i]))
            # Undex OS X (not Win or GTK), it's necessary to explicitly set
            # the value to get it to display. Setting just the range is not
            # sufficient.
            spin_control.SetValue(1)

        # By default I hide all of the loop control panels and then show
        # them as needed. Rather than hardcoding their names here, I just
        # use getattr until it fails.
        i = 1
        panel = getattr(self.control, "panel_loop%d_controls" % i)
        while panel:
            panel.Hide()
            i += 1
            try:
                panel = getattr(self.control, "panel_loop%d_controls" % i)
            except AttributeError:
                panel = None

        # Now show & populate the enabled loop panels (if any).
        if expt.pulse_sequence:
            for i, loop_label in enumerate(expt.pulse_sequence.loop_labels):
                j = i + 1
                panel = getattr(self.control, "panel_loop%d_controls" % j)
                panel.Show()

                # Show the labels for these loops and their values.
                control = getattr(self.control, "LabelLoop%dLabel" % j)
                control.SetLabel(loop_label + " = ")

                control = getattr(self.control, "LabelIndex%dValue" % j)
                control.SetLabel(str(self.experiment.dims[i][0]))

                panel.Layout()

        # Deselect everything in the PlotMetabs listbox before resetting its
        # contents. This is a fix/workaround for simulation ticket 34:
        # http://scion.duhs.duke.edu/vespa/simulation/ticket/34
        i = self.control.ListPlotMetabolites.GetCount()
        while i:
            i -= 1
            self.control.ListPlotMetabolites.Deselect(i)

        names = [metabolite.name for metabolite in expt.metabolites]
        self.control.ListPlotMetabolites.SetItems(names)

        self.control.CheckGrayscale.SetValue(self._prefs.contour_grayscale)
        self.control.SpinContourLevels.SetValue(self._prefs.contour_levels)

        if self.linewidth < constants.LINEWIDTH_MIN: self.linewidth = constants.LINEWIDTH_MIN
        if self.linewidth > constants.LINEWIDTH_MAX: self.linewidth = constants.LINEWIDTH_MAX
        if self.freq1d.sw < constants.SWEEP_WIDTH_MIN: self.freq1d.sw = constants.SWEEP_WIDTH_MIN
        if self.freq1d.sw > constants.SWEEP_WIDTH_MAX: self.freq1d.sw = constants.SWEEP_WIDTH_MAX
        if self.freq1d.dims[0] < constants.SPECTRAL_POINTS_MIN: self.freq1d.dims[0] = SPECTRAL_POINTS_MIN
        if self.freq1d.dims[0] > constants.SPECTRAL_POINTS_MAX: self.freq1d.dims[0] = SPECTRAL_POINTS_MAX

        self.control.FloatLinewidth.SetValue(float(self.linewidth))
        self.control.FloatLinewidth.SetDigits(1)
        self.control.FloatLinewidth.SetIncrement(0.5)
        self.control.FloatLinewidth.SetRange(constants.LINEWIDTH_MIN,constants.LINEWIDTH_MAX)

        self.control.Layout()

        # Oddly enough, .Refresh() and .Update() don't make visible the
        # controls hidden/shown above (or if it makes them visible, it
        # positions them incorrectly). So we resort to a trick to force
        # the pane to reconsider the layout of its contents.
        # Resizing is a good way to do that. Under Windows & OS X it's
        # sufficient to subtract then add one to the pane's width. The net
        # change is zero, but it has the desired effect.
        # Under GTK, however, the window size must actually change. If we
        # always used the same delta (+1 or -1), then the pane would gradually
        # get larger or smaller every time the user selects a new water
        # filter.
        # To avoid this, we vary the delta based on whether or not the
        # current pane width is odd or even. No matter how many times the
        # user selects from the water filter list, the size will vary at
        # most one pixel from the original width.
        window = self.top._mgr.GetPane("experiments").window

        size = window.GetSize()
        size.width += (-1 if (size.width % 2) else 1)
        window.SetSize(size)


