# -*- coding: utf-8 -*-
"""
Created on Sat Dec 31 12:12:29 2016

@author: Stephan Rein

Input parser for DTA and text files.
For .DTA files the additional description file .DSC is necessary

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2017, Stephan Rein, M.Sc., University of Freiburg
"""

import numpy as np


def initialize_var1(var1):
    var1.raw_spetrum1 = np.zeros(1)
    var1.normalizedpc_spetrum1 = np.zeros(1)
    var1.normalizedpc_imag1 = np.zeros(1)
    var1.normalizedpc_zt_spetrum1 = np.zeros(1)
    var1.normalizedpc_zt_bg_spetrum1 = np.zeros(1)
    var1.time1 = np.zeros(1)
    var1.time1 = np.zeros(1)
    var1.FFreq1 = np.zeros(1)
    var1.Fourier1 = np.zeros(1)
    var1.bg_corrected1 = np.zeros(1)
    var1.bg_time1 = np.zeros(1)
    var1.bg_fun1 = np.zeros(1)
    var1.pc_spetrum1 = np.zeros(1)
    var1.pc_imag1 = np.zeros(1)
    var1.zerotime1 = 0
    var1.filename1 = ""
    var1.pc1_phase0order = 0
    var1.pc1_phase1order = 0
    var1.pc_spetrum11 = np.zeros(1)
    var1.pc_imag11 = np.zeros(1)
    var1.normfactor1 = 0
    var1.bg_param1 = np.zeros(2)
    var1.dist_1 = np.zeros(5)
    var1.coef1 = np.zeros(5)
    var1.sigma1 = 0
    var1.Pr_1 = np.zeros(1)
    var1.dist_1 = np.zeros(1)
    var1.Fit1 = np.zeros(1)
    var1.distance_1 = np.zeros(1)
    var1.FourierFit1 = np.zeros(1)
    var1.multigaussian1 = True
    var1.lsq_fit1 = None
    var1.Globaldist = 0
    var1.Globalcoef = 0
    var1.Globalsigma = 0
    var1.GlobalPr = np.zeros(1)
    var1.Globaldistance = np.zeros(1)
    var1.GlobalFit1 = np.zeros(1)
    var1.multigaussian_glo = True
    var1.Lcurvex1 = np.zeros(20)
    var1.Lcurvey1 = np.zeros(20)
    var1.r1_reg = np.zeros(1),
    var1.Pr1_reg = np.zeros(1)
    var1.reg1 = np.zeros(1)
    var1.L_curve_number1 = 5
    var1.Thik_regul1_exist = False
    var1.bg_dim1 = 3
    var1.output_results1 = list()
    var1.overwrite_fit_res1 = False
    var1.r_reg_global = np.zeros(1)
    var1.Pr_reg_global = np.zeros(1)
    var1.reg1_global = np.zeros(1)
    var1.Lcurvex_global = np.zeros(20)
    var1.Lcurvey_global = np.zeros(20)
    var1.GlobalFourier1 = np.zeros(1)
    var1.GlobalFFreq1 = np.zeros(1)
    var1.supressing1 = False
    var1.supressingstart1 = 1
    var1.supressingend1 = 1
    var1.exclude_vol1 = None
    var1.adaptive_kernel1 = False
    var1.large_kernel1 = False
    var1.redline1 = 8
    var1.cutoff1 = 0
    var1.Lcurvex_autocorr1 = np.zeros(20)
    var1.Lcurvey_autocorr1 = np.zeros(20)
    var1.alpha_cross1 = np.zeros(20)
    var1.alpha_aic1 = np.zeros(20)
    return


def initialize_var2(var2):
    var2.raw_spetrum2 = np.zeros(1)
    var2.normalizedpc_spetrum2 = np.zeros(1)
    var2.normalizedpc_imag2 = np.zeros(1)
    var2.normalizedpc_zt_spetrum2 = np.zeros(1)
    var2.normalizedpc_zt_bg_spetrum2 = np.zeros(1)
    var2.time2 = np.zeros(1)
    var2.Fourier2 = np.zeros(1)
    var2.FFreq2 = np.zeros(1)
    var2.bg_corrected2 = np.zeros(1)
    var2.bg_time2 = np.zeros(1)
    var2.bg_fun2 = np.zeros(1)
    var2.pc_spetrum2 = np.zeros(1)
    var2.pc_imag2 = np.zeros(1)
    var2.zerotime2 = 0
    var2.pc2_phase0order = 0
    var2.pc2_phase1order = 0
    var2.filename2 = ""
    var2.pc_spetrum22 = np.zeros(1)
    var2.pc_imag22 = np.zeros(1)
    var2.normfactor2 = 0
    var2.bg_param2 = np.zeros(2)
    var2.dist_2 = np.zeros(5)
    var2.coef2 = np.zeros(5)
    var2.sigma2 = 0
    var2.Pr_2 = np.zeros(1)
    var2.dist_2 = np.zeros(1)
    var2.Fit2 = np.zeros(1)
    var2.distance_2 = np.zeros(1)
    var2.FourierFit2 = np.zeros(1)
    var2.multigaussian2 = True
    var2.lsq_fit2 = None
    var2.GlobalFit2 = np.zeros(1)
    var2.Lcurvex2 = np.zeros(20)
    var2.Lcurvey2 = np.zeros(20)
    var2.r2_reg = np.zeros(1),
    var2.Pr2_reg = np.zeros(1)
    var2.reg2 = np.zeros(1)
    var2.L_curve_number2 = 5
    var2.Thik_regul2_exist = False
    var2.bg_dim2 = 3
    var2.output_results2 = list()
    var2.overwrite_fit_res2 = False
    var2.reg2_global = np.zeros(1)
    var2.GlobalFourier2 = np.zeros(1)
    var2.GlobalFFreq2 = np.zeros(1)
    var2.supressing2 = False
    var2.supressingstart2 = 1
    var2.supressingend2 = 1
    var2.exclude_vol2 = None
    var2.adaptive_kernel2 = False
    var2.large_kernel2 = False
    var2.redline2 = 8
    var2.cutoff2 = 0
    var2.Lcurvex_autocorr2 = np.zeros(20)
    var2.Lcurvey_autocorr2 = np.zeros(20)
    var2.alpha_cross2 = np.zeros(20)
    var2.alpha_aic2 = np.zeros(20)
    return


def read_input_var(var, Input, n, boolean, filename=None):
    # Default setting for complex signal
    complexsignal = True
    if boolean:
        if len(Input[1, :]) == 3:
            if n == 1:
                var.pc_spetrum1 = Input[:, 1]
                var.pc_imag1 = Input[:, 2]
                var.pc_imag1 = var.pc_imag1/max(var.pc_spetrum1)
                var.pc_spetrum1 = var.pc_spetrum1/max(var.pc_spetrum1)
                var.time1 = Input[:, 0]
                return var.pc_spetrum1, var.pc_imag1, var.time1
            elif n == 2:
                var.pc_spetrum2 = Input[:, 1]
                var.pc_imag2 = Input[:, 2]
                var.pc_imag2 = var.pc_imag2/max(var.pc_spetrum2)
                var.pc_spetrum2 = var.pc_spetrum2/max(var.pc_spetrum2)
                var.time2 = Input[:, 0]
                return var.pc_spetrum2, var.pc_imag2, var.time2
        elif len(Input[1, :]) == 2:
            if n == 1:
                var.pc_spetrum1 = Input[:, 1]
                var.pc_spetrum1 = var.pc_spetrum1/max(var.pc_spetrum1)
                var.pc_imag1 = np.zeros(len(var.pc_spetrum1))
                var.pc_imag1 = var.pc_imag1+0.000001
                var.time1 = Input[:, 0]
                return var.pc_spetrum1, var.pc_imag1, var.time1
            elif n == 2:
                var.pc_spetrum2 = Input[:, 1]
                var.pc_spetrum2 = var.pc_spetrum2/max(var.pc_spetrum2)
                var.pc_imag2 = np.zeros(len(var.pc_spetrum2))
                var.pc_imag2 = var.pc_imag2+0.000001
                var.time2 = Input[:, 0]
                return var.pc_spetrum2, var.pc_imag2, var.time2
        return
    elif not boolean:
        if filename.endswith('.DTA'):
            filename = filename[0:len(filename)-4]
            filename = filename+".DSC"
            try:
                f = open(filename, 'r')
                t = f.readlines()
                for l in t:
                    if l.startswith('IKKF'):
                        s = l.split()
                        if s[1] == 'CPLX':
                            complexsignal = True
                        else:
                            complexsignal = False
                        continue
                    if l.startswith('XPTS'):
                        s = l.split()
                        npoints = int(s[1])
                        continue
                    if l.startswith('XMIN'):
                        s = l.split()
                        start = float(s[1])
                        continue
                    if l.startswith('XWID'):
                        s = l.split()
                        timescale = float(s[1])
                        continue
                if n == 2:
                    var.pc_spetrum2 = Input[0:len(Input):2]
                    if complexsignal:
                        var.pc_imag2 = Input[1:len(Input):2]
                    elif not complexsignal:
                        var.pc_imag2 = np.zeros(len(var.pc_spetrum2))
                    var.pc_imag2 = var.pc_imag2/max(var.pc_spetrum2)
                    var.pc_spetrum2 = var.pc_spetrum2/max(var.pc_spetrum2)
                    var.pc_imag2 = var.pc_imag2+0.000001
                    stepsize = (timescale)/(npoints-1)
                    var.time2 = np.arange(npoints)
                    var.time2 = var.time2*stepsize
                    var.time2 = var.time2+start
                    return var.pc_spetrum2, var.pc_imag2, var.time2
                elif n == 1:
                    var.pc_spetrum1 = Input[0:len(Input):2]
                    if complexsignal:
                        var.pc_imag1 = Input[1:len(Input):2]
                    elif not complexsignal:
                        var.pc_imag1 = np.zeros(len(var.pc_spetrum1))
                        var.pc_imag1 = var.pc_imag1+0.000001
                    var.pc_imag1 = var.pc_imag1/max(var.pc_spetrum1)
                    var.pc_spetrum1 = var.pc_spetrum1/max(var.pc_spetrum1)
                    var.pc_imag1 = var.pc_imag1+0.000001
                    stepsize = (timescale)/(npoints-1)
                    var.time1 = np.arange(npoints)
                    var.time1 = var.time1*stepsize
                    var.time1 = var.time1+start
                    return var.pc_spetrum1, var.pc_imag1, var.time1
            except:
                print("No .DSC file available")
                pass
        return
