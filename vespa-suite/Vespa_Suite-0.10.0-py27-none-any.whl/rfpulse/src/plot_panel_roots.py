"""
Expansion of matplotlib embed in wx example by John Bender and Edward 
Abraham, see http://www.scipy.org/Matplotlib_figure_in_a_wx_panel

This is a hack of vespa.common.wx_gravy.plot_panel that serves the specific
purpose of displaying one or two roots/poles plots for use in the 
RFPulse application Root Reflect Transformation

The figure created in the panel is initialized with two axes associated
but based on the set_mode(self, mode) method, the user can set either 
one or both axes to be shown. Left mouse is used to pick roots to be 
reflected, right mouse is used to zoom in, or when clicked in place, 
will zoom out to the self.max_radius extent, +/- max in y-direction 
and 0,max in x-direction.  The values of the poles in each plot can be
accessed through two lists, self.data_a and self.data_b for the A and
B plots, respectively. The real values (x-axis) are stored in the first
element of the list, the imaginary (y-axis) values are stored in the 
second element of each list.  The data_a and data_b arrays can be changed
and then the self.update_plots() method called to refresh the plots on 
the figure.

BoxZoom based on matplotlib.widgets.RectangleSelector

Brian J. Soher, Duke University, 30 January, 2011
"""

# Python modules
from __future__ import division
import math

# 3rd party modules
import matplotlib
import wx
import numpy as np

if matplotlib.get_backend() != "WXAgg":
    matplotlib.use('WXAgg')

from matplotlib.patches    import Rectangle, Circle
from matplotlib.lines      import Line2D

# Our modules


class PlotPanelRoots(wx.Panel):
    """
    The PlotPanel has a Figure and a Canvas and one Axes. The axes are
    specified because the zoom and reference cursors functionality need an
    axes to attach to to init properly.  The axes can be changed after
    initialization if necessary using the new_axes() method.
    
    on_size events simply set a flag, and the actual resizing of the figure is 
    triggered by an Idle event.
    
    PlotPanel Functionality
    --------------------------------------------------
    left mouse - If zoom mode is 'span', click and drag zooms the figure.  
                 A span is selected along the x-axis. On release, the 
                 axes xlim is adjusted accordingly.
               
    left mouse - click in place, un-zooms the figure to maximum xdata
                 bounds.
                 
    right mouse - If reference mode is True/On, then click and drag will draw
                  a span selector in the canvas that persists after release.

    """

    def __init__(self, panel, parent, mode=1,
                               color=None, 
                               dpi=None, 
                               do_motion_event=False,
                               do_pick_event=True,
                               props_zoom=None,
                               props_cursor=None,
                               **kwargs):

        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        from matplotlib.figure import Figure

        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, panel, **kwargs )

        self.panel  = panel
        self.parent = parent

        # initialize matplotlib stuff
        self.figure = Figure( None, dpi )
        self.canvas = FigureCanvasWxAgg( self, -1, self.figure )
        self.axes   = []
        self.lines  = []
        
        
        self.mode = mode
        self.data_a = []
        self.data_b = []
        self.data_a_flip = []
        self.data_b_flip = []
        self.max_radius = 2.0
            
        self.zoom = None
        self.refs = None
        
        self.set_color( color )
        self._set_size()
        self._resizeflag = False

        self.Bind(wx.EVT_IDLE, self._on_idle)
        self.Bind(wx.EVT_SIZE, self._on_size)

        for i in [0,1]:
            circle = Circle((0,0), 1.0,\
                             fill=False,\
                             linestyle='dotted',\
                             color='gray')
            ax = self.figure.add_subplot(1,2,i+1)
            ax.add_patch(circle)
            ax.set_xlabel('Real Part')
            ax.set_ylabel('Imaginary Part')
            ax.grid(True)
            ax.set_xlim(0,self.max_radius)
            ax.set_ylim(-self.max_radius,self.max_radius)
            for label in ax.xaxis.get_ticklabels():
                label.set_fontsize(10) # label is a Text instance            
            for label in ax.yaxis.get_ticklabels():
                label.set_fontsize(10)     
                       
            if i == 0:
                ax.set_title('A Polynomial')
            if i == 1:
                ax.set_title('B Polynomial') 
            self.axes.append(ax)

        self.figure.subplots_adjust(left=0.15, right=0.95,\
                                    bottom=0.17, top=0.9,\
                                    wspace=0.4, hspace=0.1)
        
        if props_zoom == None:
            props_zoom = dict(alpha=0.2, facecolor='yellow')

        if props_cursor == None:
            props_cursor = dict(alpha=0.2, facecolor='purple')

        self.zoom = ZoomBox(  self, self.axes,
                              drawtype='box',
                              useblit=True,
                              button=3,
                              spancoords='data',
                              rectprops=props_zoom)

        if do_motion_event:
            self.do_motion_event = True  
            self.motion_id = self.canvas.mpl_connect('motion_notify_event', self._on_move)

        if do_pick_event:
            self.do_pick_event = True  
            self.pick_id = self.canvas.mpl_connect('pick_event', self._on_pick)

        self.set_mode(self.mode)
            
            
    def _on_size( self, event ):
        self._resizeflag = True

    def _on_idle( self, evt ):
        if self._resizeflag:
            self._resizeflag = False
            self._set_size()

    def _set_size( self ):
        pixels = tuple( self.panel.GetClientSize() )
        self.SetSize( pixels )
        self.canvas.SetSize( pixels )
        self.figure.set_size_inches( float( pixels[0] )/self.figure.get_dpi(),
                                     float( pixels[1] )/self.figure.get_dpi() )

    def _on_move(self, event):
        if event.inaxes == None or not self.do_motion_event: return
        value = []
        x0, y0, x1, y1 = bounds = event.inaxes.dataLim.bounds
    
        if event.inaxes.lines != []:
            npts = len(event.inaxes.lines[0].get_ydata())
            indx = int(round((npts-1) * (event.xdata-x0)/x1))
            if indx > (npts-1): indx = npts-1
            if indx < 0: indx = 0
            for line in event.inaxes.lines:  
                dat = line.get_ydata()
                if indx < len(dat):
                    value.append(dat[indx])
                    
        if value == []: value = [0.0]
        self.on_motion(event.xdata, event.ydata, value, bounds, iaxis)
        
    def _on_pick(self, event):

        ind = event.ind
        ind = ind[0]        # in case there is more than one point picked
        thisline = event.artist
        xdata,ydata = thisline.get_data()

        if self.axes[0].lines != None:
            if thisline in self.axes[0].lines:
                flip = np.take(self.data_a_flip, [ind])
                self.data_a_flip[ind] = not flip[0]
                axes_flag = 'a'
        if self.axes[1].lines != None:
            if thisline in self.axes[1].lines:
                flip = np.take(self.data_b_flip, [ind])
                self.data_b_flip[ind] = not flip[0]
                axes_flag = 'b'
        
        xind = np.take(xdata, [ind])
        yind = np.take(ydata, [ind])
        rad = math.hypot(xind, yind)
        ang = math.atan2(yind, xind)
        rad = 2 - rad
        
        xind = rad * math.cos(ang)
        yind = rad * math.sin(ang)
        
        xdata[ind] = xind
        ydata[ind] = yind
        
        if thisline == self.lines[0]:
            self.data_a = [xdata,ydata]
        if len(self.lines)>1:
            if thisline == self.lines[1]:
                self.data_b = [xdata,ydata]
        
        thisline.set_xdata(xdata)
        thisline.set_ydata(ydata)
        self.canvas.draw()
        
        self.parent.root_flipped(axes_flag)
        

    def update_plots(self):
        self.set_mode(self.mode)

    def set_mode(self, mode):
        
        if mode == 1:
            self.mode = 1
            if len(self.figure.axes) > 1:
                self.figure.delaxes(self.axes[1])
        else:
            self.mode = 2
            if len(self.figure.axes)<2:
                ax = self.figure.add_axes(self.axes[1])

        if self.data_a != []:
            if len(self.axes[0].lines) > 0:
                self.axes[0].lines[0].set_xdata(self.data_a[0])
                self.axes[0].lines[0].set_ydata(self.data_a[1])
            else:
                linea, = self.axes[0].plot( self.data_a[0],\
                                            self.data_a[1],\
                                            'o',\
                                            picker=5,\
                                            markerfacecolor='white',\
                                            markeredgecolor='blue')
                self.lines.append(linea)
        
        if self.mode == 2:
            if self.data_b != []:
                if len(self.axes[1].lines) > 0:
                    self.axes[1].lines[0].set_xdata(self.data_b[0])
                    self.axes[1].lines[0].set_ydata(self.data_b[1])
                else:
                    lineb, = self.axes[1].plot( self.data_b[0],\
                                                self.data_b[1],\
                                                'o',\
                                                picker=5,\
                                                markerfacecolor='white',\
                                                markeredgecolor='blue')
                    self.lines.append(lineb)

        for axes in self.figure.axes:
            axes.set_xlim(0,self.max_radius)
            axes.set_ylim(-self.max_radius,self.max_radius)

        if self.mode == 1:
            self.figure.axes[0].change_geometry(1,1,1)
        else:
            self.figure.axes[0].change_geometry(1,2,1)
            self.figure.axes[1].change_geometry(1,2,2)
        
        self.canvas.draw()

    def set_color( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    def new_axes(self, axes):
        if isinstance(axes, list):
            self.axes = axes
        elif isinstance(axes, matplotlib.axes.Axes):
            self.axes = [axes]
        else:
            return

        if self.zoom is not None:
            self.zoom.new_axes(self.axes)
            
        if self.canvas is not self.axes[0].figure.canvas:
            self.canvas.mpl_disconnect(self.motion_id)
            self.canvas = self.axes[0].figure.canvas
            self.motion_id = self.canvas.mpl_connect('motion_notify_event', self._on_move)       
        if self.figure is not self.axes[0].figure:
            self.figure = self.axes[0].figure
        
        
    def on_motion(self, xdata, ydata, value, bounds, iaxis):
        """ placeholder, overload for user defined event handling """
        print 'on_move, xdata='+str(xdata)+'  ydata='+str(ydata)+'  val='+str(value)+'  bounds = '+str(bounds)
        



class ZoomBox:
    """
    Select a min/max range of the x axes for a matplotlib Axes

    Example usage::

        from matplotlib.widgets import  RectangleSelector
        from pylab import *

        def onselect(xmin, xmax, value, ymin, ymax):
          'eclick and erelease are matplotlib events at press and release'
          print ' x,y min position : (%f, %f)' % (xmin, ymin)
          print ' x,y max position   : (%f, %f)' % (xmax, ymax)
          print ' used button   : ', eclick.button

        def toggle_selector(event):
            print ' Key pressed.'
            if event.key in ['Q', 'q'] and toggle_selector.RS.active:
                print ' RectangleSelector deactivated.'
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.RS.active:
                print ' RectangleSelector activated.'
                toggle_selector.RS.set_active(True)

        x = arange(100)/(99.0)
        y = sin(x)
        fig = figure
        axes = subplot(111)
        axes.plot(x,y)

        toggle_selector.RS = ZoomBox(axes, onselect, drawtype='line')
        connect('key_press_event', toggle_selector)
        show()
    """
    def __init__(self, parent, axes, 
                     drawtype='box',
                     minspanx=None, 
                     minspany=None, 
                     useblit=False,
                     lineprops=None, 
                     rectprops=None,
                     do_zoom_select_event=False, 
                     do_zoom_motion_event=False,
                     spancoords='data',
                     button=None):

        """
        Create a selector in axes.  When a selection is made, clear
        the span and call onselect with

          onselect(pos_1, pos_2)

        and clear the drawn box/line. There pos_i are arrays of length 2
        containing the x- and y-coordinate.

        If minspanx is not None then events smaller than minspanx
        in x direction are ignored(it's the same for y).

        The rect is drawn with rectprops; default
          rectprops = dict(facecolor='red', edgecolor = 'black',
                           alpha=0.5, fill=False)

        The line is drawn with lineprops; default
          lineprops = dict(color='black', linestyle='-',
                           linewidth = 2, alpha=0.5)

        Use type if you want the mouse to draw a line, a box or nothing
        between click and actual position ny setting

        drawtype = 'line', drawtype='box' or drawtype = 'none'.

        spancoords is one of 'data' or 'pixels'.  If 'data', minspanx
        and minspanx will be interpreted in the same coordinates as
        the x and y axis, if 'pixels', they are in pixels

        button is a list of integers indicating which mouse buttons should
        be used for rectangle selection.  You can also specify a single
        integer if only a single button is desired.  Default is None, which
        does not limit which button can be used.
        Note, typically:
         1 = left mouse button
         2 = center mouse button (scroll wheel)
         3 = right mouse button
        """
        self.parent = parent
        self.axes = None
        self.canvas = None
        self.visible = True
        self.cids = []
        
        self.active = True                    # for activation / deactivation
        self.to_draw = []
        self.background = None

        self.do_zoom_select_event = do_zoom_select_event
        self.do_zoom_motion_event = do_zoom_motion_event
        
        self.useblit = useblit
        self.minspanx = minspanx
        self.minspany = minspany

        if button is None or isinstance(button, list):
            self.validButtons = button
        elif isinstance(button, int):
            self.validButtons = [button]

        assert(spancoords in ('data', 'pixels'))

        self.spancoords = spancoords
        self.eventpress = None          # will save the data (position at mouseclick)
        self.eventrelease = None        # will save the data (pos. at mouserelease)

        self.new_axes(axes, rectprops)


    def new_axes(self,axes, rectprops=None):
        self.axes = axes
        if self.canvas is not axes[0].figure.canvas:
            for cid in self.cids:
                self.canvas.mpl_disconnect(cid)

            self.canvas = axes[0].figure.canvas
            self.cids.append(self.canvas.mpl_connect('motion_notify_event', self.onmove))
            self.cids.append(self.canvas.mpl_connect('button_press_event', self.press))
            self.cids.append(self.canvas.mpl_connect('button_release_event', self.release))
            self.cids.append(self.canvas.mpl_connect('draw_event', self.update_background))
            self.cids.append(self.canvas.mpl_connect('motion_notify_event', self.onmove))
            
        if rectprops is None:
            rectprops = dict(facecolor='white', 
                             edgecolor= 'black',
                             alpha=0.5, 
                             fill=False)
        self.rectprops = rectprops

        for axes in self.axes:
            self.to_draw.append(Rectangle((0,0), 0, 1,visible=False,**self.rectprops))

        for axes,to_draw in zip(self.axes, self.to_draw):
            axes.add_patch(to_draw)
    

    def update_background(self, event):
        'force an update of the background'
        if self.useblit:
            self.background = self.canvas.copy_from_bbox(self.canvas.figure.bbox)

    def ignore(self, event):
        'return True if event should be ignored'
        # If ZoomBox is not active :
        if not self.active:
            return True

        # If canvas was locked
        if not self.canvas.widgetlock.available(self):
            return True

        # Only do selection if event was triggered with a desired button
        if self.validButtons is not None:
            if not event.button in self.validButtons:
                return True

        # If no button pressed yet or if it was out of the axes, ignore
        if self.eventpress == None:
            return event.inaxes not in self.axes

        # If a button pressed, check if the release-button is the same
        return  (event.inaxes not in self.axes or
                 event.button != self.eventpress.button)

    def press(self, event):
        'on button press event'
        # Is the correct button pressed within the correct axes?
        if self.ignore(event): return
        
        # only send one motion event while selecting
        if self.do_zoom_motion_event:
            self.parent.do_motion_event = False


        # make the drawn box/line visible get the click-coordinates,
        # button, ...
        for to_draw in self.to_draw:
            to_draw.set_visible(self.visible)
        self.eventpress = event
        return False


    def release(self, event):
        'on button release event'
        if self.eventpress is None or self.ignore(event): return
        
        # only send one motion event while selecting
        if self.do_zoom_motion_event:
            self.parent.do_motion_event = True
        
        # make the box/line invisible again
        for to_draw in self.to_draw:
            to_draw.set_visible(False)
        
        # left-click in place resets the x-axis or y-axis
        if self.eventpress.xdata == event.xdata and self.eventpress.ydata == event.ydata:
            x0, y0, x1, y1 = event.inaxes.dataLim.bounds
            for axes in self.axes:
                rad = self.parent.max_radius
                axes.set_xlim(0,rad)
                axes.set_ylim(-rad,rad)
            self.canvas.draw()
            
            if self.do_zoom_select_event:
                self.parent.on_zoom_select(x0, x0+x1, [0.0], y0, y0+y1)

# This was test code to allow me to switch back and forth between modes 1 and
# 2 by right clicking in place ...
#
#            if self.parent.mode != 1:
#                mode = 1
#            else:
#                mode = 2
#            self.parent.set_mode(mode)
            
            return
        
        self.canvas.draw()
        # release coordinates, button, ...
        self.eventrelease = event

        if self.spancoords=='data':
            xmin, ymin = self.eventpress.xdata, self.eventpress.ydata
            xmax, ymax = self.eventrelease.xdata, self.eventrelease.ydata
            # calculate dimensions of box or line get values in the right
            # order
        elif self.spancoords=='pixels':
            xmin, ymin = self.eventpress.x, self.eventpress.y
            xmax, ymax = self.eventrelease.x, self.eventrelease.y
        else:
            raise ValueError('spancoords must be "data" or "pixels"')

        # assure that min<max values
        if xmin>xmax: xmin, xmax = xmax, xmin
        if ymin>ymax: ymin, ymax = ymax, ymin
        # assure that x and y values are not equal
        if xmin == xmax: xmax = xmin*1.0001
        if ymin == ymax: ymax = ymin*1.0001

        spanx = xmax - xmin
        spany = ymax - ymin
        xproblems = self.minspanx is not None and spanx<self.minspanx
        yproblems = self.minspany is not None and spany<self.minspany
        if (xproblems or  yproblems):
            """Box too small"""    # check if drawed distance (if it exists) is
            return                 # not to small in neither x nor y-direction
        
        for axes in self.axes:
            axes.set_xlim((xmin,xmax))
            axes.set_ylim((ymin,ymax))
        self.canvas.draw()

        self.eventpress   = None              # reset the variables to their
        self.eventrelease = None              #   inital values
        return False


    def update(self):
        'draw using newfangled blit or oldfangled draw depending on useblit'
        if self.useblit:
            if self.background is not None:
                self.canvas.restore_region(self.background)
            for axes, to_draw in zip(self.axes, self.to_draw):
                # in this overly-specialized version of plot_panel, I have two
                # mode (1 and 2 axes showing), and don't want to draw two
                # zoom boxes when only one axes is showing and using up all
                # the screenspace. I save the second axes in self.axes[1] until
                # I need to add it back into the figure, so here we test for
                # when the axes == second axis but we are in mode 1 and only 
                # displaying one zoom box, and thus do not want the second
                # zoom box drawn.
                if not (self.parent.mode == 1 and self.parent.axes[1] == axes):
                    axes.draw_artist(to_draw)
            self.canvas.blit(self.canvas.figure.bbox)
        else:
            self.canvas.draw_idle()
        return False


    def onmove(self, event):
        'on motion notify event if box/line is wanted'
        if self.eventpress is None or self.ignore(event): return
        x,y = event.xdata, event.ydata              # actual position (with
                                                    #   (button still pressed)
        minx, maxx = self.eventpress.xdata, x       # click-x and actual mouse-x
        miny, maxy = self.eventpress.ydata, y       # click-y and actual mouse-y
        if minx>maxx: minx, maxx = maxx, minx       # get them in the right order
        if miny>maxy: miny, maxy = maxy, miny       
        for to_draw in self.to_draw:
            to_draw.set_x(minx)                    # set lower left of box
            to_draw.set_y(miny)
            to_draw.set_width(maxx-minx)           # set width and height of box
            to_draw.set_height(maxy-miny)
        
        self.update()
        return False

    def set_active(self, active):
        """ Use this to activate / deactivate the RectangleSelector

            from your program with an boolean variable 'active'.
        """
        self.active = active

    def get_active(self):
        """ to get status of active mode (boolean variable)"""
        return self.active




#------------------------------------------------
# Test Code
#------------------------------------------------

if __name__ == '__main__':

    import numpy as np

    xa = abs(np.random.rand(10)*2 - 1) 
    ya = np.random.rand(10)*2 - 1

    xb = abs(np.random.rand(5)*2 - 1) 
    yb = np.random.rand(5)*2 - 1
    xb = np.concatenate((xb,xb))
    yb = np.concatenate((yb,(-1*yb)))

    app   = wx.PySimpleApp( 0 )
    frame = wx.Frame( None, wx.ID_ANY, 'WxPython and Matplotlib', size=(300,300) )
    
    nb = wx.Notebook(frame, -1, style=wx.BK_BOTTOM)
    
    panel1 = wx.Panel(nb, -1)
    root_plot = PlotPanelRoots(  panel1, panel1,
                                 mode=1,    
                                 do_motion_event=False,
                                 do_pick_event=True )

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(root_plot, 1, wx.LEFT | wx.TOP | wx.EXPAND)
    panel1.SetSizer(sizer)
    root_plot.Fit()    

    root_plot.set_color( (255,255,255) )
    root_plot.data_a = [xa,ya] 
    root_plot.data_b = [xb,yb]
    root_plot.update_plots()

    nb.AddPage(panel1, "One")
    
    frame.Show()
    app.MainLoop()

