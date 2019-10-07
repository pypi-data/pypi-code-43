# Python modules
from __future__ import division


# 3rd party modules
import wx
import numpy as np
from matplotlib.patches    import Rectangle, Circle
from matplotlib.lines      import Line2D


# Our modules
import plot_panel_roots
import auto_gui.panel_root_reflect as panel_root_reflect
import tab_transform_base

       
        
class PanelRootReflect(panel_root_reflect.PanelRootReflect):
    
    def __init__(self, parent, tab):
        
        self._tab = tab

        panel_root_reflect.PanelRootReflect.__init__(self, parent)

        self.roots_a      = []
        self.roots_b      = []
        self.roots_a_flip = []
        self.roots_b_flip = []
        
        self.angle_a_index = []
        self.angle_b_index = []
        
        self.initialize_controls()

        
    ##### Event Handlers ######################################################
        
    def on_plot_selection(self, event): 
        index = event.GetEventObject().GetCurrentSelection()
        self.roots_plot.set_mode(index+1)

    def on_max_radius(self, event): 
        val = event.GetEventObject().GetValue()
        self.roots_plot.max_radius = val
        self.roots_plot.update_plots()

    def on_plot_angle(self, event): 
        val = event.GetEventObject().GetValue()
        val = np.pi * val / 180.0
        self._tab.transform.parameters.graph_angle = val
        self.plot_with_angle()
        if self.CheckAutoUpdate.IsChecked():
            self._tab._inner_notebook.run(self)

    def on_reset_roots(self, event): 
        self.reset_roots()
        self.plot_with_angle()
        if self.CheckAutoUpdate.IsChecked():
            self._tab._inner_notebook.run(self)

    def on_auto_update(self, event): 
        obj = event.GetEventObject()
        self._tab.ButtonRun.Enable(not obj.IsChecked())
                    
    ##### Internal helper functions  ##########################################

    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = { }
        
        d['plot_selection'] = self.ComboPlotSelection.GetCurrentSelection()
        d['max_radius']  = self.FloatMaxRadius.GetValue()
        d['graph_angle'] = self.FloatGraphAngle.GetValue()
        d['auto_update'] = self.CheckAutoUpdate.IsChecked()
        
        d['roots_a'] = self.roots_a
        d['roots_b'] = self.roots_b
        d['roots_a_flip'] = self.roots_a_flip
        d['roots_b_flip'] = self.roots_b_flip
        
        return d
 

    def initialize_controls(self):
        # sets up widgets in parameter panel (left side of the splitter) 
        # from values in either a new or existing rfpulse_project object.
      
        transform = self._tab.transform
      
        self.roots_plot = plot_panel_roots.PlotPanelRoots(self.PanelPlotSection,
                                                          self, 
                                                          mode=1,
                                                          do_motion_event=False,
                                                          do_pick_event=True )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.roots_plot, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.PanelPlotSection.SetSizer(sizer)
        self.roots_plot.set_color( (255,255,255) )
        self.roots_plot.Fit()          
        
        angle = transform.parameters.graph_angle * 180 / np.pi
        self.FloatGraphAngle.SetValue(angle)

        if self._pulse_project.is_frozen:
            # Frozen projects are mostly uneditable
            self.roots_plot.Disable()
            self.FloatGraphAngle.Disable()
            self.ButtonRun.Hide()


    def reset_roots(self):
        # Set the roots to our newly retrieved values.    
        self.roots_a = np.array(self._tab.transform.parameters.aroots)
        self.roots_b = np.array(self._tab.transform.parameters.broots)
        self.roots_a_flip = list(False for i in self.roots_a)
        self.roots_b_flip = list(False for i in self.roots_b)
        
        
    def plot_with_angle(self):
        
        val = self.FloatGraphAngle.GetValue()
        val = np.pi * val / 180.0
        self._tab.transform.parameters.graph_angle = val
        
        mask_a, mask_b = self._tab.transform.roots_within_angle()
        
        angle_a = []
        angle_a_flip = []
        self.angle_a_index = []

        for i,v in enumerate(mask_a):
            # these store the state of the roots that are in the angle
            if mask_a[i]:
                if self.roots_a_flip[i]:
                    angle_a.append(self._tab.transform.reflected(self.roots_a[i]))
                    angle_a_flip.append(True)
                else:
                    angle_a.append(self.roots_a[i])
                    angle_a_flip.append(False) 
                self.angle_a_index.append(i)

        angle_b = []
        angle_b_flip = []
        self.angle_b_index = []
        
        for i,v in enumerate(mask_b):
            # these store the state of the roots that are in the angle
            if mask_b[i]:
                if self.roots_b_flip[i]:
                    angle_b.append(self._tab.transform.reflected(self.roots_b[i]))
                    angle_b_flip.append(True)
                else:
                    angle_b.append(self.roots_b[i])
                    angle_b_flip.append(False) 
                self.angle_b_index.append(i)

        self.roots_plot.data_a = [[a.real for a in angle_a], [a.imag for a in angle_a]]
        self.roots_plot.data_b = [[b.real for b in angle_b], [b.imag for b in angle_b]]
        
        self.roots_plot.data_a_flip = angle_a_flip
        self.roots_plot.data_b_flip = angle_b_flip
        
        self.roots_plot.update_plots()


    def root_flipped(self, root_flag):
        
        transform = self._tab.transform
        project   = self._tab._pulse_project
        
        if root_flag == 'a':
            for i,flag in enumerate(self.roots_plot.data_a_flip):
                self.roots_a_flip[self.angle_a_index[i]] = flag
            transform.parameters.aroots_flipped = list(self.roots_a_flip)
        else:
            for i,flag in enumerate(self.roots_plot.data_b_flip):
                self.roots_b_flip[self.angle_b_index[i]] = flag
            transform.parameters.broots_flipped = list(self.roots_b_flip)
        
        if self.CheckAutoUpdate.IsChecked():
            self._tab._inner_notebook.run(self)



class TabTransformRootReflect(tab_transform_base.TabTransformBase):
    
    def __init__(self, inner_notebook, left_neighbor, pulse_project, transform):

        tab_transform_base.TabTransformBase.__init__(self,
                                                               inner_notebook, 
                                                               left_neighbor, 
                                                               transform)

        self._inner_notebook = inner_notebook
        self._pulse_project  = pulse_project
        self.transform = transform

        sizer       = self.LabelAlgorithmPlaceholder.GetContainingSizer()
        parent_base = self.LabelAlgorithmPlaceholder.GetParent()
        self.LabelAlgorithmPlaceholder.Destroy()
        
        # Note that the roots panel uses and manipulates several things
        # on this tab.
        self.roots_panel = PanelRootReflect(parent_base, self)

        self.initialize_controls()
        
        # insert the transform panel into the TabTransformBase template
        sizer.Insert(0, self.roots_panel, 1, wx.EXPAND, 0)     

        # If there are not roots listed after the transformation was
        # initialized, then we need to get them now, and plot.
        self.get_roots()

        self.plot(update_profiles=True, relim_flag=True)
        
        self.Layout()   
        self.Fit()
        self.Show(True)

        tab_transform_base.TabTransformBase.complete_init(self)
        
        
    ##### Event Handlers ######################################################
        
    def on_run(self, event):        
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        self._inner_notebook.run(self)


    def get_roots(self):
        
        self.transform.get_roots(self._pulse_project.machine_settings, 
                                 self._pulse_project.master_parameters,
                                 self._pulse_project.get_previous_result(self.transform))  
        
        # Reset the values in the plot and show.
        self.roots_panel.reset_roots()
        self.roots_panel.plot_with_angle()


    ##### Internal helper functions  ##########################################
        
    def get_cooked_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        d = self.get_raw_gui_data()

        # cook the raw values here...
        
        return d


    def get_raw_gui_data(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        # FIXME PS - the correct version of this function is the line 
        # below, but if I leave that enabled then get_raw_gui_data() 
        # always returns an empty dict which means this code thinks it is
        # always in sync which means it will never run. This hack allows
        # root reflect to run but should be removed once we get some real
        # code in here.
        # correct code:
#        return self.roots_panel.get_raw_gui_data()
        # my hack:
        d = { }
        import time
        # I create a value that's never the same twice so that this tab 
        # always looks like it needs to be re-run.
        d["dummy"] = time.time()
        return d
 

    def initialize_controls(self):
        pass

        
    def run(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        tab_transform_base.TabTransformBase.run(self)
        
        self._last_run.update(self.get_raw_gui_data())
        
        for i,flag in enumerate(self.roots_panel.roots_plot.data_a_flip):
            self.roots_panel.roots_a_flip[self.roots_panel.angle_a_index[i]] = flag
            
        self.transform.parameters.aroots_flipped = list(self.roots_panel.roots_a_flip)

        for i,flag in enumerate(self.roots_panel.roots_plot.data_b_flip):
            self.roots_panel.roots_b_flip[self.roots_panel.angle_b_index[i]] = flag
            
        self.transform.parameters.broots_flipped = list(self.roots_panel.roots_b_flip)
        
        # Pass in the result of the last transformation
        # as the initial conditions of this transformation.
        self.transform.apply_roots(self._pulse_project.machine_settings,
                                   self._pulse_project.master_parameters)
    

        self.plot(update_profiles=True)
        
        return True


    def validate_gui(self):
        """ See documentation here:
        http://scion.duhs.duke.edu/vespa/rfpulse/wiki/CommonTabFeatures
        """
        msg = ""
        
        d = self.get_raw_gui_data()
        
        # validate the contents of d here

        if msg:
            self._inner_notebook.activate_tab(self)
            common_dialogs.message(msg)

        return not bool(msg)
        

