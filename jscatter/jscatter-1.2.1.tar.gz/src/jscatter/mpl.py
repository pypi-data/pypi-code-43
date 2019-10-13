# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015-2019  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
This is a rudimentary interface to matplotlib to use dataArrays easier.
The standard way to use matplotlib is full available without using this module.

You may switch to use mpl in fitting and examples using ::

 js.usempl(True)

The intention is to allow fast/easy plotting (one command to plot) with some convenience
function in relation to dataArrays and in a non blocking mode of matplotlib.
E.g. to include automatically the value of an attribute (qq in example) in the legend::

 fig[0].Plot(mydataArray, legend='sqr=$qq',sy=[2,3,-1],li=0)
 # dataList
 fig[0].Plot(mydataList , legend='sqr=$qq',sy=[2,3,-1],li=0)

With somehow shorter form to determine the marker (sy=symbol) and line (li)
and allow plotting in one line. Matplotlib is quite slow (and looks for me ugly).
For 2D plotting use xmgrace.
For 3D plotting this will give some simple plot options (planned).

* The new methods introduced all start with a big Letter to allow still the access of the original methods.
* By indexing subplots can be accessed as figure[i] which is figure.axes[i].
* Same for axes with lines figure[0][i] is figure.axes[0].lines[i].

Example 1::

    import jscatter as js
    import numpy as np
    i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
    p=js.mplot()
    p[0].Plot(i5,sy=[-1,0.4,-1],li=1,legend='Q= $q')
    p[0].Yaxis(scale='l')
    p[0].Title('intermediate scattering function')
    p[0].Legend(x=1.13,y=1) # x,y in relative units of the plot
    p[0].Yaxis(label='I(Q,t)/I(Q,0)',min=0.01)
    p[0].Xaxis(label='Q / 1/nm',max=120)

Example 2  ( same as js.mpl.test() )::

    import jscatter as js
    import numpy as np
    from matplotlib import pyplot
    # use this
    #fig=pyplot.figure(FigureClass=js.mpl.Figure)
    # or
    fig=js.mplot()
    fig.Multi(2,1)
    fig[0].SetView(0.1,0.25,0.8,0.9)
    fig[1].SetView(0.1,0.09,0.8,0.23)
    q=js.loglist(0.01,5,100)
    aa=js.dL()
    for pp in range(5):
        aa.append(js.dA(np.c_[q,-pp*np.sin(q),0.2*np.cos(5*q)].T))
        aa[-1].qq=pp
    bb=js.dA(np.c_[q,q**2].T)
    bb.qq=123
    for pp in range(5):
        fig[0].Plot(aa[pp].X,-1*aa[pp].Y,legend='some stufff',sy=[1,(pp+1)/10.],li=0)

    fig[0].Plot(aa, legend='qq = $qq', sy=[-1, 0.4, -1, ''], li=0, markeredgewidth=1)
    for pp in range(5):
        fig[1].Plot(aa[-1].X/5+pp,pp*aa[-1].Y,legend='q=%.1f' %pp,sy=0,li=-1,markeredgewidth =1)
    fig[1].Plot(bb,legend='sqr=$qq ',sy=2,li=2)
    fig[0].Title('test')
    fig[0].Legend(x=1.3,y=1)
    fig[1].Legend(x=1.3,y=1)
    fig[0].Yaxis(label='y-axis')
    fig[1].Yaxis(label='something else')
    fig[0].tick_params(labelbottom=False)
    fig[1].Xaxis(label='x-axis')

**Some short hints for matplotlib**
Dont use the pyplot interface as it hides how most things work and e.g. how to access lines later.
See `THIS <http://pbpython.com/effective-matplotlib.html>`_ .
After fitting the errorplot can be accessed as ``data.errplot``.
::

 fig=js.mplot()                         # access figure properties from fig
 fig.axes[0]                            # access to axes properties
 fig.axes[0].lines[0]                   # access to lines properties in axes 0
 fig.axes[0].lines[1].set_color('b')    # change color
 fig.axes[0].legend(...)                # set legend
 data.errplot.axes[0].set_yscale('log') # set log scale in errplot
 # for more read matplotlib documentation

"""

import numpy as np
from functools import reduce
import copy
import numbers

import matplotlib
from matplotlib.projections import register_projection
from matplotlib import pyplot
from matplotlib.lines import Line2D
from matplotlib import colors

lineStyles = ('', '-', '--', '-.', ':')
# linecolors = ('w', 'k', 'r', 'b', 'g', 'c', 'm', 'y',)
linecolors = ('white', 'black', 'red', 'darkgreen', 'blue', 'grey', 'orange', 'magenta', 'yellow', 'green')
fillstyles = ('none', 'full', 'left', 'right', 'bottom', 'top',)
symboldefault = [1, 0.3, 1, '']  # type,size,facecolor,edgecolor
linedefault = [1, 0.5, 1]  # type,size,color

#: gracefactor to get same scaling as in grace set to 10
gf = 10


def _translate(axlen, kwargs, data=None, yerr=None):
    """
    This function transforms a short description as [1,2,3] for symbol and line to matplotlib compatible arguments.
    This allows a shorter description of the symbol and line formats.
    Additionally the replacement of $parname in dataArray attributes is done.
    
    
    """
    # split some special keywords in kwargs
    if 'legend' in kwargs:
        legend = kwargs['legend']
        del kwargs['legend']
    elif 'le' in kwargs:
        legend = kwargs['le']
        del kwargs['le']
    else:
        legend = None
    if 'line' in kwargs:
        line = kwargs['line']
        del kwargs['line']
    elif 'li' in kwargs:
        line = kwargs['li']
        del kwargs['li']
    else:
        line = ''
    if 'symbol' in kwargs:
        symbol = kwargs['symbol']
        del kwargs['symbol']
    elif 'sy' in kwargs:
        symbol = kwargs['sy']
        del kwargs['sy']
    else:
        symbol = [-1, 0.3, -1]
    if 'errorbar' in kwargs:
        errorbar = kwargs['errorbar']
        del kwargs['errorbar']
    elif 'er' in kwargs:
        errorbar = kwargs['er']
        del kwargs['er']
    else:
        errorbar = None
    # replace $attr by the value in data
    if legend is not None:
        if '$' in legend and hasattr(data, '_isdataArray'):
            for par in data.attr:
                if '$' + par in legend or '$(' + par + ')' in legend:
                    # noinspection PyBroadException
                    try:
                        vall = np.array(getattr(data, par)).flatten()[0]
                        if isinstance(vall, numbers.Number):
                            val = '%.4g' % vall
                        else:
                            val = str(vall)
                        if '$(' + par + ')' in legend:
                            legend = legend.replace('$(' + par + ')', val)
                        else:
                            legend = legend.replace('$' + par, val)
                    except:
                        pass
    # --------
    if isinstance(symbol, (int, str)):
        symbol = [symbol]  # type,size,facecolor,edgecolor
    symbol += symboldefault[len(symbol):]
    # symbol marker
    if isinstance(symbol[0], numbers.Number):
        if symbol[0] < 0: symbol[0] = axlen
        if symbol[0] > 0:
            symbol[0] = Line2D.filled_markers[divmod(symbol[0] - 1, len(Line2D.filled_markers))[1]]
        else:
            symbol[0] = None
    # symbol color
    if isinstance(symbol[2], numbers.Number):
        if symbol[2] < 0: symbol[2] = axlen
        if symbol[2] > 0:
            symbol[2] = linecolors[divmod(symbol[2] - 1, len(linecolors) - 1)[1] + 1]
        else:
            symbol[2] = None
    # edgecolor
    if isinstance(symbol[3], numbers.Number):
        if symbol[3] < 0: symbol[3] = axlen
        if symbol[3] > 0:
            symbol[3] = linecolors[divmod(symbol[3] - 1, len(linecolors) - 1)[1] + 1]
        else:
            symbol[3] = linecolors[0]
    else:
        # synchronize with facecolor
        symbol[3] = symbol[2]
    # same for line
    if isinstance(line, (int, str)):
        # type,size,color
        line = linedefault[:2] + [line]
    if isinstance(line[0], numbers.Number):  # type
        if line[0] < 0: line[0] = axlen
        if line[0] > 0:
            line[0] = lineStyles[divmod(line[0] - 1, len(lineStyles) - 1)[1] + 1]
        else:
            line[0] = None
    if isinstance(line[2], numbers.Number):  # color
        if line[2] < 0: line[2] = axlen
        if line[2] > 0:
            line[2] = linecolors[divmod(line[2] - 1, len(linecolors) - 1)[1] + 1]
        else:
            line[0] = ''  # this makes no line to overwrite default '-'
            line[2] = None
        if symbol[0] is None and line[2] is not None:
            symbol[2] = line[2]
    if yerr is None or errorbar is None:
        errorbar = [None, None]
    else:
        if isinstance(errorbar, numbers.Number):
            errorbar = [None, errorbar]
        if isinstance(errorbar[0], numbers.Number):
            if errorbar[0] < 0: errorbar[0] = axlen
            if errorbar[0] > 0:
                errorbar[0] = linecolors[divmod(errorbar[0] - 1, len(linecolors) - 1)[1] + 1]
            else:
                errorbar[0] = linecolors[0]
        else:
            errorbar[0] = None
    # fmt=fmt,markersize=ssize, markerfacecolor=mfc,linewidth=lsize,label=legend
    # capsize same as markersize
    for opt, val in zip(['color', 'marker', 'linestyle', 'markersize', 'markerfacecolor', 'markeredgecolor',
                         'linewidth', 'elinewidth', 'ecolor', 'capsize'],
                        [symbol[2], symbol[0], line[0], symbol[1] * gf, symbol[2], symbol[3],
                         line[1], errorbar[1], errorbar[0], symbol[1] * gf / 3.]):
        if opt not in kwargs:
            kwargs[opt] = val
    if legend is not None:
        if r'\n' in legend:
            lines = []
            for line in legend.replace('\\n', '\n').splitlines():
                words = line.split()
                if len(words) > 4:
                    line = ' '.join(words[:5]) + '...'
                else:
                    line = ' '.join(words)
                lines.append(line)
            kwargs['label'] = '\n'.join(lines)
        else:
            kwargs['label'] = legend
    return kwargs


# noinspection PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring,PyIncorrectDocstring
class jspaperAxes(matplotlib.axes.Axes):
    """
    An Axes that should look like typical paper layout.
    
    """

    name = 'paper'

    def __init__(self, *args, **kwargs):
        super(matplotlib.axes.Axes, self).__init__(*args, **kwargs)
        self.tick_params(axis='both', direction='in')

    def SetView(self, xmin=None, ymin=None, xmax=None, ymax=None):
        """
        This sets the bounding box of the axes.

        Parameters
        ----------
        xmin,xmax,ymin,ymax : float
            view range

        """
        self.set_position([xmin, ymin, xmax - xmin, ymax - ymin])  # [left, bottom, width, height]
        self.figure.show()

    def __getitem__(self, key):
        return self.lines[key]

    # noinspection PyIncorrectDocstring
    def plot(self, *datasets, **kwargs):
        """
        Plot dataArrays/dataList or array in matplotlib axes.

        Parameters are passed to matplotlib.axes.Axes.plot
        
        Parameters
        ----------
        datasets : dataArray/dataList or 1D arrays
            Datasets to plot.
             - Can be several dataArray/dataList (with .X, .Y and .eY) or 1D arrays (a[1,:],b[2,:]), but dont mix it.
             - If dataArray/dataList has .eY errors a errorbars are plotted.
             - If format strings are found  only the first is used. symbol, line override this.
             - Only a single line for 1D arrays is allowed.
        symbol,sy : int, list of float
            - [symbol,size,color,fillcolor,fillpattern] as [1,1,1,-1];
            - single integer to chose symbol eg symbol=3;  symbol=0 switches off
            - negative increments from last
            - symbol => see Line2D.filled_markers
            - size   =>    size in pixel
            - color  => int in sequence = wbgrcmyk
            - fillcolor=None    see color
            - fillpattern=None  0 empty, 1 full, ....test it
        line,li : int, list of float or Line object
            - [linestyle,linewidth,color] as [1,1,''];
            - negative increments
            - single integer to chose linestyle line=1; line=0 switches of
            - linestyle int   '-','--','-.',':'
            - linewidth float increasing thickness
            - color        see symbol color
        errorbar,er : int or list of float or Errorbar object
            - [color,size] as [1,1]; no increment, no repeat
            - color int             see symbol color, non-integer syncs to symbol color
            - size float            default 1.0 ; smaller is 0.5

        legend,le : string
            - determines legend for all datasets
            - string replacement: attr name prepended by '$' (eg. '$par')
              is replaced by value str(par1.flatten()[0]) if possible.
              $(par) for not unique names
        errorbar,er : float
            - errorbar thickness, zero is no errorbar

        """
        # extract format strings
        fmt = [dset for dset in datasets if isinstance(dset, str)]
        datasets = [dset for dset in datasets if not isinstance(dset, str)]
        # concat to dataList's if its not a format string
        if np.alltrue([hasattr(dset, '_isdataList') or (hasattr(dset, '_isdataArray') and np.ndim(dset) > 1)
                       for dset in datasets]):
            # use a single list
            datasets = reduce(lambda a, b: a + b, datasets)
            if hasattr(datasets, '_isdataArray'):
                # return always as dataList not only dataArray
                datasets = [datasets]
        # If 1 dim data are given
        elif np.alltrue([np.ndim(dset) == 1 for dset in datasets]):
            # We create a single dataset and use this
            shape0 = [np.shape(dset)[0] for dset in datasets]
            if shape0.count(shape0[0]) == len(shape0):
                # all same length -> make array
                datasets = [np.asanyarray(datasets)]
        else:
            raise TypeError('Dont know how to plot this.')
        # self.lines is updated only after show so we need to count explicitly
        nlines = len(self.lines)
        showerr = True
        if 'comment' in kwargs: del kwargs['comment']
        if 'errorbar' in kwargs:
            if not kwargs['errorbar']: showerr = False
        elif 'er' in kwargs:
            if not kwargs['er']:       showerr = False
        for data in datasets:
            if hasattr(data, '_isdataArray'):
                if hasattr(data, '_iey') and showerr:
                    yerr = data.eY
                else:
                    yerr = None
                nkwargs = _translate(nlines + 1, kwargs.copy(), data, yerr)
                if fmt and 'fmt' not in nkwargs:
                    # if fmt not empty and not other setting found
                    nkwargs['fmt'] = fmt[0]
                self.errorbar(x=data.X, y=data.Y, yerr=yerr, **nkwargs)
                nlines += 1
            elif hasattr(data, '_isdataList'):
                for da in data:
                    if hasattr(da, '_iey') and showerr:
                        yerr = da.eY
                    else:
                        yerr = None
                    nkwargs = _translate(nlines + 1, kwargs.copy(), da, yerr)

                    if fmt and 'fmt' not in nkwargs:
                        # if fmt not empty and not other setting found
                        nkwargs['fmt'] = fmt[0]
                    self.errorbar(x=da.X, y=da.Y, yerr=yerr, **nkwargs)
                    nlines += 1
            elif isinstance(data, np.ndarray):
                if showerr:
                    # noinspection PyBroadException
                    try:
                        yerr = data[2]
                    except:
                        yerr = None
                nkwargs = _translate(nlines + 1, kwargs.copy(), data, yerr)
                if fmt and 'fmt' not in nkwargs:
                    # if fmt not empty and not other setting found
                    nkwargs['fmt'] = fmt[0]
                self.errorbar(x=data[0], y=data[1], yerr=yerr, **nkwargs)
                nlines += 1
        self.figure.show()

    Plot = plot

    def Yaxis(self, min=None, max=None, label=None, scale=None, size=None, charsize=None, tick=None, ticklabel=None,
              **kwargs):
        """
        Set xaxis

        Parameters
        ----------
        label : string
            Label
        scale : 'log', 'normal'
            Scale
        min,max : float
            Set min and max
        size : int
            Pixelsize of label


        """
        # TODO: log scale errplot not working in makeErrPlot while setting it afterwards works
        if size is not None:
            size *= gf
        if label is not None:
            self.set_ylabel(label, size=size)
        if scale is not None and scale[0] == 'l':
            if min is None: min = 0.1
            if max is None: max = 10
        self.set_ylim(min, max)
        if scale is not None:
            if scale[0] == 'l':
                self.set_yscale(value='log', nonposy='clip', subsy=[2, 3, 4, 5, 6, 7, 8, 9])
            else:
                self.set_yscale(value='linear')

        self.figure.show()

    def Xaxis(self, min=None, max=None, label=None, scale=None, size=None, charsize=None, tick=None, ticklabel=None,
              **kwargs):
        """
        Set xaxis

        Parameters
        ----------
        label : string
            Label
        scale : 'log', 'normal'
            Scale
        min,max : float
            Set min and max of scale
        size : int
            Pixelsize of label


        """
        if size is not None:
            size *= gf
        if label is not None:
            self.set_xlabel(label, size=size)
        if scale is not None and scale[0] == 'l':
            if min is None: min = 0.1
            if max is None: max = 10
        self.set_xlim(min, max)
        if scale is not None:
            if scale[0] == 'l':
                self.set_xscale(value='log', nonposx='clip', subsx=[2, 3, 4, 5, 6, 7, 8, 9])
            else:
                self.set_xscale(value='linear')
        self.figure.show()

    def Resetlast(self, ):
        pass

    def Legend(self, **kwargs):
        """
        Show/update legend.

        Parameters
        ----------
        charsize, fontsize : int, default 12
            Font size of labels
        labelspacing : int , default =12
            Spacing of labels
        loc : int [0..10] default 1 'upper right'
            Location specifier
            - ‘best’ 	0, ‘upper right’ 1, ‘upper left’ 2, ‘lower left’ 3, ‘lower right’ 4,‘center left’ 6,
        x,y : float [0..1]
            Determines **if both** given loc and sets position in axes coordinates.
            Sets bbox_to_anchor=(x,y)
        kwargs : kwargs of axes.legend
            Any given kwarg overrides the previous


        """
        if 'charsize' in kwargs:
            kwargs['fontsize'] = kwargs.pop('charsize') * 10.
        if 'fontsize' not in kwargs: kwargs['fontsize'] = 10
        if 'labelspacing' not in kwargs: kwargs['labelspacing'] = 0.2
        if 'loc' not in kwargs: kwargs['loc'] = 0  # best
        x = kwargs.pop('x', None)
        y = kwargs.pop('y', None)
        if x is not None and y is not None:
            kwargs['loc'] = 'upper right'
            kwargs['bbox_to_anchor'] = (x, y)
        self.legend(**kwargs)
        self.figure.show()

    def Title(self, title, size=None, **kwargs):
        """set Axes title"""
        if size is not None:
            kwargs.update({'size': size * gf})
        self.set_title(title, **kwargs)
        self.figure.show()

    def Subtitle(self, subtitle, size=None, **kwargs):
        """
        Append subtitle to title
        """
        if size is not None:
            kwargs.update({'size': size * gf})
        # subtitle=self.get_title()+'\n'+subtitle
        self.set_title(subtitle, **kwargs)

    def Clear(self):
        """
        Clear content of this axes.
        """
        self.clear()
        self.figure.show()

    def Text(self, string, x, y, **kwargs):
        size = kwargs.pop('charsize', None)
        rot = kwargs.pop('rot', None)
        if size is not None: kwargs.update({'size': size * gf})
        color = kwargs.pop('color', None)
        if isinstance(color, numbers.Number):
            color = linecolors[divmod(color - 1, len(linecolors) - 1)[1] + 1]
        if color is not None:
            kwargs.update({'color': color})
        self.text(x=x, y=y, s=string, **kwargs)

    def linlog(self, *args, **kwargs):
        self.semilogx(*args, **kwargs)

    def loglin(self, *args, **kwargs):
        self.semilogy(*args, **kwargs)

    def Arrow(self, x1=None, y1=None, x2=None, y2=None, linewidth=None, arrow=None):
        """
        Plot an arrow or line.

        Parameters
        ----------
        x1,y1,x2,y2 : float
            Start/end coordinates in box units [0..1].
        linewidth : float
            Linewidth
        arrow : int or ['-','->','<-','<->']
            Type of arrow.
            If int it selects from ['-','->','<-','<->']


        Returns
        -------

        """
        if isinstance(arrow, numbers.Integral):
            arrow = ['-', '->', '<-', '<->'][arrow]
        self.annotate("",
                      xy=(x1, y1), xycoords='data',
                      xytext=(x2, y2), textcoords='data',
                      arrowprops=dict(arrowstyle=arrow, connectionstyle="arc3", linewidth=linewidth))


# register that it can be used as other Axes
register_projection(jspaperAxes)


class jsFigure(matplotlib.figure.Figure):
    def __init__(self, *args, **kwargs):
        """
        Create figure with Axes as jspaperAxes projection.

        Examples
        --------
        ::

         import jscatter as js
         import numpy as np
         i5=js.dL(js.examples.datapath+'/iqt_1hho.dat')
         p=js.mplot()
         p[0].Plot(i5,sy=[-1,0.4,-1],li=1,legend='Q= $q')
         p[0].Yaxis(scale='l')
         p[0].Title('intermediate scattering function')
         p[0].Legend(x=1.13,y=1) # x,y in relative units of the plot
         p[0].Yaxis(label='I(Q,t)/I(Q,0)',min=0.01, max=1.1)
         p[0].Xaxis(label='Q / 1/nm',min=0,max=120)

        """
        for opt, val in zip(['facecolor', 'frameon', 'facecolor', 'edgecolor'], ['w', False, 'w', 'w']):
            if opt not in kwargs:
                kwargs[opt] = val
        matplotlib.figure.Figure.__init__(self, *args, **kwargs)
        self.add_subplot(1, 1, 1, projection='paper')
        # lastsymbol=[0,0.5,0,0,0]
        # lastline=[0,0,0,0]
        # lasterror=[0,0,0,0]

    def Multi(self, n, m):
        """
        Creates multiple subplots on grid n,m. with projection "jspaperAxes".

        Subplots can be accesses as fig[i]

        """
        for ax in self.axes: self.delaxes(ax)
        nn = 0
        for ni in range(n):
            for mi in range(m):
                nn += 1
                self.add_subplot(n, m, nn, projection='paper')
        self.show()

    def Addsubplot(self, bbox=(0.2, 0.2, 0.6, 0.6), *args, **kwargs):
        """
        Add a subplot in the foreground.

        Parameters
        ----------
        bbox : rect [left, bottom, width, height]
            Bounding box position and size.
        args,kwargs :
            See all arguments for matplotlib subplot except projection.

        Examples
        --------
        ::

         import jscatter as js
         fig=js.mplot()
         fig.Addsubplot() # a default position (dont repeat same positions)
         fig.Addsubplot([0.3,0.3,0.3,0.3])

        """
        bb_axes = [bb.get_position() for bb in self.axes]
        kwargs.update({'position': bbox, 'projection': 'paper'})
        self.add_subplot(*args, **kwargs)
        #for i, bb in enumerate(self.axes[:-1]):
        #    bb.set_position(bb_axes[i])
        self[-1].set_zorder(self[-2].get_zorder() + 1)
        self.show()

    def __getitem__(self, key):
        return self.axes[key]

    def Clear(self):
        """
        Clear content of all axes

        to clear axes use fig.clear()
        """
        for ax in self:
            ax.clear()
        self.show()

    def Save(self, filename, format=None, dpi=None, **kwargs):
        """
        Save with filename
        """
        self.savefig(filename, format=format, dpi=None, **kwargs)

    def is_open(self):
        """
        Is the figure window still open.
        """
        return pyplot.fignum_exists(self.number)

    def Exit(self):
        pass

    def Close(self):
        """
        Close the figure
        """
        pyplot.close(self)

    def plot(self, *args, **kwargs):
        self[0].Plot(*args, **kwargs)

    Plot = plot

    def Xaxis(self, *args, **kwargs):
        self[0].Xaxis(*args, **kwargs)

    def Yaxis(self, *args, **kwargs):
        self[0].Yaxis(*args, **kwargs)

    def Legend(self, *args, **kwargs):
        self[0].Legend(*args, **kwargs)

    def Title(self, *args, **kwargs):
        self[0].Title(*args, **kwargs)

    def Subtitle(self, *args, **kwargs):
        self[0].Subtitle(*args, **kwargs)

    def Text(self, *args, **kwargs):
        self[0].Text(*args, **kwargs)

    def Line(self, *args, **kwargs):
        self[0].Line(*args, **kwargs)


def show(**kwargs):
    """
    Same as pyplot.show(**kwargs)

    Parameters
    ----------
    kwargs : args
        Passed to pyplot.show added by block=False

    """
    kwargs.update(block=False)
    pyplot.show(**kwargs)


def mplot(width=None, height=None, **kwargs):
    """
    Open matplotlib figure in interactive mode with mplot.jsFigure and mplot.jspaperAxes.

    Parameters
    ----------
    width,height : float
        Size of plot in cm.
    kwargs :
        Keyword args of matplotlib.pyplot.figure .

    Returns
    -------
        matplotlib figure

    Notes
    -----
     - By indexing as the axes subplots can be accessed as figure[i] which is figure.axes[i].
     - Same for axes with lines figure[0][i] is figure.axes[0].lines[i].
     - Some methods with similar behaviour as in grace are defined (big letter commands)
     - matplotlib methods are still available (small letters commands)



    """
    inch = 2.54
    pyplot.ion()
    if width is not None and height is not None:
        kwargs.update({'figsize': (width * inch, height * inch)})
    kwargs.update({'FigureClass': jsFigure})
    fig = pyplot.figure(**kwargs)
    return fig


def regrid(x, y, z, shape=None):
    """
    Make a meshgrid from XYZ data columns.

    Parameters
    ----------
    x,y,z : array like
        Array like data should be quadratic or rectangular.
    shape : None, shape or first dimension size
        If None the number of unique values in x is used as first dimension.
        If integer the second dimension is guessed from size.

    Returns
    -------
        2dim arrays for x,y,z

    """
    if shape is None:
        shape = len(np.unique(x))
    if isinstance(shape, numbers.Number):
        shape=(shape, -1)
    try:
        xx = x.reshape(shape)
    except ValueError:
        xx = None
    try:
        yy = y.reshape(shape)
    except ValueError:
        yy = None
    try:
        zz = z.reshape(shape)
    except ValueError:
        zz = None
    return xx, yy, zz


def surface(x, y, z, shape=None, levels=8, colorMap='jet', lineMap=None, alpha=0.7):
    """
    Surface plot of x,y,z, data

    If x,y,z differ because of numerical precision use the shape parameter to give the shape explicitly.

    Parameters
    ----------
    x,y,z : array
        Data as array
    shape : integer, 2x integer
        Shape of image with len(x)=shape[0]*shape[1] or only first dimension.
        See regrid shape parameter.
    levels : integer, array
        Levels for contour lines as number of levels or array of specific values.
    colorMap : string
        Color map name, see showColors.
    lineMap : string
        Color name for contour lines
            b: blue
            g: green
            r: red
            c: cyan
            m: magenta
            y: yellow
            k: black
            w: white
    alpha : float [0,1], default 0.7
        Transparency of surface

    Returns
    -------
        figure

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     R=8
     N=50
     qxy=np.mgrid[-R:R:N*1j, -R:R:N*1j].reshape(2,-1).T
     qxyz=np.c_[qxy,np.zeros(qxy.shape[0])]
     sclattice= js.lattice.scLattice(2.1, 5)
     ds=[[20,1,0,0],[5,0,1,0],[5,0,0,1]]
     sclattice.rotatehkl2Vector([1,0,0],[0,0,1])
     ffs=js.sf.orientedLatticeStructureFactor(qxyz,sclattice,domainsize=ds,rmsd=0.1,hklmax=2)
     fig=js.mpl.surface(qxyz[:,0],qxyz[:,1],ffs[3].array)

    """
    if np.ndim(x) < 2:
        X, Y, Z = regrid(x, y, z, shape)
        if X is None or Z is None or Y is None:
            raise Exception('x,y,z seem not to be on regular grid.')
    cmap = pyplot.get_cmap(colorMap)
    try:
        lmap = pyplot.get_cmap(lineMap)
    except ValueError:
        lmap = lineMap

    fig = pyplot.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, linewidth=1, antialiased=True, alpha=alpha)
    # noinspection PyBroadException
    try:
        contour = ax.contour3D(X, Y, Z, levels, linewidths=1, cmap=lmap)
    except:
        contour = ax.contour3D(X, Y, Z, levels, linewidths=1, colors=lmap)

    ax.set_xlim([min(x), max(x)])
    ax.set_ylim([min(y), max(y)])
    ax.set_zlim([min(z), max(z)])
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    fig.colorbar(surf, shrink=0.8)  # note that colorbar is a method of the figure, not the axes
    pyplot.tight_layout()
    pyplot.show(block=False)
    return fig


def scatter3d(x, y=None, z=None, pointsize=3, color='k'):
    """
    Scatter plot of x,y,z data points.

    Parameters
    ----------
    x,y,z : arrays
        Data to plot. If x.shape is Nx3 these points are used.
    pointsize : float
        Size of points
    color : string
        Colors for points

    Returns
    -------
        figure

    Examples
    --------
    ::

     # ellipsoid with grid build by mgrid
     import jscatter as js
     import numpy as np
     # cubic grid points
     ig=js.formel.randomPointsInCube(200)
     js.mpl.scatter3d(ig.T)


    """
    if np.ndim(x) == 2 and (3 in x.shape):
        try:
            x, y, z = x.T
        except ValueError:
            x, y, z = x
    # cmap = pyplot.get_cmap(colorMap)
    fig = pyplot.figure()
    ax = fig.add_subplot(111, projection='3d')
    sc = ax.scatter(x, y, z, s=pointsize, color=color)
    mi = np.min([x, y])
    ma = np.max([x, y])
    ax.set_xlim(mi, ma)
    ax.set_ylim(mi, ma)
    ax.set_zlim(min(z), max(z))
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_zlabel('Z axis')
    try:
        ax.set_aspect("equal")
    except NotImplementedError:
        # It is not currently possible to manually set the aspect on 3D axes
        pass
    pyplot.tight_layout()
    # fig.colorbar(scatter ,shrink=0.8) # note that colorbar is a method of the figure, not the axes
    pyplot.show(block=False)
    return fig


def _isregularspaced(sequence):
    diff=np.diff(np.unique(sequence))
    return np.all(np.isclose(diff, diff[0]))


def contourImage(x, y=None, z=None, levels=None, fontsize=10, colorMap='jet', scale='norm', lineMap=None, title=None,
                 axis=None, origin='lower', block=False, invert_yaxis=False, invert_xaxis=False,
                 linthresh=1, linscale=1, badcolor=None):
    """
    Image with contour lines of 3D dataArrays or image array.

    Parameters
    ----------
    x,y,z : arrays
        x,y,z coordinates for z display in x,y location.
        If x is image array this is used.
        If x is dataArray we plot like x,y,z=x.X,x.Z,x.Y as dataArray use always .Y as value in X,Z coordinates.
    levels : int, None, sequence of values
        Number of contour lines between min and max or sequence of specific values.
    colorMap : string
        Get a colormap instance from name.
        Standard mpl colormap name (see showColors).
    badcolor : float, color
        Set the color for bad values (like masked pixel) values in an image.
        Default is  bad values be transparent.
        Color can be matplotlib color as 'k','b' or
        float value in interval [0,1] of the chosen colorMap.
        0 sets to minimum value, 1 to maximum value.
    scale : 'log', 'symlog', default = 'norm'
        Scale for intensities.

        - 'norm' Linear scale.
        - 'log' Logarithmic scale
        - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
          and negative directions from the origin. This works also for only positive data.
          Use linthresh, linscale to adjust.
    linthresh : float, default = 1
        Only used for scale 'sym'.
        The range within which the plot is linear (-linthresh to linthresh).
    linscale : float, default = 1
        Only used for scale 'sym'.
        Its value is the number of decades to use for each half of the linear range.
        E.g. 10 uses 1 decade.
    lineMap : string
        Label color
        Colormap name as in colorMap, otherwise as cs in in Axes.clabel
        * if None, the color of each label matches the color of the corresponding contour
        * if one string color, e.g., colors = ‘r’ or colors = ‘red’, all labels will be plotted in this color
        * if a tuple of matplotlib color args (string, float, rgb, etc),
          different labels will be plotted in different colors in the order specified
    fontsize : int, default 10
        Size of line labels in pixel
    title : None, string
        Title of the plot.
        May be set by fig.axes[0].set_title('title')
    axis : None, 'pixel'
        If coordinates should be forced to pixel.
        Wavevectors are used only for sasImage using getPixelQ.
    invert_yaxis,invert_xaxis : bool
        Invert corresponding axis.
    block : bool
        Open in blocking or non-blocking mode
    origin : 'lower','upper'
        Origin of the plot. See matplotlib imshow.


    Returns
    -------
        figure

    Notes
    -----
    For irregular distributed points (x,z,y) the point positions can later be added by ::

     fig.axes[0].plot(x, y, 'ko', ms=1)
     js.mpl.pyplot.show(block=False)


    Examples
    --------
    Create log scale image for maskedArray (sasImage) ::

     import jscatter as js
     import numpy as np
     # sets negative values to zero
     calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
     fig=js.mpl.contourImage(calibration,title='Calibration lin scale')
     fig=js.mpl.contourImage(calibration,scale='log')
     #
     # change labels and title
     ax=fig.axes[0]
     ax.set_xlabel('qx ')
     ax.set_ylabel('qy')
     ax.set_title(r'Calibration log scaled')
     js.mpl.pyplot.show(block=False)

    Use ``scale='symlog'`` for mixed lin=log scaling to pronounce low scattering. ::

     import jscatter as js
     import numpy as np
     # sets negative values to zero
     bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
     fig=js.mpl.contourImage(bsa,scale='sym',linthresh=30, linscale=10)

    Other examples ::

     import jscatter as js
     import numpy as np
     # On a regular grid
     x,z=np.mgrid[-5:5:0.1,-5:5:0.1]
     xyz=js.dA(np.c_[x.flatten(),
                     z.flatten(),
                     0.3*np.sin(x*z/np.pi).flatten()+0.01*np.random.randn(len(x.flatten())),
                     0.01*np.ones_like(x).flatten() ].T)
     # set columns where to find X,Y,Z )
     xyz.setColumnIndex(ix=0,iy=2,iz=1)
     # determine yourself what is x,y,z
     fig=js.mpl.contourImage(xyz.X,xyz.Z,xyz.Y)
     # determined automatically from values in setColumnIndex above
     js.mpl.contourImage(xyz)
     #fig.savefig(js.examples.imagepath+'/contourImage.jpg')

    .. image:: ../../examples/images/contourImage.jpg
     :align: center
     :width: 50 %
     :alt: contourImage

    If points are missing the tricontour allows interpolation of missing contours.
    In this case contour lines are used. ::

     # remove each 3rd point that we have missing points
     # like random points
     x,z=js.formel.randomPointsInCube(1500,0,2).T*10-5
     xyz=js.dA(np.c_[x.flatten(),
                     z.flatten(),
                     1.3*np.sin(x*z/np.pi).flatten()+0.001*np.random.randn(len(x.flatten()))].T)
     xyz.setColumnIndex(ix=0,iy=2,iz=1)
     js.mpl.contourImage(xyz)



    """
    fig = pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)

    # use copy so that we do not mutate the global colormap instance; stupid matplotlib programmers
    cmap = copy.copy(pyplot.get_cmap(colorMap))
    if badcolor is not None:
        # set bad color
        if isinstance(badcolor, numbers.Number):
            cmap.set_bad(color=cmap(badcolor))
        else:
            cmap.set_bad(color=badcolor)

    try:
        lmap = copy.copy(pyplot.get_cmap(lineMap))
    except ValueError:
        lmap = lineMap

    # determine the scaling (norm)
    # determine vmin,vmax later
    if scale[:3] == 'log':
        norm=colors.LogNorm(clip=True)
    elif scale[:3] == 'sym':
        norm = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
    else:  # default: scale == 'normalize':
        norm=colors.Normalize(clip=True)

    if np.ndim(x) < 2 or hasattr(x, '_isdataArray'):
        if hasattr(x, '_isdataArray'):
            x, y, z = x.X, x.Z, x.Y

        z = np.copy(z)
        # test if data are gridded otherwise tricontour interpolates
        if _isregularspaced(x) and _isregularspaced(y):
            # treat like image with regular pixels
            xx, yy, zz = regrid(x, y, z, np.unique(x).shape[0])
            extend = [np.min(xx), np.max(xx), np.min(yy), np.max(yy)]
            norm.autoscale(zz)
            im = ax.imshow(zz, cmap=cmap, extent=extend, origin=origin, norm=norm)
            if levels is not None:
                im.cset = ax.contour(zz, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin, norm=norm)
                im.labels = ax.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
        else:
            # interpolate to regular grid inside of tricontour
            extend = [np.min(x), np.max(x), np.min(y), np.max(y)]
            norm.autoscale(z)
            if isinstance(levels, numbers.Integral):
                levels=np.r_[norm.vmin:norm.vmax:levels*1j]
            elif not isinstance(levels, (list, tuple)):
                levels=None
            im2 = ax.tricontour(x, y, z, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin, norm=norm)
            im = ax.tricontourf(x, y, z, levels=levels, cmap=cmap, extent=extend, origin=origin, norm=norm)
        fig.colorbar(im)  # note that colorbar is a method of the figure, not the axes

    else:
        # image array, copy protects original from being modified
        # we need to take care if it is array or masked_array to copy
        # using e.g. norm='log'  mask zero values
        if np.ma.is_masked(x):
            # copy including mask
            z = np.ma.copy(x)
        else:
            z = np.copy(x)

        if np.issubdtype(z.dtype, np.integer):
            # dtype int32 throws sometimes error  "TypeError: Cannot cast array data from dtype('int32') ..."
            z=z.astype('float')

        if axis != 'pixel':
            # if it is an sasImage we get xy from getPixelQ
            x, y = x.pQaxes()
            extend = [np.min(y), np.max(y), np.min(x), np.max(x)]
        else:
            extend = None

        # determine vmax and vmin
        norm.autoscale(z)

        im = ax.imshow(z, cmap=cmap, extent=extend, origin=origin, norm=norm)
        if levels is not None:
            im.cset = ax.contour(z, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin, norm=norm)
            im.labels = ax.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
        fig.colorbar(im)  # note that colorbar is a method of the figure, not the axes

    if title is not None:
        ax.set_title(title)
    if invert_yaxis:   ax.invert_yaxis()
    if invert_xaxis:   ax.invert_xaxis()

    pyplot.show(block=block)
    return fig


def showColors():
    """
    Get a list of the colormaps in matplotlib.

    Ignore the ones that end with '_r' because these are
    simply reversed versions of ones that don't end with '_r'

    Colormaps Names
     Accent, Accent_r, Blues, Blues_r, BrBG, BrBG_r, BuGn, BuGn_r, BuPu, BuPu_r,
     CMRmap, CMRmap_r, Dark2, Dark2_r, GnBu, GnBu_r, Greens, Greens_r, Greys,
     Greys_r, OrRd, OrRd_r, Oranges, Oranges_r, PRGn, PRGn_r, Paired, Paired_r,
     Pastel1, Pastel1_r, Pastel2, Pastel2_r, PiYG, PiYG_r, PuBu, PuBuGn,
     PuBuGn_r, PuBu_r, PuOr, PuOr_r, PuRd, PuRd_r, Purples, Purples_r,
     RdBu, RdBu_r, RdGy, RdGy_r, RdPu, RdPu_r, RdYlBu, RdYlBu_r, RdYlGn,
     RdYlGn_r, Reds, Reds_r, Set1, Set1_r, Set2, Set2_r, Set3, Set3_r,
     Spectral, Spectral_r, Vega10, Vega10_r, Vega20, Vega20_r, Vega20b,
     Vega20b_r, Vega20c, Vega20c_r, Wistia, Wistia_r, YlGn, YlGnBu, YlGnBu_r,
     YlGn_r, YlOrBr, YlOrBr_r, YlOrRd, YlOrRd_r, afmhot, afmhot_r, autumn,
     autumn_r, binary, binary_r, bone, bone_r, brg, brg_r, bwr, bwr_r, cool,
     cool_r, coolwarm, coolwarm_r, copper, copper_r, cubehelix, cubehelix_r,
     flag, flag_r, gist_earth, gist_earth_r, gist_gray, gist_gray_r, gist_heat,
     gist_heat_r, gist_ncar, gist_ncar_r, gist_rainbow, gist_rainbow_r, gist_stern,
     gist_stern_r, gist_yarg, gist_yarg_r, gnuplot, gnuplot2, gnuplot2_r, gnuplot_r,
     gray, gray_r, hot, hot_r, hsv, hsv_r, inferno, inferno_r, jet, jet_r, magma,
     magma_r, nipy_spectral, nipy_spectral_r, ocean, ocean_r, pink, pink_r, plasma,
     plasma_r, prism, prism_r, rainbow, rainbow_r, seismic, seismic_r, spectral,
     spectral_r, spring, spring_r, summer, summer_r, tab10, tab10_r, tab20, tab20_r,
     tab20b, tab20b_r, tab20c, tab20c_r, terrain, terrain_r, viridis, viridis_r,
     winter, winter_r

    From
    https://matplotlib.org/1.2.1/examples/pylab_examples/show_colormaps.html

    """
    a = np.linspace(0, 1, 256).reshape(1, -1)
    a = np.vstack((a, a))
    # Get a list of the colormaps in matplotlib.  Ignore the ones that end with
    # '_r' because these are simply reversed versions of ones that don't end
    # with '_r'
    maps = sorted(m for m in pyplot.cm.datad if not m.endswith("_r"))
    nmaps = len(maps) + 1
    #
    fig = pyplot.figure(figsize=(5, 10))
    fig.subplots_adjust(top=0.99, bottom=0.01, left=0.2, right=0.99)
    for i, m in enumerate(maps):
        ax = pyplot.subplot(nmaps, 1, i + 1)
        pyplot.axis("off")
        pyplot.imshow(a, aspect='auto', cmap=pyplot.get_cmap(m), origin='lower')
        pos = list(ax.get_position().bounds)
        fig.text(pos[0] - 0.01, pos[1], m, fontsize=10, horizontalalignment='right')
    #
    pyplot.show(block=False)


def test(keepopen=True):
    """
    A small test for mpl module making a plot.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     from matplotlib import pyplot
     # use this
     #fig=pyplot.figure(FigureClass=js.mpl.Figure)
     # or
     fig=js.mplot()
     fig.Multi(2,1)
     fig[0].SetView(0.1,0.25,0.8,0.9)
     fig[1].SetView(0.1,0.09,0.8,0.23)
     q=js.loglist(0.01,5,100)
     aa=js.dL()
     for pp in range(5):
         aa.append(js.dA(np.c_[q,-pp*np.sin(q),0.2*np.cos(5*q)].T))
         aa[-1].qq=pp
     bb=js.dA(np.c_[q,q**2].T)
     bb.qq=123
     for pp in range(5):
         fig[0].Plot(aa[pp].X,-1*aa[pp].Y,legend='some stufff',sy=[1,(pp+1)/10.],li=0)

     fig[0].Plot(aa, legend='qq = $qq', sy=[-1, 0.4, -1, ''], li=0, markeredgewidth=1)
     for pp in range(5):
         fig[1].Plot(aa[-1].X/5+pp,pp*aa[-1].Y,legend='q=%.1f' %pp,sy=0,li=-1,markeredgewidth =1)
     fig[1].Plot(bb,legend='sqr=$qq ',sy=2,li=2)
     fig[0].Title('test')
     fig[0].Legend(x=1.3,y=1)
     fig[1].Legend(x=1.3,y=1)
     fig[0].Yaxis(label='y-axis')
     fig[1].Yaxis(label='something else')
     fig[0].tick_params(labelbottom=False)
     fig[1].Xaxis(label='x-axis')

    """

    import jscatter as js
    import numpy as np
    # use this
    # fig=pyplot.figure(FigureClass=js.mpl.Figure)
    # or
    fig = js.mplot()
    fig.Multi(2, 1)
    fig[0].SetView(0.1, 0.25, 0.8, 0.9)
    fig[1].SetView(0.1, 0.09, 0.8, 0.23)
    q = js.loglist(0.01, 5, 100)
    aa = js.dL()
    for pp in range(5):
        aa.append(js.dA(np.c_[q, -pp * np.sin(q), 0.2 * np.cos(5 * q)].T))
        aa[-1].qq = pp
    bb = js.dA(np.c_[q, q ** 2].T)
    bb.qq = 123
    for pp in range(5):
        fig[0].Plot(aa[pp].X, -1 * aa[pp].Y, legend='some stufff', sy=[1, (pp + 1) / 10.], li=0)

    fig[0].Plot(aa, legend='qq = $qq', sy=[-1, 0.4, -1, ''], li=0, markeredgewidth=1)
    for pp in range(5):
        fig[1].Plot(aa[-1].X / 5 + pp, pp * aa[-1].Y, legend='q=%.1f' % pp, sy=0, li=-1, markeredgewidth=1)
    fig[1].Plot(bb, legend='sqr=$qq ', sy=2, li=2)
    fig[0].Title('test')
    fig[0].Legend(x=1.3, y=1)
    fig[1].Legend(x=1.3, y=1)
    fig[0].Yaxis(label='y-axis')
    fig[1].Yaxis(label='something else')
    fig[0].tick_params(labelbottom=False)
    fig[1].Xaxis(label='x-axis')

    import jscatter as js
    import numpy as np
    calibration = js.sas.sasImage(js.examples.datapath + '/calibration.tiff')
    fig = js.mpl.contourImage(np.ma.log(calibration))

    x, z = np.mgrid[-5:5:0.25, -5:5:0.25]
    xyz = js.dA(np.c_[x.flatten(), z.flatten(), 0.3 * np.sin(x * z / np.pi).flatten() + 0.01 * np.random.randn(
        len(x.flatten())), 0.01 * np.ones_like(x).flatten()].T)
    xyz.setColumnIndex(ix=0, iy=2, iz=1)
    js.mpl.contourImage(xyz)

    # random distributed points
    x, z = js.formel.randomPointsInCube(1500, 0, 2).T * 10 - 5
    xyz = js.dA(np.c_[x.flatten(), z.flatten(), 0.3 * np.sin(x * z / np.pi).flatten() + 0.01 * np.random.randn(
        len(x.flatten()))].T)
    xyz.setColumnIndex(ix=0, iy=2, iz=1)
    js.mpl.contourImage(xyz)

    if keepopen:
        return fig
    else:
        fig.Close()
