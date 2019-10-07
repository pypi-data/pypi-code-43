# Python modules
from __future__ import division
import math
import os


# 3rd party modules
import wx
import matplotlib as mpl
import numpy as np

# Our modules
import prefs
import util_menu
import util_rfpulse_config
import plot_panel_transform
import auto_gui.transformation_base as transformation_base
import vespa.common.wx_gravy.common_dialogs as common_dialogs
import vespa.common.constants as constants
        
        
PLOT_PANEL_X_BUMP = 0.02   
PLOT_PANEL_Y_BUMP = 0.1
        

class TabTransformBase(transformation_base.PanelTransformationBase):

    def __init__(self, inner_notebook, left_neighbor, transform):

        transformation_base.PanelTransformationBase.__init__(self, inner_notebook)

        # This tab needs to know who its left neighbor is during init. 
        # Ordinarily we get the left neighbor by asking the notebook 
        # "who is to the left of me?" But during init, the notebook doesn't 
        # know about "me" yet, so the notebook can't find this tab in the 
        # list of tabs and therefore can't determine who is to the left.
        # We resolve this annoyance by having the caller pass in the left 
        # neighbor as a param and stashing it in this attribute. Once init is
        # complete we clear the attribute and ignore it thereafter.
        self._left_neighbor = left_neighbor

        self._inner_notebook = inner_notebook
        self.transform = transform
        self._last_run = { }
        self._last_save = { }
        self._current_focus_id = None
        
        self._prefs = prefs.PrefsMain()

        # local storage for possible profile plot data
        self.profile = None
        self.profile_ext = None
        self.profile_grad_refocus = None

        self.initialize_controls_transformation()
        
        # plot_init creates placeholder line2D objects in each of 
        # the 9 axes that were created to display results
        self.plot_init()
        
        # we default to not showing any axes on initialization
        self.view.display_naxes([False,False,False,False,False,False,False,False,False])
        
        # we call plot here in case this is an existing pulse_project
        # being loaded into memory that already has results to plot.
        self.plot(relim_flag=True)
        
        # Setting the sash position won't work if the containing window 
        # hasn't sized itself yet, and that's the case under GTK and Windows.
        # So we use the CallAfter hack to allow the window to settle down 
        # before the call to SetSashPosition(). Under OSX, the call to 
        # SetSashPosition() works regardless of whether we call it directly
        # here or via wx.CallAfter().
        wx.CallAfter(self.window_splitter.SetSashPosition, 440, True)
        
        self.Layout()   
        self.Fit()

        self.Bind(wx.EVT_WINDOW_DESTROY, self.on_destroy, self)
        self.Bind(wx.EVT_CHILD_FOCUS, self.on_child_focus)


    @property
    def is_saved(self):
        """True if the current input is the same as it was when the tab
        was last saved.
        """
        return self._last_save == self.get_raw_gui_data()


    @property
    def is_synced(self):
        """True if the current input is in sync with the results."""
        if self.transform.result and (self.get_raw_gui_data() == self._last_run):
            # I'm only in sync if my left neighbor is is sync. If not, then
            # the results that were passed to me as input are no longer valid.
            if self.left_neighbor:
                return self.left_neighbor.is_synced
            else:
                return True
        else:
            # Definitely not in sync
            return False


    @property
    def left_neighbor(self):
        """
        Returns the tab that is the left neighbor of this one, or
        None if there is no left neighbor.
        
        """
        # We use self._left_neighbor while it's populated (during init), but
        # not thereafter.
        if self._left_neighbor:
            return self._left_neighbor
        else:
            return self._inner_notebook.get_left_neighbor(self)


    ##### Event Handlers ######################################################

    def on_activation(self):
        # This is a faux event handler. wx doesn't call it directly. It's 
        # a notification from my parent (the experiment notebook) to let
        # me know that this tab has become the current one.
        
        # Force the View menu to match the current plot options.
        util_menu.bar.set_menu_from_state(self._prefs.menu_state)

               
    def on_child_focus(self, event):
        # When the focus changes we take the opportunity to note if the 
        # user has made any changes and, if so, we update the sync status
        # indicator. The project notebook actually does that work; this 
        # is just a trigger.
        
        # The wx doc for wxChildFocusEvent says --
        # "Notice that child window is the direct child of the window 
        # receiving event. Use FindFocus to retrieve [sic] the window which  
        # is actually getting focus."
        recipient = wx.Window.FindFocus()

        # I'm not sure why, but we seem to get a surplus of these messages.
        # Here we ensure that the focus really is somewhere else.
        if self._current_focus_id != recipient.Id:
            # Focus changed
            self._current_focus_id = recipient.Id            
            self._inner_notebook.update_sync_status(self)
                
                
    def on_destroy(self, event):
        self._prefs.save()
                
                
    def on_run(self, event):
        # See documentation here:
        # http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        # Subclasses must override this method.
        pass


    def on_usage(self, event):
        
        use_type = self.ComboUsageType.GetStringSelection()

# bjs-start - temporary comment out to do a release without Grad_Refocus

        use_type = constants.UsageType.get_type_for_value(use_type, 'display')
        
        if use_type == constants.UsageType.EXCITE:
            self.PanelGradRefocus.Show()
        else:
            self.PanelGradRefocus.Hide()
            self.CheckGradRefocus.SetValue(False)
        self.PanelLeftSide.Layout()
        self.PanelLeftSide.Refresh()        
        
        self.plot(update_profiles=True, relim_flag=True)
# bjs-end - temporary comment out to do a release without Grad_Refocus

    def on_check(self, event):
        self.plot()

    def on_check_grad_refocus(self, event):
        result = self.transform.result
        if result:
            self.plot(update_profiles=True)
        
    def on_float_grad_refocus(self, event):
        result = self.transform.result
        if result: 
            self.plot(update_profiles=True, update_refocus=True)

    def on_menu_view_option(self, event):
        event_id = event.GetId()

        if self._prefs.handle_event(event_id):
            if event_id == util_menu.ViewIds.ZERO_LINE_SHOW:
                for i, axes in enumerate(self.view.all_axes):
                    axes.lines[2].set_visible(self._prefs.zero_line_show)
                self.view.canvas.draw()      
        
            elif event_id == util_menu.ViewIds.XAXIS_SHOW:
                for i, axes in enumerate(self.view.all_axes):
                    axes.xaxis.set_visible(self._prefs.xaxis_show)
                self.view.canvas.draw()
        
            elif event_id in (util_menu.ViewIds.DATA_TYPE_REAL,
                              util_menu.ViewIds.DATA_TYPE_REAL_IMAGINARY,
                             ):
                if self.transform and self.transform.result:
                    for i, axes in enumerate(self.view.all_axes):
                        if self._prefs.data_type_real:
                            axes.lines[1].set_visible(False)
                        if self._prefs.data_type_real_imaginary:
                            if i in [0,2,4,8]:
                                axes.lines[1].set_visible(True)
                    self.view.canvas.draw()
                

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


    ##### Internal helper functions  ##########################################

    def accept_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_cooked_gui_data()
        self.transform.parameters.inflate(d)


    def clear_result(self):
        """Destroys this tab's result and forces the plot to redraw."""
        self.transform.result = None
        self.plot()

        
    def complete_init(self, is_new):
        if not is_new:
            self._last_run.update(self.get_raw_gui_data())
            self._last_save.update(self.get_raw_gui_data())

        # We use _left_neighbor during init but not thereafter.
        self._left_neighbor = None


    def get_cooked_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        return self.get_raw_gui_data()
        
        
    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # We stash the Python id of my result and my left neighbor's 
        # result in the raw GUI data. It's a bit of a hack, mitigated 
        # (not really) by the fact that I hide the keys by prefixing them
        # with an underscore.
        if hasattr(self.left_neighbor, "transform") and \
           self.left_neighbor.transform:
            left_neighbor_result_id = id(self.left_neighbor.transform.result)
        else:
            left_neighbor_result_id = id(None)

        if self.transform and self.transform.result:
            my_result_id = id(self.transform.result)
        else:
            my_result_id = id(None)
            
        return  { "_left_neighbor_result_id" : left_neighbor_result_id, 
                  "_my_result_id"            : my_result_id,
                }


    def initialize_controls_transformation(self):
        
        self.ComboUsageType.Clear()        
        self.ComboUsageType.AppendItems( \
                            [constants.UsageType.EXCITE['display'], \
                             constants.UsageType.INVERSION['display'], \
                             constants.UsageType.SATURATION['display'], \
                             constants.UsageType.SPIN_ECHO['display']])

        # Small hack for OS X problem -- this combobox believes it is sized
        # correctly but paints itself only about 15 pixels wide. Slightly
        # altering the size gives OS X the nudge it needs to render it 
        # correctly. I'm sure there's a more elegant solution but I had 
        # trouble finding one.
        x, y = self.ComboUsageType.GetSize()
        self.ComboUsageType.SetMinSize( (x - 1, y) )
       
        # Add a plot_panel to right splitter window
        self.view = plot_panel_transform.PlotPanelTransform(self.PanelRhs,
                                                naxes=9,
                                                reversex=False,
                                                zoom='box', 
                                                reference=True,
                                                unlink=True,
                                                do_zoom_select_event=False,
                                                do_zoom_motion_event=True,
                                                do_refs_select_event=False,
                                                do_refs_motion_event=True,
                                                xscale_bump = PLOT_PANEL_X_BUMP,
                                                yscale_bump = PLOT_PANEL_Y_BUMP,
                                                props_zoom=dict(alpha=0.2, facecolor='yellow'),
                                                props_cursor=dict(alpha=0.1, facecolor='gray') )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.view, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelRhs.SetSizer(sizer)
        self.view.Fit()    

        self.view.figure.set_facecolor('white')
        for axes in self.view.axes:
            axes.set_facecolor(self._prefs.bgcolor)
            mpl.artist.setp(axes.axes.xaxis, visible=True)
            self.view.figure.subplots_adjust(left=0.12,right=0.98,
                                               bottom=0.05,top=0.95,
                                               wspace=0.0,hspace=0.3)
        
        # default plot settings on startup for all transforms
        self.CheckWaveform.SetValue(True)        
        self.ComboUsageType.SetStringSelection(constants.UsageType.EXCITE['display'])

        if not self.transform.result:
            grad_refocus_fraction = 0.0
        else:
            grad_refocus_fraction = self.transform.result.grad_refocus_fraction

        result = self.transform.result
        if result:
            if grad_refocus_fraction == 0.0:
                result.gradient_refocusing()
                grad_refocus_fraction = result.grad_refocus_fraction
            else:
                result.gradient_refocusing(grad_refocus_fraction)
            self.profile_grad_refocus = result.refocused_profile

        self.FloatGradRefocus.SetMinSize((75, -1))
        self.FloatGradRefocus.SetSize((75, -1))
        self.FloatGradRefocus.SetDigits(5)
        self.FloatGradRefocus.SetIncrement(0.0005)
        self.FloatGradRefocus.SetRange(0.0, 1.0)
        self.FloatGradRefocus.SetValue(grad_refocus_fraction)      

        self.PanelGradRefocus.Hide()

# bjs-start - temporary comment out to do release without Grad_Refocus

        use_type = self.ComboUsageType.GetStringSelection()
        use_type = constants.UsageType.get_type_for_value(use_type, 'display')
        if use_type == constants.UsageType.EXCITE:
            self.PanelGradRefocus.Show()
        else:
            self.PanelGradRefocus.Hide()

# bjs-end - temporary comment out to do a release without Grad_Refocus

    def on_save(self):
        self._last_save = self.get_raw_gui_data()


    def plot(self, update_profiles=False, relim_flag=False, update_refocus=False):            
        '''
        Here we either update the data in each axes in the plot_panel or just
        select which ones to display in the figure. If "update_profiles" is
        True then we go through each axes, calculate the profile and extended
        profile based on the usage_type and then plot the real, imag and zero
        line into lines[0], [1] and [2] respectively. We then go through and
        make lines visible or not and xaxis on/off depending on prefs.
        '''
        if not self.transform or not self.transform.result:
            # Clear the plot.
            for axes in self.view.all_axes:
                for line in axes.lines:
                    line.set_visible(False)
                axes.xaxis.set_visible(False)
    
            self.view.canvas.draw()
            return
        
        checks = []
        checks.append(self.CheckProfile.IsChecked())
        checks.append(self.CheckAbsolute.IsChecked())
        checks.append(self.CheckProfileExtended.IsChecked())
        checks.append(self.CheckAbsoluteExtended.IsChecked())
        checks.append(self.CheckGradient.IsChecked())
        checks.append(self.CheckWaveform.IsChecked())
        checks.append(self.CheckWaveformMagn.IsChecked())
        checks.append(self.CheckWaveformPhase.IsChecked())
#        checks.append(self.CheckContour.IsChecked())
        checks.append(self.CheckGradRefocus.IsChecked())
        # tell the view which plot axes to include in the figure
        self.view.display_naxes(checks)
        naxes = len(self.view.figure.axes) 
        
        if naxes == 0: return
        
        fsize = ['medium','medium','small','small','x-small','x-small','x-small','x-small','x-small']
        fsize = fsize[naxes-1]
        use_type = self.ComboUsageType.GetStringSelection()
        use_type = constants.UsageType.get_type_for_value(use_type, 'display')

        if update_profiles != False or self.profile == None or self.profile_ext == None:
            result = self.transform.result
            self.profile     = result.get_profile(use_type, False, False)
            self.profile_ext = result.get_profile(use_type, True, False)
            if self.CheckGradRefocus.GetValue():
                grad_value = self.FloatGradRefocus.GetValue()
                if grad_value == 0.0:
                    result.gradient_refocusing()
                    self.FloatGradRefocus.SetValue(result.grad_refocus_fraction)
                else:
                    result.gradient_refocusing(grad_value)
                self.profile_grad_refocus = result.refocused_profile
            if self.profile_grad_refocus is None:
                 self.profile_grad_refocus = self.profile[0] * 0.0
            
            # :FIXME: For the next 4 plots .. Will these 
            # always be in Frequency or will we allow it 
            # in spatial coordinates (e.g. millimeters).

            # Frequency Profile  
            fy, fx = self.profile
            fx0 = np.array(fx)
            fx1 = np.array(fx)
            fy0 = np.array([i.real for i in fy])            
            fy1 = np.array([i.imag for i in fy])
            axes = self.view.all_axes[0]
            axes.lines[0].set_xdata(fx0)
            axes.lines[0].set_ydata(fy0)
            axes.lines[1].set_xdata(fx1)
            axes.lines[1].set_ydata(fy1)

            # Absolute Frequency Profile
            fy, fx = self.profile 
            fy = abs(fy)
            axes = self.view.all_axes[1]
            axes.lines[0].set_xdata(np.array(fx))
            axes.lines[0].set_ydata(np.array([i.real for i in fy]))
            axes.lines[1].set_visible(False)

            # Extended Frequency Profile  
            fy, fx = self.profile_ext
            axes = self.view.all_axes[2]
            axes.lines[0].set_xdata(np.array(fx))
            axes.lines[0].set_ydata(np.array([i.real for i in fy]))
            axes.lines[1].set_xdata(np.array(fx))
            axes.lines[1].set_ydata(np.array([i.imag for i in fy]))

            # Extended Absolute Frequency Profile  
            fy, fx = self.profile_ext
            fy = abs(fy)
            axes = self.view.all_axes[3]
            axes.lines[0].set_xdata(np.array(fx))
            axes.lines[0].set_ydata(np.array([i.real for i in fy]))
            axes.lines[1].set_visible(False)

            # Gradient Waveform
            fy, fx = result.get_gradient()
            fx0 = np.array([t*1000 for t in fx])
            axes = self.view.all_axes[4]
            axes.lines[0].set_xdata(np.array(fx0))
            axes.lines[0].set_ydata(np.array(fy))
            axes.lines[1].set_visible(False)

            # Time Waveform
            fx = result.rf.waveform_x_axis
            fy = result.rf.waveform
            fx0 = np.array([t*1000 for t in fx])
            fx1 = np.array([t*1000 for t in fx])
            
            # Multiply by 1000 to convert to microtesla.
            fy0 = np.array([i.real*1000 for i in fy])            
            fy1 = np.array([i.imag*1000 for i in fy])
            
            # Next 4 lines added so that plot of results spans
            # the total time desired: Each point represents a value 
            # for a time period equal to the dwell time.
            # Note this is similar to what J.M. does in Matpulse.
            # see MATPULSE/CPLANE/MCLB1FIG.M
            # e.g.
            # % To make stairs look 'right'
            # k = length(b1) ;    
            # c1 = 1000*real(b1) ;
            # c1(k+1) = c1(k) ;
            # d1 = 1000*imag(b1) ;
            # d1(k+1) = d1(k) ;
            fx0 = np.append(fx0, fx0[-1] + result.dwell_time/1000)
            fx1 = np.append(fx1, fx1[-1] + result.dwell_time/1000)
            fy0 = np.append(fy0, fy0[-1])
            fy1 = np.append(fy1, fy1[-1])
            
            axes = self.view.all_axes[5]  
            axes.lines[0].set_xdata(fx0)
            axes.lines[0].set_ydata(fy0)
            axes.lines[1].set_xdata(fx1)
            axes.lines[1].set_ydata(fy1)

            # Time Waveform (Magnitude)
            fx = result.rf.waveform_x_axis
            fy = result.rf.waveform
            fx0 = np.array([t*1000 for t in fx])
            fy0 = np.array([np.abs(i)*1000.0 for i in fy])  # Multiply by 1000 to convert to microtesla.

            axes = self.view.all_axes[6]
            axes.lines[0].set_xdata(fx0)
            axes.lines[0].set_ydata(fy0)
            axes.lines[1].set_visible(False)

            # Time Waveform (Phase Degrees)
            fx = result.rf.waveform_x_axis
            fy = result.rf.waveform
            fx0 = np.array([t*1000 for t in fx])
            fy0 = np.array([np.angle(i, deg=True) for i in fy])

            axes = self.view.all_axes[7]
            axes.lines[0].set_xdata(fx0)
            axes.lines[0].set_ydata(fy0)
            axes.lines[1].set_visible(False)
            
#             # B1 Contour Profile Plot 
#             fy, fx = self.profile
#             axes = self.view.all_axes[8]
#             axes.lines[0].set_xdata(np.array(fx))
#             axes.lines[0].set_ydata(np.array([i.real for i in fy]))
#             axes.lines[1].set_xdata(np.array(fx))
#             axes.lines[1].set_ydata(np.array([i.imag for i in fy]))

            # Grad Refocused Profile  
            fy = self.profile_grad_refocus
            _, fx = self.profile
            axes = self.view.all_axes[8]
            axes.lines[0].set_xdata(np.array(fx))
            axes.lines[0].set_ydata(np.array([i.real for i in fy]))
            axes.lines[1].set_xdata(np.array(fx))
            axes.lines[1].set_ydata(np.array([i.imag for i in fy]))

        for i in range(9):
            self.format_plot(self.view.all_axes[i], i, use_type,  fsize)
            
        for i, axes in enumerate(self.view.all_axes):
            if self._prefs.data_type_real:
                axes.lines[0].set_visible(True)
                axes.lines[1].set_visible(False)
            if self._prefs.data_type_real_imaginary:
                axes.lines[0].set_visible(True)
                if i in [0,2,5,8]:
                    axes.lines[1].set_visible(True)
            axes.lines[2].set_visible(self._prefs.zero_line_show)
            axes.xaxis.set_visible(self._prefs.xaxis_show)

        for i, axes in enumerate(self.view.figure.axes):
            axes.change_geometry(naxes,1,i+1)

        if relim_flag or update_profiles and not update_refocus:
            # here we bump out the viewing window a bit on the
            # overall plot so we can get a zoom box around the
            # all sides of the plotted data
            for axes in self.view.all_axes:
                # first calculate the tight bounds for data
                x  = axes.lines[0].get_xdata()
                y0 = axes.lines[0].get_ydata()
                y1 = axes.lines[1].get_ydata()
                xmin = min(x)
                xmax = max(x)
                ymin = min([min(y0),min(y1)])
                ymax = max([max(y0),max(y1)])
                if xmin == xmax:
                    # Workaround for ticket #24:
                    # http://scion.duhs.duke.edu/vespa/project/ticket/24
                    xmax += np.finfo(type(xmax)).eps
                axes.set_xlim([xmin,xmax])
                if ymin == ymax:
                    # Workaround for ticket #24:
                    # http://scion.duhs.duke.edu/vespa/project/ticket/24
                    ymax += np.finfo(type(ymax)).eps
                axes.set_ylim([ymin,ymax])
                axes.ignore_existing_data_limits = True
                axes.update_datalim([[xmin,ymin],[xmax,ymax]])
                # now loosen the bounds a bit for display purposes
                x0, y0, x1, y1 = axes.dataLim.bounds  
                xdel = PLOT_PANEL_X_BUMP*np.abs(x1-x0)
                ydel = PLOT_PANEL_Y_BUMP*np.abs(y1-y0)
                axes.set_xlim(x0-xdel,x0+x1+xdel)
                axes.set_ylim(y0-ydel,y0+y1+ydel)
                
                      
        self.view.canvas.draw()       


    def plot_init(self):
        '''
        This method plots place holder data into all axes so that
        from here on out all we have to do is set_xdata() and set_ydata()
        rather than recreating new plots in each axis. This way we keep
        the same xlim and ylim values as plots are turned off/on 
        '''
        for i,axes in enumerate(self.view.all_axes):
            axes.cla()
            x = np.arange(255)*10/255.0
            y = np.zeros(255)
            
            width = self._prefs.line_width
            color_real = self._prefs.line_color_real
            color_imag = self._prefs.line_color_imaginary
            color_magn = self._prefs.line_color_magnitude
            color_phas = self._prefs.line_color_phase_degrees
            
            if i == 0 or i == 2:    # waveform and extended waveform
                axes.plot(x, y, color=color_real, linewidth=width)
                axes.plot(x, y, color=color_imag, linewidth=width)
            elif i == 1 or i == 3:  # absolute and absolute extended waveforms
                axes.plot(x, y, color=color_magn, linewidth=width)
                axes.plot(x, y, color=color_imag, linewidth=width)
            elif i == 4:    # time waveform
                axes.step(x, y, where='post', color=color_real, linewidth=width)
                axes.step(x, y, where='post', color=color_imag, linewidth=width)
            elif i == 5:    # time waveform magnitude
                axes.step(x, y, where='post', color=color_magn, linewidth=width)
                axes.step(x, y, where='post', color=color_imag, linewidth=width)
            elif i == 6:    # time waveform phase-degrees
                axes.step(x, y, where='post', color=color_phas, linewidth=width)
                axes.step(x, y, where='post', color=color_imag, linewidth=width)
            elif i == 7:    # contour plot FIXME bjs figure out a real contour plot please
                axes.plot(x, y, color=color_real, linewidth=width)
                axes.plot(x, y, color=color_imag, linewidth=width)
            elif i == 8:    # grad_refocus
                axes.plot(x, y, color=color_real, linewidth=width)
                axes.plot(x, y, color=color_imag, linewidth=width)
                
            axes.axhline(0, color=self._prefs.zero_line_color, 
                            linestyle=self._prefs.zero_line_style, 
                            linewidth=width)  
                
        

    def format_plot(self, axes, plot, use_type, fsize):
        
        xlabel, ylabel, title = self.get_labels(plot, use_type)
        
        axes.set_xlabel(xlabel, size=fsize)
        axes.set_ylabel(ylabel, size=fsize)
        axes.set_title( title,  size=fsize)  
        self.set_ticklabel_size(axes, fsize)
        axes.grid(True)

        
    def set_ticklabel_size(self, axes, size):
        xlabels = axes.get_xticklabels()
        ylabels = axes.get_yticklabels()
        for xtext, ytext in zip(xlabels, ylabels):
            xtext.set_size(size)
            ytext.set_size(size)



    def get_labels(self, plot, use_type):
        labels = ['','','']
        if plot < 4 or plot == 8:
            labels = ['frequency [kHz]']
            if use_type == constants.UsageType.EXCITE:
                if self._prefs.data_type_real:
                    labels.append('Mx [normal]')
                elif self._prefs.data_type_real_imaginary:
                    labels.append('Mx/My [normal]')
            elif use_type == constants.UsageType.INVERSION:
                labels.append('Mz [normal]')
            elif use_type == constants.UsageType.SATURATION:
                labels.append('Mz [normal]')
            elif use_type == constants.UsageType.SPIN_ECHO:
                if self._prefs.data_type_real:
                    labels.append('+Mx [normal]')
                elif self._prefs.data_type_real_imaginary:
                    labels.append('+Mx/-My [normal]')
        
            if plot == 0:
                labels.append('Frequency Profile')
            elif plot == 1:
                labels.append('Absolute Frequency Profile')
            elif plot == 2:
                labels.append('Extended Profile')
            elif plot == 3:
                labels.append('Extended Absolute Profile')
            elif plot == 8:
                labels.append('Grad Refocused Profile')
 
        if plot == 4:
            labels = ['time [ms]','microTesla','Gradient Waveform']
        if plot == 5:
            labels = ['time [ms]','Complex [uT]','RF Pulse Waveform']
        if plot == 6:
            labels = ['time [ms]','Magnitude [uT]','RF Pulse Waveform']
        if plot == 7:
            labels = ['time [ms]','Phase [degrees]','RF Pulse Waveform']

        return labels
 

    def run(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        pass


    def update_sync_status(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # Subclasses may override this
        pass


    def validate_gui(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # Subclasses must override this
        pass

    


