# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 16:58:17 2018

@author: Stephan Rein

SubGUI for validation of the Tikhonov solution.

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein
"""


import datetime
from PyQt5.QtWidgets import (QVBoxLayout, QDialog, QApplication,
                             QMessageBox, QFileDialog)
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigCanv
from matplotlib.figure import Figure
import numpy as np
import time as times
try:
    from GloPel.Dialog_Validation import Ui_Dialog as Child2
    from GloPel.Calculations import bg_correction, bg_subtraction
    from GloPel.Regularization import regularization
    from GloPel.Warning_Validation import Ui_Warning_validation_Number as ChildValWarn
    from GloPel.Validation_Progress_Bar import Ui_Validation_Progress_Dialog as ChildProg
except ImportError:
    from Dialog_Validation import Ui_Dialog as Child2
    from Calculations import bg_correction, bg_subtraction
    from Regularization import regularization
    from Warning_Validation import Ui_Warning_validation_Number as ChildValWarn
    from Validation_Progress_Bar import Ui_Validation_Progress_Dialog as ChildProg
from reportlab.pdfgen import canvas
matplotlib.use("Qt5Agg", force=True)


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


def init_validation(s):
    s.figure7 = Figure()
    s.figure7.set_facecolor('white')
    s.canvas7 = FigCanv(s.figure7)
    s.layout7 = QVBoxLayout(s.Validation_container)
    s.layout7.addWidget(s.canvas7)
    s.figure8 = Figure()
    s.figure8.set_facecolor('white')
    s.canvas8 = FigCanv(s.figure8)
    s.layout8 = QVBoxLayout(s.Validation_time_trace)
    s.layout8.addWidget(s.canvas8)
    return


def ValidationSubGUIhandling(s, boolean=False):
    if boolean and not s.Subguiinit_Valid:
        s.dialog4 = QDialog()
        s.dialog4.ui = Child2()
        s.dialog4.ui.setupUi(s.dialog4)
        s.dialog4.ui.Exitbutton_Validation_GUI.clicked.connect(s.dialog4.accept)
        # Initializing temporary member variables of the SubGUI class
        s.bg_range = None
        s.max_kdist = None
        s.min_kdist = None
        s.noiselevel = None
        s.number_noise = None
        s.bg_dim_range = None
        s.total_trials = None
        s.validation_carried_out = False
        s.validation_global = False
        s.prune = False
        s.pruneval = None
        s.weighting = None
        s.calctime = None
        if not s.GlobalAnalysis.isChecked():
            s.dialog4.ui.Validate_Button.clicked.connect(lambda:
                make_validation(s.dialog4.ui, s, time_org, TT_org, Fit_org))
        else:
            s.dialog4.ui.Validate_Button.clicked.connect(lambda:
                make_global_validation(s.dialog4.ui, s))
        init_validation(s.dialog4.ui)
        if s.activeset == 1:
            r_org = s.r1_reg
            Pr_org = s.Pr1_reg[:, s.L_curve_number1-1]
            Pr_org = Pr_org/sum(Pr_org)
            time_org = s.bg_time1_cut
            TT_org = s.bg_corrected1_cut
            Fit_org = s.reg1[:, s.L_curve_number1-1]
        else:
            r_org = s.r2_reg
            Pr_org = s.Pr2_reg[:, s.L_curve_number2-1]
            Pr_org = Pr_org/sum(Pr_org)
            time_org = s.bg_time2_cut
            TT_org = s.bg_corrected2_cut
            Fit_org = s.reg2[:, s.L_curve_number2-1]
        if not s.GlobalAnalysis.isChecked():
            s.dialog4.ui.Weighting_factor_trials.setReadOnly(True)
            str_tmp = ("background-color: rgb(160, 160, 160);" +
                       "color: rgb(160, 160, 160);")
            s.dialog4.ui.Weighting_factor_trials.setStyleSheet(str_tmp)
            s.dialog4.ui.Weighting_factor_validation.setReadOnly(True)
            s.dialog4.ui.Weighting_factor_validation.setStyleSheet(str_tmp)
            s.dialog4.ui.Enable_weighting_factor_validation.setStyleSheet(str_tmp)
            s.dialog4.ui.Enable_weighting_factor_validation.setCheckable(False)
            s.dialog4.ui.Weighting_factor_validation.setEnabled(False)
            s.dialog4.ui.Weighting_factor_trials.setEnabled(False)
            detach_plot_validation(s.dialog4.ui, s, r_org, Pr_org, time_org,
                                   TT_org, Fit_org)
        else:
            Pr_org = s.Pr_reg_global[:, s.global_L_curve_num-1]
            Pr_org = Pr_org/sum(Pr_org)
            r_org = s.r_reg_global
            s.dialog4.ui.Enable_prune.setCheckable(False)
            s.dialog4.ui.Prune_value.setReadOnly(True)
            str_tmp = ("background-color: rgb(160, 160, 160);" +
                       "color: rgb(160, 160, 160);")
            s.dialog4.ui.Prune_value.setStyleSheet(str_tmp)
            s.dialog4.ui.Enable_prune.setStyleSheet(str_tmp)
            detach_plot_validation(s.dialog4.ui, s, r_org, Pr_org, time_org,
                                   TT_org, Fit_org)
            ln = s.global_L_curve_num-1
            detach_plot_global_validation(s.dialog4.ui, s, s.r_reg_global,
                                          s.Pr_reg_global[:, ln],
                                          s.bg_time1_cut, s.bg_corrected1_cut,
                                          s.reg1_global[:, ln], s.bg_time2_cut,
                                          s.bg_corrected2_cut,
                                          s.reg2_global[:, ln])
        s.dialog4.show()
        s.dialog4.ui.Validate_Save_Button.clicked.connect(lambda:
            save_results_validation(s.dialog4.ui, s, r_org, Pr_org))
    return


def Warning_Val(s, num):
    s.dialog5 = QDialog()
    s.dialog5.ui = ChildValWarn()
    s.dialog5.ui.setupUi(s.dialog5)
    s.dialog5.ui.Lable_with_Number_of_eval.setText(str(num))
    s.dialog5.ui.Continue_Evaluation_Button.clicked.connect(s.dialog5.accept)
    s.dialog5.ui.Cancel_Evaluation_Button_reject.clicked.connect(s.dialog5.reject)
    s.dialog5.show()
    if s.dialog5.exec_():
        boolean = True
        return boolean
    if s.dialog5.accept:
        boolean = False
        return boolean
    if s.dialog5.reject:
        boolean = True
        return boolean


def make_validation(s1, s, time_org, TT_org, Fit_org):
    try:
        if (s.Checkbox_GlobalBg.isChecked() and s.setexists[0] and
           s.setexists[1]):
            if max(s.time1) > max(s.time2):
                start_tmp = s.bg_start1
            else:
                start_tmp = s.bg_start2
        else:
            if s.activeset == 1:
                start_tmp = s.bg_start1
            else:
                start_tmp = s.bg_start2

        if s.dialog4.ui.Enable_Bg_range_valid.isChecked():
            number_bg_diff = s.dialog4.ui.BG_validation_trials.value()
            range_tmp = s.dialog4.ui.Bg_valiation_range.value()
            bg_range = np.linspace(start_tmp-range_tmp, start_tmp+range_tmp,
                                   number_bg_diff)
        else:
            number_bg_diff = 1
            bg_range = np.ones(1)*start_tmp
        # Decide which dataset
        if s.activeset == 1:
            bg_dim_start = s.bg_dim1
        else:
            bg_dim_start = s.bg_dim2
        if s.dialog4.ui.Enable_Bg_dim_valid.isChecked():
            number_bg_dim = s.dialog4.ui.Bg_dim_validation_points.value()
            range_tmp = s.dialog4.ui.Bg_dimension_range.value()
            bg_dim_range = np.linspace(bg_dim_start-range_tmp,
                                       bg_dim_start+range_tmp, number_bg_dim)
        else:
            number_bg_dim = 1
            start_tmp = s.Bg_Start.value()
            bg_dim_range = np.ones(1)*bg_dim_start
        # White noise varariation
        if s.dialog4.ui.Enable_noise_validation.isChecked():
            number_noise = s.dialog4.ui.Nois_validation_Points.value()
            value = s.dialog4.ui.Noise_level_validation.value()
            rms = np.std(TT_org-Fit_org)
            noisef = np.linspace(0, 1, number_noise)
            add_noise = np.zeros((number_noise, len(Fit_org)))
            for i in range(0, number_noise):
                add_noise[i, :] = (noisef[i]*value *
                                   np.random.normal(size=len(Fit_org),
                                                    scale=rms))
        else:
            number_noise = 1
            value = 1
            add_noise = np.zeros((1, len(Fit_org)))
        fulldim = int(number_noise*number_bg_dim*number_bg_diff)
        L_val = s.L_Curve_numberBox.value()-1
        method = s.reg_method
        # Ask if number of validation is not too large
        boolean = True
        if fulldim >= 500:
            boolean = Warning_Val(s, fulldim)
        if not boolean:
            return
        # Allocations for single dataset
        if s.activeset == 1:
            medKer = s.adaptive_kernel1
            lKer = s.large_kernel1
            issup = s.supressing1
            supstart = s.supressingstart1,
            suppend = s.supressingend1
            r_org = s.r1_reg
            Pr_org = s.Pr1_reg[:, s.L_curve_number1-1]
            Pr_org = Pr_org/sum(Pr_org)
            kdist = np.zeros((fulldim, len(s.Pr1_reg[:, 0])))
            r = np.ones((fulldim, len(s.Pr1_reg[:, 0])))
            r = r*s.r1_reg
            normalizedpc_sp = s.normalizedpc_spetrum1
            normalizedpc_spf = s.normalizedpc_spetrum1
            timef = s.time1
            time = s.time1
            excludvol = s.exclude_vol1
            zerot = s.zerotime1
            cutoff = s.cutoff1
        elif s.activeset == 2:
            medKer = s.adaptive_kernel2
            lKer = s.large_kernel2
            issup = s.supressing2
            supstart = s.supressingstart2,
            suppend = s.supressingend2
            r_org = s.r2_reg
            Pr_org = s.Pr2_reg[:, s.L_curve_number2-1]
            Pr_org = Pr_org/sum(Pr_org)
            kdist = np.zeros((fulldim, len(s.Pr2_reg[:, 0])))
            r = np.ones((fulldim, len(s.Pr2_reg[:, 0])))
            r = r*s.r2_reg
            normalizedpc_sp = s.normalizedpc_spetrum2
            normalizedpc_spf = s.normalizedpc_spetrum2
            timef = s.time2
            time = s.time2
            excludvol = s.exclude_vol2
            zerot = s.zerotime2
            cutoff = s.cutoff2
        # Vary global background function in validation
        if (s.Checkbox_GlobalBg.isChecked() and s.setexists[0] and
           s.setexists[1]):
            if max(s.time1) > max(s.time2):
                normalizedpc_sp = s.normalizedpc_spetrum1
                time = s.time1
            else:
                normalizedpc_sp = s.normalizedpc_spetrum12
                time = s.time2
        s.dialog6 = QDialog()
        s.dialog6.ui = ChildProg()
        s.dialog6.ui.setupUi(s.dialog6)
        s.dialog6.ui.Validation_Progress_OK.clicked.connect(s.dialog6.accept)
        s.dialog6.ui.Validation_Progress_Exit.clicked.connect(s.dialog6.reject)
        s.dialog6.ui.progressBar_Validation.setValue(int(0))
        s.dialog6.show()
        start = times.time()
        while times.time() - start < 0.2:
            QApplication.processEvents()
        ps = int(0)
        do_prunning = False
        lsq = least_squares(TT_org, Fit_org)
        if s.dialog4.ui.Enable_prune.isChecked():
            prun_level = s.dialog4.ui.Prune_value.value()
            do_prunning = True
            s.prune = True
            s.pruneval = prun_level
        # Measure calculation time
        sttime = times.time()
        for i in range(0, len(bg_range)):
            for l in range(0, len(bg_dim_range)):
                bg_param_t = bg_correction(normalizedpc_sp, time, bg_range[i],
                                           bg_dim_range[l], excludvol)
                (bg_corrected_tmp, bg_time1_tmp,
                 bg_fun1_tmp) = bg_subtraction(normalizedpc_spf, timef,
                                               bg_param_t, zerot,
                                               bg_dim_range[l], None,
                                               excludvol)
                # Induce Cut if enabled
                if cutoff < max(bg_time1_tmp):
                    bg_time1_tmp = bg_time1_tmp[bg_time1_tmp <= cutoff]
                    bg_corrected_tmp = bg_corrected_tmp[0:len(bg_time1_tmp)]
                bg_corrected_tmp_st = bg_corrected_tmp
                for p in range(0, number_noise):
                    bg_corrected_tmp = bg_corrected_tmp_st+add_noise[p, :]
                    (k, kdist[ps, :],
                     TT2) = regularization(bg_time1_tmp, bg_corrected_tmp,
                                           method, False, L_val, False, None,
                                           None, None, issup, supstart,
                                           suppend, medKer, lKer)
                    if do_prunning:
                        val = ((prun_level) *
                               np.sqrt(lsq**2+np.std(add_noise[p, :])**2))
                        if val > least_squares(bg_corrected_tmp,
                                               TT2.transpose()):
                            kdist[ps, :] = kdist[ps, :]/sum(kdist[ps, :])
                        else:
                            kdist[ps, :] = Pr_org/sum(Pr_org)
                    else:
                        kdist[ps, :] = kdist[ps, :]/sum(kdist[ps, :])
                    percent = 100*(ps+1)/fulldim
                    if np.mod(percent, 10) == 0:
                        s.dialog6.ui.progressBar_Validation.setValue(int(percent))
                        start = times.time()
                        while times.time() - start < 0.1:
                            QApplication.processEvents()
                    ps += 1
        s.dialog6.accept()
        QApplication.processEvents()
        min_kdist, max_kdist = min_max_kdist(kdist)
        detach_plot_validation(s1, s, r_org, Pr_org, time_org, TT_org, Fit_org,
                               r, kdist, min_kdist, max_kdist)
        s.calctime = times.time()-sttime
        s.bg_range = bg_range
        s.max_kdist = max_kdist
        s.min_kdist = min_kdist
        s.noiselevel = value
        s.number_noise = number_noise
        s.bg_dim_range = bg_dim_range
        s.total_trials = fulldim
        s.validation_carried_out = True
        s.rms = lsq
        return
    except Exception as e:
        string_tmp = "Something went wrong!\n"+str(e)
        s.War4 = QMessageBox.warning(s, "Error",
                                     string_tmp, QMessageBox.Ok)
        return


def least_squares(data, fit):
    return np.sum(np.power(data-fit, 2))


def make_global_validation(s1, s):
    try:
        ln = s.global_L_curve_num-1
        if s.dialog4.ui.Enable_Bg_range_valid.isChecked():
            number_bg_diff = s.dialog4.ui.BG_validation_trials.value()
            range_tmp = s.dialog4.ui.Bg_valiation_range.value()
            # Vary global background function in validation
            if max(s.time1) > max(s.time2):
                start_tmp = s.bg_start1
            else:
                start_tmp = s.bg_start2
            bg_range = np.linspace(start_tmp-range_tmp, start_tmp+range_tmp,
                                   number_bg_diff)
        else:
            number_bg_diff = 1
            if max(s.time1) > max(s.time2):
                start_tmp = s.bg_start1
            else:
                start_tmp = s.bg_start2
            bg_range = np.ones(1)*start_tmp
        # Decide which dataset
        if s.activeset == 1:
            bg_dim_start = s.bg_dim1
        else:
            bg_dim_start = s.bg_dim2
        # Background dimension variation
        if s.dialog4.ui.Enable_Bg_dim_valid.isChecked():
            number_bg_dim = s.dialog4.ui.Bg_dim_validation_points.value()

            range_tmp = s.dialog4.ui.Bg_dimension_range.value()

            bg_dim_range = np.linspace(bg_dim_start-range_tmp,
                                       bg_dim_start+range_tmp, number_bg_dim)
        else:
            number_bg_dim = 1
            start_tmp = s.Bg_Start.value()
            bg_dim_range = np.ones(1)*bg_dim_start
        # White noise varariation
        if s.dialog4.ui.Enable_noise_validation.isChecked():
            number_noise = s.dialog4.ui.Nois_validation_Points.value()
            value = s.dialog4.ui.Noise_level_validation.value()
            rms1 = np.std(s.bg_corrected1_cut-s.reg1_global[:, ln])
            rms2 = np.std(s.bg_corrected2_cut-s.reg2_global[:, ln])
            noisef = np.linspace(0, 1, number_noise)
            add_noise1 = np.zeros((number_noise, len(s.reg1_global[:, ln])))
            for i in range(0, number_noise):
                add_noise1[i, :] = (noisef[i]*value*rms1 *
                 np.random.normal(size=len(s.reg1_global[:, ln])))
            add_noise2 = np.zeros((number_noise, len(s.reg2_global[:, ln])))
            for i in range(0, number_noise):
                add_noise2[i, :] = (noisef[i]*value*rms2 *
                 np.random.normal(size=len(s.reg2_global[:, ln])))
        else:
            number_noise = 1
            add_noise1 = np.zeros((1, len(s.reg1_global[:, ln])))
            add_noise2 = np.zeros((1, len(s.reg2_global[:, ln])))
        if s.dialog4.ui.Enable_weighting_factor_validation.isChecked():
            weighting_range = s.dialog4.ui.Weighting_factor_validation.value()
            number_weighting = s.dialog4.ui.Weighting_factor_trials.value()
            weighting = np.linspace(s.fitweight-weighting_range,
                                    s.fitweight+weighting_range,
                                    number_weighting)
        else:
            number_weighting = 1
            weighting = np.ones(1)*s.fitweight
        fulldim = int(number_noise*number_bg_dim*number_bg_diff *
                      number_weighting)
        kdist = np.zeros((fulldim, len(s.Pr_reg_global[:, 0])))
        r = np.ones((fulldim, len(s.Pr_reg_global[:, 0])))
        r = r*s.r_reg_global
        # Ask if number of validation is not too large
        boolean = True
        if fulldim >= 500:
            boolean = Warning_Val(s, fulldim)
        if not boolean:
            return
        # Vary global background function in validation
        if (s.Checkbox_GlobalBg.isChecked() and s.setexists[0] and
           s.setexists[1]):
            if max(s.time1) > max(s.time2):
                normalizedpc_sp = s.normalizedpc_spetrum1
                time = s.time1
            else:
                normalizedpc_sp = s.normalizedpc_spetrum12
                time = s.time2
        s.dialog6 = QDialog()
        s.dialog6.ui = ChildProg()
        s.dialog6.ui.setupUi(s.dialog6)
        s.dialog6.ui.Validation_Progress_OK.clicked.connect(s.dialog6.accept)
        s.dialog6.ui.Validation_Progress_Exit.clicked.connect(s.dialog6.reject)
        s.dialog6.ui.progressBar_Validation.setValue(int(0))
        s.dialog6.show()
        start = times.time()
        while times.time() - start < 0.2:
            QApplication.processEvents()
        ps = int(0)
        sttime = times.time()
        for i in range(0, len(bg_range)):
            for l in range(0, len(bg_dim_range)):
                bg_param_t = bg_correction(normalizedpc_sp, time, bg_range[i],
                                           bg_dim_range[l], s.exclude_vol1)
                (bg_corrected_tmp1, bg_time1_tmp,
                 bg_fun1_tmp) = bg_subtraction(s.normalizedpc_spetrum1,
                                               s.time1, bg_param_t,
                                               s.zerotime1,
                                               bg_dim_range[l],
                                               None, s.exclude_vol1)
                (bg_corrected_tmp2, bg_time2_tmp,
                 bg_fun1_tmp) = bg_subtraction(s.normalizedpc_spetrum2,
                                               s.time2, bg_param_t,
                                               s.zerotime2,
                                               bg_dim_range[l],
                                               None, s.exclude_vol2)
                # Induce Cut if enabled
                if s.cutoff1 < max(s.bg_time1):
                    bg_time1_tmp = bg_time1_tmp[bg_time1_tmp <= s.cutoff1]
                    bg_corrected_tmp1 = bg_corrected_tmp1[0:len(bg_time1_tmp)]
                # Induce Cut if enabled
                if s.cutoff2 < max(s.bg_time2):
                    bg_time2_tmp = bg_time2_tmp[bg_time2_tmp <= s.cutoff1]
                    bg_corrected_tmp2 =bg_corrected_tmp2[0:len(bg_time2_tmp)]
                bg_corrected_tmp1_st = bg_corrected_tmp1
                bg_corrected_tmp2_st = bg_corrected_tmp2
                for p in range(0, number_noise):
                    bg_corrected_tmp1 = bg_corrected_tmp1_st+add_noise1[p, :]
                    bg_corrected_tmp2 = bg_corrected_tmp2_st+add_noise2[p, :]
                    for m in range(0, number_weighting):
                        (k, kdist[ps, :],
                         TT2) = regularization(bg_time1_tmp, bg_corrected_tmp1,
                                               s.reg_method, False, ln, True,
                                               bg_time2_tmp, bg_corrected_tmp2,
                                               weighting[m], s.supressingglob,
                                               s.supressingstartglo,
                                               s.supressingendglo,
                                               s.global_adaptive,
                                               s.global_large_kernel1)
                        kdist[ps, :] = kdist[ps, :]/sum(kdist[ps, :])
                        percent = 100*(ps+1)/fulldim
                        if np.mod(percent, 10) == 0:
                            s.dialog6.ui.progressBar_Validation.setValue(int(percent))
                            start = times.time()
                            while times.time() - start < 0.1:
                                QApplication.processEvents()
                        ps += 1
        s.dialog6.accept()
        QApplication.processEvents()
        min_kdist, max_kdist = min_max_kdist(kdist)
        detach_plot_global_validation(s.dialog4.ui, s, s.r_reg_global,
                                      s.Pr_reg_global[:, ln],
                                      s.bg_time1_cut, s.bg_corrected1_cut,
                                      s.reg1_global[:, ln], s.bg_time2_cut,
                                      s.bg_corrected2_cut,
                                      s.reg2_global[:, ln], r, kdist,
                                      min_kdist, max_kdist)
        s.calctime = times.time()-sttime
        s.bg_range = bg_range
        s.max_kdist = max_kdist
        s.min_kdist = min_kdist
        s.noiselevel = value
        s.number_noise = number_noise
        s.bg_dim_range = bg_dim_range
        s.total_trials = fulldim
        s.validation_carried_out = True
        s.rms = rms1+s.fitweight*rms2
        s.validation_global = True
        s.weighting = weighting
        return
    except:
        str_tmp = ("Something went wrong! Global backgound function " +
                   "is required. ")
        s.War4 = QMessageBox.warning(s, "Error", str_tmp, QMessageBox.Ok)
        return


def min_max_kdist(kdist):
    shape = kdist.shape
    min_kdist = np.zeros(shape[1])
    max_kdist = np.zeros(shape[1])
    for i in range(0, shape[1]):
        min_kdist[i] = np.min(kdist[:, i])
        max_kdist[i] = np.max(kdist[:, i])
    return min_kdist, max_kdist


def detach_plot_validation(s, s1, r_org, Pr_org, time_org, TT_org, Fit_org,
                           r=None, Pr=None, min_kdist= None,
                           max_kdist=None):
    try:
        s.ax7.clear()
        s.ax7.set_visible(False)
        s.ax8.clear()
        s.ax8.set_visible(False)
    except:
        pass
    s.ax7 = s.figure7.add_subplot(1, 1, 1)
    s.ax7.set_visible(True)
    s.ax8 = s.figure8.add_subplot(1, 1, 1)
    s.ax8.set_visible(True)
    # Distance Distribution Figure
    for tick in s.ax7.xaxis.get_major_ticks():
        tick.label.set_fontsize(fonts)
    for tick in s.ax7.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts-2)
    s.ax7.set_xlabel('$r \, \mathrm{/ \, nm}$', size=fonts)
    s.ax7.set_ylabel('$P(r)$', size=fonts)
    if r is not None:
        for i in range(0, len(Pr[:, 0])):
            s.ax7.plot(r[0, :], Pr[i, :]/np.sum(Pr[i, :]), color='gray')
        s.ax7.plot(r[0, :], min_kdist, color='green')
        s.ax7.plot(r[0, :], max_kdist, color='green')
    s.ax7.plot(r_org, Pr_org, color='r')
    if r is not None:
        s.ax7.set_ylim([0-np.max(Pr_org)/100,
                        np.max(Pr[:, :])+np.max(Pr[:, :])/6])
    else:
        s.ax7.set_ylim([0-np.max(Pr_org)/100, np.max(Pr_org)+np.max(Pr_org)/6])
    s.ax7.set_xlim([np.min(r_org), np.max(r_org)])
    s.figure7.subplots_adjust(left=0.15, bottom=0.22, right=0.98, top=0.95)
    s.canvas7.draw()
    times.sleep(0.05)
    s.canvas7.show()
    # Time Trace Figure
    for tick in s.ax8.xaxis.get_major_ticks():
        tick.label.set_fontsize(fonts)
    for tick in s.ax8.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts-2)
    s.ax8.set_xlabel('$time \, \mathrm{/ \, ns}$', size=fonts)
    s.ax8.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
    s.ax8.plot(time_org, TT_org, 'b')
    s.ax8.plot(time_org, Fit_org, 'r')
    s.ax8.set_xlim([np.min(time_org), np.max(time_org)])
    s.figure8.subplots_adjust(left=0.15, bottom=0.22, right=0.98, top=0.95)
    # Draw the current figure
    s.canvas8.draw()
    times.sleep(0.05)
    s.canvas8.show()
    return


def detach_plot_global_validation(s, s1, r_org, Pr_org, time_org, TT_org,
                                  Fit_org, time_org2, TT_org2, Fit_org2,
                                  r=None, Pr=None, min_kdist=None,
                                  max_kdist=None):
    try:
        s.ax7.clear()
        s.ax7.set_visible(False)
        s.ax8.clear()
        s.ax8.set_visible(False)
    except:
        pass
    s.ax7 = s.figure7.add_subplot(1, 1, 1)
    s.ax7.set_visible(True)
    s.ax8 = s.figure8.add_subplot(1, 1, 1)
    s.ax8.set_visible(True)
    # Distance Distribution Figure
    for tick in s.ax7.xaxis.get_major_ticks():
        tick.label.set_fontsize(fonts)
    for tick in s.ax7.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts-2)
    s.ax7.set_xlabel('$r \, \mathrm{/ \, nm}$', size=fonts)
    s.ax7.set_ylabel('$P(r)$', size=fonts)
    if r is not None:
        for i in range(0, len(Pr[:, 0])):
            s.ax7.plot(r[0, :], Pr[i, :]/np.sum(Pr[i, :]), color='gray')
        s.ax7.plot(r[0, :], min_kdist, color='green')
        s.ax7.plot(r[0, :], max_kdist, color='green')
    s.ax7.plot(r_org, Pr_org/np.sum(Pr_org), color='r')
    s.ax7.set_ylim([0-np.max(Pr_org)/100.0,
                    (np.max(Pr_org/np.sum(Pr_org)) +
                     np.max(Pr_org/np.sum(Pr_org))/6)])
    s.ax7.set_xlim([np.min(r_org), np.max(r_org)])
    s.figure7.subplots_adjust(left=0.15, bottom=0.22, right=0.98, top=0.95)
    s.canvas7.draw()
    times.sleep(0.05)
    s.canvas7.show()
    # Time Trace Figure
    for tick in s.ax8.xaxis.get_major_ticks():
        tick.label.set_fontsize(fonts)
    for tick in s.ax8.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts-2)
    s.ax8.set_xlabel('$time \, \mathrm{/ \, ns}$', size=fonts)
    s.ax8.set_ylabel('$Int\, \mathrm{/ \, Mod. Depth}$', size=fonts)
    s.ax8.plot(time_org, TT_org, 'b')
    s.ax8.plot(time_org, Fit_org, 'r')
    s.ax8.plot(time_org2, TT_org2+np.max(Fit_org), 'b')
    s.ax8.plot(time_org2, Fit_org2+np.max(Fit_org), 'r')
    maxval = np.max([np.max(time_org2), np.max(time_org)])
    s.ax8.set_xlim([np.min(time_org), maxval])
    s.figure8.subplots_adjust(left=0.15, bottom=0.22, right=0.98, top=0.95)
    # Draw the current figure
    s.canvas8.draw()
    times.sleep(0.05)
    s.canvas8.show()
    return


def save_results_validation(s1, s, r_org=None, Pr_org=None):
    if not s.validation_carried_out:
        return
    else:
        s.dialog10 = QFileDialog()
        s.dialog10.setStyleSheet("background-color:rgb(0, 196, 255)")
        str_tmp = "*.txt (*.txt);;*dat (*.dat)"
        name, name_tmp = s.dialog10.getSaveFileName(s, 'Save File', None,
                                                    str_tmp)
        if not name:
            return
        s.save_name = name
        s.save_name = str(s.save_name)
        if not (s.save_name.endswith('.txt') or s.save_name.endswith('.dat')):
            s.save_name += '.txt'
        if '.txt' in s.save_name:
            pos = s.save_name.index('.txt')
            filetyp = '.txt'
            s.save_name = s.save_name[0:pos]
        elif '.dat' in s.save_name:
            pos = s.save_name.index('.dat')
            filetyp = '.dat'
            s.save_name = s.save_name[0:pos]
        # Save the validation results
        strings = ('_validation_info', '_validation_distr')
        y = (r_org, Pr_org, s.min_kdist, s.max_kdist)
        y = np.asarray(y)
        y = np.transpose(y)
        with open(s.save_name+strings[1]+filetyp, 'w') as file:
            file.write("\n".join("   ".join(map("{:.8f}".format, x)) for x in (y)))
        file.close()
        if s.activeset == 1:
            str_tmp = s.filename1
        else:
            str_tmp = s.filename2
        with open(s.save_name+strings[0]+filetyp, 'w') as file:
            if not s.validation_global:
                file.write("Infosheet (Validation) for:\n"+str_tmp+"\n\n")
            else:
                file.write("Infosheet (Global Validation) for:\n" +
                           str(s.filename1))
                file.write("\n and "+str(s.filename2)+"\n\n")
            file.write("Analyzed at: ")
            now = datetime.datetime.now()
            file.write(now.strftime("%Y-%m-%d %H:%M:%S"))
            file.write("\n\nAnalyzed with: "+s.GlopelVersion+"\n")
            file.write("\n\n*************Validation results**********" +
                       "*******\n\n")
            file.write("RMS of the initial solution: "+str(s.rms))
            file.write("\n\nTotal function evaluations: "+str(s.total_trials))
            file.write("\n\nPoints background variation: " +
                       str(s.bg_range.shape[0]))
            file.write("\nBackground start (min/max): " +
                       str(np.min(s.bg_range))+"/"+str(np.max(s.bg_range)))
            file.write("\n\nPoints background dimension: " +
                       str(s.bg_dim_range.shape[0]))
            file.write("\nBackground dimension (min/max): " +
                       str(np.min(s.bg_dim_range))+"/" +
                       str(np.max(s.bg_dim_range)))
            file.write("\n\nPoints for additive white noise: " +
                       str(s.number_noise))
            file.write("\nAdditive relative noise level: " +
                       str(np.min(s.noiselevel)))
            if s.prune:
                file.write("\n\nPruning level: " +
                           str(s.pruneval))
            if s.weighting is None:
                pass
            else:
                file.write("\n\nPoints variation weighting factor: " +
                           str(s.weighting.shape[0]))
                file.write("\nWeighting factor (min/max): " +
                           str(np.min(s.weighting))+"/" +
                           str(np.max(s.weighting)))
            file.write("\n\n******************************************\n\n")
            file.write("Calculation time: " +
                       str(round(s.calctime, 5))+" s")
            str_tmp = ("\n\nInitial solution, upper bound and lower bound " +
                       "is saved in:\n")
            file.write(str_tmp+s.save_name+strings[1]+filetyp)
        file.close()
        filename = s.save_name+strings[0]+filetyp
        filename_out = s.save_name
        SavetoPDF(s1, filename, filename_out, file, s)
        return


def SavetoPDF(s, filename, filename_out, file, s1):
    # Save figures
    currsize = s.figure7.get_size_inches()
    currsize2 = s.figure8.get_size_inches()
    for tick in s.ax8.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts)
    for tick in s.ax7.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts)
    s.figure7.set_size_inches(4, 3)
    s.figure8.set_size_inches(4, 3)
    str1 = filename_out+"_Inital_solution"
    s.figure7.savefig(str1+".png", bbox_inches='tight', papertype='a4',
                      format='png', dpi=600)
    str11 = filename_out+"_Validation_DD"
    s.figure8.savefig(str11+".png", bbox_inches='tight', papertype='a4',
                      format='png', dpi=600)
    filename_out = filename_out+"_Report"+".pdf"
    c = canvas.Canvas(filename_out)
    textobject = c.beginText(20, 750)
    textobject.setFont('Times-Bold', 14)
    textobject.textLine("                     Validation Information Sheet")
    textobject.textLine("")
    textobject.textLine("")
    textobject.setFont('Times-Roman', 12)
    with open(filename, "r") as f:
        for lines in f:
            lines = lines.replace("\n", "")
            textobject.textLine(lines)
    f.close
    try:
        pathname = str(s1.iconpath)
        c.drawImage(pathname, 420, 750, 80, 80)
    except:
        pass
    str2 = str1+".png"
    str22 = str11+".png"
    c.setFont('Times-Bold', 16)
    c.drawString(200, 780, "Validation Results")
    c.setFont('Times-Roman', 12)
    c.setFillColorRGB(0, 0, 1)
    c.drawString(20, 720, "-- Experimental data")
    c.setFillColorRGB(1, 0, 0)
    c.drawString(20, 700, "-- Original time trace and Tikhonov solution:")
    c.setFillColorRGB(0, 0, 0)
    c.drawImage(str22, 100, 440, 320, 240)
    c.drawString(20, 420, "Validation results:")
    c.setFillColorRGB(1, 0, 0)
    c.drawString(20, 400, "-- Original Tikhonov solution")
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.drawString(20, 380, "-- All variational solutions")
    c.setFillColorRGB(0, 0.6, 0)
    c.drawString(20, 360, "-- Error range")
    c.setFillColorRGB(0, 0, 0)
    c.drawImage(str2, 90, 100, 320, 240)
    c.showPage()
    try:
        pathname = str(s1.iconpath)
        c.drawImage(pathname, 420, 750, 80, 80)
    except:
        pass
    c.drawText(textobject)
    c.save()
    c.showPage()
    for tick in s.ax8.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts-2)
    for tick in s.ax7.yaxis.get_major_ticks():
        tick.label.set_fontsize(fonts-2)
    s.figure7.set_size_inches(currsize, forward=True)
    s.figure8.set_size_inches(currsize2, forward=True)
    s.canvas7.draw()
    s.canvas8.draw()
    return
