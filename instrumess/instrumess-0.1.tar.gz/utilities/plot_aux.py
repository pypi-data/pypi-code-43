# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 01:23:20 2017

@author: Rastko
"""

import matplotlib.pyplot as plt
import matplotlib.colors
import numpy as np
import win32gui
import win32con
import matplotlib.gridspec as gridspec
from pathlib import Path
import utilities as ut

colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

# TODO update existing fiugures instead of generating new ones
# TODO add figure name when ploting


def save_last_fig(name=None, dest=None, filetype='png', dpi=150):
    """Save last ploted figure"""
    if name is None:
        name = plt.gcf().get_label()
    if dest is None:
        dest = 'D:/Dropbox/PhD - ITL for SS-OCT/Presentations'
    dest = Path(dest)
    if filetype in ['png', 'pdf']:
        plt.savefig(dest/'{}.{}'.format(name,filetype),
                    bbox_inches='tight', dpi=dpi)
    else:
        raise ValueError('"{}" is not caught by if-elif of '
                         'save_last_fig function'.format(filetype))




def fig_label(ax, string, pos='tl', offset=0.04, size=14):
    """Label axis ax with string
    
    Parameters:
    -----------
    pos - position on the axis takes [t(op), b(ottom), r(ight), l(eft)]
          strings in any order
    """
    pos = pos.lower()

    # allign horizontally
    if 'l' in pos:
        x = offset
        xal = 'left'
    elif 'r':
        x = 1 - offset
        xal = 'right'
    else:
        x = 0.5
        xal = 'center'

    # get the aspect ratio
    coo = ax.get_window_extent().get_points()
    aspect_r = (coo[0][0]-coo[1][0])/(coo[0][1]-coo[1][1])
    offset = aspect_r*offset
    
    # align vertically
    if 't' in pos:
        y = 1 - offset
        yal = 'top'
    elif 'b' in pos:
        y = offset
        yal = 'bottom'
    else:
        y = 0.5
        yal = 'center'
    
    # print text
    text_object = ax.text(x, y, string, ha=xal, va=yal, transform=ax.transAxes,
                          fontsize=size)
    return text_object


def fig_pos(position=None):
    """Set figure position from 0, works nicely up to 5, then tile"""
    if position is None:
        position = len(plt.get_fignums())-1
    manager = plt.get_current_fig_manager()
    geom = manager.window.geometry().getRect()
    dx = geom[2]
    dy = geom[3]
    # x position in pixels from left
    x = (position % 3)*(dx + 5) + 5
    # y position in pixels from top
    y = position//3*dy + 35*(1+position//3)
    
    if position > 5:
        x = 2*(dx + 5) + 5
        y = dy + 35*2
        y = y + 35*(position-5)
    manager.window.setGeometry(x, y, dx, dy)
#    print(position)
    return y


def fft(time, y, name='fft'):
    """Plot fft of a time domain signal, assumed equidistand"""
    from utilities import fft as ut_fft
    try:
        dy = time[1] - time[0]
    except:
        pass
    try:
        dy = time.iloc[1] - time.iloc[0]
    except:
        pass
    f, y = ut_fft(y, dy)
    fig, ax = fig_new(name=name)
    ax.plot(f, y)
    ax.set(
        xlabel='Frequency [Hz]',
        ylabel='ylab',
    )
    fig.tight_layout()
    return fig, ax
    

def _fig_raise():
    """Raise figure window"""
    plt.ion()
    plt.show()
    plt.get_current_fig_manager().window.activateWindow()
    plt.get_current_fig_manager().window.raise_()
    
#    win32gui.SetForegroundWindow()
    
    # if that didn't work, use this
    HWND = win32gui.GetActiveWindow()
    win32gui.ShowWindow(HWND, win32con.SW_RESTORE)
    win32gui.SetWindowPos(HWND,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(HWND,win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)
    win32gui.SetWindowPos(HWND,win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_SHOWWINDOW + win32con.SWP_NOMOVE + win32con.SWP_NOSIZE)

    return 1


def fig_2y(color_left=colors[0], color_right=colors[1], name='fig_2y'):
    """Plot with 2y axis"""
    existing_figures = plt.get_figlabels()
    figure_exists = name in existing_figures
    fig = plt.figure(name)
    if figure_exists:
        fig.clf()
    else:
        # don't reposition the figure if it already exists
        fig_pos()
    ax1 = fig.add_subplot(1,1,1)
    ax2 = ax1.twinx()
    
    ax1.set_ylabel('left label', color=color_left)
    ax2.spines['left'].set_color(color_left)
    ax2.spines['right'].set_color(color_right)
    ax1.tick_params('y', colors=color_left)
    
    ax2.set_ylabel('right label', color=color_right)
    ax2.tick_params('y', colors=color_right)
    
    plt.tight_layout()
    _fig_raise()
    return fig, ax1, ax2


def fig_2y_stacked(name=None, top_ticks='right'):
    """Two stacked Plots with shared x axis"""
    existing_figures = plt.get_figlabels()
    figure_exists = name in existing_figures
    
    fig = plt.figure(name)
    _fig_raise()
    if figure_exists:
        fig.clf()
    else:
        # don't reposition the figure if it already exists
        fig_pos()
    (ax1,ax2) = fig.subplots(nrows=2, sharex=True)
    
    if top_ticks=='right':
        ax1.yaxis.tick_right()
        ax1.yaxis.set_label_position("right")
    plt.setp(ax1.get_xticklabels(), visible=False)
    
    fig.subplots_adjust(hspace=0)
    return fig, ax1, ax2


def fig_3y_stacked(name=None):
    """Three stacked Plots with shared x axis"""
    existing_figures = plt.get_figlabels()
    figure_exists = name in existing_figures
    
    fig = plt.figure(name)
    _fig_raise()
    if figure_exists:
        fig.clf()
    else:
        # don't reposition the figure if it already exists
        fig_pos()
    (ax1,ax2,ax3) = fig.subplots(nrows=3, sharex=True)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    ax3.set(xlabel='xlab', ylabel='ylab')
    fig.tight_layout()
    fig.subplots_adjust(hspace=0)
    return fig, ax1, ax2, ax3


def fig_2x(name=None):
    """Two plots side-by-side with share y axis"""
    existing_figures = plt.get_figlabels()
    figure_exists = name in existing_figures
    
    fig = plt.figure(name)
    _fig_raise()
    if figure_exists:
        fig.clf()  # don't reposition the figure if it already exists
    else:
        fig_pos()
    gs = gridspec.GridSpec(nrows=1, ncols=2, wspace=0.1,
                           width_ratios=[2,1])
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1], sharey=ax1)

    # (ax1,ax2) = fig.subplots(ncols=2, sharey=True,
    #                          gridspec_kw={'width_ratios':[2,1],
    #                                       'wspace':0.1,
    #                                       })
    plt.setp(ax2.get_xticklabels()[0], visible=False)
    ax2.set_xlabel('# in bin')
    plt.tick_params(axis='y',          # changes apply to the y-axis
                    which='both',      # both major and minor ticks are affected
                    left=False,        # ticks along the left edge are off
                    labelleft=False)
    return fig, ax1, ax2, gs


def fig_new(name=None,position=None):
    """New figure, placed and named"""
    existing_figures = plt.get_figlabels()
    figure_exists = name in existing_figures
    
    fig = plt.figure(name)
    if figure_exists:
        fig.clf()
    else:
        # don't reposition the figure if it already exists
        fig_pos(position)
    ax = fig.add_subplot(1,1,1)
    _fig_raise()
    return fig, ax


def spectrum(wl, p, name='Spectrum', ylabel='Power [dBm]'):
    """Plot a spectrum"""
    fig, ax = fig_new(name=name)
    ax.plot(wl, p)
    ax.set(
        xlabel='Wavelength [nm]',
        ylabel=ylabel,
    )
    fig.tight_layout()
    return fig, ax


def array2cmap(x):
    """Turn a 3 column rgb array into a LinearSegmentedColormap"""
    N = x.shape[0]

    r = np.linspace(0., 1., N+1)
    r = np.sort(np.concatenate((r, r)))[1:-1]

    rd = np.concatenate([[x[i, 0], x[i, 0]] for i in range(N)])
    gr = np.concatenate([[x[i, 1], x[i, 1]] for i in range(N)])
    bl = np.concatenate([[x[i, 2], x[i, 2]] for i in range(N)])

    rd = tuple([(r[i], rd[i], rd[i]) for i in range(2 * N)])
    gr = tuple([(r[i], gr[i], gr[i]) for i in range(2 * N)])
    bl = tuple([(r[i], bl[i], bl[i]) for i in range(2 * N)])

    cdict = {'red': rd, 'green': gr, 'blue': bl}
    return matplotlib.colors.LinearSegmentedColormap('my_colormap', cdict, N)

        
def interactive_legend(ax=None):
    """Add an interactive legend to ax"""
    if ax is None:
        ax = plt.gca()
    if ax.legend_ is None:
        ax.legend()
    return InteractiveLegend(ax.legend_)


class InteractiveLegend(object):
    """Interactive legend from teh internets"""
    
    def __init__(self, legend):
        """Initialize interactive legend instance"""
        self.legend = legend
        self.fig = legend.axes.figure

        self.lines, self.leg_lines, self.text = self._build_handles(legend)
        self.clickables = self.lines+self.leg_lines+self.text
        self._setup_connections()

        self.fig.canvas.draw()
#        self.update()

    def _setup_connections(self):
        for artist in self.legend.texts + self.legend.legendHandles:
            artist.set_picker(10) # 10 points tolerance

        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)

    def _build_handles(self, legend):
        text = legend.texts
        leg_lines = legend.legendHandles
        lines = []
        labels = [t.get_text() for t in legend.texts]
        for artist in legend.axes.get_children():
            if artist.get_label() in labels:
                lines.append(artist)

        return lines, leg_lines, text

    def on_pick(self, event):
        self.toggle_vis(event.artist)
        self.fig.canvas.draw()

    def on_click(self, event):
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lines+self.leg_lines:            
            self.set_vis(artist, visible)
        self.fig.canvas.draw()

    def set_vis(self, artist, vis):
        if artist in self.leg_lines:
            if vis is True:
                artist.set_alpha(1)
            else:
                artist.set_alpha(0.2)
        else:
            artist.set_visible(vis)
            
    def toggle_vis(self, artist):
        if artist in self.leg_lines:
            ind = self.leg_lines.index(artist)
            vis = self.lines[ind].get_visible()
            if vis is True:
                artist.set_alpha(0.2)
            else:
                artist.set_alpha(1)
            self.lines[ind].set_visible(not vis)
        elif artist in self.text:
            ind = self.text.index(artist)
            vis = self.lines[ind].get_visible()
            if vis is True:
                self.leg_lines[ind].set_alpha(0.2)
            else:
                self.leg_lines[ind].set_alpha(1)
            self.lines[ind].set_visible(not vis)
        elif artist in self.lines:
            artist.set_visible(not vis)
            ind = self.lines.index(artist)
            if vis is True:
                self.leg_lines[ind].set_alpha(0.2)
            else:
                self.leg_lines[ind].set_alpha(1)

    def show(self):
        plt.show()

def update_errorbar(errobj, x, y, y_error):
    ln, (erry_top, erry_bot), (barsy,) = errobj

    ln.set_data(x,y)
    x_base = x
    y_base = y

    yerr_top = y_base + y_error
    yerr_bot = y_base - y_error

    erry_top.set_xdata(x_base)
    erry_bot.set_xdata(x_base)
    erry_top.set_ydata(yerr_top)
    erry_bot.set_ydata(yerr_bot)

    new_segments_y = [np.array([[x, yt], [x,yb]])
                      for x, yt, yb in zip(x_base, yerr_top, yerr_bot)]
    barsy.set_segments(new_segments_y)

backend = plt.rcParams['backend']


def update_fig(wait=0.01):
    """Update figure in the bkg, plt.ion() and plt.show(block=False) first"""
    if backend in matplotlib.rcsetup.interactive_bk:
        figManager = matplotlib._pylab_helpers.Gcf.get_active()
        if figManager is not None:
            canvas = figManager.canvas
            if canvas.figure.stale:
                canvas.draw()
            canvas.start_event_loop(wait)
            return
