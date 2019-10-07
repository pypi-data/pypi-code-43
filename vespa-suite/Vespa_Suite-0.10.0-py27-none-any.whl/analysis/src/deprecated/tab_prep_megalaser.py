# Python modules
from __future__ import division
import math
import os
import sys
import tempfile
import webbrowser


# 3rd party modules
import wx
import numpy as np


# Our modules
import tab_base
import prefs as prefs_module
import constants
import util
import util_menu
import util_analysis_config
import plot_panel_prep_megalaser
import auto_gui.fidsum_megalaser as fidsum_megalaser
import vespa.common.constants as common_constants
import vespa.common.util.misc as util_misc
import vespa.common.util.ppm as util_ppm
import vespa.common.wx_gravy.util as wx_util
import vespa.common.wx_gravy.common_dialogs as common_dialogs



#------------------------------------------------------------------------------


def _configure_combo(control, choices, selection=''):
        lines = choices.values()
        control.SetItems(lines)
        if selection in lines:
            control.SetStringSelection(selection)
        else: 
            control.SetStringSelection(lines[0])    


def _paired_event(obj_min, obj_max):
        val_min = obj_min.GetValue()
        val_max = obj_max.GetValue()
        pmin = min(val_min, val_max)
        pmax = max(val_min, val_max)
        obj_min.SetValue(pmin)
        obj_max.SetValue(pmax)
        return pmin, pmax    

#------------------------------------------------------------------------------
#
#  Tab RAW FIDSUM 
#
#------------------------------------------------------------------------------

class TabPrepMegalaser(tab_base.Tab, fidsum_megalaser.PanelPrepMegalaserUI):
    # This attr allows the notebook to identify this tab. The value of the attr
    # doesn't actually matter; its presence is sufficient.
    IS_PREP_FIDSUM = True
    
    def __init__(self, tab_dataset, top, block):
        
        fidsum_megalaser.PanelPrepMegalaserUI.__init__(self, tab_dataset.NotebookDataset)
        
        tab_base.Tab.__init__(self, tab_dataset, top, prefs_module.PrefsPrepFidsum)
        
        self.top      = top               # application frame
        self.block    = block             # processing object

        # Plotting is disabled during some of init. That's because the plot
        # isn't ready to plot, but the population of some controls 
        # (e.g. spin controls on the water filter panel) fires their 
        # respective change event which triggers a call to plot(). This
        # appears to happen only under Windows; it might be a Windows-specific
        # bug.
        # In any case, skipping some calls to plot() will speed things up. =)
        self._plotting_enabled = False
        self.plot_results = None
        
        self.fid_index      = 0
        self.initialize_controls()
        self.populate_controls()

        self._plotting_enabled = True 

        #------------------------------------------------------------
        # Setup the canvas 
        self.process_and_plot()


        # If the sash position isn't recorded in the INI file, we use the
        # arbitrary-ish value of 400.
        if not self._prefs.sash_position:
            self._prefs.sash_position = 400

        # Under OS X, wx sets the sash position to 10 (why 10?) *after*
        # this method is done. So setting the sash position here does no
        # good. We use wx.CallAfter() to (a) set the sash position and
        # (b) fake an EVT_SPLITTER_SASH_POS_CHANGED.
        wx.CallAfter(self.SplitterWindow.SetSashPosition, 
                     self._prefs.sash_position, True)
        wx.CallAfter(self.on_splitter)


    #=======================================================
    #
    #           GUI Setup Handlers 
    #
    #=======================================================

    def initialize_controls(self):
        """ 
        Initializes the controls to be the right size or have the right
        range or number of decimal places. It typically does not set the
        default value (that's for populate_controls method to do). This
        method does the one-time setup bits.
        
        """
        dataset = self.dataset
        dim0, dim1, dim2, dim3 = dataset.spectral_dims
        sw      = dataset.sw
        maxppm  = util_ppm.pts2ppm(0, dataset)
        minppm  = util_ppm.pts2ppm(dim0-1, dataset)
        ppmlim  = (minppm, maxppm)
        
        
        wx_util.configure_spin(self.SpinFidIndex, 60)

        wx_util.configure_spin(self.FloatGaussianApodization, 70, 2, constants.PrepMegalaser.STEP_APODIZE,
                       (constants.PrepMegalaser.MIN_APODIZE, constants.PrepMegalaser.MAX_APODIZE))

        wx_util.configure_spin(self.SpinFidLeftShift, 70, None, None,
                       (constants.PrepMegalaser.MIN_LEFT, constants.PrepMegalaser.MAX_LEFT))

        wx_util.configure_spin(self.SpinFidLeftShiftB0, 70, None, None,
                       (constants.PrepMegalaser.MIN_LEFT_B0, constants.PrepMegalaser.MAX_LEFT_B0))

        wx_util.configure_spin(self.SpinFidLeftShiftPhase0, 70, None, None,
                       (constants.PrepMegalaser.MIN_LEFT_PHASE0, constants.PrepMegalaser.MAX_LEFT_PHASE0))

        wx_util.configure_spin(self.FloatPeakShiftValue, 70, 3, constants.PrepMegalaser.STEP_PEAK,
                       (constants.PrepMegalaser.MIN_PEAK,constants.PrepMegalaser.MAX_PEAK))

        wx_util.configure_spin(self.FloatPhase0, 70, 3, constants.PrepMegalaser.STEP_PHASE,
                       (constants.PrepMegalaser.MIN_PHASE,constants.PrepMegalaser.MAX_PHASE))

        wx_util.configure_spin(self.FloatPhase1, 70, 3, constants.PrepMegalaser.STEP_PHASE1,
                       (constants.PrepMegalaser.MIN_PHASE1,constants.PrepMegalaser.MAX_PHASE1))

        wx_util.configure_spin(self.FloatReferencePeakCenter, 70, 3, constants.PrepMegalaser.STEP_CENTER,
                       (constants.PrepMegalaser.MIN_CENTER,constants.PrepMegalaser.MAX_CENTER))

        wx_util.configure_spin(self.FloatPeakSearchWidth, 70, 3, constants.PrepMegalaser.STEP_WIDTH,
                       (constants.PrepMegalaser.MIN_WIDTH,constants.PrepMegalaser.MAX_WIDTH))

        wx_util.configure_spin(self.SpinRefPeakLineWidth, 70, None, None,
                       (constants.PrepMegalaser.MIN_REF_LINE_WIDTH, constants.PrepMegalaser.MAX_REF_LINE_WIDTH))
        
        wx_util.configure_spin(self.SpinConstantPhase0Offset, 70, None, None,
                       (constants.PrepMegalaser.MIN_CONSTANT_PH0, constants.PrepMegalaser.MAX_CONSTANT_PH0))

        wx_util.configure_spin(self.FloatPhase0RangeStart, 70, 2, 0.25, ppmlim)
        wx_util.configure_spin(self.FloatPhase0RangeEnd,   70, 2, 0.25, ppmlim)

        # set up combo selections
        _configure_combo(self.ComboRefSpectrumSource, constants.MegalaserRefSpectrumSource.choices)


        #-------------------------------------------------------------
        # Raw Fidsum View setup 

        self.view = plot_panel_prep_megalaser.PlotPanelPrepMegalaser(self.PanelViewPrepFidsum, 
                                                            self,
                                                            self._tab_dataset,
                                                            naxes=3,
                                                            reversex=True,
                                                            zoom='span', 
                                                            reference=True,
                                                            middle=True,
                                                            do_zoom_select_event=True,
                                                            do_zoom_motion_event=True,
                                                            do_refs_select_event=True,
                                                            do_refs_motion_event=True,
                                                            do_middle_select_event=True,
                                                            do_middle_motion_event=True,
                                                            do_scroll_event=True,
                                                            props_zoom=dict(alpha=0.2, facecolor='yellow'),
                                                            props_cursor=dict(alpha=0.2, facecolor='gray'),
                                                            xscale_bump=0.0,
                                                            yscale_bump=0.05,
                                                            data = [],
                                                            prefs=self._prefs, 
                                                            dataset=self.dataset,
                                                            )
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelViewPrepFidsum.SetSizer(sizer)
        self.view.Fit()    

        width, height = self.SpinFidLeftShift.GetSize()

        if "__WXMAC__" in wx.PlatformInfo:
            # Under OS X this spin control needs a poke to paint itself 
            # properly. Without this code, the control doesn't appear on screen
            # even though the wx Inspector reports that it has an appropriate
            # size & position. Go figger.
            wx.CallAfter(self.SpinFidLeftShift.SetSize, (width + 1, height))

  
    def populate_controls(self):
        """ 
        Populates the raw data tab with values from the dataset.raw 
        object. It's meant to be called when a new data object is loaded.

        """
        block = self.block
        
        raw = self._tab_dataset.dataset.get_source_data('prep')

        self.SpinFidIndex.SetValue(self.fid_index+1)
        self.SpinFidIndex.SetRange(1, raw.shape[-2])

        self.FloatGaussianApodization.SetValue(self.block.set.gaussian_apodization)
        self.SpinFidLeftShift.SetValue(self.block.set.fid_left_shift)
        self.SpinFidLeftShiftB0.SetValue(self.block.set.fid_left_shift_b0)
        self.SpinFidLeftShiftPhase0.SetValue(self.block.set.fid_left_shift_phase0)
        
        self.FloatPeakShiftValue.SetValue(self.block.frequency_shift[self.fid_index])
        self.FloatPhase0.SetValue(self.block.phase_0[self.fid_index])
        
        self.CheckApplyPeakShift.SetValue(self.block.set.apply_peak_shift)
        self.FloatReferencePeakCenter.SetValue(self.block.set.reference_peak_center)
        self.FloatPeakSearchWidth.SetValue(self.block.set.peak_search_width)
        self.CheckApplyPhase0.SetValue(self.block.set.apply_phase0)
        self.FloatPhase0RangeStart.SetValue(self.block.set.phase0_range_start)
        self.FloatPhase0RangeEnd.SetValue(self.block.set.phase0_range_end)
        
        self.SpinRefPeakLineWidth.SetValue(self.block.set.ref_peak_line_width)
        self.SpinConstantPhase0Offset.SetValue(self.block.set.constant_phase0_offset)

        refspec = constants.MegalaserRefSpectrumSource.choices[self.block.set.ref_spectrum_source]
        self.ComboRefSpectrumSource.SetStringSelection(refspec)
        if self.block.set.ref_spectrum_source == 'average_all_fids':
            self.SpinRefPeakLineWidth.Enable(False)
        else:
            self.SpinRefPeakLineWidth.Enable(True)


        

    
    #=======================================================
    #
    #           Global and Menu Event Handlers 
    #
    #=======================================================

    def on_menu_view_option(self, event):
        event_id = event.GetId()

        if self._prefs.handle_event(event_id):

            if event_id in (util_menu.ViewIdsPrepFidsum.ZERO_LINE_SHOW,
                           util_menu.ViewIdsPrepFidsum.ZERO_LINE_TOP,
                           util_menu.ViewIdsPrepFidsum.ZERO_LINE_MIDDLE,
                           util_menu.ViewIdsPrepFidsum.ZERO_LINE_BOTTOM,
                           util_menu.ViewIdsPrepFidsum.XAXIS_SHOW,
                          ):
                self.view.update_axes()
                self.view.canvas.draw()

            # note. these need to come before next
            if event_id == util_menu.ViewIdsPrepFidsum.DATA_TYPE_REAL:
                self.view.set_data_type_real()
            if event_id == util_menu.ViewIdsPrepFidsum.DATA_TYPE_IMAGINARY:
                self.view.set_data_type_imaginary()
            if event_id == util_menu.ViewIdsPrepFidsum.DATA_TYPE_MAGNITUDE:
                self.view.set_data_type_magnitude()

            if event_id in (util_menu.ViewIdsPrepFidsum.DATA_TYPE_REAL,
                           util_menu.ViewIdsPrepFidsum.DATA_TYPE_IMAGINARY,
                           util_menu.ViewIdsPrepFidsum.DATA_TYPE_MAGNITUDE,
                           util_menu.ViewIdsPrepFidsum.XAXIS_PPM,
                           util_menu.ViewIdsPrepFidsum.XAXIS_HERTZ,
                          ):
                self.view.update()
                self.view.canvas.draw()

            if event_id in (util_menu.ViewIdsPrepFidsum.AREA_CALC_PLOT_A,
                            util_menu.ViewIdsPrepFidsum.AREA_CALC_PLOT_B,
                           ):
                area, rms = self.view.calculate_area()
                if self._prefs.area_calc_plot_a:
                    index = 0
                else:
                    index = 1
                self.top.statusbar.SetStatusText(util.build_area_text(area[index], rms[index]), 3)
                

    def on_menu_view_output(self, event):
        event_id = event.GetId()

        formats = { util_menu.ViewIdsPrepFidsum.VIEW_TO_PNG : "PNG",
                    util_menu.ViewIdsPrepFidsum.VIEW_TO_SVG : "SVG", 
                    util_menu.ViewIdsPrepFidsum.VIEW_TO_EPS : "EPS", 
                    util_menu.ViewIdsPrepFidsum.VIEW_TO_PDF : "PDF", 
                  }

        if event_id in formats:
            format = formats[event_id]
            lformat = format.lower()
            filter_ = "%s files (*.%s)|*.%s" % (format, lformat, lformat)
            figure = self.view.figure

            filename = common_dialogs.save_as("", filter_)

            if filename:
                msg = ""
                try:
                    figure.savefig( filename,
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
    #           Widget Event Handlers  
    #
    #=======================================================

    def on_splitter(self, event=None):
        # This is sometimes called programmatically, in which case event is None
        self._prefs.sash_position = self.SplitterWindow.GetSashPosition()

    def on_fid_index(self, event): 
        value = event.GetEventObject().GetValue()
        self.fid_index = value - 1
        shft = self.block.frequency_shift[self.fid_index]
        phas = self.block.phase_0[self.fid_index]
        self.FloatPeakShiftValue.SetValue(shft)        
        self.FloatPhase0.SetValue(phas)
        self.process_and_plot()

    def on_gaussian_apodization(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.gaussian_apodization = value
        self.process_and_plot()

    def on_fid_left_shift(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.fid_left_shift = value
        self.process_and_plot()

    def on_fid_left_shift_b0(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.fid_left_shift_b0 = value
        self.process_and_plot()

    def on_fid_left_shift_phase0(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.fid_left_shift_phase0 = value
        self.process_and_plot()

    def on_peak_shift_value(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.frequency_shift[self.fid_index] = value
        self.process_and_plot()
        
    def on_phase0(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.phase_0[self.fid_index] = value
        self.process_and_plot()

    def on_phase1(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.global_phase1 = value
        self.process_and_plot()
        
    def on_apply_peak_shift(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.apply_peak_shift = value
        self.process_and_plot()
        self.update_shift_phase()

    def on_reset_peak_shift(self, event): 
        self.block.frequency_shift *= 0
        self.FloatPeakShiftValue.SetValue(self.block.frequency_shift[self.fid_index])
        self.process_and_plot()
        self.update_shift_phase()

    def on_reference_peak_center(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.reference_peak_center = value
        self.process_and_plot()
        self.update_shift_phase()

    def on_peak_search_width(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.peak_search_width = value
        self.process_and_plot()
        self.update_shift_phase()

    def on_apply_phase0(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.apply_phase0 = value
        self.process_and_plot()
        self.update_shift_phase()

    def on_reset_phase0(self, event): 
        self.block.phase_0 *= 0
        self.FloatPhase0.SetValue(self.block.phase_0[self.fid_index])
        self.process_and_plot()
        self.update_shift_phase()

    def on_phase0_range_start(self, event): 
        # Note. min=End and max=Start because dealing with PPM range
        min, max = _paired_event(self.FloatPhase0RangeEnd,
                                 self.FloatPhase0RangeStart)
        self.block.set.phase0_range_start = max 
        self.block.set.phase0_range_end   = min
        self.process_and_plot()
        self.update_shift_phase()

    def on_phase0_range_end(self, event): 
        # Note. min=End and max=Start because dealing with PPM range
        min, max = _paired_event(self.FloatPhase0RangeEnd,
                                 self.FloatPhase0RangeStart)
        self.block.set.phase0_range_start = max
        self.block.set.phase0_range_end   = min
        self.process_and_plot()
        self.update_shift_phase()

    def on_ref_spectrum_source(self, event): 
        index = event.GetEventObject().GetSelection()
        val = constants.MegalaserRefSpectrumSource.choices.keys()[index]
        self.block.set.ref_spectrum_source = val
        self.process_and_plot()
        self.update_shift_phase()
        if val == 'average_all_fids':
            self.SpinRefPeakLineWidth.Enable(False)
        else:
            self.SpinRefPeakLineWidth.Enable(True)

    def on_ref_peak_line_width(self, event): 
        value = event.GetEventObject().GetValue()
        self.block.set.ref_peak_line_width = value
        self.process_and_plot()
        self.update_shift_phase()

    def on_constant_phase0_offset(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.constant_phase0_offset = value
        self.process_and_plot()
        self.update_shift_phase()

    def update_shift_phase(self):
        shft = self.block.frequency_shift[self.fid_index]
        phas = self.block.phase_0[self.fid_index]
        self.FloatPeakShiftValue.SetValue(shft)        
        self.FloatPhase0.SetValue(phas)


    #=======================================================
    #
    #           Public Methods
    #
    #=======================================================

    def process_and_plot(self, entry='all', do_calculate=True): 
        """
        The process(), plot() and process_and_plot() methods are standard in
        all processing tabs. They are called to update the data in the plot
        results dictionary, the plot_panel in the View side of the tab or both.

        """
        tab_base.Tab.process_and_plot(self, entry)

        self.process(entry=entry, do_calculate=do_calculate)
        self.plot()


    def process(self, entry='all', do_calculate=True):
        """
        Data processing results are stored into the Block inside the Chain,
        but the View results are returned as a dictionary from the Chain.run()
        method. The plot routine takes its inputs from this dictionary.
        
        """
        print 'prep_megalaser - process '+self._tab_dataset.indexAB[0]
        tab_base.Tab.process(self, entry)

        voxel = self.fid_index
        self.plot_results = self.block.chain.run([voxel], 
                                                 entry=entry, 
                                                 do_calculate=do_calculate)
        
        
    def plot(self):
        """
        The set_data() method sets data into the plot_panel_spectrum object
        in the plot in the right panel. 

        """
        if self._plotting_enabled:
            
            print 'prep_megalaser - plot '+self._tab_dataset.indexAB[0]
            
            tab_base.Tab.plot(self)

            results = self.plot_results

            data1 = results['freq_current']         # no phase offset
            data2 = results['freq_summed']          # no phase offset
            data3 = results['freq_summed_offset']   # with constant phase offset added in

            data = [[data1], [data2], [data3]]
            self.view.set_data(data)
            self.view.update(set_scale=not self._scale_intialized)

            if not self._scale_intialized:
                self._scale_intialized = True

            # Calculate the new area after phasing
            area, rms = self.view.calculate_area()
            index = (0 if self._prefs.area_calc_plot_a else 1)
            area = area[index]
            rms = rms[index]

            self.top.statusbar.SetStatusText(util.build_area_text(area, rms), 3)


    #=======================================================
    #
    #           Internal Helper Functions  
    #
    #=======================================================
    

    def _display_header_text(self):
    
        index = self.fid_index
        header = self.dataset.blocks["raw"].headers[index]
        lines = "\nCurrent Header, FID index = "+unicode(index)+"\n" + "-" * 75 + "\n\n"
        lines += unicode(header)
        wx_util.display_text_as_file(lines)

