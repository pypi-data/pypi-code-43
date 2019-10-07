# Python modules
from __future__ import division
import math
import os
import sys
import time
import tempfile
import webbrowser


# 3rd party modules
import numpy as np
import hlsvdpro
import wx

from pubsub import pub as pubsub
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from wx.lib.mixins.listctrl import ColumnSorterMixin


# Our modules
import vespa.analysis.src.tab_base as tab_base
import vespa.analysis.src.constants as constants
import vespa.analysis.src.util_menu as util_menu
import vespa.analysis.src.prefs as prefs_module
import vespa.analysis.src.util as util
import vespa.analysis.src.util_analysis_config as util_analysis_config
import vespa.analysis.src.dialog_dataset_browser as dialog_dataset_browser
import vespa.analysis.src.plot_panel_spectral as plot_panel_spectral
import vespa.analysis.src.plot_panel_svd_filter as plot_panel_svd_filter
import auto_gui.spectral as spectral
import vespa.analysis.src.functors.funct_ecc as funct_ecc
import vespa.analysis.src.functors.funct_water_filter as funct_watfilt

import vespa.common.util.fileio as util_fileio

import vespa.common.wx_gravy.util as wx_util
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.util.misc as util_misc
import vespa.common.util.ppm as util_ppm

import vespa.common.util.export as util_export
import vespa.common.util.time_ as util_time
import vespa.common.mrs_data_raw as mrs_data_raw

from vespa.common.constants import DEGREES_TO_RADIANS, RADIANS_TO_DEGREES


#------------------------------------------------------------------------------

_HLSVD_RESULTS_DISPLAY_SIZE = 6

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ColumnSorterMixin):
    def __init__(self, _inner_notebook, tab):
        style = wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES
        wx.ListCtrl.__init__(self, _inner_notebook, -1, style=style)
        CheckListCtrlMixin.__init__(self)
        ColumnSorterMixin.__init__(self, _HLSVD_RESULTS_DISPLAY_SIZE)
        self.itemDataMap = {}
        self._tab_dataset = _inner_notebook
        self.tab = tab
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)

    def GetListCtrl(self):
        return self

    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        self.tab.on_check_item(self, index, flag)


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
#  Tab SPECTRAL
#
#------------------------------------------------------------------------------

class TabSpectral(tab_base.Tab, spectral.PanelSpectralUI):
    # This attr allows the notebook to identify this tab. The value of the attr
    # doesn't actually matter; its presence is sufficient.
    IS_SPECTRAL = True

    def __init__(self, tab_dataset, top, block):

        spectral.PanelSpectralUI.__init__(self, tab_dataset.NotebookDataset)
        tab_base.Tab.__init__(self, tab_dataset, top, prefs_module.PrefsSpectral)

        self.top      = top               # application frame
        self.block    = block             # processing object

        self.cursor_span_picks_lines = False

        # the button at bottom of tab can be set to a number of user defined
        # purposes, namely:
        #
        # 1. Automatic Phasing of data
        #
        # 2. Output of current area value to a text file
        #    - each time it is hit a file select dialog comes up
        #    - default file is last filename selected
        #    - if file exists, value is appended, else file created
        #    - both the dataset name, x,y,z voxel numbers, and area values
        #      are saved in a tab delineated text line

        self.user_button_area_fname = ''

        # _svd_scale_intialized performs the same role as
        # tab_base.Tab._scale_intialized (q.v.)
        self._svd_scale_intialized = False

        # Plotting is disabled during some of init. That's because the plot
        # isn't ready to plot, but the population of some controls
        # (e.g. spin controls on the water filter panel) fires their
        # respective change event which triggers a call to plot(). This
        # is a Windows-specific bug.
        # See http://trac.wxwidgets.org/ticket/14583
        # In any case, skipping some calls to plot() will speed things up. =)
        self._plotting_enabled = False
        self.plot_results = None

        # self.plot_C_function refers to either None or a callable object
        # (i.e. a function) that takes two params which are typically the
        # data from plots A & B.
        # The plot_C_map relates the various options to the
        # appropriate function. The functions currently used are so simple
        # that I implement them with anonymous lambda functions
        self.plot_C_map =   {
            util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_NONE      : (lambda a, b: (a+b)*0.0),
            util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_A_MINUS_B : (lambda a, b: a - b),
            util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_B_MINUS_A : (lambda a, b: b - a),
            util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_A_PLUS_B  : (lambda a, b: a + b),
                            }
        # The default plot 3 function is set here
        self.plot_C_function = self.plot_C_map[util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_A_MINUS_B]
        self.plot_C_final = None

        self.initialize_controls()
        self.populate_controls()

        self._plotting_enabled = True

        #------------------------------------------------------------
        # Setup the canvas
        self.process_and_plot()

        #------------------------------------------------------------
        # PubSub subscriptions
        pubsub.subscribe(self.on_check_datasetb_status, "check_datasetb_status")
        pubsub.subscribe(self.on_dataset_keys_change, "dataset_keys_change")

        #------------------------------------------------------------
        # Set window events
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_changed, self.NotebookSpectral)

        # If the sash position isn't recorded in the INI file, we use the
        # arbitrary-ish value of 400.
        if not self._prefs.sash_position_main:
            self._prefs.sash_position_main = 400
        if not self._prefs.sash_position_svd:
            self._prefs.sash_position_svd = 400

        # Under OS X, wx sets the sash position to 10 (why 10?) *after*
        # this method is done. So setting the sash position here does no
        # good. We use wx.CallAfter() to (a) set the sash position and
        # (b) fake an EVT_SPLITTER_SASH_POS_CHANGED.
        wx.CallAfter(self.SplitterWindow.SetSashPosition,
                     self._prefs.sash_position_main, True)
        wx.CallAfter(self.SplitterWindowSvd.SetSashPosition,
                     self._prefs.sash_position_svd, True)
        wx.CallAfter(self.on_splitter)


    @property
    def datasetB(self):
        return self.top.datasets.get(self._tab_dataset.indexAB[1], None)

    @property
    def tabB_spectral(self):
        label = self._tab_dataset.indexAB[1]
        if not label:
            return None
        tab = self._tab_dataset._outer_notebook.get_tab_by_label(label)
        if not tab:
            return None
        tab = tab.get_tab("spectral")
        return tab

    @property
    def do_sync(self):
        sync = self._tab_dataset.sync
        indexB = self._tab_dataset.indexAB[1]
        if indexB and sync:
            return True
        else:
            return False

    @property
    def svd_tab_active(self):
        """Returns True if HLSVD is the active tab on the spectral notebook,
        False otherwise."""
        tab = self.NotebookSpectral.GetPage(self.NotebookSpectral.GetSelection())
        return (tab.Id == self.PanelSvdFilter.Id)


    #=======================================================
    #
    #           GUI Setup Handlers
    #
    #=======================================================

    def initialize_controls(self):
        """
        This methods goes through the widgets and sets up certain sizes
        and constraints for those widgets. This method does not set the
        value of any widget except insofar that it is outside a min/max
        range as those are being set up.

        Use populate_controls() to set the values of the widgets from
        a data object.

        """
        dataset = self.dataset
        dim0, dim1, dim2, dim3 = dataset.spectral_dims
        sw      = dataset.sw
        maxppm  = util_ppm.pts2ppm(0, dataset)
        minppm  = util_ppm.pts2ppm(dim0-1, dataset)
        ppmlim  = (minppm, maxppm)
        
        # Here I set up the spin controls. Some are standard wxSpinCtrls and
        # some are floatspins (from wx.lib.agw.floatspin or wx_common).
        # For some of our variables, the default increment of +/-1 makes
        # sense, but that's not true for all of them. For example, the phase 1
        # spin control changes in increments of 2.
        # These increments are arbitrary and expressed only once in the code
        # below. If you don't like them, feel free to change them.

        wx_util.configure_spin(self.FloatWidth, 70, 3,
                       constants.Apodization.INCREMENT,
                       (constants.Apodization.MIN, constants.Apodization.MAX))

        wx_util.configure_spin(self.FloatFrequency, 70, 3,
                       constants.FrequencyShift.INCREMENT,
                       (constants.FrequencyShift.MIN, constants.FrequencyShift.MAX))

        wx_util.configure_spin(self.FloatAmplitude, 70, 3, None,
                       (constants.AmplitudeMultiplier.MIN, constants.AmplitudeMultiplier.MAX))
        self.FloatAmplitude.multiplier = constants.AmplitudeMultiplier.MULTIPLIER

        wx_util.configure_spin(self.FloatPhase0, 70, 3,
                       constants.Phase_0.INCREMENT,
                       (constants.Phase_0.MIN, constants.Phase_0.MAX))

        wx_util.configure_spin(self.FloatPhase1, 70, 3,
                       constants.Phase_1.INCREMENT,
                       (constants.Phase_1.MIN, constants.Phase_1.MAX))

        wx_util.configure_spin(self.FloatPhase1Pivot, 70, 3,
                       constants.Phase_1.INCREMENT_PIVOT,
                       (constants.Phase_1.MIN_PIVOT, constants.Phase_1.MAX_PIVOT))

        wx_util.configure_spin(self.FloatDcOffset, 70, 3,
                       constants.DcOffset.INCREMENT,
                       (constants.DcOffset.MIN, constants.DcOffset.MAX))

        wx_util.configure_spin(self.SpinKissOff, 70)



        # set up combo selections
        _configure_combo(self.ComboApodization,      constants.Apodization.choices)

        # set up the user function button initial setting
        if self._prefs.user_button_phasing:
            self.ButtonUserFunction.SetLabel(constants.UserButton.AUTOPHASE)
        elif self._prefs.user_button_area:
            self.ButtonUserFunction.SetLabel(constants.UserButton.AREAOUTPUT)

        # Water Filter widget constraints
        #
        # - note. by setting the default value first, we avoid having an event
        #     sent that sets the block attribute to the min value because the
        #     widget's original value was outside min/max range when they're set

        self.SpinFirLength.SetValue(funct_watfilt.FIR_LENGTH_DEFAULT)
        wx_util.configure_spin(self.SpinFirLength, 60, None, None,
                               (funct_watfilt.FIR_LENGTH_MIN,
                                funct_watfilt.FIR_LENGTH_MAX))

        self.FloatFirWidth.SetValue(funct_watfilt.FIR_HALF_WIDTH_DEFAULT)
        wx_util.configure_spin(self.FloatFirWidth, 60, None,
                                funct_watfilt.FIR_HALF_WIDTH_STEP,
                               (funct_watfilt.FIR_HALF_WIDTH_MIN,
                                funct_watfilt.FIR_HALF_WIDTH_MAX))

        self.FloatFirRipple.SetValue(funct_watfilt.FIR_RIPPLE_DEFAULT)
        wx_util.configure_spin(self.FloatFirRipple, 60, None,
                                funct_watfilt.FIR_RIPPLE_STEP,
                               (funct_watfilt.FIR_RIPPLE_MIN,
                                funct_watfilt.FIR_RIPPLE_MAX))

        self.SpinFirExtrapValue.SetValue(funct_watfilt.FIR_EXTRAPOLATION_POINTS_DEFAULT)
        wx_util.configure_spin(self.SpinFirExtrapValue, 60, None, None,
                               (funct_watfilt.FIR_EXTRAPOLATION_POINTS_MIN,
                                funct_watfilt.FIR_EXTRAPOLATION_POINTS_MAX))

        self.SpinHamLength.SetValue(funct_watfilt.HAM_LENGTH_DEFAULT)
        wx_util.configure_spin(self.SpinHamLength, 60, None, None,
                               (funct_watfilt.HAM_LENGTH_MIN,
                                funct_watfilt.HAM_LENGTH_MAX))

        self.SpinHamExtrapValue.SetValue(funct_watfilt.HAM_EXTRAPOLATION_POINTS_DEFAULT)
        wx_util.configure_spin(self.SpinHamExtrapValue, 60, None, None,
                               (funct_watfilt.HAM_EXTRAPOLATION_POINTS_MIN,
                                funct_watfilt.HAM_EXTRAPOLATION_POINTS_MAX))

        #-------------------------------------------------------------
        # Dataset View setup
        #-------------------------------------------------------------

        self.view = plot_panel_spectral.PlotPanelSpectral(self.PanelViewSpectral,
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
        self.PanelViewSpectral.SetSizer(sizer)
        self.view.Fit()
        self.view.change_naxes(1)

        #------------------------------------------------------------
        # SVD tab settings
        #------------------------------------------------------------

        data = self.dataset

        #------------------------------------------------------------
        # View code
        #
        # instantiate the plot_panel_svd_filter into the ViewUI

        self.view_svd = plot_panel_svd_filter.PlotPanelSvdFilter(self.PanelViewSvd,
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
        sizer.Add(self.view_svd, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelViewSvd.SetSizer(sizer)
        self.view_svd.Fit()


        #------------------------------------------------------------
        # Results Control

        self.list_svd_results = CheckListCtrl(self.PanelResults, self)
        sizer = wx.BoxSizer()
        sizer.Add(self.list_svd_results, 1, wx.EXPAND)
        self.PanelResults.SetSizer(sizer)
        self.Fit()

        self.list_svd_results.InsertColumn(0, "Rank", wx.LIST_FORMAT_CENTER)
        self.list_svd_results.InsertColumn(1, "PPM", wx.LIST_FORMAT_CENTER)
        self.list_svd_results.InsertColumn(2, "Freq", wx.LIST_FORMAT_CENTER)
        self.list_svd_results.InsertColumn(3, "Damping", wx.LIST_FORMAT_CENTER)
        self.list_svd_results.InsertColumn(4, "Phase", wx.LIST_FORMAT_CENTER)
        self.list_svd_results.InsertColumn(5, "Area", wx.LIST_FORMAT_CENTER)

        self.list_svd_results.SetColumnWidth(0, 60)
        self.list_svd_results.SetColumnWidth(1, 60)
        self.list_svd_results.SetColumnWidth(2, 80)
        self.list_svd_results.SetColumnWidth(3, 80)
        self.list_svd_results.SetColumnWidth(4, 80)
        self.list_svd_results.SetColumnWidth(5, 80)

        # Manual selection is the default
        self.RadioSvdManual.SetValue(True)


        #------------------------------------------------------------
        # Algorithm Controls

        # Here's our safe hard limit for # of data points.
        min_data_points = hlsvdpro.MAX_SINGULAR_VALUES + 1

        # min_data_points is now in safe territory. Since everything in this
        # code is expressed in powers of 2, we'll keep the same style with
        # min_data_points. Plus it gives us a little margin of error.
        i = 1
        while 2**i < min_data_points:
            i += 1
        min_data_points = 2**i

        # Max # of data points can't be more than the # of points in the data.
        max_data_points = min(hlsvdpro.MAX_DATA_POINTS, data.spectral_dims[0])
        self.SliderDataPoints.SetRange(min_data_points, max_data_points)

        # Range is set; now set value.
#        n_data_points = min(constants.HlsvdDefaults.N_DATA_POINTS, max_data_points)
        n_data_points = min(funct_watfilt.SVD_N_DATA_POINTS, max_data_points)
        self.SliderDataPoints.SetValue(n_data_points)

        # Singular values
#        self.SliderSingularValues.SetRange(1, hlsvdpro.MAX_SINGULAR_VALUES)
        self.SliderSingularValues.SetRange(1, hlsvdpro.MAX_SINGULAR_VALUES)
        self.SliderSingularValues.SetValue(funct_watfilt.SVD_N_SINGULAR_VALUES)

        # There's a lot of ways to change sliders -- dragging the thumb,
        # clicking on either side of the thumb, using the arrow keys to
        # move one tick at a time, and hitting home/end. Fortunately all
        # platforms cook these down into a simple "the value changed" event.
        # Unfortunately it has different names depending on the platform.
        if "__WXMAC__" in wx.PlatformInfo:
            event = wx.EVT_SCROLL_THUMBRELEASE
        else:
            event = wx.EVT_SCROLL_CHANGED

        for slider in (self.SliderDataPoints, self.SliderSingularValues):
                self.Bind(event, self.on_slider_changed, slider)

        wx_util.configure_spin(self.FloatSvdThreshold, 70, 2, 0.1,
                               (constants.SvdThreshold.MIN, constants.SvdThreshold.MAX))

        _configure_combo(self.ComboSvdThresholdUnit, constants.SvdThresholdUnit.choices)

        wx_util.configure_spin(self.FloatSvdExcludeLipidStart, 50, 2, 0.5, ppmlim)
        wx_util.configure_spin(self.FloatSvdExcludeLipidEnd,   50, 2, 0.5, ppmlim)


    def populate_controls(self, preset=False):
        """
        Populates the widgets with relevant values from the data object.
        It's meant to be called when a new data object is loaded.

        This function trusts that the data object it is given doesn't violate
        any rules. Whatever is in the data object gets slapped into the
        controls, no questions asked.

        This function is, however, smart enough to enable and disable
        other widgets depending on settings.

        """
        dataset = self.dataset
        dim0, dim1, dim2, dim3 = dataset.spectral_dims
        voxel   = self._tab_dataset.voxel
        maxppm  = util_ppm.pts2ppm(0, dataset)
        minppm  = util_ppm.pts2ppm(dim0-1, dataset)

        #------------------------------------------------------------
        # ECC Filters

        # (Re)populate the ECC list
        self.ComboEcc.Clear()
        for item in funct_ecc.ECC_MENU_ITEMS:
            self.ComboEcc.Append(item, "")
        if self.block.set.ecc_method == '':
            self.block.set.ecc_method = 'None'
        self.ComboEcc.SetStringSelection(self.block.set.ecc_method)
        if self.block.set.ecc_method == u'None':
            self.PanelEccBrowse.Hide()
        else:
            self.PanelEccBrowse.Show()
            self.TextEccFilename.SetValue(self.block.set.ecc_filename)

        #------------------------------------------------------------
        # Water Filter settings

        # (Re)populate the Water Filter list

        self.ComboWater.Clear()
        for item in funct_watfilt.WATFILT_MENU_ITEMS:
            self.ComboWater.Append(item, "")
        if self.block.set.water_filter_method == '':
            self.block.set.water_filter_method = 'None'
        self.ComboWater.SetStringSelection(self.block.set.water_filter_method)

        # set all the other filter panel widgets to attribute settings
        self.SpinFirLength.SetValue(self.block.set.fir_length)
        self.FloatFirWidth.SetValue(self.block.set.fir_half_width)
        self.FloatFirRipple.SetValue(self.block.set.fir_ripple)
        self.SpinFirExtrapValue.SetValue(self.block.set.fir_extrapolation_point_count)
        self.ComboFirExtrapMethod.Clear()
        for label in funct_watfilt.FIR_EXTRAPOLATION_ALL:
            self.ComboFirExtrapMethod.Append(label, "")
            if self.block.set.fir_extrapolation_method == label:
                # This is the active filter, so I select it in the list
                self.ComboFirExtrapMethod.SetSelection(self.ComboFirExtrapMethod.GetCount() - 1)
        self.SpinFirExtrapValue.Enable(self.block.set.fir_extrapolation_method == 'AR Model')

        self.SpinHamLength.SetValue(self.block.set.ham_length)
        self.SpinHamExtrapValue.SetValue(self.block.set.ham_extrapolation_point_count)
        self.ComboHamExtrapMethod.Clear()
        for label in funct_watfilt.HAM_EXTRAPOLATION_ALL:
            self.ComboHamExtrapMethod.Append(label, "")
            if self.block.set.ham_extrapolation_method == label:
                # This is the active filter, so I select it in the list
                self.ComboHamExtrapMethod.SetSelection(self.ComboHamExtrapMethod.GetCount() - 1)
        self.SpinHamExtrapValue.Enable(self.block.set.ham_extrapolation_method == 'AR Model')

        choice = self.ComboWater.GetStringSelection()
        if choice == 'None' or choice == 'SVD - water filter':
            self.PanelWaterFir.Hide()
            self.PanelWaterHamming.Hide()
        elif choice == 'FIR - water filter':
            self.PanelWaterFir.Show()
            self.PanelWaterHamming.Hide()
        elif choice == 'Hamming - water filter':
            self.PanelWaterFir.Hide()
            self.PanelWaterHamming.Show()

        #------------------------------------------------------------
        # Spectral Control setup

        self.ComboDataB.SetStringSelection(str(self._tab_dataset.indexAB[1]))
        self.CheckSync.Disable()

        self.CheckFlip.SetValue(self.block.set.flip)
        self.CheckFFT.SetValue(self.block.set.fft)
        self.CheckChop.SetValue(self.block.set.chop)

        # Apodization width is disabled if there's no method chosen
        apodize = constants.Apodization.choices[self.block.set.apodization]
        self.ComboApodization.SetStringSelection(apodize)
        self.FloatWidth.SetValue(self.block.set.apodization_width)
        self.FloatWidth.Enable(bool(self.block.set.apodization))
        self.ComboZeroFill.SetStringSelection(str(int(self.block.set.zero_fill_multiplier)))
        self.FloatFrequency.SetValue(self.dataset.get_frequency_shift(voxel))
        self.CheckFreqLock.SetValue(self.block.frequency_shift_lock)
        self.FloatAmplitude.SetValue(self.block.set.amplitude)
        self.FloatPhase0.SetValue(self.dataset.get_phase_0(voxel))
        self.CheckPhaseLock.SetValue(self.block.phase_lock)
        self.FloatPhase1.SetValue(self.dataset.get_phase_1(voxel))
        self.CheckZeroPhase1.SetValue(self.block.phase_1_lock_at_zero)
        self.FloatPhase1Pivot.SetValue(self.block.set.phase_1_pivot)
        self.FloatDcOffset.SetValue(self.block.set.dc_offset)
        self.SpinKissOff.SetValue(self.block.set.kiss_off_point_count)
        self.SpinKissOff.SetRange(0, dataset.raw_dims[0])
        self.CheckCorrectPhase1.SetValue(self.block.set.kiss_off_correction)

        #------------------------------------------------------------
        # SVD tab settings
        #------------------------------------------------------------

        # SVD Algorithm Controls
        self.SliderDataPoints.SetValue(self.block.get_data_point_count(voxel))
        self.SliderSingularValues.SetValue(self.block.get_signal_singular_value_count(voxel))

        # SVD Results Controls
        self.svd_checklist_update()

        self.RadioSvdApplyThreshold.SetValue(self.block.set.svd_apply_threshold)
        self.FloatSvdThreshold.SetValue(self.block.set.svd_threshold)
        if self.block.set.svd_apply_threshold:
            self.FloatSvdThreshold.Enable()
        else:
            self.FloatSvdThreshold.Disable()

        item = constants.SvdThresholdUnit.choices[self.block.set.svd_threshold_unit]
        self.ComboSvdThresholdUnit.SetStringSelection(item)
        if item == 'PPM':
            # threshold value used to be in Hz and allowed to range +/- 200
            #  units can now be PPM, so check if we are outside min/max ppm
            val = self.block.set.svd_threshold
            if val < minppm:
                self.block.set.svd_threshold = minppm
            elif val > maxppm:
                self.block.set.svd_threshold = maxppm
                self.FloatSvdThreshold.SetValue(self.block.set.svd_threshold)
        
        self.CheckSvdExcludeLipid.SetValue(self.block.set.svd_exclude_lipid)
        self.FloatSvdExcludeLipidStart.SetValue(self.block.set.svd_exclude_lipid_start)    
        self.FloatSvdExcludeLipidEnd.SetValue(self.block.set.svd_exclude_lipid_end)
        if self.block.set.svd_exclude_lipid:
            self.FloatSvdExcludeLipidStart.Enable()
            self.FloatSvdExcludeLipidEnd.Enable()
        else:
            self.FloatSvdExcludeLipidStart.Disable()
            self.FloatSvdExcludeLipidEnd.Disable()
            
            



    #=======================================================
    #
    #           Global and Menu Event Handlers
    #
    #=======================================================

    def on_activation(self):
        tab_base.Tab.on_activation(self)

        # these BlockSpectral object values may be changed by other tabs, so
        # update their widget values on activation of this tab
        voxel      = self._tab_dataset.voxel
        freq_shift = self.dataset.get_frequency_shift(voxel)
        phase_0    = self.dataset.get_phase_0(voxel)
        phase_1    = self.dataset.get_phase_1(voxel)
        self.FloatFrequency.SetValue(freq_shift)
        self.FloatPhase0.SetValue(phase_0)
        self.FloatPhase1.SetValue(phase_1)

        # Force re-process when switching from a PreProcess tab in case it has
        # changed. It will also trigger other times, but ...
        self.process_and_plot()


    def on_menu_view_option(self, event):
        event_id = event.GetId()

        if self._prefs.handle_event(event_id):

            if event_id in (util_menu.ViewIdsSpectral.ZERO_LINE_SHOW,
                            util_menu.ViewIdsSpectral.ZERO_LINE_TOP,
                            util_menu.ViewIdsSpectral.ZERO_LINE_MIDDLE,
                            util_menu.ViewIdsSpectral.ZERO_LINE_BOTTOM,
                            util_menu.ViewIdsSpectral.XAXIS_SHOW,
                           ):
                self.view.update_axes()
                self.view_svd.update_axes()
                self.view.canvas.draw()
                self.view_svd.canvas.draw()


            elif event_id in (util_menu.ViewIdsSpectral.DATA_TYPE_REAL,
                              util_menu.ViewIdsSpectral.DATA_TYPE_IMAGINARY,
                              util_menu.ViewIdsSpectral.DATA_TYPE_MAGNITUDE,
                              util_menu.ViewIdsSpectral.DATA_TYPE_SUMMED,
                              util_menu.ViewIdsSpectral.XAXIS_PPM,
                              util_menu.ViewIdsSpectral.XAXIS_HERTZ,
                           ):
                if event_id == util_menu.ViewIdsSpectral.DATA_TYPE_REAL:
                    self.view.set_data_type_real()
                    self.view_svd.set_data_type_real()
                elif event_id == util_menu.ViewIdsSpectral.DATA_TYPE_IMAGINARY:
                    self.view.set_data_type_imaginary()
                    self.view_svd.set_data_type_imaginary()
                elif event_id == util_menu.ViewIdsSpectral.DATA_TYPE_MAGNITUDE:
                    self.view.set_data_type_magnitude()
                    self.view_svd.set_data_type_magnitude()
                elif event_id == util_menu.ViewIdsSpectral.DATA_TYPE_SUMMED:
                    # no effect on main view plots
                    self.view_svd.set_data_type_summed(index=[1])


                self.view.update(no_draw=True)
                self.view.set_phase_0(0.0, no_draw=True)
                self.view_svd.update(no_draw=True)
                self.view_svd.set_phase_0(0.0, no_draw=True)
                self.set_plot_c()
                self.view.canvas.draw()
                self.view_svd.canvas.draw()

            elif event_id in (util_menu.ViewIdsSpectral.AREA_CALC_PLOT_A,
                              util_menu.ViewIdsSpectral.AREA_CALC_PLOT_B,
                              util_menu.ViewIdsSpectral.AREA_CALC_PLOT_C,
                             ):
                area, rms = self.view.calculate_area()
                if self._prefs.area_calc_plot_a:
                    index = 0
                    labl = 'A'
                elif  self._prefs.area_calc_plot_b:
                    index = 1
                    labl = 'B'
                elif  self._prefs.area_calc_plot_c:
                    index = 2
                    labl = 'C'
                self.top.statusbar.SetStatusText(util.build_area_text(area[index], rms[index], plot_label=labl), 3)

            elif event_id in (util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_NONE,
                              util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_A_MINUS_B,
                              util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_B_MINUS_A,
                              util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_A_PLUS_B,
                             ):
                if event_id == util_menu.ViewIdsSpectral.PLOT_C_FUNCTION_NONE:
                    if len(self.view.axes) == 3:
                        if self.datasetB:
                            self.view.change_naxes(2)
                        else:
                            self.view.change_naxes(1)
                else:
                    if len(self.view.axes) != 3:
                        self.view.change_naxes(3)

                self.plot_C_function = self.plot_C_map[event_id]

                self.set_plot_c()
                self.view.canvas.draw()

            elif event_id in (util_menu.ViewIdsSpectral.USER_BUTTON_PHASING,
                              util_menu.ViewIdsSpectral.USER_BUTTON_AREA,
                             ):
                if event_id == util_menu.ViewIdsSpectral.USER_BUTTON_PHASING:
                    label = constants.UserButton.AUTOPHASE
                elif event_id == util_menu.ViewIdsSpectral.USER_BUTTON_AREA:
                    label = constants.UserButton.AREAOUTPUT
                self.ButtonUserFunction.SetLabel(label)



    def on_menu_view_output(self, event):
        event_id = event.GetId()
        
        if event_id == util_menu.ViewIdsSpectral.VIFF_DATA_PLOTA:
            self.dump_to_viff('freq')
        elif event_id == util_menu.ViewIdsSpectral.VIFF_SVD_FIDS_CHECKED_SUM:
            self.dump_to_viff('svd_fids_checked_sum')
        else:
            formats = { util_menu.ViewIdsSpectral.VIEW_TO_PNG : "PNG",
                        util_menu.ViewIdsSpectral.VIEW_TO_SVG : "SVG",
                        util_menu.ViewIdsSpectral.VIEW_TO_EPS : "EPS",
                        util_menu.ViewIdsSpectral.VIEW_TO_PDF : "PDF",
                      }
    
            if event_id in formats:
                format = formats[event_id]
                lformat = format.lower()
                filter_ = "%s files (*.%s)|*.%s" % (format, lformat, lformat)
    
                if self.svd_tab_active:
                    figure = self.view_svd.figure
                else:
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
    
            elif event_id == util_menu.ViewIdsSpectral.PLOTS_TO_BINARY:
                filename = common_dialogs.save_as("", "BIN files (*.bin)|*.bin")
                if filename:
                    dataA = self.view.get_data(0)
                    util_fileio.dump_iterable(filename, dataA)
    
            elif event_id == util_menu.ViewIdsSpectral.PLOTS_TO_ASCII:
                filename = common_dialogs.save_as("", "TXT files (*.txt)|*.txt")
                if filename:
                    dataA = self.view.get_data(0)
                    dataA.tofile(filename, sep=' ')


    def on_dataset_keys_change(self, keys):
        """ Pubsub notifications handler. """
        # The list of available datasets has changed so we update the
        # list of datasets available for plot B. We make note of the
        # currently selected item so we can re-select it if it's
        # still in the list.
        _keys = [item for item in keys]
        do_update = False
        if self._tab_dataset.indexAB[0] in _keys:
            # need this if because for some reason a deleted tab is still being
            # reported to by PubSub but 'DatasetX' isn't in the _keys list.
            #
            # next lines removes current dataset from plot B list
            _keys.remove(self._tab_dataset.indexAB[0])
            labels = ["None"] + _keys
            # save current value to see if we can re-select it
            valueB = self.ComboDataB.GetStringSelection()
            self.ComboDataB.SetItems(labels)
            indexB = self.ComboDataB.FindString(valueB)
            if (indexB == wx.NOT_FOUND) or (valueB == "None"):
                # Ooops, the previously selected item is gone.
                indexB = 0
                if valueB != "None":
                    do_update = True
                    self._tab_dataset.sync = False
                    self.CheckSync.SetValue(False)
                    self.CheckSync.Disable()
                    self.view.change_naxes(1)
                valueB = None
    
            self.ComboDataB.SetSelection(indexB)
            self._tab_dataset.indexAB[1] = valueB
    
            if do_update:
                self.process_and_plot()


    def on_check_datasetb_status(self, label):
        """ Pubsub notifications handler. """
        # This gets called after any change to a dataset that requires
        # it to be re-processed. Any other dataset using the referenced
        # dataset will have to update its PlotB
        # 
        # first if checks if the main Dataset tab is still in existence. Had
        # bug where this pubsub was called for a tab being closed.
        if self._tab_dataset.indexAB[0] in self.top.datasets.keys():
            if label == self._tab_dataset.indexAB[1]:
                self.plot()


    def dump_to_viff(self, key):

        msg     = ''
        voxel   = self._tab_dataset.voxel
        dataset = self.dataset 
        if dataset:
            block    = dataset.blocks["spectral"]
            results  = block.chain.run([voxel], entry='viff')
            filename = common_dialogs.save_as("", "XML files (*.xml)|*.xml")
            if filename:

                stamp = util_time.now(util_time.ISO_TIMESTAMP_FORMAT).split('T')
            
                if key == 'freq':
                    lines     = ['Data_Export_from_Analysis_Spectrum_Tab - Data from PlotA']
                elif key == 'svd_fids_checked_sum':
                    lines     = ['Data_Export_from_Analysis_Spectrum_Tab - SVD FIDs Checked Summed']
                lines.append('------------------------------------------------------------------')
                lines.append('Someday I will write something useful here')
                lines.append(' ')
                lines.append('Creation_date            - '+stamp[0])
                lines.append('Creation_time            - '+stamp[1])
                lines.append(' ')
                lines = "\n".join(lines)
                if (sys.platform == "win32"):
                    lines = lines.replace("\n", "\r\n")

                ph0    = dataset.get_phase_0(voxel) * DEGREES_TO_RADIANS
                ph1    = dataset.get_phase_1(voxel) * DEGREES_TO_RADIANS
                piv    = dataset.phase_1_pivot
                dat    = results[key].copy()
                dat[0] *= 2.0
                dim0   = len(dat)
                piv    = (dim0 / 2) - (dataset.frequency * (piv - dataset.resppm) / (dataset.sw/dim0))
                arr1   = (np.arange(dim0) - piv) / dim0

                ph1 = ph1 * arr1
                phase  = np.exp(1j * (ph0 + ph1))
                dat *= phase

                met = mrs_data_raw.DataRaw() 
                met.data_sources = ['analysis_spectrum_tab_data_export']
                met.headers      = [lines]
                met.sw           = dataset.sw
                met.frequency    = dataset.frequency
                met.resppm       = dataset.resppm
                met.midppm       = dataset.midppm
                met.data         = dat
                try:
                    util_export.export(filename, [met], None, lines, False)
                except IOError:
                    msg = """I can't write the file "%s".""" % filename
            
                if msg:
                    common_dialogs.message(msg, style=common_dialogs.E_OK)
                    return
            
                


    #=======================================================
    #
    #           Widget Event Handlers
    #
    #=======================================================

    def on_tab_changed(self, event):
        voxel = self._tab_dataset.voxel
        ph0 = self.dataset.get_phase_0(voxel)
        ph1 = self.dataset.get_phase_1(voxel)
        # refresh the plot in the current sub-tab
        if self.svd_tab_active:
            view = self.view_svd
            view.set_phase_0(ph0, absolute=True)
            view.set_phase_1(ph1, absolute=True)
        else:
            view = self.view
            view.set_phase_0(ph0, index=[0], absolute=True)
            view.set_phase_1(ph1, index=[0], absolute=True)
            if self.tabB_spectral:
                ph0b = self.datasetB.get_phase_0(voxel)
                ph1b = self.datasetB.get_phase_1(voxel)
                view.set_phase_0(ph0b, index=[1], absolute=True)
                view.set_phase_1(ph1b, index=[1], absolute=True)

        self._tab_dataset.FloatScale.SetValue(view.vertical_scale)


    def on_splitter(self, event=None):
        # This is sometimes called programmatically, in which case event is None
        self._prefs.sash_position_main = self.SplitterWindow.GetSashPosition()
        self._prefs.sash_position_svd = self.SplitterWindowSvd.GetSashPosition()


    def on_combo_dataB(self, event):
        val = event.GetEventObject().GetStringSelection()
        if val == "" or val == "None":
            self._tab_dataset.indexAB[1] = None
            self._tab_dataset.sync = False
            self.CheckSync.SetValue(False)
            self.CheckSync.Disable()
            self.view.change_naxes(1)
        else:
            self._tab_dataset.indexAB[1] = val
            if self._prefs.plot_c_function_none:
                self.view.change_naxes(2)
            else:
                self.view.change_naxes(3)
            self.CheckSync.Enable()
            self.process_and_plot('all', 1)


    def on_flip(self, event):
        # flip respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='flip')

    def set_flip(self, value):
        self.block.set.flip = value
        self.CheckFlip.SetValue(value)
        self.process_and_plot()


    def on_fft(self, event):
        # FFT is always the same across datasets regardless of sync A/B
        value = event.GetEventObject().GetValue()
        self.block.set.fft = value
        if self.do_sync:
            self.datasetB.blocks["spectral"].set.fft = value
            self.tabB_spectral.CheckFFT.SetValue(value)
            self.tabB_spectral.process_and_plot()
        self.process_and_plot()


    def on_chop(self, event):
        # chop respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='chop')


    def on_sync(self, event):
        """
        This check should only be turned on if there is a dataset selected for
        plot B. Otherwise this is always turned off.
        """
        value = event.GetEventObject().GetValue()
        self._tab_dataset.sync = value


    def on_ecc_method(self, event=None):
        # ecc method ignores the sync A/B setting
        # This event handler is sometimes called programmatically, in which
        # case event is None. Don't rely on its existence!
        label = event.GetEventObject().GetStringSelection()
        self.block.set.ecc_method = label

        self.top.Freeze()
        if label == u'None':
            self.PanelEccBrowse.Hide()
        else:
            self.PanelEccBrowse.Show()

        self.top.Layout()
        self.PanelSpectral.Layout()
        self.top.Thaw()

        self.process_and_plot()


    def on_ecc_browse(self, event):
        # Allows the user to select an ECC dataset.
        dialog = dialog_dataset_browser.DialogDatasetBrowser(self.top.datasets)
        dialog.ShowModal()
        ecc_dataset = dialog.dataset
        dialog.Destroy()

        if ecc_dataset:
            self.dataset.set_associated_dataset_ecc(ecc_dataset)
            self.TextEccFilename.SetValue(ecc_dataset.blocks["raw"].data_source)
            self.process_and_plot()


    def on_water_method(self, event=None):
        # water filter type ignores the sync A/B setting
        # This event handler is sometimes called programmatically, in which
        # case event is None. Don't rely on its existence!
        label = event.GetEventObject().GetStringSelection()
        self.block.set.water_filter_method = label

        self.top.Freeze()
        if label == 'None' or label == 'SVD - water filter':
            self.PanelWaterFir.Hide()
            self.PanelWaterHamming.Hide()
        elif label == 'FIR - water filter':
            self.PanelWaterFir.Show()
            self.PanelWaterHamming.Hide()
        elif label == 'Hamming - water filter':
            self.PanelWaterFir.Hide()
            self.PanelWaterHamming.Show()

        self.top.Layout()
        self.PanelSpectral.Layout()
        self.top.Thaw()
        self.process_and_plot()


    def on_fir_length(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.fir_length = value
        self.process_and_plot()

    def on_fir_width(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.fir_half_width = value
        self.process_and_plot()

    def on_fir_ripple(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.fir_ripple = value
        self.process_and_plot()

    def on_fir_extrap_method(self, event):
        value = event.GetEventObject().GetStringSelection()
        self.block.set.fir_extrapolation_method = value
        flag = self.block.set.fir_extrapolation_method == 'AR Model'
        self.SpinFirExtrapValue.Enable(flag)
        self.process_and_plot()

    def on_fir_extrap_value(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.fir_extrapolation_point_count = value
        self.process_and_plot()


    def on_ham_length(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.ham_length = value
        self.process_and_plot()

    def on_ham_extrap_method(self, event):
        value = event.GetEventObject().GetStringSelection()
        self.block.set.ham_extrapolation_method = value
        flag = self.block.set.ham_extrapolation_method == 'AR Model'
        self.SpinHamExtrapValue.Enable(flag)
        self.process_and_plot()

    def on_ham_extrap_value(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.ham_extrapolation_point_count = value
        self.process_and_plot()


    def on_frequency_shift_lock(self, event):
        # frequency shift lock respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='frequency_shift_lock')

    def set_frequency_shift_lock(self, value):
        self.block.frequency_shift_lock = value
        self.CheckFreqLock.SetValue(value)


    def on_phase_lock(self, event):
        # phase 0 lock respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='phase_lock')

    def set_phase_lock(self, value):
        self.block.phase_lock = value
        self.CheckPhaseLock.SetValue(value)


    def on_phase1_zero(self, event):
        # phase 1 zero respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='phase1_zero')

    def set_phase1_zero(self, value):
        self.block.phase_1_lock_at_zero = value
        voxel = self._tab_dataset.voxel
        self.dataset.set_phase_1(0.0, voxel)
        self.FloatPhase1.SetValue(0.0)
        self.CheckZeroPhase1.SetValue(value)
        self.process_and_plot( )


    def on_ko_correction(self, event):
        # kiss off correction respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='ko_correction')

    def set_ko_correction(self, value):
        self.block.set.kiss_off_correction = value
        self.CheckCorrectPhase1.SetValue(value)
        self.process_and_plot()


    def on_zero_fill(self, event):
        # zero fill multiplier is always synched across spectra
        zf_value = int(event.GetEventObject().GetStringSelection())

        # reset ALL dataset then ALL gui stuff as needed
        self._tab_dataset._outer_notebook.global_block_zerofill_update(zf_value)
        self._tab_dataset._outer_notebook.global_tab_zerofill_update(zf_value)


    def on_apodization_method(self, event):
        # apodization type ignores the synch A/B setting
        index = event.GetEventObject().GetSelection()
        apodization = constants.Apodization.choices.keys()[index]
        self.block.set.apodization = apodization

        # Enable the value textbox if a method is selected
        self.FloatWidth.Enable(bool(apodization))
        self.process_and_plot()


    def on_apodization_value(self, event):
        # apodization width ignores the sync A/B setting
        value = event.GetEventObject().GetValue()
        self.block.set.apodization_width = value
        self.process_and_plot()


    def on_b0_shift(self, event):
        # frequency shift respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        voxel = self._tab_dataset.voxel
        orig = self.dataset.get_frequency_shift(voxel)
        # we use the notebook level method to deal with this change because it
        # covers all the actions that need to be taken for manual changes
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        self.top.notebook_datasets.global_poll_frequency_shift(poll_labels, value-orig, voxel)


    def on_amplitude(self, event):
        # amplitude multiplier ignores the sync A/B setting
        value = event.GetEventObject().GetValue()
        self.block.set.amplitude = value
        self.process_and_plot()

    def on_phase0(self, event):
        # phase 0 respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        voxel = self._tab_dataset.voxel
        orig = self.dataset.get_phase_0(voxel)
        # we use the notebook level method to deal with this change because it
        # covers all the actions that need to be taken for manual changes
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        self.top.notebook_datasets.global_poll_phase(poll_labels, value-orig, voxel, do_zero=True)

    def on_phase1(self, event):
        # phase 1 respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        voxel = self._tab_dataset.voxel
        orig = self.dataset.get_phase_1(voxel)
        # we use the notebook level method to deal with this change because it
        # covers all the actions that need to be taken for manual changes
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        self.top.notebook_datasets.global_poll_phase(poll_labels, value-orig, voxel, do_zero=False)


    def on_phase1_pivot(self, event):
        # phase 1 pivot respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='phase1_pivot')

    def set_phase1_pivot(self, value):
        self.block.set.phase_1_pivot = value
        self.FloatPhase1Pivot.SetValue(value)
        self.process_and_plot()


    def on_dc_offset(self, event):
        # DC offset respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='dc_offset')

    def set_dc_offset(self, value):
        self.block.set.dc_offset = value
        self.FloatDcOffset.SetValue(value)
        self.process_and_plot()


    def on_kiss_off(self, event):
        # kiss off points respects the sync A/B setting
        value = event.GetEventObject().GetValue()
        nb = self.top.notebook_datasets
        poll_labels = [self._tab_dataset.indexAB[0]]
        if self.do_sync:
            poll_labels = [self._tab_dataset.indexAB[0],self._tab_dataset.indexAB[1]]
        nb.global_poll_sync_event(poll_labels, value, event='kiss_off')

    def set_kiss_off(self, value):
        self.block.set.kiss_off_point_count = value
        self.SpinKissOff.SetValue(value)
        self.process_and_plot()


    def on_user_function(self, event):
        label = event.GetEventObject().GetLabel()

        if label == constants.UserButton.AUTOPHASE:

            freq = self.plot_results['freq']
            phase = util.automatic_phasing(freq)
            voxel = self._tab_dataset.voxel
            self.dataset.set_phase_0(phase, voxel)
            self.FloatPhase0.SetValue(phase)
            self.process_and_plot()

        elif label == constants.UserButton.AREAOUTPUT:

            ini_name = "spectral_output_area_as_csv"
            default_path_name = util_analysis_config.get_path(ini_name)
            default_path, default_fname = os.path.split(default_path_name)
            filetype_filter = "CSV (*.csv)|*.csv"

            filename = common_dialogs.save_as(default_path=default_path,
                                              filetype_filter=filetype_filter,
                                              default_filename=default_fname)
            if filename:
                # Create output header and results strings, check element count.
                # If the file exists, check that the element count is the same in
                # in the last line as for this results line. If it is, just write
                # out the results string. If different length, output both the
                # header and results strings.

                voxel = self._tab_dataset.voxel
                dfname = self.dataset.dataset_filename
                if not dfname:
                    dfname = self.dataset.blocks['raw'].data_sources[voxel[0]]
                dpath, dfname = os.path.split(dfname)
                area, rms = self.view.calculate_area()
                refs      = self.view.ref_locations_ppm()
                if   self._prefs.area_calc_plot_a:
                    labl = 'A'
                    area = area[0]
                    rms  = rms[0]
                elif self._prefs.area_calc_plot_b:
                    labl = 'B'
                    area = area[1]
                    rms  = rms[1]
                elif self._prefs.area_calc_plot_c:
                    labl = 'C'
                    area = area[2]
                    rms  = rms[2]

                xstr = unicode(voxel[0])
                ystr = unicode(voxel[1])
                zstr = unicode(voxel[2])
                sppm = "%.4f" % refs[0]
                eppm = "%.4f" % refs[1]

                hdr = ['Dataset File', 'x', 'y', 'z', 'Plot', 'Start PPM', 'End PPM', 'Area', 'RMS', 'Path']
                val = [dfname, xstr, ystr, zstr, labl, sppm, eppm, unicode(area), unicode(rms), dpath]

                nhdr = len(hdr)
                val = ",".join(val)
                hdr = ",".join(hdr)
                val += "\n"
                hdr += "\n"

                hdr_flag = True
                if os.path.isfile(filename):
                    with open(filename, 'r+') as f:
                        data = f.readlines()
                        if len(data)>1:
                            last = data[-1]
                            nlast = len(last.split(','))
                            if nlast == nhdr:
                                hdr_flag = False

                with open(filename, 'a') as f:
                    if hdr_flag:
                        f.write(hdr)
                    f.write(val)

                # We saved results, so we write the path to the INI file.
                util_analysis_config.set_path(ini_name, filename)



    # start SVD tab event handlers --------------------------------------------

    def on_reset_all(self, event):

        msg = "This will set parameters to default values and erase \nall results. Are you sure you want to continue?"
        if wx.MessageBox(msg, "Reset All Voxels", wx.YES_NO, self) == wx.YES:
            # set all results to 0, turn off all lines. Note. when we replot
            # the current voxel, this will calculate a result for that voxel
            self.block.set_dims(self.dataset)
            self.on_voxel_change(self._tab_dataset.voxel)
            self.process_and_plot()

    def on_slider_changed(self, event):
        # One of the sliders was changed. Each change requires re-applying
        # the HLSVD algorithm.
        # We allow the control to update itself before performing the HLSVD.
        # If we don't, then there can be a noticeable & confusing pause
        # between interacting with the control and seeing it actually change.
        wx.CallAfter(self._apply_hlsvd)

    def on_check_item(self, listctrl, index, flag):
        # Clicking on a check box in the table causes both the Threshold and
        # Exclude Lipid automatic calculations to be turned off. If you are
        # clicking you obviously want a 'manual' mode. No other boxes are set
        # or unset when the Threshold or Exclude Lipid boxes are unchecked,
        # but those algorithms don't run when their flag are off.

        voxel = self._tab_dataset.voxel
        # because the user can sort the list using any column, we need to
        # get the rank value for the item at index that is causing the event,
        # this is the actual index of the line in the block
        block_index = int(self.list_svd_results.GetItemText(index))-1

        svd_output = self.block.get_svd_output(voxel)
        svd_output.in_model[block_index] = flag

        self.block.set.svd_apply_threshold = False
        if self.RadioSvdApplyThreshold.GetValue():
            self.RadioSvdManual.SetValue(True)
        self.FloatSvdThreshold.Disable()
        self.ComboSvdThresholdUnit.Disable()

        self.block.set.svd_exclude_lipid = False
        self.CheckSvdExcludeLipid.SetValue(False)
        self.FloatSvdExcludeLipidStart.Disable()
        self.FloatSvdExcludeLipidEnd.Disable()

        self.process_and_plot()

    def on_svd_manual(self, event):
        self.cursor_span_picks_lines = False
        self.block.set.svd_apply_threshold = False
        self.FloatSvdThreshold.Disable()
        self.ComboSvdThresholdUnit.Disable()

    def on_svd_cursor_span_picks_lines(self, event):
        self.cursor_span_picks_lines = True
        self.block.set.svd_apply_threshold = False
        self.FloatSvdThreshold.Disable()
        self.ComboSvdThresholdUnit.Disable()

    def on_svd_apply_threshold(self, event):
        self.cursor_span_picks_lines = False
        self.block.set.svd_apply_threshold = True
        self.FloatSvdThreshold.Enable()
        self.ComboSvdThresholdUnit.Enable()
        self.process_and_plot()

    def on_svd_threshold(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.svd_threshold = value
        if self.block.set.svd_threshold_unit == 'PPM':
            dataset = self.dataset
            dim0, dim1, dim2, dim3 = dataset.spectral_dims
            maxppm  = util_ppm.pts2ppm(0, dataset)
            minppm  = util_ppm.pts2ppm(dim0-1, dataset)
            # threshold value used to be in Hz and allowed to range +/- 200
            #  units can now be PPM, so check if we are outside min/max ppm
            val = self.block.set.svd_threshold
            if val < minppm:
                self.block.set.svd_threshold = minppm
                self.FloatSvdThreshold.SetValue(self.block.set.svd_threshold)
            elif val > maxppm:
                self.block.set.svd_threshold = maxppm
                self.FloatSvdThreshold.SetValue(self.block.set.svd_threshold)
        self.process_and_plot()

    def on_svd_threshold_unit(self, event):
        index = event.GetEventObject().GetSelection()
        item = constants.SvdThresholdUnit.choices.keys()[index]
        self.block.set.svd_threshold_unit = item

        if self.block.set.svd_threshold_unit == 'PPM':
            dataset = self.dataset
            dim0, dim1, dim2, dim3 = dataset.spectral_dims
            maxppm  = util_ppm.pts2ppm(0, dataset)
            minppm  = util_ppm.pts2ppm(dim0-1, dataset)
            # threshold value used to be in Hz and allowed to range +/- 200
            #  units can now be PPM, so check if we are outside min/max ppm
            if self.block.set.svd_threshold < minppm:
                self.block.set.svd_threshold = minppm
                self.FloatSvdThreshold.SetValue(self.block.set.svd_threshold)
            elif self.block.set.svd_threshold > maxppm:
                self.block.set.svd_threshold = maxppm
                self.FloatSvdThreshold.SetValue(self.block.set.svd_threshold)
        self.process_and_plot()

    def on_svd_exclude_lipid(self, event):
        value = event.GetEventObject().GetValue()
        self.block.set.svd_exclude_lipid = value
        if value:
            self.FloatSvdExcludeLipidStart.Enable()
            self.FloatSvdExcludeLipidEnd.Enable()
        else:
            self.FloatSvdExcludeLipidStart.Disable()
            self.FloatSvdExcludeLipidEnd.Disable()
        self.process_and_plot()

    def on_svd_exclude_lipid_start(self, event):
        # Note. min=End and max=Start because dealing with PPM range
        min, max = _paired_event(self.FloatSvdExcludeLipidEnd,
                                 self.FloatSvdExcludeLipidStart)
        self.block.set.svd_exclude_lipid_start = max 
        self.block.set.svd_exclude_lipid_end   = min
        self.process_and_plot()

    def on_svd_exclude_lipid_end(self, event):
        # Note. min=End and max=Start because dealing with PPM range
        min, max = _paired_event(self.FloatSvdExcludeLipidEnd,
                                 self.FloatSvdExcludeLipidStart)
        self.block.set.svd_exclude_lipid_start = max 
        self.block.set.svd_exclude_lipid_end   = min
        self.process_and_plot()

    def on_all_on(self, event):
        # Spectral water filter HLSVD threshold value will take precedence
        # over this setting if it is on. The change in the in_model array takes
        # place in the process() call to run the chain.
        voxel = self._tab_dataset.voxel
        svd_output = self.block.get_svd_output(voxel)
        svd_output.in_model.fill(True)

        self.block.set.svd_apply_threshold = False
        self.FloatSvdThreshold.Disable()
        if self.RadioSvdApplyThreshold.GetValue():
            self.RadioSvdManual.SetValue(True)

        self.block.set.svd_exclude_lipid = False
        self.CheckSvdExcludeLipid.SetValue(False)
        self.FloatSvdExcludeLipidStart.Disable()
        self.FloatSvdExcludeLipidEnd.Disable()

        self.process_and_plot()

    def on_all_off(self, event):
        # Spectral water filter HLSVD threshold value will take precedence
        # over this setting if it is on. The change in the in_model array takes
        # place in the process() call to run the chain.
        voxel = self._tab_dataset.voxel
        svd_output = self.block.get_svd_output(voxel)
        svd_output.in_model.fill(False)

        self.block.set.svd_apply_threshold = False
        self.FloatSvdThreshold.Disable()
        if self.RadioSvdApplyThreshold.GetValue():
            self.RadioSvdManual.SetValue(True)

        self.block.set.svd_exclude_lipid = False
        self.CheckSvdExcludeLipid.SetValue(False)
        self.FloatSvdExcludeLipidStart.Disable()
        self.FloatSvdExcludeLipidEnd.Disable()
        

        
        self.process_and_plot()


    #=======================================================
    #
    #           Public Methods
    #
    #=======================================================

    def process_and_plot(self, entry='all',
                               dataset_to_process=(0, 1),
                               no_draw=False):
        """
        The process(), plot() and process_and_plot() methods are standard in
        all processing tabs. They are called to update the data in the plot
        results dictionary, the plot_panel in the View side of the tab or both.

        """
        tab_base.Tab.process_and_plot(self, entry)

        if self._plotting_enabled:
            self.process(entry, dataset_to_process)
            self.plot(no_draw=no_draw)
            self.plot_svd(no_draw=no_draw)



    def process(self, entry='all', dataset_to_process=(0,1)):
        """
        Data processing results are stored into the Block inside the Chain,
        but the View results are returned as a dictionary from the Chain.run()
        method. The plot routine takes its inputs from this dictionary.

        The dataset_to_process param can be a single integer or a tuple/list
        in the range (0, 1). It defaults to (0, 1). Since the Spectral tab has
        the option to compare a "datasetB" to the "dataset" in the tab, and
        datasetB can also be synched to the tab's dataset, we may need to
        process both dataset and datasetB for each call to process(). The
        parameter "dataset_to_process" can be set to process either dataset or
        datasetB or both by setting it to a tuple of (0,) or (1,) or (0,1)
        respectively
        """
        tab_base.Tab.process(self, entry)

        if self._plotting_enabled:

            if not util_misc.is_iterable(dataset_to_process):
                # Make it a tuple
                dataset_to_process = (dataset_to_process,)

            # update plot results arrays if required
            voxel = self._tab_dataset.voxel

            for i in dataset_to_process:
                dataset = self.dataset if i==0 else self.datasetB
                tab = self if i==0 else self.tabB_spectral
                if dataset:
                    block = dataset.blocks["spectral"]
                    do_fit = block.get_do_fit(voxel)
                    tab.plot_results = block.chain.run([voxel], entry=entry)

                    if dataset == self.dataset:
                        # refresh the hlsvd sub-tab on the active dataset tab
                        if do_fit:
                            # we changed results, now need to update results widget
                            self.svd_checklist_update()
                        else:
                            # same results, but check boxes may have changed
                            self.set_check_boxes()
                        pubsub.sendMessage("check_datasetb_status",
                                           label=self._tab_dataset.indexAB[0])


    def plot_svd(self, no_draw=False):
        """
        The set_data() method sets data into the plot_panel_spectrum object
        in the plot in the right panel.

        """
        if self._plotting_enabled:
            if not self._tab_dataset.indexAB[0]:
                return

            voxel = self._tab_dataset.voxel
            results = self.plot_results

            data1 = {'data' : results['svd_data'],
                     'line_color_real'      : self._prefs.line_color_real,
                     'line_color_imaginary' : self._prefs.line_color_imaginary,
                     'line_color_magnitude' : self._prefs.line_color_magnitude }

            data2 = {'data' : results['svd_peaks_checked'],
                     'line_color_real'      : self._prefs.line_color_svd,
                     'line_color_imaginary' : self._prefs.line_color_svd,
                     'line_color_magnitude' : self._prefs.line_color_svd }

            data3 = {'data' : results['svd_data'] - results['svd_peaks_checked_sum'],
                     'line_color_real'      : self._prefs.line_color_real,
                     'line_color_imaginary' : self._prefs.line_color_imaginary,
                     'line_color_magnitude' : self._prefs.line_color_magnitude }

            data = [[data1], [data2], [data3]]
            self.view_svd.set_data(data)
            self.view_svd.update(no_draw=True, set_scale=not self._svd_scale_intialized)

            if not self._svd_scale_intialized:
                self._svd_scale_intialized = True

            ph0 = self.dataset.get_phase_0(voxel)
            ph1 = self.dataset.get_phase_1(voxel)
            self.view_svd.set_phase_0(ph0, absolute=True, no_draw=True)
            self.view_svd.set_phase_1(ph1, absolute=True)



    def plot(self, no_draw=False):
        """
        The set_data() method sets data into the plot_panel_spectrum object
        in the plot in the right panel.

        """
        tab_base.Tab.plot(self)

        if self._plotting_enabled:

            #print 'spectral - plot '+self._tab_dataset.indexAB[0]

            voxel  = self._tab_dataset.voxel

            results = self.plot_results
            data1   = results['freq']
            ph0_1   = self.dataset.get_phase_0(voxel)
            ph1_1   = self.dataset.get_phase_1(voxel)

            if self.datasetB:
                resultsB = self.tabB_spectral.plot_results
                data2    = resultsB['freq']
                ph0_2    = self.datasetB.get_phase_0(voxel)
                ph1_2    = self.datasetB.get_phase_1(voxel)
            else:
                data2 = np.zeros_like(data1)
                ph0_2 = 0.0
                ph1_2 = 0.0

            data3 = np.zeros_like(data1)

            # these data will use default line colors in view  data1 == data2
            data = [[data1], [data2], [data3]]
            self.view.set_data(data)
            self.view.update(no_draw=True, set_scale=not self._scale_intialized)

            if not self._scale_intialized:
                self._scale_intialized = True

            # we take this opportunity to ensure that our phase values reflect
            # the values in the block.
            self.view.set_phase_0(ph0_1, absolute=True, no_draw=True, index=[0])
            self.view.set_phase_1(ph1_1, absolute=True, no_draw=True, index=[0])
            self.view.set_phase_0(ph0_2, absolute=True, no_draw=True, index=[1])
            self.view.set_phase_1(ph1_2, absolute=True, no_draw=True, index=[1])

            self.set_plot_c()

            self.view.canvas.draw()

            # Calculate the new area after phasing
            area, rms = self.view.calculate_area()
            if self._prefs.area_calc_plot_a:
                index = 0
                labl = 'A'
            elif  self._prefs.area_calc_plot_b:
                index = 1
                labl = 'B'
            elif  self._prefs.area_calc_plot_c:
                index = 2
                labl = 'C'
            self.top.statusbar.SetStatusText(util.build_area_text(area[index], rms[index], plot_label=labl), 3)


    def set_check_boxes(self):
        """
        This method only refreshes the checkboxes in the current checklist
        widget.

        """
        voxel   = self._tab_dataset.voxel
        num     = self.list_svd_results.GetItemCount()
        svd_output = self.block.get_svd_output(voxel)
        for i in range(num):
            if i < self.list_svd_results.GetItemCount():
                index = int(self.list_svd_results.GetItemText(i))-1
                self.list_svd_results.SetItemImage(i, svd_output.in_model[index])


    def set_chop(self, value):
        self.block.set.chop = value
        self.CheckChop.SetValue(value)
        self.process_and_plot()


    def set_plot_c(self):
        data1 = self.view.all_axes[0].lines[0].get_ydata()
        data2 = self.view.all_axes[1].lines[0].get_ydata()
        data3 = self.plot_C_function(data1, data2)
        self.view.all_axes[2].lines[0].set_ydata(data3)


    def svd_checklist_update(self):
        """
        This method totally rebuilds the result set in the checklist widget.

        Take the hlsvd results for the current voxel and set them into the
        checklist widget. If the spectral tab hlsvd water filter is on and
        has checked the "Apply Threshold" box, then we modify (and save) the
        index values according to the threshold.

        """
        voxel = self._tab_dataset.voxel

        svd_output = self.block.get_svd_output(voxel)

        amp = svd_output.amplitudes
        dam = svd_output.damping_factors
        fre = svd_output.frequencies
        pha = svd_output.phases
        in_model = svd_output.in_model
        nsvd = len(svd_output)

        ppm = self.dataset.resppm - (fre*1000.0/self.dataset.frequency)

        # Update the list_svd_results widget
        if sum(amp) == 0:
            in_model.fill(False)

        res = {}
        self.list_svd_results.DeleteAllItems()
        for i in range(nsvd):
            res[i] = (i + 1, ppm[i], fre[i]*1000, dam[i], pha[i], amp[i])
            index = self.list_svd_results.InsertItem(sys.maxint, ' '+str(res[i][0])+' ')    # bjs_ccx
            self.list_svd_results.SetItemImage(index, in_model[i])
            self.list_svd_results.SetItem(index, 1, '%.2f'%(res[i][1])) # bjs_ccx
            self.list_svd_results.SetItem(index, 2, '%.1f'%(res[i][2])) # bjs_ccx
            self.list_svd_results.SetItem(index, 3, '%.1f'%(res[i][3])) # bjs_ccx
            self.list_svd_results.SetItem(index, 4, '%.1f'%(res[i][4])) # bjs_ccx
            self.list_svd_results.SetItem(index, 5, '%.1f'%(res[i][5])) # bjs_ccx
            self.list_svd_results.SetItemData(index, i)

        self.list_svd_results.itemDataMap = res


    def on_voxel_change(self, voxel):
        # this just updates widgets that vary based on the voxel number
        # selection. We do not update plot here because that is only done
        # for the active tab in the inner notebook.
        freq_shift = self.dataset.get_frequency_shift(voxel)
        phase_0    = self.dataset.get_phase_0(voxel)
        phase_1    = self.dataset.get_phase_1(voxel)
        self.FloatFrequency.SetValue(freq_shift)
        self.FloatPhase0.SetValue(phase_0)
        self.FloatPhase1.SetValue(phase_1)

        self.SliderDataPoints.SetValue(self.block.get_data_point_count(voxel))
        self.SliderSingularValues.SetValue(self.block.get_signal_singular_value_count(voxel))

        self.svd_checklist_update()






    #=======================================================
    #
    #           Internal Helper Functions
    #
    #=======================================================

    def _apply_hlsvd(self):
        # Updates the plot in response to changes in the HLSVD inputs.
        # This exists just so that we can call it via wx.CallAfter().
        voxel = self._tab_dataset.voxel

        n_data_points = self.SliderDataPoints.GetValue()
        n_singular_values = self.SliderSingularValues.GetValue()
        
        self.block.set.svd_last_n_data_points = n_data_points
        self.block.set.svd_last_n_singular_values = n_singular_values

        self.block.set_data_point_count(n_data_points, voxel)
        self.block.set_signal_singular_value_count(n_singular_values, voxel)
        self.block.set_do_fit(True, voxel)
        self.process_and_plot(no_draw=True)
        self.set_check_boxes()







