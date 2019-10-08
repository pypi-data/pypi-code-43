# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 14:39:35 2016

@author: Stephan Rein

Handlings of the three figures during preprocessing and analysis procedure.
Figure Canvas class is used in a PyQt container.
Different functions are used for the representation
of preprocessing, fitting, regularization and
global fitting. Most handlers are overloaded to
handle variable input.

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2017, Stephan Rein, M.Sc., University of Freiburg
"""
from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanv
from matplotlib.figure import Figure
import numpy as np
import warnings as warnings
warnings.filterwarnings("ignore")
matplotlib.use("Qt5Agg")


try:
    mat_version = repr(matplotlib.__version__)
    mat_version_str = (eval(mat_version))
    num_ver = (mat_version_str).split('.')
    if int(num_ver[0]) == 2:
        fonts = 8
    else:
        fonts = 10
except:
    fonts = 9


def figure_handler_init(s, boolean, n):
    FigCanv.setSizePolicy(s, QSizePolicy.Expanding, QSizePolicy.Expanding)
    if boolean:
        if n == 1:
            s.figuresw = Figure()
            s.figuresw.set_facecolor('white')
            s.canvas1 = FigCanv(s.figuresw)
            s.layout1 = QVBoxLayout(s.Plotdist1)
            s.layout1.addWidget(s.canvas1)
            s.ax1 = s.figuresw.add_subplot(111)
            s.ax1.set_yticks([])
            s.ax1.set_xticks([])
        elif n == 2:
            s.figurese = Figure()
            s.figurese.set_facecolor('white')
            s.canvas2 = FigCanv(s.figurese)
            s.layout2 = QVBoxLayout(s.Plotdist2)
            s.layout2.addWidget(s.canvas2)
            s.ax2 = s.figurese.add_subplot(111)
            s.ax2.set_yticks([])
            s.ax2.set_xticks([])
        elif n == 3:
            s.figuren = Figure()
            s.figuren.set_facecolor('white')
            s.canvas3 = FigCanv(s.figuren)
            s.layout3 = QVBoxLayout(s.PlotTT1)
            s.layout3.addWidget(s.canvas3)
            s.ax3 = s.figuren.add_subplot(111)
            s.ax3.set_yticks([])
            s.ax3.set_xticks([])
        return


def figure_handler(s, xdata, ydata, n, cut=300000, bg_time=None, bg=None,
                   zerotime=0):
    if n == 3:
        # PELDOR time trace
        not_red = False
        s.ax3.clear()
        s.ax3 = s.figuren.add_subplot(111)
        s.ax3.set_autoscaley_on(False)
        s.ax3.axis('auto')
        s.ax3.set_xlabel('$time\, \mathrm{/ \, ns}$', size=fonts)
        s.ax3.set_ylabel('$Intensity$', size=fonts)
        zooming = 6/(s.ZoomFTScrollBar_2.value()+1)
        if (abs(max(ydata))+abs(min(ydata)) > 0.01 and abs(max(ydata)) > 0.5):
            s.ax3.set_ylim([min(ydata)-0.02*abs(min(ydata)), max(ydata) +
                            0.02*abs(max(ydata))])
        elif (abs(max(ydata))+abs(min(ydata)) > 0.01 and
              abs(max(ydata)) < 0.5):
            s.ax3.set_ylim([min(ydata)-0.8*abs(min(ydata)), max(ydata) +
                            0.8*abs(max(ydata))])
        else:
            s.ax3.set_ylim([min(ydata)-0.01, max(ydata)+0.01])
            not_red = True
        s.ax3.set_xlim([min(xdata), max(xdata)/zooming])
        s.ax3.set_title('PELDOR time trace', size=fonts)
        for tick in s.ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax3.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-1)
        s.ax3.plot(xdata, ydata)
        if bg_time is not None:
            pass
            s.ax3.plot(bg_time, bg)
        s.ax3.plot(xdata, np.ones(len(xdata)))
        if not not_red:
            s.ax3.plot(xdata, np.zeros(len(xdata)))
        s.ax3.axvline(zerotime, color='k', linestyle='--')
        s.ax3.axvline(cut, color='r')
        s.figuren.tight_layout()
        s.figuren.subplots_adjust(left=0.12, bottom=0.18, right=0.98, top=0.92)
        s.canvas3.draw()
    if n == 1:
        # PELDOR time trace
        s.ax1.clear()
        s.ax1 = s.figuresw.add_subplot(111)
        s.ax1.set_autoscaley_on(False)
        s.ax1.axis('auto')
        s.ax1.set_xlabel('$time\, \mathrm{/ \, ns}$', size=fonts)
        s.ax1.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
        xmax = max(xdata)
        if cut < xmax:
            xmax = cut
        s.ax1.set_ylim([min(ydata)-0.05*abs(min(ydata)), max(ydata) +
                        0.05*abs(max(ydata))])
        zooming = 6/(s.ZoomFTScrollBar_3.value()+1)
        s.ax1.set_xlim([min(xdata), xmax/zooming])
        s.ax1.set_title('Bg. corrected', size=fonts)
        #if max(xdata)/zooming > 2000:
        #    s.ax1.xaxis.set_ticks(np.arange(0, xmax/zooming, 1000))
        for tick in s.ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        for tick in s.ax1.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax1.plot(xdata, ydata)
        s.figuresw.tight_layout()
        s.figuresw.subplots_adjust(left=0.24, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas1.draw()
    if n == 2:
        # Fourier transform
        s.ax2.clear()
        s.ax2 = s.figurese.add_subplot(111)
        s.ax2.set_autoscaley_on(False)
        s.ax2.axis('auto')
        s.ax2.set_xlabel('$\omega\, \mathrm{/ \, MHz}$', size=fonts)
        s.ax2.set_ylabel('$Int$', size=fonts)
        zooming = pow(1.4, 3-s.ZoomFTScrollBar.value())
        s.ax2.set_ylim([min(ydata[0:100]), max(ydata) +
                        0.02*abs(max(ydata))])
        s.ax2.set_xlim([-10*zooming, 10*zooming])
        s.ax2.set_title('Fourier transform', size=fonts)
        for tick in s.ax2.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax2.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax2.plot(xdata, ydata)
        s.ZoomFTScrollBar.value()
        s.figurese.tight_layout()
        s.figurese.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas2.draw()
    return


def figure_handler_fit(s, xdata, ydata, n, redline=8, y2data=None):
    if n == 3:
        # PELDOR time trace
        s.ax3.clear()
        s.ax3 = s.figuren.add_subplot(111)
        s.ax3.set_autoscaley_on(False)
        s.ax3.axis('auto')
        s.ax3.set_xlabel('$time \, \mathrm{/ \, ns}$', size=fonts)
        s.ax3.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
        if abs(max(ydata))-abs(min(ydata)) > 0.01:
            s.ax3.set_ylim([min(ydata)-0.02*abs(min(ydata)), max(ydata) +
                            0.02*abs(max(ydata))])
        else:
            s.ax3.set_ylim([min(ydata)-1.0*abs(min(ydata)), max(ydata) +
                            1.0*abs(max(ydata))])
        s.ax3.set_xlim([min(xdata), max(xdata)])
        s.ax3.set_title('PELDOR time trace', size=fonts)
        for tick in s.ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax3.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-1)
        s.ax3.plot(xdata, ydata)
        s.ax3.plot(xdata, y2data, 'r', linewidth=1.5)
        s.figuren.tight_layout()
        s.figuren.subplots_adjust(left=0.14, bottom=0.18, right=0.97, top=0.92)
        s.canvas3.draw()
    if n == 1:
        # Distance distribution
        if s.normalize_to_maximum:
            ydata = ydata/max(ydata)
        else:
            ydata = ydata/sum(ydata)
        s.ax1.clear()
        s.ax1 = s.figuresw.add_subplot(111)
        s.ax1.set_autoscaley_on(False)
        s.ax1.axis('on')
        s.ax1.set_xlabel('$r \, \mathrm{/ \, nm}$', size=fonts)
        s.ax1.set_ylabel('$P(r)$', size=fonts)
        s.ax1.set_ylim([0, max(ydata)+max(ydata)/15])
        s.ax1.set_xlim([min(xdata), max(xdata)])
        s.ax1.axvline(redline, color='r', linestyle='--')
        s.ax1.set_title('Distance distribution', size=fonts)
        for tick in s.ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax1.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax1.plot(xdata, ydata)
        s.figuresw.tight_layout()
        s.figuresw.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas1.draw()
    if n == 2:
        # Fourier transform
        s.ax2.clear()
        s.ax2 = s.figurese.add_subplot(111)
        s.ax2.set_autoscaley_on(False)
        s.ax2.axis('auto')
        s.ax2.set_xlabel('$\omega\, \mathrm{/ \, MHz}$', size=fonts)
        s.ax2.set_ylabel('$Int$', size=fonts)
        s.ax2.set_ylim([min(ydata[0:100]), max(ydata) +
                        0.02*abs(max(ydata))])
        s.ax2.set_xlim([-10, 10])
        s.ax2.set_title('Fourier transform', size=fonts)
        for tick in s.ax2.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax2.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax2.plot(xdata, ydata)
        s.ax2.plot(xdata, y2data, 'r', linewidth=1.0)
        s.figurese.tight_layout()
        s.figurese.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas2.draw()
    return


def figure_handler_globalfit(s, xdata, ydata, n, redline=8, x2data=None,
                             y2data=None, fit1=None, fit2=None):
    if n == 3:
        # PELDOR time trace
        s.ax3.clear()
        s.ax3 = s.figuren.add_subplot(111)
        s.ax3.set_autoscaley_on(False)
        s.ax3.axis('auto')
        s.ax3.set_xlabel('$time\, \mathrm{/ \,ns}$', size=fonts)
        s.ax3.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
        s.ax3.set_ylim([min(ydata)-0.02*abs(min(ydata)), max(ydata) +
                        0.02*abs(max(ydata))+0.5*max(ydata)])
        s.ax3.set_xlim([min(xdata), max(xdata)])
        s.ax3.set_title('PELDOR time trace', size=fonts)
        for tick in s.ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax3.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-1)
        s.figuren.tight_layout()
        s.ax3.plot(xdata, ydata)
        s.ax3.plot(xdata, fit1, 'r', linewidth=1.5)
        s.ax3.plot(x2data, y2data+0.5*max(ydata), 'b')
        s.ax3.plot(x2data, fit2+0.5*max(ydata), 'r', linewidth=1.5)
        s.figuren.tight_layout()
        s.figuren.subplots_adjust(left=0.14, bottom=0.18, right=0.97, top=0.92)
        s.canvas3.draw()
    if n == 1:
        # Distance distribution
        if s.normalize_to_maximum:
            ydata = ydata/max(ydata)
        else:
            ydata = ydata/sum(ydata)
        s.ax1.clear()
        s.ax1 = s.figuresw.add_subplot(111)
        s.ax1.set_autoscaley_on(False)
        s.ax1.axis('on')
        s.ax1.set_xlabel('$r \, \mathrm{/ \, nm}$', size=fonts)
        s.ax1.set_ylabel('$P(r)$', size=fonts)
        s.ax1.set_ylim([0, max(ydata)+max(ydata)/15])
        s.ax1.set_xlim([min(xdata), max(xdata)])
        s.ax1.set_title('Distance distribution', size=fonts)
        s.ax1.axvline(redline, color='r', linestyle='--')
        for tick in s.ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax1.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax1.plot(xdata, ydata)
        s.figuresw.tight_layout()
        s.figuresw.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas1.draw()
    if n == 2:
        # FT
        s.ax2.clear()
        s.ax2 = s.figurese.add_subplot(111)
        s.ax2.set_autoscaley_on(False)
        s.ax2.axis('auto')
        s.ax2.set_xlabel('$\omega\, \mathrm{/ \, MHz}$', size=fonts)
        s.ax2.set_ylabel('$Int$', size=fonts)
        s.ax2.set_ylim([min(ydata[0:100]), max(ydata) +
                        0.02*abs(max(ydata))+0.4])
        s.ax2.set_xlim([-10, 10])
        s.ax2.set_title('Fourier transform', size=fonts)
        for tick in s.ax2.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax2.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax2.plot(xdata, ydata)
        s.ax2.plot(xdata, y2data+0.4, 'b', linewidth=1.0)
        s.ax2.plot(xdata, fit1, 'r', linewidth=1.0)
        s.ax2.plot(xdata, fit2+0.4, 'r', linewidth=1.0)
        s.figurese.tight_layout()
        s.figurese.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas2.draw()
    return


def figure_handler_reg(s, xdata, ydata, n, redline=8, fit=None,
                       globalana=False, xdata2=None, ydata2=None, fit2=None):
    if n == 3:
        # PELDOR time trace
        lw1 = 1.0
        col1 = 'b'
        s.ax3.clear()
        s.ax3 = s.figuren.add_subplot(111)
        s.ax3.set_autoscaley_on(False)
        s.ax3.axis('auto')
        s.ax3.set_xlabel('$time\,  \mathrm{/ \,  ns}$', size=fonts)
        s.ax3.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
        if abs(max(ydata))+abs(min(ydata)) > 0.01:
            s.ax3.set_ylim([min(ydata)-0.02*abs(min(ydata)), max(ydata) +
                            0.02*abs(max(ydata))])
        else:
            s.ax3.set_ylim([min(ydata)-1.0*abs(min(ydata)), max(ydata) +
                            1.0*abs(max(ydata))])
        if globalana:
            if max(xdata) > max(xdata2):
                s.ax3.set_ylim([min(ydata)-0.02*abs(min(ydata)), max(ydata) +
                                0.6*abs(max(ydata))])
                s.ax3.set_xlim([0, max(xdata)])
            else:
                s.ax3.set_ylim([min(ydata2)-0.02*abs(min(ydata2)), max(ydata) +
                                0.6*abs(max(ydata2))])
                s.ax3.set_xlim([0, max(xdata2)])
        else:
            s.ax3.set_xlim([min(xdata), max(xdata)])
        s.ax3.set_title('PELDOR time trace', size=fonts)
        for tick in s.ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax3.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-1)
        s.figuren.tight_layout()
        s.ax3.plot(xdata, ydata, color=col1, linewidth=lw1)
        s.ax3.plot(xdata, fit, 'r', linewidth=1.5)
        if globalana:
            s.ax3.plot(xdata2, ydata2+0.5*abs(max(ydata2)), color=col1,
                       linewidth=lw1)
            s.ax3.plot(xdata2, fit2+0.5*abs(max(ydata2)), 'r', linewidth=1.5)
        s.figuren.tight_layout()
        s.figuren.subplots_adjust(left=0.14, bottom=0.18, right=0.97, top=0.92)
        s.canvas3.draw()
    if n == 1:
        # Distance distribution
        if s.normalize_to_maximum:
            ydata = ydata/max(ydata)
        else:
            ydata = ydata/sum(ydata)
        s.ax1.clear()
        s.ax1 = s.figuresw.add_subplot(111)
        s.ax1.set_autoscaley_on(False)
        s.ax1.axis('on')
        s.ax1.set_xlabel('$r \, \mathrm{/ \, nm}$', size=fonts)
        s.ax1.set_ylabel('$P(r)$', size=fonts)
        s.ax1.set_ylim([0, max(ydata)+max(ydata)/15])
        s.ax1.set_xlim([min(xdata), max(xdata)])
        s.ax1.set_title('Distance distribution', size=fonts)
        s.ax1.axvline(redline, color='r', linestyle='--')
        for tick in s.ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax1.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.ax1.plot(xdata, ydata)
        s.figuresw.tight_layout()
        s.figuresw.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas1.draw()
    if n == 2:
        if s.L_autocorr:
            title = 'Autocorr. Plot'
            xlabel = "$N$"
            ylabel = "$RMS(||\Delta \, \overline{A_N}||)$"
        else:
            title = 'L-Curve'
            xlabel = "$\mathrm{log}(||Kx-y||_2^2)$"
            ylabel = "$\mathrm{log}(||Dx||_2^2)$"
        s.ax2.clear()
        s.ax2 = s.figurese.add_subplot(111)
        s.ax2.set_autoscaley_on(False)
        s.ax2.axis('on')
        s.ax2.set_yticklabels([])
        s.ax2.set_xticklabels([])
        s.ax2.set_xlabel(xlabel, size=fonts)
        s.ax2.set_ylabel(ylabel, size=fonts)
        ymargin = (max(ydata)-min(ydata))/20
        xmargin = (max(xdata)-min(xdata))/20
        s.ax2.set_ylim([min(ydata)-ymargin, max(ydata) +
                        ymargin])
        s.ax2.set_xlim([min(xdata)-xmargin, max(xdata)+xmargin])
        s.ax2.set_title(title, size=fonts)
        s.figurese.tight_layout()
        s.ax2.plot(xdata, ydata, 'o')
        s.ax2.plot(xdata[fit-1], ydata[fit-1], 'o', color='r', linewidth=1.0)
        s.figurese.tight_layout()
        s.figurese.subplots_adjust(left=0.15, bottom=0.18, right=0.98,
                                   top=0.92)
        s.canvas2.draw()
    return


def figure_handler_dual_disp(s, xdata, ydata, x2data, y2data, n, cut1=100000,
                             cut2=10000, bg_time=None, bg=None, bg_time2=None,
                             bg2=None, zerotime=0):
    if n == 3:
        lw1 = 1.0
        col1 = 'b'
        lw2 = 1.0
        col2 = 'b'
        s.ax3.clear()
        s.ax3 = s.figuren.add_subplot(111)
        s.ax3.set_autoscaley_on(False)
        s.ax3.axis('auto')
        s.ax3.set_xlabel('$time \mathrm{/ ns}$', size=fonts)
        s.ax3.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
        zooming = 6/(s.ZoomFTScrollBar_2.value()+1)
        if (max(ydata))-abs(min(ydata)) > (max(y2data))-abs(min(y2data)):
            s.ax3.set_ylim([min(ydata)-0.02*abs(min(ydata)), max(ydata) +
                            0.02*abs(max(ydata))])
            lw2 = 1.5
            col2 = 'r'
        else:
            s.ax3.set_ylim([min(y2data)-0.02*abs(min(y2data)), max(y2data) +
                            0.02*abs(max(y2data))])
            lw1 = 1.5
            col1 = 'r'
        if max(xdata) > max(x2data):
            s.ax3.set_xlim([min(xdata), max(xdata)/zooming])
        else:
            s.ax3.set_xlim([min(x2data), max(x2data)/zooming])
        s.ax3.set_title('PELDOR time trace', size=fonts)
        for tick in s.ax3.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax3.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-1)
        s.figuren.tight_layout()
        s.ax3.plot(xdata, ydata, color=col1, linewidth=lw1)
        s.ax3.plot(x2data, y2data, color=col2, linewidth=lw2)
        s.ax3.plot(bg_time, bg, color='g', linewidth=1.5)
        s.ax3.plot(bg_time2, bg2, color='g', linewidth=1.5)
        s.ax3.plot(xdata, np.ones(len(xdata)), color='k')
        s.ax3.plot(xdata, np.zeros(len(xdata)))
        s.ax3.axvline(zerotime, color='k', linestyle='--')
        if cut1 < 100000:
            s.ax3.axvline(cut1, color='r')
        if cut2 < 100000:
            s.ax3.axvline(cut2, color='r')
        s.figuren.tight_layout()
        s.figuren.subplots_adjust(left=0.14, bottom=0.18, right=0.97, top=0.92)
        s.canvas3.draw()
    if n == 1:
        # PELDOR time trace
        lw1 = 1.0
        col1 = 'b'
        lw2 = 1.0
        col2 = 'b'
        s.ax1.clear()
        s.ax1 = s.figuresw.add_subplot(111)
        s.ax1.set_autoscaley_on(False)
        s.ax1.axis('auto')
        s.ax1.set_xlabel('$time \, \mathrm{/ \, ns}$', size=fonts)
        s.ax1.set_ylabel('$Int$', size=fonts)
        zooming = 6/(s.ZoomFTScrollBar_3.value()+1)
        if max(xdata) > max(x2data):
            s.ax1.set_ylim([min(ydata)-0.05*abs(min(ydata)), max(ydata) +
                            0.05*abs(max(ydata))])
            lw2 = 1.5
            col2 = 'r'
            #if max(xdata)/zooming > 2000:
            #    s.ax1.xaxis.set_ticks(np.arange(0, max(xdata)/zooming, 1000))
        else:
            s.ax1.set_ylim([min(y2data)-0.05*abs(min(y2data)), max(y2data) +
                            0.05*abs(max(y2data))])
            lw1 = 1.5
            col1 = 'r'
            #if max(x2data)/zooming > 2000:
            #    s.ax1.xaxis.set_ticks(np.arange(0, max(x2data)/zooming, 1000))
        if max(xdata) > max(x2data):
            xmax = max(xdata)
            if cut1 < xmax:
                xmax = cut1
            s.ax1.set_xlim([min(xdata), xmax/zooming])
        else:
            xmax = max(x2data)
            if cut2 < xmax:
                xmax = cut2
            s.ax1.set_xlim([min(x2data), xmax/zooming])
        s.ax1.set_title('Bg. corrected', size=fonts)
        for tick in s.ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax1.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.figuresw.tight_layout()
        s.ax1.plot(xdata, ydata, color=col1, linewidth=lw1)
        s.ax1.plot(x2data, y2data, color=col2, linewidth=lw2)
        s.figuresw.tight_layout()
        s.figuresw.subplots_adjust(left=0.20, bottom=0.18, right=0.97,
                                   top=0.92)
        s.canvas1.draw()
    if n == 2:
        # Fourier transform
        lw1 = 1.0
        col1 = 'b'
        lw2 = 1.0
        col2 = 'b'
        s.ax2.clear()
        s.ax2 = s.figurese.add_subplot(111)
        s.ax2.set_autoscaley_on(False)
        s.ax2.axis('auto')
        s.ax2.set_xlabel('$\omega\, \mathrm{/ \, MHz}$', size=fonts)
        s.ax2.set_ylabel('$Int$', size=fonts)
        if max(xdata) > max(x2data):
            s.ax2.set_ylim([min(ydata)-0.05*abs(min(ydata)), max(ydata) +
                            0.05*abs(max(ydata))])
            lw2 = 1.5
            col2 = 'r'
        else:
            s.ax2.set_ylim([min(y2data)-0.05*abs(min(y2data)), max(y2data) +
                            0.05*abs(max(y2data))])
            lw1 = 1.5
            col1 = 'r'
        zooming = pow(1.4, 3-s.ZoomFTScrollBar.value())
        s.ax2.set_xlim([-10*zooming, 10*zooming])
        s.ax2.set_title('Fourier transform', size=fonts)
        for tick in s.ax2.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts)
        for tick in s.ax2.yaxis.get_major_ticks():
            tick.label.set_fontsize(fonts-2)
        s.figurese.tight_layout()
        s.ax2.plot(xdata, ydata, color=col1, linewidth=lw1)
        s.ax2.plot(x2data, y2data, color=col2, linewidth=lw2)
        s.figurese.tight_layout()
        s.figurese.subplots_adjust(left=0.15, bottom=0.18, right=0.98,
                                   top=0.92)
        s.canvas2.draw()
    return
