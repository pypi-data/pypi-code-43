# Python modules
from __future__ import division
import os
import struct
from datetime import datetime


# 3rd party modules
import wx
import numpy as np

# Our modules
import prefs
import util_menu
import util_priorset
import util_priorset_config
import plot_panel_priorset
import dynamic_metabolite_list
import dynamic_macromolecule_list
import dialog_priorset_resolution

import auto_gui.priorset as priorset_ui

import vespa.common.util.ppm as util_ppm
import vespa.common.util.export as util_export
import vespa.common.util.time_ as util_time
import vespa.common.util.math_ as util_math
import vespa.common.util.fileio as util_fileio
import vespa.common.wx_gravy.util as wx_util
import vespa.common.configobj as configobj
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.mrs_data_raw as mrs_data_raw

from vespa.common.constants import DEGREES_TO_RADIANS


#------------------------------------------------------------------------------

def _calculate_linewidth(ta, tb):
    """
    creates an on resonance FID with the Voigt (Ta/Tb) decay envelope
    specified, then FFTs to spectral domain and finds full width at
    half max linewidth of the single peak.
    
    """
    xx = np.arange(2000)/100.0
    val = -(xx/ta + (xx/tb)**2)
    lineshape = util_math.safe_exp(val)
    peak = np.fft.fft(lineshape) / len(lineshape)
    peak /= peak[0]
    
    # Calculate FWHM
    for i in range(1000):
        if peak[i] < 0.5:
            return i / 10.0
    return i / 10.0
    

def _chop(data):
    """ 
    Alternates points between positive and negative. That is, even points 
    are multiplied by 1 and odd points are multiplied by -1
    """
    return data * ((((np.arange(len(data)) + 1) % 2) * 2) - 1)


    



class TabPriorset(priorset_ui.PriorsetUI):
    
    def __init__(self, outer_notebook, top, priorset=None):

        priorset_ui.PriorsetUI.__init__(self, outer_notebook)
        
        # global attributes

        self.top                = top
        self.parent             = outer_notebook
        self.priorset           = priorset

        self._prefs = prefs.PrefsMain()
        
        self.dataymax               = 1.0          # used for zoom out
        self.vertical_scale         = 1.0
        
        # values used in plot and export routines, filled in process()
        self.display_noise_in_plot  = True      
        self.metabolites_all        = None      
        self.metabolites_sum        = None
        self.metabolites_time_all   = None
        self.metabolites_time_sum   = None
        self.baseline_all           = None
        self.baseline_sum           = None
        self.baseline_time_all      = None
        self.baseline_time_sum      = None
        self.noise_freq             = None
        self.noise_time             = None
        self.last_export_filename   = ''
        
        self.plotting_enabled = False

        self.initialize_controls()        
        self.populate_controls()
        
        self.plotting_enabled = True
        
        # plot_init creates placeholder line2D objects in each of 
        # the 3 axes that were created to display results
#        self.plot_init()
        self.process_and_plot(set_scale=True)

        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy, self)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self.on_splitter, self.SplitterWindow)

        # Under OS X, wx sets the sash position to 10 (why 10?) *after*
        # this method is done. So setting the sash position here does no
        # good. We use wx.CallAfter() to (a) set the sash position and
        # (b) fake an EVT_SPLITTER_SASH_POS_CHANGED.
        wx.CallAfter(self.SplitterWindow.SetSashPosition, 
                     self._prefs.sash_position, True)

    @property
    def view_mode(self):
        return (3 if self._prefs.plot_view_all else 1)


    ##### GUI Setup Handlers ##################################################

    def initialize_controls(self):
        """ 
        This methods goes through the widgets and sets up certain sizes
        and constraints for those widgets. This method does not set the 
        value of any widget except insofar that it is outside a min/max
        range as those are being set up. 
        
        Use populate_controls() to set the values of the widgets from
        a data object.
        """

        # calculate a few useful values
        
        priorset = self.priorset
        dim0, dim1, dim2, dim3 = priorset.dims
        sw      = priorset.sw
        hpp     = sw / dim0
        resppm  = priorset.resppm
        freq    = priorset.frequency
        ppm_min = util_ppm.pts2ppm(dim0-1, priorset)
        ppm_max = util_ppm.pts2ppm(0,      priorset)
        
        # The many controls on various tabs need configuration of 
        # their size, # of digits displayed, increment and min/max. 

        wx_util.configure_spin(self.FloatScale, 70, 4, None, (0.0001, 1000))
        self.FloatScale.multiplier = 1.1
        
        wx_util.configure_spin(self.SpinIndex1, 60, None, None, (1,priorset.loop_dims[1]))
        wx_util.configure_spin(self.SpinIndex2, 60, None, None, (1,priorset.loop_dims[2]))
        wx_util.configure_spin(self.SpinIndex3, 60, None, None, (1,priorset.loop_dims[3]))

        wx_util.configure_spin(self.FloatTb, 70, 3, 0.01, (0.001, 1000))
        wx_util.configure_spin(self.FloatPhase0, 70, 2, 5, (-360,360))
        wx_util.configure_spin(self.FloatPhase1, 70, 2, 100, (-10000,10000))
        wx_util.configure_spin(self.FloatPhase1Pivot, 70, 2, 0.5, (ppm_min,ppm_max))
        wx_util.configure_spin(self.FloatB0Shift, 70, 2, 5, (-10000,10000))        
        wx_util.configure_spin(self.SpinLeftShift, 70, None, None, (0,dim0-1))
        wx_util.configure_spin(self.FloatRefPeakArea,  70, 3, 0.5, (0.0,10000.0))
        wx_util.configure_spin(self.FloatRefPeakTa, 70, 3, 0.01, (0,1000.0))
        wx_util.configure_spin(self.FloatRefPeakTb, 70, 3, 0.01, (0,1000.0))
        wx_util.configure_spin(self.FloatNoiseRmsMultiplier, 70, 2, 5, (0.0000001,1000000.0))
        wx_util.configure_spin(self.SpinMonteCarloVoxels, 70, None, None, (1,10000))



    def populate_controls(self):
        """ 
        Populates the widgets with relevant values from the data object. 
        It's meant to be called when a new data object is loaded.
        
        This function trusts that the data object it is given doesn't violate
        any rules. Whatever is in the data object gets slapped into the 
        controls, no questions asked. 
        
        """
        priorset = self.priorset
        loop     = self.priorset.loop

        hpp = priorset.hpp


        #############################################################
        # Dataset View setup 
        #############################################################

        self.view = plot_panel_priorset.PlotPanelPriorset(  self.PanelPriorsetPlot, 
                                        self,
                                        self.parent,
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
                                        props_cursor=dict(alpha=0.3, facecolor='gray'),
                                        xscale_bump=0.0,
                                        yscale_bump=0.05,
                                        data=[],
                                        prefs=self._prefs,
                                        dataset=self.priorset,
                                     )
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelPriorsetPlot.SetSizer(sizer)
        self.view.Fit() 
#        self.view.set_color( (255,255,255) )   

        #############################################################
        # Global controls            
        #############################################################
            
        self.TextData.SetValue(self.priorset.experiment.name)
        
        self.FloatScale.SetValue(self.vertical_scale)
        self.SpinIndex1.SetValue(loop[0]+1)
        self.SpinIndex2.SetValue(loop[1]+1)
        self.SpinIndex3.SetValue(loop[2]+1)

        #############################################################
        # Spectral settings controls            
        #############################################################
        
        self.FloatTb.SetValue(priorset.tb)
        self.FloatPhase0.SetValue(self.priorset.phase0)
        self.FloatPhase1.SetValue(self.priorset.phase1)
        self.FloatPhase1Pivot.SetValue(self.priorset.phase_1_pivot)
        self.FloatB0Shift.SetValue(self.priorset.b0shift)
        self.FloatRefPeakArea.SetValue(self.priorset.noise_ref_peak_area)
        self.FloatRefPeakTa.SetValue(self.priorset.noise_ref_peak_ta)
        self.FloatRefPeakTb.SetValue(self.priorset.noise_ref_peak_tb)
        self.FloatNoiseRmsMultiplier.SetValue(self.priorset.noise_rms_multiplier)
        self.SpinMonteCarloVoxels.SetValue(self.priorset.montecarlo_voxels)

        self.CheckDisplayNoiseInPlot.SetValue(self.display_noise_in_plot)
        self.TextLinewidth.SetLabel("%.3f" % (_calculate_linewidth(priorset.ta,priorset.tb),))
        self.TextEffectiveLinewidth.SetLabel("%.3f" % (_calculate_linewidth(priorset.noise_ref_peak_ta,priorset.noise_ref_peak_tb),))
        
        #############################################################
        # Metabolite signal controls            
        #
        # - set up Metabolite dynamic list
        #############################################################

        # The list grid sizer is marked so we can find it at run-time
        self.MetaboliteGridSizer = self.LabelMetabolites.GetContainingSizer()
        grid_parent = self.LabelMetabolites.GetParent()
        self.LabelMetabolites.Destroy()
        
        # By setting the row count to 0, we signal to wx that we will let it 
        # decide how many rows the grid sizer needs.
        self.MetaboliteGridSizer.Clear()
        self.MetaboliteGridSizer.SetRows(0)

        # Add headings to the first row of the grid sizer.
        headings = ( "Metabolites", "Area Scale\nFactor", "T2 (Ta) Decay\n[sec]")
        
        for heading in headings:
            if heading:
                label = wx.StaticText(grid_parent, label=heading, style=wx.ALIGN_CENTRE)
                self.MetaboliteGridSizer.Add(label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)  
            else:
                self.MetaboliteGridSizer.AddSpacer( 1 )
                
        self.dynamic_metabolite_list = dynamic_metabolite_list.DynamicMetaboliteList( self.PanelMetaboliteLines,
                                                                                      self,
                                                                                      self.MetaboliteGridSizer,
                                                                                      self.priorset)        
        

        #############################################################
        # set up Macromolecule dynamic list
        #############################################################

        # The list grid sizer is marked so we can find it at run-time
        self.MacromoleculeGridSizer = self.LabelBaselines.GetContainingSizer()
        grid_parent = self.LabelBaselines.GetParent()
        self.LabelBaselines.Destroy()
        
        # By setting the row count to 0, we signal to wx that we will let it 
        # decide how many rows the grid sizer needs.
        self.MacromoleculeGridSizer.Clear()
        self.MacromoleculeGridSizer.SetRows(0)

        # Add headings to the first row of the grid sizer.
        headings = ( "Peaks", "PPM", "Area Factor", "Linewidth [Hz]")
        
        for heading in headings:
            if heading:
                label = wx.StaticText(grid_parent, label=heading, style=wx.ALIGN_CENTRE)
                self.MacromoleculeGridSizer.Add(label, 0, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)
            else:
                self.MacromoleculeGridSizer.AddSpacer( 1 )
                
        self.dynamic_macromolecule_list = \
                dynamic_macromolecule_list.DynamicMacromoleculeList( self.PanelBaselineLines,
                                                                      self,
                                                                      self.MacromoleculeGridSizer,
                                                                      self.priorset)        
        


    ##### Menu & Notebook Event Handlers ######################################################

    def on_activation(self):
        # This is a faux event handler. wx doesn't call it directly. It's 
        # a notification from my parent (the dataset notebook) to let
        # me know that this tab has become the current one.
        
        # Force the View menu to match the current plot options.
        util_menu.bar.set_menu_from_state(self._prefs.menu_state)
       

    def on_destroy(self, event):
        self._prefs.save()


    def on_menu_view_option(self, event):
        event_id = event.GetId()

        if self._prefs.handle_event(event_id):
            if event_id in (util_menu.ViewIds.ZERO_LINE_SHOW,
                            util_menu.ViewIds.ZERO_LINE_TOP,
                            util_menu.ViewIds.ZERO_LINE_MIDDLE,
                            util_menu.ViewIds.ZERO_LINE_BOTTOM,
                            util_menu.ViewIds.XAXIS_SHOW,
                           ):
                self.view.update_axes()
                self.view.canvas.draw()

            if event_id in (util_menu.ViewIds.DATA_TYPE_REAL,
                            util_menu.ViewIds.DATA_TYPE_IMAGINARY,
                            util_menu.ViewIds.DATA_TYPE_MAGNITUDE,
                            util_menu.ViewIds.DATA_TYPE_SUMMED,
                            util_menu.ViewIds.XAXIS_PPM,
                            util_menu.ViewIds.XAXIS_HERTZ,
                           ):
                if event_id == util_menu.ViewIds.DATA_TYPE_REAL:
                    self.view.set_data_type_real()
                elif event_id == util_menu.ViewIds.DATA_TYPE_IMAGINARY:
                    self.view.set_data_type_imaginary()
                elif event_id == util_menu.ViewIds.DATA_TYPE_MAGNITUDE:
                    self.view.set_data_type_magnitude()
                elif event_id == util_menu.ViewIds.DATA_TYPE_SUMMED:
                    self.view.set_data_type_summed(index=[1,2])

                self.view.update(no_draw=True)
                self.view.set_phase_0(0.0, no_draw=True)
                self.view.canvas.draw()

            if event_id in (util_menu.ViewIds.PLOT_VIEW_FINAL,
                            util_menu.ViewIds.PLOT_VIEW_ALL,
                           ):
                if event_id == util_menu.ViewIds.PLOT_VIEW_FINAL:
                    self.view.change_naxes(1)
                else:
                    self.view.change_naxes(3)
            

    def on_menu_view_output(self, event):

        event_id = event.GetId()

        formats = { util_menu.ViewIds.VIEW_TO_PNG : "PNG",
                    util_menu.ViewIds.VIEW_TO_SVG : "SVG", 
                    util_menu.ViewIds.VIEW_TO_EPS : "EPS", 
                    util_menu.ViewIds.VIEW_TO_PDF : "PDF", 
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


        if event_id in (util_menu.ViewIds.EXPERIMENT_TO_TEXT,):
            experiment = self.priorset.experiment
            lines = unicode(experiment)
            lines += "\n\nVespa Simulation Experment Results\n" + "-" * 75 + "\n\n"
            lines += "\n".join([simulation.summary() for simulation in experiment.simulations])
            wx_util.display_text_as_file(lines)


    ########## Widget Event Handlers ####################    
    
    def on_scale(self, event):
        view = self.view
        scale = self.FloatScale.GetValue()
        if scale > view.vertical_scale:
            view.set_vertical_scale(1.0, scale_mult=1.1)
        else:
            view.set_vertical_scale(-1.0, scale_mult=1.1)
        self.FloatScale.SetValue(view.vertical_scale)



    def on_index1(self, event):
        # Sets the index of the loop if the prior file has more than one loop
        self.priorset.loop[0] = self.SpinIndex1.GetValue()-1
        self.process_and_plot()

    def on_index2(self, event):
        # Sets the index of the loop if the prior file has more than one loop
        self.priorset.loop[1] = self.SpinIndex2.GetValue()-1
        self.process_and_plot()

    def on_index3(self, event):
        # Sets the index of the loop if the prior file has more than one loop
        self.priorset.loop[2] = self.SpinIndex3.GetValue()-1
        self.process_and_plot()
        

    def on_set_spectral_resolution(self, event):

        priorset = self.priorset
        pts       = priorset.dims[0]
        sw        = priorset.sw
        frequency = priorset.frequency
        ppm_start = self.priorset.mets_ppm_start
        ppm_end   = self.priorset.mets_ppm_end

        dialog = dialog_priorset_resolution.DialogPriorsetResolution(self, 
                                                                     sw, 
                                                                     pts, 
                                                                     frequency, 
                                                                     ppm_start, 
                                                                     ppm_end)
        if dialog.ShowModal() == wx.ID_OK:
            
            self.priorset.sw        = dialog.sweep_width
            self.priorset.dims[0]   = int(dialog.points)
            self.priorset.frequency = dialog.frequency
            self.priorset.mets_ppm_start = dialog.ppm_range_start
            self.priorset.mets_ppm_end   = dialog.ppm_range_end

            wx.SetCursor(wx.HOURGLASS_CURSOR)
            self.priorset.calculate_basis()
            self.update_macromolecule_basis()
            self.process_and_plot()
            wx.SetCursor(wx.NullCursor)
            
        dialog.Destroy()


    def on_splitter(self, event):
        self._prefs.sash_position = self.SplitterWindow.GetSashPosition()


    def on_tb(self, event):
        self.priorset.tb = self.FloatTb.GetValue()
        self.TextLinewidth.SetLabel("%.3f" % (_calculate_linewidth(self.priorset.ta,self.priorset.tb),))
        self.process_and_plot()

    def on_phase0(self, event):
        # Sets the 0th order phase for display
        val = self.FloatPhase0.GetValue()
        self.priorset.phase0 = val
        self.view.set_phase_0(val, absolute=True)
        self.view.canvas.draw()        

    def on_phase1(self, event):
        # Sets the 1th order phase for display
        val = self.FloatPhase1.GetValue()
        self.priorset.phase1 = val
        self.view.set_phase_1(val, absolute=True)
        self.view.canvas.draw()        

    def on_phase_1_pivot(self, event):
        # Sets the 1th order phase pivot location for display
        val = self.FloatPhase1Pivot.GetValue()
        self.priorset.phase_1_pivot = val
        # next line just refreshes the plot with new pivot
        self.view.set_phase_1(0.0, absolute=False)
        self.view.canvas.draw()        

    def on_b0_shift(self, event):
        # Sets the B0 shift in Hz for display
        self.priorset.b0shift = self.FloatB0Shift.GetValue()
        self.process_and_plot()

    def on_left_shift(self, event):
        # Sets the left shift in pts for display
        self.priorset.left_shift = self.SpinLeftShift.GetValue()
        self.process_and_plot()

    def on_display_noise_in_plot(self, event):    
        self.display_noise_in_plot = self.CheckDisplayNoiseInPlot.GetValue()
        self.process_and_plot()
        self.TextEffectiveSnr.SetLabel("%.3f" % (self.snr_actual),)

    def on_ref_peak_area(self, event):
        self.priorset.noise_ref_peak_area = self.FloatRefPeakArea.GetValue()
        self.process_and_plot()
        self.TextEffectiveSnr.SetLabel("%.3f" % (self.snr_actual),)

    def on_ref_peak_ta(self, event):
        self.priorset.noise_ref_peak_ta = self.FloatRefPeakTa.GetValue()
        self.process_and_plot()
        self.TextEffectiveSnr.SetLabel("%.3f" % (self.snr_actual),)
        val = _calculate_linewidth(self.priorset.noise_ref_peak_ta,self.priorset.noise_ref_peak_tb)
        self.TextEffectiveLinewidth.SetLabel("%.3f" % (val,))

    def on_ref_peak_tb(self, event):
        self.priorset.noise_ref_peak_tb = self.FloatRefPeakTb.GetValue()
        self.process_and_plot()
        self.TextEffectiveSnr.SetLabel("%.3f" % (self.snr_actual,))
        val = _calculate_linewidth(self.priorset.noise_ref_peak_ta,self.priorset.noise_ref_peak_tb)
        self.TextEffectiveLinewidth.SetLabel("%.3f" % (val,))
    
    def on_noise_rms_multiplier(self, event):
        self.priorset.noise_rms_multiplier = self.FloatNoiseRmsMultiplier.GetValue() 
        self.process_and_plot()
        self.TextEffectiveSnr.SetLabel("%.3f" % (self.snr_actual,))
        

    def on_matrix_size(self, event):
        self.priorset.montecarlo_voxels = self.SpinMonteCarloVoxels.GetValue()

    

    def on_dynamic_metabolite_list(self, event):
        # this is a fudged event called directly from the actual event
        # that occurs inside the dynamic list class.  
        self.TextLinewidth.SetLabel("%.3f" % (_calculate_linewidth(self.priorset.ta,self.priorset.tb),))
        # FIXME - select one of the Ta values here to base LW calc on
        self.process_and_plot()

    def on_select_all(self, event):
        self.dynamic_metabolite_list.select_all()
        self.process_and_plot()

    def on_select_none(self, event):
        self.dynamic_metabolite_list.deselect_all()
        self.process_and_plot()


    def on_dynamic_macromolecule_list(self, event):
        # this is a fudged event called directly from the actual event
        # that occurs inside the dynamic list class. 
        self.update_macromolecule_basis()
        self.process_and_plot()

    def on_select_all_macromolecules(self, event):
        self.dynamic_macromolecule_list.select_all()
        self.update_macromolecule_basis()
        self.process_and_plot()

    def on_select_none_macromolecules(self, event):
        self.dynamic_macromolecule_list.deselect_all()
        self.update_macromolecule_basis()
        self.process_and_plot()

    def on_delete_selected(self, event):
        self.dynamic_macromolecule_list.remove_checked_rows()
        self.update_macromolecule_basis()
        self.process_and_plot()

    def on_add_line(self, event):
        self.dynamic_macromolecule_list.add_row(False, 4.7, 1.0, 20)
        self.update_macromolecule_basis()
        self.process_and_plot()
    
    
    

    

    
    ##### Internal helper functions  ##########################################
    
#    def set_mode(self):
#        self.view.change_naxes(self.view_mode)  
#
#        if self.view_mode == 1:
#            self.view.figure.axes[0].change_geometry(1,1,1)
#        elif self.view_mode == 2:
#            self.view.figure.axes[0].change_geometry(2,1,1)
#            self.view.figure.axes[1].change_geometry(2,1,2)
#        elif self.view_mode == 3:
#            self.view.figure.axes[0].change_geometry(3,1,1)
#            self.view.figure.axes[1].change_geometry(3,1,2)
#            self.view.figure.axes[2].change_geometry(3,1,3)
#        
#        self.view.canvas.draw()         

   
    def update_macromolecule_basis(self):
        flags, ppms, areas, widths = self.dynamic_macromolecule_list.get_macromolecule_settings() 
        self.priorset.mmol_flags = flags
        self.priorset.mmol_ppms = ppms
        self.priorset.mmol_areas = areas
        self.priorset.mmol_widths = widths
        self.priorset.calculate_basis_macromolecule(ppms, areas, widths)

    
    def rms(self, data):
        return np.sqrt(np.sum( (data - np.mean(data))**2 )/(len(data)-1.0) )


    def export_spectrum_to_viff(self, monte_carlo_flag=False):
        default_path = util_priorset_config.get_last_export_path()
        
        filename = common_dialogs.save_as("Save As XML/VIFF (Vespa Interchange File Format)",
                                          "VIFF/XML files (*.xml)|*.xml",
                                          default_path,
                                          self.last_export_filename)        
        if filename:
            priorset = self.priorset
    
            sw   = priorset.sw
            if not monte_carlo_flag:
                dims0 = priorset.dims[0]
                dims1 = 1
            else:
                dims0  = priorset.dims[0]
                dims1  = priorset.montecarlo_voxels            

            val    = 1j * priorset.phase0 * DEGREES_TO_RADIANS
            phase  = np.exp(val)
            
            if not monte_carlo_flag:
                data  = self.metabolites_time_sum.copy() * phase
                base  = self.baseline_time_sum.copy() * phase
                noise = self.noise_time.copy() * phase
                final = (self.metabolites_time_sum + self.baseline_time_sum + self.noise_time).copy() * phase
                snra  = self.snr_actual
                results = [data, base, noise, final]
                for item in results:
                    item.shape = 1,1,1,item.shape[0]
            else:
                data  = np.zeros((1, 1, dims1, dims0), complex)
                base  = np.zeros((1, 1, dims1, dims0), complex)
                final = np.zeros((1, 1, dims1, dims0), complex)
                noise = np.zeros((1, 1, dims1, dims0), complex)
                snra  = np.zeros((dims1,), float)            # actual measured SNR for each voxel

                save_flag = self.display_noise_in_plot
                self.display_noise_in_plot = True

                for i in range(dims1):
                    self.process()
                    data[0,0,i,:]  = self.metabolites_time_sum.copy()  * phase
                    base[0,0,i,:]  = self.baseline_time_sum.copy() * phase
                    noise[0,0,i,:] = self.noise_time.copy() * phase
                    final[0,0,i,:] = (self.metabolites_time_sum + self.baseline_time_sum + self.noise_time).copy() * phase
                    snra[i]        = self.snr_actual

                results = [data, base, noise, final]
                self.display_noise_in_plot = save_flag


            unames = []
            flags, areas, decays = self.dynamic_metabolite_list.get_metabolite_settings()    
            indx  = np.where(flags)[0]
            if len(indx) > 0:
                unames = np.array(priorset.names)[indx]
                decays = np.array(decays)[indx]
                areas  = np.array(areas)[indx]
            unames = ", ".join(unames)
            areas  = ", ".join([str(val) for val in areas])
            decays = ", ".join([str(val) for val in decays])

            flags, b_ppms, b_areas, b_widths = self.dynamic_macromolecule_list.get_macromolecule_settings()            
            indx = np.where(flags)[0]
            if len(indx) > 0:
                b_ppms   = np.array(b_ppms)[indx]
                b_areas  = np.array(b_areas)[indx]
                b_widths = np.array(b_widths)[indx]
            b_ppms   = ", ".join([str(val) for val in b_ppms])
            b_areas  = ", ".join([str(val) for val in b_areas])
            b_widths = ", ".join([str(val) for val in b_widths])
        
            stamp = util_time.now(util_time.ISO_TIMESTAMP_FORMAT).split('T')
        
            lines     = ['Priorset - An Application for Simulated MRS Data']
            lines.append('------------------------------------------------')
            lines.append('The following information is a summary of the')
            lines.append('settings used to generate the enclosed MRS')
            lines.append('data.')
            lines.append(' ')
            lines.append('Creation_date            - '+stamp[0])
            lines.append('Creation_time            - '+stamp[1])
            lines.append(' ')
            lines.append('Prior Experiment Name    - '+priorset.experiment.name)
            lines.append('Prior Experiment ID      - '+priorset.experiment.id)
            lines.append('Metabolite Names         - '+unames)
            lines.append('Metabolite Area Values   - '+areas)
            lines.append('Metabolite Ta Decays     - '+decays)
            lines.append('Metabolite Tb Decay      - '+str(priorset.tb))
            lines.append('Metabolite Range Start   - '+str(priorset.mets_ppm_start))
            lines.append('Metabolite Range End     - '+str(priorset.mets_ppm_end))
            lines.append('Baseline PPM Values      - '+b_ppms)
            lines.append('Baseline Area Values     - '+b_areas)
            lines.append('Baseline Tb Decay Values - '+b_widths)
            lines.append('Noise RMS Multiplier     - '+str(priorset.noise_rms_multiplier / 100.0))
            lines.append('Noise Ref Peak Area      - '+str(priorset.noise_ref_peak_area))
            lines.append('Noise Ref Peak Ta        - '+str(priorset.noise_ref_peak_ta))
            lines.append('Noise Ref Peak Tb        - '+str(priorset.noise_ref_peak_tb))
            lines.append('Measured SNR (actual)    - '+str(self.snr_actual))
            lines.append('Spectrum Phase0          - '+str(priorset.phase0))
            lines = "\n".join(lines)
            if (wx.Platform == "__WXMSW__"):
                lines = lines.replace("\n", "\r\n")

            datasets = [] 
            msg = ''   
            filename, _ = os.path.splitext(filename)
            out_filenames = [ ]
            for extension in ('metabolites', 'baselines', 'noise', 'summed'):
                out_filenames.append("%s_%s.xml" % (filename, extension))

            for i,item in enumerate(results):
                raw = mrs_data_raw.DataRaw() 
                raw.data_sources = [filename]
                raw.headers = [lines]
                raw.sw = self.priorset.sw
                raw.frequency = self.priorset.frequency
                raw.resppm = self.priorset.resppm
                raw.midppm = self.priorset.midppm
                raw.data = item.copy()
                filename = out_filenames[i]
                try:
                    util_export.export(filename, [raw], None, lines, False)
                except IOError:
                    msg = """I can't write the file "%s".""" % filename
                else:
                    path, _ = os.path.split(filename)
                    util_priorset_config.set_last_export_path(path)
                
                if msg:
                    common_dialogs.message(msg, style=common_dialogs.E_OK)
    
    
    def export_monte_carlo_to_viff(self):

        self.export_spectrum_to_viff(monte_carlo_flag=True)
        return


    def export_spectrum_to_vasf(self):
        """ 
        Generates an rsd output file along with a generic rsp parameter file.
        The generic rsp file is modified using the specific parameters 
        used in creating the spectrum 
        """
        filename = common_dialogs.save_as(filetype_filter="Pick RSD Filename (*.rsd)|*.rsd")
        
        if filename: 
            priorset = self.priorset

            sw    = priorset.sw
            dim0  = priorset.dims[0]
            dim1  = 1            
            dim2  = 1   
            loop  = priorset.loop

            save_flag = self.display_noise_in_plot
            self.display_noise_in_plot = True

            val   = 1j * priorset.phase0 * DEGREES_TO_RADIANS
            phase = np.exp(val)
            
            data  = self.metabolites_time_sum.copy() * phase
            base  = self.baseline_time_sum.copy() * phase
            noise = self.noise_time.copy() * phase
            final = (self.metabolites_time_sum + self.baseline_time_sum + self.noise_time).copy() * phase
            snra  = self.snr_actual
                
            results = [data, base, noise, final]
            self.display_noise_in_plot = save_flag
            
            unames = []
            flags, areas, decays = self.dynamic_metabolite_list.get_metabolite_settings()    
            indx  = np.where(flags)[0]
            if len(indx) > 0:
                unames = np.array(priorset.names)[indx]
                decays = np.array(decays)[indx]
                areas  = np.array(areas)[indx]
            unames = ", ".join(unames)
            areas  = ", ".join([str(val) for val in areas])
            decays = ", ".join([str(val) for val in decays])

            flags, b_ppms, b_areas, b_widths = self.dynamic_macromolecule_list.get_macromolecule_settings()            
            indx = np.where(flags)[0]
            if len(indx) > 0:
                b_ppms   = np.array(b_ppms)[indx]
                b_areas  = np.array(b_areas)[indx]
                b_widths = np.array(b_widths)[indx]
            b_ppms   = ", ".join([str(val) for val in b_ppms])
            b_areas  = ", ".join([str(val) for val in b_areas])
            b_widths = ", ".join([str(val) for val in b_widths])
        
            # Create RSP header - add DisPrior specific info
            stamp = util_time.now(util_time.ISO_TIMESTAMP_FORMAT).split('T')
            ini = configobj.ConfigObj()
            self.fill_blank_form(ini)
        
            section = ini['FILE INFORMATION']
            section['total_data_bytes'] = 8 * dim0 * dim1 * dim2 
            section['data_format'] = 'native'
        
            section = ini['DATA INFORMATION']
            section['data_size_spectral'] = dim0
            section['sweep_width'] = sw
            section['frequency_offset'] = 0.0
            section['data_size_column'] = dim2
            section['data_size_line'] = dim1
        
            section = ini['MEASUREMENT INFORMATION']
            section['frequency'] = priorset.frequency * 1000000.0
            section['sweep_width'] = priorset.sw    
            section['measure_size_spectral'] = dim0
            section['measure_size_column'] = dim2
            section['measure_size_line'] = dim1
        
            section = { }
            section['Prior Source Name'] = priorset.experiment.name
            section['Prior Source ID'] = priorset.experiment.id
            section['Metabolite Names'] = unames
            section['Metabolite Areas'] = areas
            section['Metabolite Ta Decays'] = decays
            section['Metabolite Tb Decay'] = priorset.tb
            section['Metabolite Range Start'] = priorset.mets_ppm_start
            section['Metabolite Range End'] = priorset.mets_ppm_end
            section['Baseline PPM Values'] = b_ppms
            section['Baseline Area Values'] = b_areas
            section['Baseline Tb Decay Values'] = b_widths
            section['Noise RMS Multiplier'] = priorset.noise_rms_multiplier / 100.0
            section['Noise Ref Peak Area'] = priorset.noise_ref_peak_area
            section['Noise Ref Peak Ta'] = priorset.noise_ref_peak_ta
            section['Noise Ref Peak Tb'] = priorset.noise_ref_peak_tb
            section['Measured SNR (actual)'] = self.snr_actual
            section['Spectrum Phase0'] = priorset.phase0
            section['Creation Date'] = stamp[0]
            section['Creation Time'] = stamp[1]
            ini['PRIORSET SIMULATION INFORMATION'] = section
            
            filename, _ = os.path.splitext(filename)
            rsd_filenames = [ ]
            rsp_filenames = [ ]
            for extension in ('metabolites', 'baselines', 'noise', 'summed'):
                rsd_filenames.append("%s_%s.rsd" % (filename, extension))
                rsp_filenames.append("%s_%s.rsp" % (filename, extension))

            for i, item in enumerate(results):
                try:
                    f = open(rsp_filenames[i], "wb")
                    ini.write(outfile=f)
                    f.close()
                    # Analysis cannot read complex 128 bit data, so convert to 
                    # 64 bit data
                    data = np.complex64(item)
                    data.tofile(rsd_filenames[i])
                except IOError:
                    msg = "I was unable to write one or both of the following files:\n"
                    msg += rsp_filenames[i] + '\n'
                    msg += rsd_filenames[i] + '\n'
                    common_dialogs.message(msg, style=common_dialogs.E_OK)        


    def export_spectrum_to_vasf_sid(self):
        """ 
        Generates an sid output file along with a generic sip parameter file.
        The generic sip file is modified using the specific parameters 
        used in creating the spectrum 
        """
        
        filename = common_dialogs.save_as(filetype_filter="Pick SID Filename (*.sid)|*.sid")
        
        if filename: 
            priorset = self.priorset
            
            sw    = priorset.sw
            dim0  = priorset.dims[0]
            dim1  = 1            
            dim2  = 1   
            loop  = priorset.loop

            save_flag = self.display_noise_in_plot
            self.display_noise_in_plot = True

            val   = 1j * priorset.phase0 * DEGREES_TO_RADIANS
            phase = np.exp(val)
            
            data  = self.metabolites_sum.copy() * phase
            base  = self.baseline_sum.copy() * phase
            noise = self.noise_freq.copy() * phase
            final = (self.metabolites_sum + self.baseline_sum + self.noise_freq).copy() * phase
            snra  = self.snr_actual
                
            results = [data, base, noise, final]
            self.display_noise_in_plot = save_flag
            
            unames = []
            flags, areas, decays = self.dynamic_metabolite_list.get_metabolite_settings()    
            indx  = np.where(flags)[0]
            if len(indx) > 0:
                unames = np.array(priorset.names)[indx]
                decays = np.array(decays)[indx]
                areas  = np.array(areas)[indx]
            unames = ", ".join(unames)
            areas  = ", ".join([str(val) for val in areas])
            decays = ", ".join([str(val) for val in decays])

            flags, b_ppms, b_areas, b_widths = self.dynamic_macromolecule_list.get_macromolecule_settings()            
            indx = np.where(flags)[0]
            if len(indx) > 0:
                b_ppms   = np.array(b_ppms)[indx]
                b_areas  = np.array(b_areas)[indx]
                b_widths = np.array(b_widths)[indx]
            b_ppms   = ", ".join([str(val) for val in b_ppms])
            b_areas  = ", ".join([str(val) for val in b_areas])
            b_widths = ", ".join([str(val) for val in b_widths])
        
            # Create RSP header - add DisPrior specific info
            stamp = util_time.now(util_time.ISO_TIMESTAMP_FORMAT).split('T')
            ini = configobj.ConfigObj()
            self.fill_blank_form(ini, form_type='sid')
        
            section = ini['FILE INFORMATION']
            section['total_data_bytes'] = 8 * dim0 * dim1 * dim2 
            section['data_format'] = 'native'
        
            section = ini['DATA INFORMATION']
            section['data_size_spectral'] = dim0
            section['sweep_width'] = sw
            section['frequency_offset'] = 0.0
            section['data_size_column'] = dim2
            section['data_size_line'] = dim1
        
            section = ini['MEASUREMENT INFORMATION']
            section['frequency'] = priorset.frequency * 1000000.0
            section['sweep_width'] = priorset.sw    
            section['measure_size_spectral'] = dim0
            section['measure_size_column'] = dim2
            section['measure_size_line'] = dim1

            section = ini['4DFT PROCESSING INFORMATION']
            section['ft1_size'] = dim0
            section['select1_start'] = 1
            section['select1_points'] = dim0
        
            section = { }
            section['Prior Source Name'] = priorset.experiment.name
            section['Prior Source ID'] = priorset.experiment.id
            section['Metabolite Names'] = unames
            section['Metabolite Areas'] = areas
            section['Metabolite Ta Decays'] = decays
            section['Metabolite Tb Decay'] = priorset.tb
            section['Metabolite Range Start'] = priorset.mets_ppm_start
            section['Metabolite Range End'] = priorset.mets_ppm_end
            section['Baseline PPM Values'] = b_ppms
            section['Baseline Area Values'] = b_areas
            section['Baseline Tb Decay Values'] = b_widths
            section['Noise RMS Multiplier'] = priorset.noise_rms_multiplier / 100.0
            section['Noise Ref Peak Area'] = priorset.noise_ref_peak_area
            section['Noise Ref Peak Ta'] = priorset.noise_ref_peak_ta
            section['Noise Ref Peak Tb'] = priorset.noise_ref_peak_tb
            section['Measured SNR (actual)'] = self.snr_actual
            section['Spectrum Phase0'] = priorset.phase0
            section['Creation Date'] = stamp[0]
            section['Creation Time'] = stamp[1]
            ini['PRIORSET SIMULATION INFORMATION'] = section

            filename, _ = os.path.splitext(filename)
            sid_filenames = [ ]
            sip_filenames = [ ]
            for extension in ('metabolites', 'baselines', 'noise', 'summed'):
                sid_filenames.append("%s_%s.sid" % (filename, extension))
                sip_filenames.append("%s_%s.sip" % (filename, extension))

            for i, item in enumerate(results):
                try:
                    f = open(sip_filenames[i], "wb")
                    ini.write(outfile=f)
                    f.close()
                    # Analysis cannot read complex 128 bit data, so convert to 
                    # 64 bit data
                    data = np.complex64(item)
                    data.tofile(sid_filenames[i])
                except IOError:
                    msg = "I was unable to write one or both of the following files:\n"
                    msg += sid_filenames[i] + '\n'
                    msg += sip_filenames[i] + '\n'
                    common_dialogs.message(msg, style=common_dialogs.E_OK)  
                        
    
    def export_monte_carlo_to_vasf(self):
        """ 
        Generates an rsd output file along with a generic rsp parameter file.
        The generic rsp file is modified using the specific parameters 
        used in creating the spectrum 
        """
        
        filename = common_dialogs.save_as(filetype_filter="Pick RSD Filename (*.rsd)|*.rsd")
        
        if filename: 
            priorset = self.priorset

            sw    = priorset.sw
            dim0  = priorset.dims[0]
            dim1  = priorset.montecarlo_voxels            
            dim2  = 1   
            loop  = priorset.loop

            data  = np.zeros((1, 1, dim1, dim0), complex)
            base  = np.zeros((1, 1, dim1, dim0), complex)
            final = np.zeros((1, 1, dim1, dim0), complex)
            noise = np.zeros((1, 1, dim1, dim0), complex)
            snra  = np.zeros((dim1,), float)            # actual measured SNR for each voxel
            
            save_flag = self.display_noise_in_plot
            self.display_noise_in_plot = True
            
            for i in range(dim1):
                self.process()
                data[0,0,i,:]  = self.metabolites_time_sum 
                base[0,0,i,:]  = self.baseline_time_sum
                noise[0,0,i,:] = self.noise_time
                final[0,0,i,:] = self.metabolites_time_sum + self.baseline_time_sum + self.noise_time
                snra[i]        = self.snr_actual
                
            results = [data, base, noise, final]
            self.display_noise_in_plot = save_flag
            
            unames = []
            flags, areas, decays = self.dynamic_metabolite_list.get_metabolite_settings()    
            indx  = np.where(flags)[0]
            if len(indx) > 0:
                unames = np.array(priorset.names)[indx]
                decays = np.array(decays)[indx]
                areas  = np.array(areas)[indx]
            unames = ", ".join(unames)
            areas  = ", ".join([str(val) for val in areas])
            decays = ", ".join([str(val) for val in decays])

            flags, b_ppms, b_areas, b_widths = self.dynamic_macromolecule_list.get_macromolecule_settings()            
            indx = np.where(flags)[0]
            if len(indx) > 0:
                b_ppms   = np.array(b_ppms)[indx]
                b_areas  = np.array(b_areas)[indx]
                b_widths = np.array(b_widths)[indx]
            b_ppms   = ", ".join([str(val) for val in b_ppms])
            b_areas  = ", ".join([str(val) for val in b_areas])
            b_widths = ", ".join([str(val) for val in b_widths])

        
            # Create RSP header - add Prior specific info
            stamp = util_time.now(util_time.ISO_TIMESTAMP_FORMAT).split('T')
            ini = configobj.ConfigObj()
            self.fill_blank_form(ini)
        
            section = ini['FILE INFORMATION']
            section['total_data_bytes'] = 8 * dim0 * dim1 * dim2 
            section['data_format'] = 'native'
        
            section = ini['DATA INFORMATION']
            section['data_size_spectral'] = dim0
            section['sweep_width'] = sw
            section['frequency_offset'] = 0.0
            section['data_size_column'] = dim2
            section['data_size_line'] = dim1
        
            section = ini['MEASUREMENT INFORMATION']
            section['frequency'] = priorset.frequency * 1000000.0
            section['sweep_width'] = priorset.sw    
            section['measure_size_spectral'] = dim0
            section['measure_size_column'] = dim2
            section['measure_size_line'] = dim1
        
            section = { }
            section['Prior Source Name'] = priorset.experiment.name
            section['Prior Source ID'] = priorset.experiment.id
            section['Metabolite Names'] = unames
            section['Metabolite Areas'] = areas
            section['Metabolite Ta Decays'] = decays
            section['Metabolite Tb Decay'] = priorset.tb
            section['Metabolite Range Start'] = priorset.mets_ppm_start
            section['Metabolite Range End'] = priorset.mets_ppm_end
            section['Baseline PPM Values'] = b_ppms
            section['Baseline Area Values'] = b_areas
            section['Baseline Tb Decay Values'] = b_widths
            section['Noise RMS Multiplier'] = priorset.noise_rms_multiplier / 100.0
            section['Noise Ref Peak Area'] = priorset.noise_ref_peak_area
            section['Noise Ref Peak Ta'] = priorset.noise_ref_peak_ta
            section['Noise Ref Peak Tb'] = priorset.noise_ref_peak_tb
            section['Measured SNR (actual)'] = self.snr_actual
            section['Spectrum Phase0'] = priorset.phase0
            section['Creation Date'] = stamp[0]
            section['Creation Time'] = stamp[1]            
            ini['PRIORSET SIMULATION INFORMATION'] = section

            filename, _ = os.path.splitext(filename)
            rsd_filenames = [ ]
            rsp_filenames = [ ]
            for extension in ('metabolites', 'baselines', 'noise', 'summed'):
                rsd_filenames.append("%s_%s.rsd" % (filename, extension))
                rsp_filenames.append("%s_%s.rsp" % (filename, extension))

            for i, item in enumerate(results):
                try:
                    f = open(rsp_filenames[i], "wb")
                    ini.write(outfile=f)
                    f.close()
                    # Analysis cannot read complex 128 bit data, so convert to 
                    # 64 bit data
                    data = np.complex64(item)
                    data.tofile(rsd_filenames[i])

                except IOError:
                    msg = "I was unable to write one or both of the following files:\n"
                    msg += rsp_filenames[i] + '\n'
                    msg += rsd_filenames[i] + '\n'
                    common_dialogs.message(msg, style=common_dialogs.E_OK)        


    def export_spectrum_to_siemens_rda(self):
        """ 
        Generates Siemens *.RDA formatted fake data
        
        Five files are output, four data and one provenance. The user selects a 
        base filename (fbase) and then extension strings are added to fbase to
        indicate which data is in the file
        
        1. fbase_metabolites - time domain summed metabolite signals, no noise
        2. fbase_baseline    - time domain summed baseline signals, no noise
        3. fbase_noise       - the time domain added noise in the summed data
        4. fbase_summed      - the sum of the three above file, final spectrum
        
        5. fbase_provenance - text file, info about Vespa-Priorset setting used
                              to create the above files. This is created because
                              Siemens RDA has limited ability to store provenance
                              information within its header 
         
        """
        priorset = self.priorset

        filename = common_dialogs.save_as(filetype_filter="Pick Filename for Siemens RDA file (*.rda)|*.rda")
        
        if filename: 

            hdr = self.make_rda_header()

            phase = np.exp(1j * priorset.phase0 * DEGREES_TO_RADIANS)
            
            data  = self.metabolites_time_sum.copy() * phase
            base  = self.baseline_time_sum.copy() * phase
            noise = self.noise_time.copy() * phase
            final = (self.metabolites_time_sum + self.baseline_time_sum + self.noise_time).copy() * phase
            snra  = self.snr_actual
                
            results = [data, base, noise, final]
            
            #-------------------------------------------
            
            filename, _ = os.path.splitext(filename)
            rda_filenames = [ ]
            for extension in ('metabolites', 'baselines', 'noise', 'summed'):
                rda_filenames.append("%s_%s.rda" % (filename, extension))
            fname_provenance = "%s_provenance.txt" % filename

            # write the four numpy results arrays to file
            for i, item in enumerate(results):
                try:
                    # write the header to a file
                    with open(rda_filenames[i], 'w') as f:
                        for line in hdr:
                            f.write("%s\n" % line)
                    
                    # append data after header text
                    format = 'd'
                    item = np.complex128(item)
                    item = item.ravel().tolist()
                    item = util_fileio.expand_complexes(item)
                    item = struct.pack(format * len(item), *item)
                    
                    f = open(rda_filenames[i], 'ab')
                    f.write(item)
                    f.close()
                        
                except IOError:
                    msg = "I was unable to write the following file:\n"
                    msg += rda_filenames[i] + '\n'
                    common_dialogs.message(msg, style=common_dialogs.E_OK)   
                
                # write the Priorset provenance to text file    
                provenance = str(priorset)
                f = open(fname_provenance,'w')
                f.write(provenance)
                f.close()

    def make_rda_header(self):
        
        dt = datetime.now()
        _date = '{:%Y%m%d}'.format(dt)
        _time = '{:%Y%m%d}'.format(dt)

        sw    = self.priorset.sw
        dim0  = self.priorset.dims[0]
        freq  = self.priorset.frequency
        nuc   = '1H'
        field = '0.1'
        if freq > 60 and freq < 68:
            field = '1.5'
        elif freq > 80 and freq < 100:
            field = '2.0'
        elif freq > 120 and freq < 130:
            field = '3.0'
        elif freq > 170 and freq < 190:
            field = '4.0'
        elif freq > 200 and freq < 225:
            field = '4.7'
        elif freq > 290 and freq < 335:
            field = '7.0'
        dwell = 1000000.0 / sw
        
        
        hdr = []
        hdr.append(">>> Begin of header <<<")
        hdr.append("PatientName: Vespa-Priorset Fake Data")
        hdr.append("PatientID: Vespa-Priorset")
        hdr.append("PatientSex: O")
        hdr.append("PatientBirthDate: 19190101")
        hdr.append("StudyDate: {0}".format(_date))
        hdr.append("StudyTime: 100000.000000")
        hdr.append("StudyDescription: Vespa-Priorset Fake Data")
        hdr.append("PatientAge: 050Y")
        hdr.append("PatientWeight: 60.0000")
        hdr.append("SeriesDate: {0}".format(_date))
        hdr.append("SeriesTime: 100000.000000")
        hdr.append("SeriesDescription: Vespa-Priorset Fake Data")
        hdr.append("ProtocolName: Vespa-Priorset Fake Data")
        hdr.append("PatientPosition: HFS")
        hdr.append("SeriesNumber: 1")
        hdr.append("InstitutionName: Vespa-Priorset")
        hdr.append("StationName: Vespa-Priorset")
        hdr.append("ModelName: Vespa-Priorset")
        hdr.append("DeviceSerialNumber: 76543")
        hdr.append("SoftwareVersion[0]: Vespa-Priorset")
        hdr.append("InstanceDate: {0}".format(_date))
        hdr.append("InstanceTime: 100000.000000")
        hdr.append("InstanceNumber: 1")
        hdr.append("InstanceComments: Vespa-Priorset Fake Data")
        hdr.append("AcquisitionNumber: 1")
        hdr.append("SequenceName: {0}".format(self.priorset.experiment.name))
        hdr.append("SequenceDescription: {0}".format(self.priorset.experiment.id))
        hdr.append("TR: 1000.000000")
        hdr.append("TE: 30.000000")
        hdr.append("TM: 0.000000")
        hdr.append("TI: 0.000000")
        hdr.append("DwellTime: {0}".format(str(dwell)))  # sw in Hz, dwell in usec
        hdr.append("EchoNumber: 0")
        hdr.append("NumberOfAverages: 1.000000")
        hdr.append("MRFrequency: {0}".format(str(freq)))            # in MHz
        hdr.append("Nucleus: {0}".format(nuc))                      # string
        hdr.append("MagneticFieldStrength: {0}".format(str(field))) # should be float 1.5 or 3.0 or 7.0 etc.
        hdr.append("NumOfPhaseEncodingSteps: 1")
        hdr.append("FlipAngle: 90.000000")
        hdr.append("VectorSize: {0}".format(dim0))                  # should be int
        hdr.append("CSIMatrixSize[0]: 1")
        hdr.append("CSIMatrixSize[1]: 1")
        hdr.append("CSIMatrixSize[2]: 1")
        hdr.append("CSIMatrixSizeOfScan[0]: 1")
        hdr.append("CSIMatrixSizeOfScan[1]: 1")
        hdr.append("CSIMatrixSizeOfScan[2]: 1")
        hdr.append("CSIGridShift[0]: 0")
        hdr.append("CSIGridShift[1]: 0")
        hdr.append("CSIGridShift[2]: 0")
        hdr.append("HammingFilter: Off")
        hdr.append("FrequencyCorrection: NO")
        hdr.append("TransmitCoil: TxRx_Head")
        hdr.append("TransmitRefAmplitude[1H]: 100.000000")
        hdr.append("SliceThickness: 20.000000")
        hdr.append("PositionVector[0]: 0.000000")
        hdr.append("PositionVector[1]: 0.000000")
        hdr.append("PositionVector[2]: 0.000000")
        hdr.append("RowVector[0]: -1.000000")
        hdr.append("RowVector[1]: 0.000000")
        hdr.append("RowVector[2]: 0.000000")
        hdr.append("ColumnVector[0]: 0.000000")
        hdr.append("ColumnVector[1]: 1.000000")
        hdr.append("ColumnVector[2]: 0.000000")
        hdr.append("VOIPositionSag: 0.000000")
        hdr.append("VOIPositionCor: 0.000000")
        hdr.append("VOIPositionTra: 0.000000")
        hdr.append("VOIThickness: 20.000000")
        hdr.append("VOIPhaseFOV: 20.000000")
        hdr.append("VOIReadoutFOV: 20.000000")
        hdr.append("VOINormalSag: 0.000000")
        hdr.append("VOINormalCor: 0.000000")
        hdr.append("VOINormalTra: 1.000000")
        hdr.append("VOIRotationInPlane: 0.000000")
        hdr.append("FoVHeight: 20.000000")
        hdr.append("FoVWidth: 20.000000")
        hdr.append("FoV3D: 20.000000")
        hdr.append("PercentOfRectFoV: 1.000000")
        hdr.append("NumberOfRows: 1")
        hdr.append("NumberOfColumns: 1")
        hdr.append("NumberOf3DParts: 1")
        hdr.append("PixelSpacingRow: 20.000000")
        hdr.append("PixelSpacingCol: 20.000000")
        hdr.append("PixelSpacing3D: 20.000000")
        hdr.append(">>> End of header <<<")
        
        return hdr

    
    def process_and_plot(self, set_scale=False):
        
        self.process()
        self.plot(set_scale=set_scale)


    def process(self):
        """ 
        Converts spectral (metabolite, macromolecule and noise) signals from 
        ideal time basis functions to spectral domain peaks by applying a line
        shape envelope, scaling and phasing and then applying the FFT.
        
        """
        if not self.plotting_enabled: 
            return

        priorset = self.priorset
        loop     = priorset.loop
        dims     = priorset.dims
        xx       = np.arange(dims[0]) / priorset.sw

        val = 1j * self.priorset.b0shift * 2.0 * np.pi * xx
        b0  = np.exp(val) # in Radians

        ###################################################
        # METABOLITE Section
        #
        # The time signal in both metabs and baseline are have
        # _chop() applied to shift the water signal to
        # the zero frequency location. This is so that the
        # hlsvd algorithm works appropriately. However, this
        # does require the spectral tab to default to _chop ON.

        flags, scales, decays = self.dynamic_metabolite_list.get_metabolite_settings()

        self.priorset.mets_flags = flags
        self.priorset.mets_scales = scales
        self.priorset.mets_decays = decays

        # get the proper loop and metabolite names
        metab_time     = np.zeros((dims[0],), complex)
        metab_freq     = np.zeros((dims[0],), complex)
        metab_freq_sum = np.zeros((dims[0],), complex)
        metab_time_sum = np.zeros((dims[0],), complex)
        indx  = np.where(flags)[0]
        if len(indx) > 0:
            metab_time = priorset.basis[loop[2],loop[1],loop[0],indx,:].copy()
            metab_freq = np.zeros((len(indx),dims[0]), complex)
            ta    = np.array(decays)[indx]
            area  = np.array(scales)[indx]
            val = -(xx/priorset.tb)**2
            lineshape = util_math.safe_exp(val)

            for i,time in enumerate(metab_time):
                val  = -xx/ta[i]
                
                time = time * area[i] * util_math.safe_exp(val) * lineshape * b0

                # apply left_shift early, as per Analysis
                if self.priorset.left_shift:
                    time = np.roll(time, -self.priorset.left_shift)
                    time[-self.priorset.left_shift:] = time[0]*0.0  
                
                #time = time * area[i] * util_math.safe_exp(val) * lineshape * b0
                metab_time[i,:] = _chop(time.copy())  # consistent with Analysis
                time[0] *= 0.5
                metab_freq[i,:] = np.fft.fft(time) / dims[0]     

                if len(indx) > 1:
                    metab_freq_sum = np.sum(metab_freq, axis=0)
                    metab_time_sum = np.sum(metab_time, axis=0)
                else:
                    metab_freq_sum = metab_freq[0,:]
                    metab_time_sum = metab_time[0,:]

        # divide by spectral points so areas match first point in FID
        self.metabolites_all      = metab_freq
        self.metabolites_sum      = metab_freq_sum
        self.metabolites_time_all = metab_time
        self.metabolites_time_sum = metab_time_sum

        ###################################################
        # MACROMOLECULE Section

        base_time     = np.zeros((dims[0],), complex)
        base_freq     = np.zeros((dims[0],), complex)
        base_time_sum = np.zeros((dims[0],), complex)
        base_freq_sum = np.zeros((dims[0],), complex)
        if priorset.macromolecular_basis is not None:
            flags, ppms, areas, widths = self.dynamic_macromolecule_list.get_macromolecule_settings() 
            
            self.priorset.mmol_flags = flags
            self.priorset.mmol_ppms = ppms
            self.priorset.mmol_areas = areas
            self.priorset.mmol_widths = widths
            
            indx = np.where(flags)[0]
            if len(indx) > 0:
                base_time = priorset.macromolecular_basis[indx,:].copy()
                base_freq = np.zeros((len(indx),dims[0]), complex)
                for i, time in enumerate(base_time):
                    time = time.copy() * b0
                    base_time[i,:] = _chop(base_time[i,:]) # consistent with Analysis
                    time[0] *= 0.5
                    base_freq[i,:] = np.fft.fft(time) / dims[0]  

                if len(indx) > 1:
                    base_freq_sum = np.sum(base_freq, axis=0)
                    base_time_sum = np.sum(base_time, axis=0)
                else:
                    base_freq_sum = base_freq[0,:]
                    base_time_sum = base_time[0,:]

        # divide by spectral points so areas match first point in FID
        self.baseline_all         = base_freq
        self.baseline_sum         = base_freq_sum
        self.baseline_time_all    = base_time
        self.baseline_time_sum    = base_time_sum


        ###################################################
        # NOISE Section
            
        self.noise_time = np.zeros(dims[0], complex)
        self.noise_freq = np.zeros(dims[0], complex)
        self.snr_actual = 0.0
        
        if self.display_noise_in_plot:
            ref_peak_area    = priorset.noise_ref_peak_area
            ref_peak_ta      = priorset.noise_ref_peak_ta
            ref_peak_tb      = priorset.noise_ref_peak_tb
            noise_multiplier = priorset.noise_rms_multiplier / 100.0

            val  = -(xx/ref_peak_tb)**2
            val2 = -xx/ref_peak_ta
            nexpo = ref_peak_area * util_math.safe_exp(val) * util_math.safe_exp(val2)
            nexpo[0] *= 0.5
            noise_time = np.random.randn(dims[0]) * noise_multiplier
            rms_noise_time = self.rms(noise_time.real)

            noise_freq     =  np.fft.fft(noise_time) / dims[0]
            noise_time     = _chop(noise_time)   # consistent with Analysis           
            refpeak_height = (np.fft.fft(nexpo) / dims[0]).real[0]
            rms_noise_freq = self.rms(noise_freq.real) 
            snr_actual     = refpeak_height / rms_noise_freq

            # divide by spectral points so areas match first point in FID
            self.noise_freq = noise_freq
            self.noise_time = noise_time
            self.snr_actual = snr_actual


    
    def plot(self, is_replot=False, set_scale=False):
        # The parameter, is_replot, is used to determine if the plot is
        # the initial plot or a replot.  The variable will fix the axis
        # xscale to the full width of the spectrum for the initial plot,
        # and the scale will remain constant if it is a replot.  For
        # example, the xscale should remain constant during phasing, but
        # should reset if a new spectrum is loaded.

        if not self.plotting_enabled: 
            return
        
        if self.metabolites_all is None:
            return

        data1 = {'data' : (self.metabolites_sum + self.baseline_sum + self.noise_freq), 
                 'line_color_real'      : self._prefs.line_color_real,
                 'line_color_imaginary' : self._prefs.line_color_imaginary,
                 'line_color_magnitude' : self._prefs.line_color_magnitude }

        data2 = {'data' : self.metabolites_all, 
                 'line_color_real'      : self._prefs.line_color_metabolite,
                 'line_color_imaginary' : self._prefs.line_color_metabolite,
                 'line_color_magnitude' : self._prefs.line_color_metabolite }

        data3 = {'data' : self.baseline_all, 
                 'line_color_real'      : self._prefs.line_color_baseline,
                 'line_color_imaginary' : self._prefs.line_color_baseline,
                 'line_color_magnitude' : self._prefs.line_color_baseline }

        data = [[data1], [data2], [data3]]
        self.view.set_data(data)
        self.view.update(no_draw=True, set_scale=set_scale)
        self.view.set_phase_0(0.0)


    
    def fill_blank_form(self, ini, form_type='rsd'):
        """ Fills a blank rsp/sip form and outputs ini 
        
            Specifying the section name at the head of each line ensures
            that the line order is maintained all the way to when it is
            written out to file
        """
        
        ini['FILE INFORMATION'] = { }
        ini['FILE INFORMATION']['ascii_header_version'] = '2.50'
        ini['FILE INFORMATION']['data_blocks'] = 1
        ini['FILE INFORMATION']['data_format'] = 'native'
        ini['FILE INFORMATION']['data_type'] = 'complex float'
        ini['FILE INFORMATION']['software_version'] = 'syngo MR 2004A 4VA25A'
        ini['FILE INFORMATION']['total_data_bytes'] = 16384
        ini['FILE INFORMATION']['total_data_sets'] = 1
        
        ini['PATIENT INFORMATION'] = { }
        ini['PATIENT INFORMATION']['patient_name'] = 'default_name'
        ini['PATIENT INFORMATION']['patient_id'] = 'default_id'
        ini['PATIENT INFORMATION']['patient_birthdate'] = '01/01/01  ;(dd/mm/yy)'
        ini['PATIENT INFORMATION']['patient_age'] = 20
        ini['PATIENT INFORMATION']['patient_sex'] = 0
        ini['PATIENT INFORMATION']['patient_weight'] = 80
        ini['PATIENT INFORMATION']['study_code'] = 'default_code'
        
        ini['IDENTIFICATION INFORMATION'] = { }
        ini['IDENTIFICATION INFORMATION']['bed_move_date'] = '01/01/01  ;(dd/mm/yy)'
        ini['IDENTIFICATION INFORMATION']['bed_move_time'] = '00:00:00  ;(h:mm:ss)'
        ini['IDENTIFICATION INFORMATION']['bed_move_fraction'] = 0.0
        ini['IDENTIFICATION INFORMATION']['comment_1'] = ''
        ini['IDENTIFICATION INFORMATION']['comment_2'] = ''
        ini['IDENTIFICATION INFORMATION']['institution_id'] = ''
        ini['IDENTIFICATION INFORMATION']['measure_date'] = '01/01/01  ;(dd/mm/yy)'
        ini['IDENTIFICATION INFORMATION']['measure_time'] = '00:00:00  ;(h:mm:ss)'
        ini['IDENTIFICATION INFORMATION']['parameter_filename'] = 'default_param'
        ini['IDENTIFICATION INFORMATION']['sequence_filename'] = 'default_seq'
        ini['IDENTIFICATION INFORMATION']['study_type'] = 'default_stytype'
        ini['IDENTIFICATION INFORMATION']['sequence_type'] = 'default_seqtype'
    
        ini['MEASUREMENT INFORMATION'] = { }
        ini['MEASUREMENT INFORMATION']['averages'] = 4
        ini['MEASUREMENT INFORMATION']['echo_position'] = 0.0
        ini['MEASUREMENT INFORMATION']['echo_time'] = 44.0
        ini['MEASUREMENT INFORMATION']['flip_angle'] = 90
        ini['MEASUREMENT INFORMATION']['frequency'] = 123190064
        ini['MEASUREMENT INFORMATION']['image_contrast_mode'] = 'unknown'
        ini['MEASUREMENT INFORMATION']['inversion_time_1'] = 0.0
        ini['MEASUREMENT INFORMATION']['kspace_mode'] = 'unknown'
        ini['MEASUREMENT INFORMATION']['measured_slices'] = 1
        ini['MEASUREMENT INFORMATION']['measured_echoes'] = 1
        ini['MEASUREMENT INFORMATION']['nucleus'] = '1H'
        ini['MEASUREMENT INFORMATION']['prescans'] = 4
        ini['MEASUREMENT INFORMATION']['receiver_gain'] = 0.0
        ini['MEASUREMENT INFORMATION']['ft_scale_factor'] = 1.0
        ini['MEASUREMENT INFORMATION']['receiver_coil'] = 'CP_HEAD'
        ini['MEASUREMENT INFORMATION']['repetition_time_1'] = 1500.0
        ini['MEASUREMENT INFORMATION']['saturation_bands'] = 0
        ini['MEASUREMENT INFORMATION']['sweep_width'] = 2000.0
        ini['MEASUREMENT INFORMATION']['transmitter_voltage'] = 100.0
        ini['MEASUREMENT INFORMATION']['total_duration'] = 12.0
        ini['MEASUREMENT INFORMATION']['image_dimension_line'] = 20.0
        ini['MEASUREMENT INFORMATION']['image_dimension_column'] = 20.0
        ini['MEASUREMENT INFORMATION']['image_dimension_partition'] = 20.0
        ini['MEASUREMENT INFORMATION']['image_position_sagittal'] = 0.0
        ini['MEASUREMENT INFORMATION']['image_position_coronal'] = 0.0
        ini['MEASUREMENT INFORMATION']['image_position_transverse'] = 0.0
        ini['MEASUREMENT INFORMATION']['image_normal_sagittal'] = 0.0
        ini['MEASUREMENT INFORMATION']['image_normal_coronal'] = 0.0
        ini['MEASUREMENT INFORMATION']['image_normal_transverse'] = 1.0
        ini['MEASUREMENT INFORMATION']['image_column_sagittal'] = 1.0
        ini['MEASUREMENT INFORMATION']['image_column_coronal'] = 0.0
        ini['MEASUREMENT INFORMATION']['image_column_transverse'] = 0.0
        ini['MEASUREMENT INFORMATION']['measure_size_spectral'] = 2048
        ini['MEASUREMENT INFORMATION']['measure_size_line'] = 1
        ini['MEASUREMENT INFORMATION']['measure_size_column'] = 1
        ini['MEASUREMENT INFORMATION']['measure_size_partition'] = 1
        ini['MEASUREMENT INFORMATION']['region_dimension_line'] = 20.0
        ini['MEASUREMENT INFORMATION']['region_dimension_column'] = 20.0
        ini['MEASUREMENT INFORMATION']['region_dimension_partition'] = 20.0
        ini['MEASUREMENT INFORMATION']['region_position_sagittal'] = 0.0
        ini['MEASUREMENT INFORMATION']['region_position_coronal'] = 0.0
        ini['MEASUREMENT INFORMATION']['region_position_transverse'] = 0.0
        ini['MEASUREMENT INFORMATION']['slice_distance'] = 0.0
        ini['MEASUREMENT INFORMATION']['slice_thickness'] = 20.0
        
        ini['DATA INFORMATION'] = { }
        ini['DATA INFORMATION']['current_slice'] = 1
        ini['DATA INFORMATION']['number_echoes'] = 1
        ini['DATA INFORMATION']['number_inversions'] = 0
        ini['DATA INFORMATION']['number_slices'] = 1
        ini['DATA INFORMATION']['data_size_spectral'] = 2048
        ini['DATA INFORMATION']['data_size_line'] = 1
        ini['DATA INFORMATION']['data_size_column'] = 1
        ini['DATA INFORMATION']['data_size_partition'] = 1
        ini['DATA INFORMATION']['image_dimension_line'] = 20.0
        ini['DATA INFORMATION']['image_dimension_column'] = 20.0
        ini['DATA INFORMATION']['image_dimension_partition'] = 20.0
        ini['DATA INFORMATION']['image_position_sagittal'] = 0.0
        ini['DATA INFORMATION']['image_position_coronal'] = 0.0
        ini['DATA INFORMATION']['image_position_transverse'] = 0.0
        ini['DATA INFORMATION']['region_position_sagittal'] = 0.0
        ini['DATA INFORMATION']['region_position_coronal'] = 0.0
        ini['DATA INFORMATION']['region_position_transverse'] = 0.0
        ini['DATA INFORMATION']['slice_distance'] = 0.0
        ini['DATA INFORMATION']['slice_thickness'] = 20.0
        ini['DATA INFORMATION']['slice_orientation_pitch'] = 'Tra'
        ini['DATA INFORMATION']['slice_orientation_roll'] = ''
    
        if form_type == 'sid':
            ini['4DFT PROCESSING INFORMATION'] = { }
            ini['4DFT PROCESSING INFORMATION']['processing_date'] = 'Thu Apr 1 00:00:00 2009'
            ini['4DFT PROCESSING INFORMATION']['processing_filename'] = 'test.prc'
            ini['4DFT PROCESSING INFORMATION']['ft_dimensions'] = 'spacetime'
            ini['4DFT PROCESSING INFORMATION']['ft1_size'] = 1024
            ini['4DFT PROCESSING INFORMATION']['select1_start'] = 1
            ini['4DFT PROCESSING INFORMATION']['select1_points'] = 1024
            ini['4DFT PROCESSING INFORMATION']['gm1'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['h2o_filter_len'] = 0
            ini['4DFT PROCESSING INFORMATION']['echo_top_position'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['ft2_size'] = 1
            ini['4DFT PROCESSING INFORMATION']['select2_start'] = 1
            ini['4DFT PROCESSING INFORMATION']['select2_points'] = 1
            ini['4DFT PROCESSING INFORMATION']['voxel_shift2'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['ft3_size'] = 1
            ini['4DFT PROCESSING INFORMATION']['select3_start'] = 1
            ini['4DFT PROCESSING INFORMATION']['select3_points'] = 1
            ini['4DFT PROCESSING INFORMATION']['voxel_shift3'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['do_selection'] = 'preset'
            ini['4DFT PROCESSING INFORMATION']['refselection_start'] = 1
            ini['4DFT PROCESSING INFORMATION']['refselection_end'] = 256
            ini['4DFT PROCESSING INFORMATION']['phase_0_correction'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['phase_1_correction'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['phase_1_center'] = 0
            ini['4DFT PROCESSING INFORMATION']['baseline'] = 'no'
            ini['4DFT PROCESSING INFORMATION']['transpose'] = 0
            ini['4DFT PROCESSING INFORMATION']['ft1_filter'] = 'gaussian'
            ini['4DFT PROCESSING INFORMATION']['filter_value'] = 0.0
            ini['4DFT PROCESSING INFORMATION']['flip1'] = 'no'
            ini['4DFT PROCESSING INFORMATION']['ft2_filter'] = 'none'
            ini['4DFT PROCESSING INFORMATION']['flip2'] = 'no'
            ini['4DFT PROCESSING INFORMATION']['ft3_filter'] = 'none'
            ini['4DFT PROCESSING INFORMATION']['flip3'] = 'no'
            


        
        
            
