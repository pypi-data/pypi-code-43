# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 08:55:06 2018

@author: Stephan Rein

SubGUI for residual inspection

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein
"""


from PyQt5.QtWidgets import QVBoxLayout, QDialog
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanv
from matplotlib.figure import Figure
from scipy.ndimage import gaussian_filter
import numpy as np
import time as times
try:
    from GloPel.Dialog_Residue import Ui_Dialog as Child
except ImportError:
    from Dialog_Residue import Ui_Dialog as Child
matplotlib.use("Qt5Agg")


try:
    mat_version = repr(matplotlib.__version__)
    mat_version_str = (eval(mat_version))
    num_ver = (mat_version_str).split('.')
    if int(num_ver[0]) == 2:
        fonts = 7
    else:
        fonts = 9
except:
    fonts = 8


def make_autokorrelation(s, filtering=False):
    if not filtering:
        s.show_autocorr = True
        s.show_autocorr_av = False
    else:
        s.show_autocorr_av = True
        s.show_autocorr = False
    line = True
    rms = False
    if s.save_glob_fit:
        residual1 = np.correlate(s.residual_global1, s.residual_global1,
                                 mode='same')
        residual2 = np.correlate(s.residual_global2, s.residual_global2,
                                 mode='same')
        residual1 = residual1/max(residual1)
        ydatat = residual1
        rmax = np.argmax(residual1)
        residual1[rmax] = residual1[rmax+1]
        residual2 = residual2/max(residual2)
        rmax = np.argmax(residual2)
        residual2[rmax] = residual2[rmax+1]
        if filtering:
            residual1 = gaussian_filter(residual1, sigma=2)
            residual2 = gaussian_filter(residual2, sigma=2)
        ydatat = residual1
        ysignificant_tmp = 0
        for k in range(1, 3):
            ysignificant_tmp += (ydatat+np.roll(ydatat, k))
        ysignificant_tmp = ysignificant_tmp-np.mean(ysignificant_tmp)
        ysignificant_tmp = np.sqrt(ysignificant_tmp**4)
        ysignificant = 0.25*100*np.std(ysignificant_tmp)
        # Second data set
        ydatat = residual2
        ysignificant_tmp = 0
        for k in range(1, 3):
            ysignificant_tmp += (ydatat+np.roll(ydatat, k))
        ysignificant_tmp = ysignificant_tmp-np.mean(ysignificant_tmp)
        ysignificant_tmp = np.sqrt(ysignificant_tmp**4)
        ysignificant2 = 0.25*100*np.std(ysignificant_tmp)
        xvalues1 = np.linspace(-len(residual1), len(residual1), len(residual1))
        xvalues2 = np.linspace(-len(residual2), len(residual2), len(residual2))
        detach_plot_residuals(s.dialog3.ui, xvalues1, residual1, line, rms,
                              ysignificant, True, xvalues2, residual2,
                              ysignificant2)
    else:
        if s.activeset == 1:
            residual = np.correlate(s.residual1, s.residual1, mode='same')
            residual = residual/max(residual)
        else:
            residual = np.correlate(s.residual2, s.residual2, mode='same')
            residual = residual/max(residual)
        xvalues = np.linspace(-len(residual), len(residual), len(residual))
        ydatat = residual
        rmax = np.argmax(residual)
        residual[rmax] = residual[rmax+1]
        if filtering:
            residual = gaussian_filter(residual, sigma=2)
        ydatat = residual
        ysignificant_tmp = 0
        for k in range(1, 4):
            ysignificant_tmp += (ydatat+np.roll(ydatat, k))
        ysignificant_tmp = ysignificant_tmp-np.mean(ysignificant_tmp)
        ysignificant_tmp = np.sqrt(ysignificant_tmp**4)
        ysignificant = 0.25*100*np.std(ysignificant_tmp)
        xvalues1 = np.linspace(-len(residual), len(residual), len(residual))
        detach_plot_residuals(s.dialog3.ui, xvalues, residual, line, rms,
                              ysignificant)
    return


def make_residues(s):
    s.show_autocorr = False
    s.show_autocorr_av = False
    line = False
    rms = True
    if s.save_glob_fit:
        ysignificant = 0
        detach_plot_residuals(s.dialog3.ui, s.bg_time1_cut,
                              s.residual_global1, line, rms, ysignificant,
                              True, s.bg_time2_cut, s.residual_global2)
    else:
        if s.activeset == 1:
            residual = s.residual1
            bg_time = s.bg_time1_cut
        else:
            residual = s.residual2
            bg_time = s.bg_time2_cut
        detach_plot_residuals(s.dialog3.ui, bg_time, residual, line, rms)
    return


def ResidueSubGUIhandling(s, boolean=False):
    if boolean and not s.Subguiinit:
        s.dialog3 = QDialog()
        s.dialog3.ui = Child()
        s.dialog3.ui.setupUi(s.dialog3)
        s.dialog3.ui.OK_Dialog_Button.clicked.connect(s.dialog3.accept)
        s.dialog3.ui.Autokorrelation.clicked.connect(lambda:
                                                     make_autokorrelation(s, False))
        s.dialog3.ui.Residues_Button.clicked.connect(lambda: make_residues(s))
        s.dialog3.ui.Av_Autokorrelation.clicked.connect(lambda:
                                                        make_autokorrelation(s,True))
        init_detach_plot_residuals(s.dialog3.ui)
        s.dialog3.show()
        s.Subguiinit = True
    elif boolean and s.Subguiinit:
        s.dialog3.setVisible(True)
    else:
        pass
    if s.show_autocorr:
        make_autokorrelation(s, False)
    elif s.show_autocorr_av:
        make_autokorrelation(s, True)
    else:
        make_residues(s)
    return


def init_detach_plot_residuals(s):
    s.figure4 = Figure()
    s.figure4.set_facecolor('white')
    s.canvas4 = FigCanv(s.figure4)
    s.layout4 = QVBoxLayout(s.Matplotlib_container_Dialog)
    s.layout4.addWidget(s.canvas4)
    return


def detach_plot_residuals(s, xdata, ydata, line=True, rms=False,
                          ysignificant=0, boolean=False, xdata2=None,
                          ydata2=None, ysignificant2=0):
    try:
        s.ax4.clear()
        s.ax4.set_visible(False)
    except:
        pass
    try:
        s.ax5.clear()
        s.ax6.clear()
        s.ax5.set_visible(False)
        s.ax6.set_visible(False)
    except:
        pass
    if line:
        li = '-'
        string = '$Autocorrelation$'
        axlabel = "$Lag \, \, time$"
        colors = 'blue'
        if ysignificant > 2:
            colors = 'y'
        if ysignificant > 4:
            colors = 'orange'
        if ysignificant > 8:
            colors = 'orangered'
        if ysignificant > 15:
            colors = 'r'
    else:
        li = '.'
        string = '$Residues$'
        axlabel = "$time\ \mathrm{/ \ ns}$"
        mean_value = np.mean(ydata)
        rms_value = np.std(ydata)
        colors = 'blue'
    if not boolean:
        s.ax4 = s.figure4.add_subplot(1, 1, 1)
        s.ax4.set_visible(True)
        s.ax4.set_autoscaley_on(False)
        s.ax4.axis('on')
        s.ax4.set_xlabel(axlabel, size=fonts+1)
        s.ax4.set_ylabel(string, size=fonts+1)
        ymargin = (max(ydata)-min(ydata))/3
        xmargin = (max(xdata)-min(xdata))/200
        if not line:
            s.ax4.set_ylim([min(ydata)-ymargin, max(ydata) +
                            1.5*ymargin])
        else:
            s.ax4.set_ylim([min(ydata)-0.2*ymargin, max(ydata) +
                            0.4*ymargin])
        s.ax4.set_xlim([min(xdata)-xmargin, max(xdata)+xmargin])
        for tick in s.ax4.xaxis.get_major_ticks():
                tick.label.set_fontsize(fonts+1)
        for tick in s.ax4.yaxis.get_major_ticks():
                tick.label.set_fontsize(fonts+1)
        s.ax4.plot(xdata, ydata, li, color=colors)
        s.ax4.plot(xdata, np.zeros(len(xdata)), 'r', linewidth=1.5)
        if not line:
            string_tmp = "RMS: "+str(round(rms_value, 6))
            s.ax4.text(max(xdata)-50*xmargin, max(ydata)+1.0*ymargin,
                       string_tmp, fontsize=fonts)
            string_tmp = "Mean: "+str(round(mean_value, 6))
            s.ax4.text(max(xdata)-50*xmargin, max(ydata)+0.5*ymargin,
                       string_tmp, fontsize=fonts)
        else:
            string_tmp = "Significances: "+str(round(ysignificant, 1))
            s.ax4.text(max(xdata)-50*xmargin, max(ydata), string_tmp,
                       fontsize=fonts)
        s.figure4.subplots_adjust(left=0.14, bottom=0.22, right=0.98, top=0.98)
    else:
        s.ax6 = s.figure4.add_subplot(2, 1, 1)
        s.ax6.set_autoscaley_on(False)
        ymargin = (max(ydata)-min(ydata))/3
        xmargin = (max(xdata)-min(xdata))/200
        if not line:
            s.ax6.set_ylim([min(ydata)-ymargin, max(ydata) +
                            1.5*ymargin])
        else:
            s.ax6.set_ylim([min(ydata)-0.2*ymargin, max(ydata) +
                            0.4*ymargin])
        s.ax6.set_xlim([min(xdata)-xmargin, max(xdata)+xmargin])
        for tick in s.ax6.xaxis.get_major_ticks():
            tick.label.set_fontsize(fonts+1)
        for tick in s.ax6.yaxis.get_major_ticks(fonts+1):
            tick.label.set_fontsize(fonts+1)
        s.ax6.xaxis.tick_top()
        s.ax6.xaxis.set_tick_params(labelsize=fonts+1)
        s.ax6.plot(xdata, ydata, li, color=colors)
        s.ax6.plot(xdata, np.zeros(len(xdata)), 'r', linewidth=1.5)
        if not line:
            string_tmp = "RMS: "+str(round(rms_value, 6))
            s.ax6.text(max(xdata)-150*xmargin, max(ydata)+0.4*ymargin,
                       string_tmp, fontsize=fonts)
            string_tmp = "Mean: "+str(round(mean_value, 6))
            s.ax6.text(max(xdata)-80*xmargin, max(ydata)+0.4*ymargin,
                       string_tmp, fontsize=fonts)
        else:
            string_tmp = "Significances: "+str(round(ysignificant, 1))
            s.ax6.text(max(xdata)-50*xmargin, max(ydata)-0.2*ymargin,
                       string_tmp, fontsize=fonts)
        # Plot number 2
        s.ax5 = s.figure4.add_subplot(2, 1, 2)
        s.ax5.set_autoscaley_on(False)
        s.ax5.set_xlabel(axlabel, size=fonts+1)
        ymargin2 = (max(ydata2)-min(ydata2))/3
        xmargin2 = (max(xdata2)-min(xdata2))/200
        if not line:
            colors = 'blue'
            mean_value = np.mean(ydata2)
            rms_value = np.std(ydata2)
            s.ax5.set_ylim([min(ydata2)-ymargin2, max(ydata2) +
                            1.5*ymargin2])
        else:
            colors = 'blue'
            if ysignificant2 > 1:
                colors = 'y'
            if ysignificant2 > 3:
                colors = 'orange'
            if ysignificant2 > 5:
                colors = 'orangered'
            if ysignificant2 > 15:
                colors = 'r'
            s.ax5.set_ylim([min(ydata2)-0.2*ymargin2, max(ydata2) +
                            0.4*ymargin2])
        s.ax5.set_xlim([min(xdata2)-xmargin2, max(xdata2)+xmargin2])
        for tick in s.ax5.xaxis.get_major_ticks():
                tick.label.set_fontsize(fonts+1)
        for tick in s.ax5.yaxis.get_major_ticks():
                tick.label.set_fontsize(fonts+1)
        s.ax5.plot(xdata2, ydata2, li, color=colors)
        s.ax5.plot(xdata2, np.zeros(len(xdata2)), 'r', linewidth=1.5)
        if not line:
            string_tmp = "RMS: "+str(round(rms_value, 6))
            s.ax5.text(max(xdata2)-150*xmargin2, max(ydata2)+0.4*ymargin2,
                       string_tmp, fontsize=fonts)
            string_tmp = "Mean: "+str(round(mean_value, 6))
            s.ax5.text(max(xdata2)-80*xmargin2, max(ydata2)+0.4*ymargin2,
                       string_tmp, fontsize=fonts)
        else:
            string_tmp = "Significances: "+str(round(ysignificant2, 1))
            s.ax5.text(max(xdata)-50*xmargin, max(ydata2)-0.2*ymargin2,
                       string_tmp, fontsize=fonts)
        s.ax5.set_visible(True)
        s.ax6.set_visible(True)
        s.figure4.subplots_adjust(left=0.1, bottom=0.22, right=0.96, top=0.88)
    # Draw the current figure
    s.canvas4.draw()
    times.sleep(0.1)
    s.canvas4.show()
    return
