#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 11:42:10 2017


@author: Stephan Rein

Subfunction for fitting analysis.
For non-linear optimization different routines from the scipy optimize package
are available. Preoptimization is carried out the accelerate the convergence
of the full function evaluation by using the preoptimized parameters as
initial parameter guess.

The two kernel functions are available for nonlinear optimization:
Model 1: 5 independent Gaussian functions with indentical standard deviation
Model 2: 4 independent Gaussian functions with separate standard deviation

The available minimize algorithms are:
1: Trust-region-reflective
2: Sequential Least SQuares Programming (SLSQP)
3: Modification of Powell’s method
4: Quasi-Newton method of Broyden, Fletcher, Goldfarb, and Shanno (BFGS)
5: Stochastic Trust-region-reflective
6: Constrained Optimization BY Linear Approximation (COBYLA)

F-test is used to check the significance.
The corresponding function for the F-value is:
F=((lsq_r-lsq_f)/(l_r-l_f))/(lsq_f/(l_f/4.0))

where lsq_r is the least-square deviation of the reduced model,
lsq_f is the least-square deviation of the full model, l_r and l_f
are the degrees of freedom of the reduced and full model, respectively.

According to the F-value the reduced model is accepted or rejected. The
number of Gaussians is iteratively reduced. The model with the smallest
amount of Gaussian function which got accepted is used as final result.

Please not that the expression Trimodal is an alias for 4 Gaussian functions
with variable standard deviation!!!

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein, M.Sc., University of Freiburg
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import minimize
from scipy.special import fresnel
from scipy import stats as stat


# Boundaries (default values, can be changed in fitconfig.txt file)
sigma_lb = 0.05
sigma_ub = 0.4
dist_ub = 8.0
dist_lb = 1.5


# Dictionary for optimization algorithms
dictionary = {2: 'SLSQP', 3: 'Powell', 4: 'BFGS', 6: 'COBYLA'}
exact_name = {1: "Trust-region-reflective",
              2: 'Sequential Least SQuares Programming (SLSQP)',
              3: 'Modification of Powell’s method',
              4: ("\nQuasi-Newton method of Broyden, Fletcher, " +
                  "Goldfarb, and Shanno (BFGS)"),
              5: "Stochastic Trust-region-reflective",
              6: 'Constrained Optimization BY Linear Approximation (COBYLA)'}
dict_maxiter = {2: 3000, 3: 500, 4: 4000, 6: 1000}


"""****************************************************************************
                    POST ANALYSIS FUNCTIONS
****************************************************************************"""


def final_PELDOR_Calculation(time, moddepth, dist, coef, sigma,
                             multigaussian=True):
    if multigaussian:
        param = np.append(np.append(dist, coef), sigma)
        spectrum = PELDOR_Calculation((time, moddepth), *param)
    elif not multigaussian:
        param = np.append(np.append(dist, coef), sigma)
        spectrum = PELDOR_Calculation_TriModal((time, moddepth), *param)
    return spectrum


def lsq_deviation(spectrum, fit):
    lsq = sum(np.power((fit-spectrum), 2))
    return lsq


"""****************************************************************************
                       KERNEL FITTING FUNCTIONS
****************************************************************************"""


def internal_PELDOR_kernel(dist, coef, sigma, moddepth, time, num,
                           gaussiansteps):
    # High dimensional array for time (vectorized Fresnel integrals)
    time_tmp_mat = np.ones((len(dist), gaussiansteps, len(time)))
    time_tmp_mat = time_tmp_mat*time
    y = np.zeros((gaussiansteps, len(dist)))
    fr = np.zeros((gaussiansteps, len(dist)))
    ditr = np.zeros((gaussiansteps, len(dist)))
    for gau in range(0, len(dist)):
        # Point in space with subsequent transform to frequency space
        y = np.linspace(dist[gau]-num*sigma[gau], dist[gau]+num*sigma[gau],
                        gaussiansteps)
        ditr[:, gau] = np.exp(-0.5*np.power((dist[gau]-y), 2) /
                              (sigma[gau]*sigma[gau]))
        ditr[:, gau] = ditr[:, gau]/np.sum(ditr[:, gau])
        fr[:, gau] = (327.0/np.power(y, 3))

    # Fully vectorized Fresnel integral evaluation
    fi = np.transpose(np.abs(fr)*np.transpose(time_tmp_mat))
    b1 = np.sqrt(6/np.pi)*np.sqrt(fi)
    tmpfresnel = fresnel(b1)
    b1[:, :, 0] = 1.0
    integral = np.transpose((np.cos(fi)*tmpfresnel[1]+np.sin(fi) *
                            tmpfresnel[0])/(b1))*coef
    integral[0, :, :] = coef
    signal = np.sum(np.sum((ditr*(integral)), axis=2), axis=1)
    if max(signal) < 1e-20:
        signal += 1e-8
    return (moddepth*(signal/max(signal)))


def PELDOR_Calculation(time, *frequencies):
    # Allocations and settings
    moddepth = time[1]
    if len(time) == 3:
        pre = time[2]
    else:
        pre = False
    frequencies = np.absolute(frequencies)
    number = (len(frequencies)-1)//2
    sigma = frequencies[-1]
    dist = frequencies[0:number]
    coef = frequencies[number:2*number]
    coef = coef/np.sum(coef+1e-7)
    time_tmp = time[0]/1000.0
    # Internal boundaries
    for k in range(0, len(dist)):
        if dist[k] > dist_ub:
            dist[k] = dist_ub
        if dist[k] < dist_lb:
            dist[k] = dist_lb
    if sigma < sigma_lb:
        sigma = sigma_lb
    if sigma > sigma_ub:
        sigma = sigma_ub
    gaussiansteps = 7+int(round(sigma*30))
    gaussiansteps = gaussiansteps*2+1
    # Reduce the discretization interval if preoptimization is enabled
    if not pre:
        num = 3
    else:
        num = 2
        gaussiansteps = gaussiansteps//2
    sigma = np.ones(len(dist))*sigma
    signal = internal_PELDOR_kernel(dist, coef, sigma, moddepth, time_tmp, num,
                                    gaussiansteps)
    return signal


def PELDOR_Calculation_sup(args, *frequencies):
    # Allocations and settings
    moddepth = args[1]
    supstart = args[2]
    supend = args[3]
    if len(args) == 5:
        pre = args[4]
    else:
        pre = False
    frequencies = np.absolute(frequencies)
    number = (len(frequencies)-1)//2
    sigma = frequencies[-1]
    dist = frequencies[0:number]
    coef = frequencies[number:2*number]
    time_tmp = args[0]/1000.0
    signal = np.zeros(len(args[0]))
    # Internal boundaries
    for k in range(0, len(dist)):
        if dist[k] > 8:
            dist[k] = 8
        if dist[k] < 1.4:
            dist[k] = 1.4
    # Respecting the suppression conditions
    if sigma < 0.08:
        sigma = 0.08
    if sigma > 0.4:
        sigma = 0.4
    for k in range(0, len(dist)):
        if (np.absolute(dist[k])-2.6*sigma < supend and
           np.absolute(dist[k])+2.6*sigma > supstart):
            coef[k] = 0.000000
    coef = np.abs(coef)
    coef = coef/(np.sum(coef)+0.00000001)
    gaussiansteps = 7+int(round(sigma*30))
    gaussiansteps = gaussiansteps*2+1
    if not pre:
        num = 3
    else:
        num = 2
        gaussiansteps = gaussiansteps//2
    # High dimensional array for time (vectorized Fresnel integrals)
    sigma = np.ones(len(dist))*sigma
    signal = internal_PELDOR_kernel(dist, coef, sigma, moddepth, time_tmp, num,
                                    gaussiansteps)
    return signal


def PELDOR_Calculation_TriModal(time, *frequencies):
    # Allocations and settings
    moddepth = time[1]
    if len(time) == 3:
        pre = time[2]
    else:
        pre = False
    frequencies = np.absolute(frequencies)
    number = len(frequencies)//3
    sigma = frequencies[2*number:3*number]
    dist = frequencies[0:number]
    coef = frequencies[number:2*number]
    coef = coef/np.sum(coef)
    time_tmp = time[0]/1000.0
    # Internal boundaries
    for k in range(0, len(dist)):
        if dist[k] > 8:
            dist[k] = 8
        if dist[k] < 1.4:
            dist[k] = 1.4
        if sigma[k] < 0.05:
            sigma[k] = 0.05
        if sigma[k] > 0.4:
            sigma[k] = 0.4
    # The same number of Gaussian steps due to multiple standard deviations
    if pre:
        gaussiansteps = 15
        num = 2
    else:
        gaussiansteps = 31
        num = 3
    # High dimensional array for time (vectorized Fresnel integrals)
    signal = internal_PELDOR_kernel(dist, coef, sigma, moddepth, time_tmp, num,
                                    gaussiansteps)
    return signal


def PELDOR_Calculation_TriModal_sup(args, *frequencies):
    # Allocations and settings
    moddepth = args[1]
    supstart = args[2]
    supend = args[3]
    time = args[0]
    if len(args) == 5:
        pre = args[4]
    else:
        pre = False
    frequencies = np.absolute(frequencies)
    number = len(frequencies)//3
    sigma = frequencies[2*number:3*number]
    dist = frequencies[0:number]
    coef = frequencies[number:2*number]
    coef = coef/np.sum(coef)
    time_tmp = time/1000.0
    # Internal boundaries
    for k in range(0, len(dist)):
        if dist[k] > 8:
            dist[k] = 8
        if dist[k] < 1.4:
            dist[k] = 1.4
        if sigma[k] < 0.05:
            sigma[k] = 0.05
        if sigma[k] > 0.4:
            sigma[k] = 0.4
    # Respecting the suppression conditions
    for k in range(0, len(dist)):
        if (np.absolute(dist[k])-2.6*sigma[k] < supend and
           np.absolute(dist[k])+2.6*sigma[k] > supstart):
            coef[k] = 0.000000
    coef = np.abs(coef)
    coef = coef/(np.sum(coef)+0.00000001)
    # The same number of Gaussian steps due to multiple standard deviations
    # precalculation algorithm with 15 steps
    if pre:
        gaussiansteps = 15
        num = 2
    else:
        gaussiansteps = 31
        num = 3
    # High dimensional array for time (vectorized Fresnel integrals)
    signal = internal_PELDOR_kernel(dist, coef, sigma, moddepth, time_tmp, num,
                                    gaussiansteps)
    return signal


"""****************************************************************************
            NON-LINEAR OPTIMIZATION ROUTINES
****************************************************************************"""


def Algorithm_and_function_setting(multigaussan, globalAna, suppresion):
    if multigaussan:
        model = 1
        fun = 'simple_errf'
        fun2 = 'PELDOR_Calculation'
        maxGaus = 5
        popt_best_F_test = np.zeros(11)
        if globalAna:
            fun = 'simplex_errf_global_mult'
            fun2 = 'PELDOR_Calculation_mult_global'
        if suppresion:
            fun = 'simple_errf_sup'
            fun2 = 'PELDOR_Calculation_sup'
            if globalAna:
                fun = 'simplex_errf_global_mult_sup'
                fun2 = 'PELDOR_Calculation_Mult_global_sup'
    else:
        model = 2
        maxGaus = 4
        popt_best_F_test = np.zeros(12)
        fun = 'simple_errf_tri'
        fun2 = 'PELDOR_Calculation_TriModal'
        if globalAna:
            fun = 'simplex_errf_global_mult'
            fun2 = 'PELDOR_Calculation_TriModal_global'
        if suppresion:
                fun = 'simple_errf_sup'
                fun2 = 'PELDOR_Calculation_TriModal_sup'
                if globalAna:
                    fun = 'simplex_errf_global_tri_sup'
                    fun2 = 'PELDOR_Calculation_TriModal_global_sup'
    return fun, fun2, model, popt_best_F_test, maxGaus


def objective_min(xdata, ydata, moddepth, minmethod=2, multigaussan=True,
                  xdata2=None, ydata2=None, weight=0,
                  globalAna=False, suppresion=False, supstart=None,
                  supend=None):
    printline(True)
    print("Algorithm: "+exact_name[minmethod])
    (fun, fun2, model, popt_best_F_test,
     maxGaus) = Algorithm_and_function_setting(multigaussan, globalAna,
                                               suppresion)
    if suppresion:
            pass_args_f = (xdata, ydata, moddepth, supstart, supend, False)
            pass_args2 = (xdata, moddepth, supstart, supend, True)
            if globalAna:
                pass_args_f = (xdata, ydata, xdata2, ydata2, weight, moddepth,
                               supstart, supend, False)
                pass_args2 = (xdata, xdata2, weight, moddepth, supstart,
                              supend, True)
    else:
            pass_args_f = (xdata, ydata, moddepth, False)
            pass_args2 = (xdata, moddepth, True)

            if globalAna:
                pass_args_f = (xdata, ydata, xdata2, ydata2, weight, moddepth,
                               False)
                pass_args2 = (xdata, xdata2, weight, moddepth, supstart,
                              supend, True)
    lsq_best_F_test = 0
    for k in range(maxGaus, 0, -1):
        init = make_init(k, model, popt_best_F_test)
        # Restore initial parameter in bounce by suppression
        if suppresion:
            dist, coeff, sigma = convert_init2dist_coeff_sigma(model, init)
            init = throw_in_bounce(model, dist, coeff, sigma, supend, supstart)
        try:
            try:
                boundaries = make_boundaries(k, model)
                if globalAna:
                    ydata_tmp = np.concatenate((ydata, np.sqrt(weight)*ydata2))
                else:
                    ydata_tmp = ydata
                popt_out, pcov = curve_fit(eval(fun2), pass_args2, ydata_tmp,
                                           (init), bounds=boundaries,
                                           verbose=0,
                                           max_nfev=500, ftol=5e-5)
                distances, coef, sigma = return_result(np.abs(popt_out), model)
                if suppresion:
                    distances, coef, sigma = suppression_handler(model,
                                                                 distances,
                                                                 coef, sigma,
                                                                 supstart,
                                                                 supend)
                opt_init = restore_popt(distances, coef, sigma)
            except:
                opt_init = init
            popt = minimize(eval(fun), opt_init, args=pass_args_f,
                            method=dictionary[minmethod], tol=1e-5,
                            options={'maxiter': dict_maxiter[minmethod],
                                     'disp': False})
            distances, coef, sigma = return_result(np.abs(popt.x), model)
            popt_res = restore_popt(distances, coef, sigma)
        except:
            popt_res = init
        distances, coef, sigma = return_result(np.abs(popt_res), model)
        if suppresion:
            distances, coef, sigma = suppression_handler(model, distances,
                                                         coef, sigma, supstart,
                                                         supend)
        popt_res = restore_popt(distances, coef, sigma)
        if not globalAna:
            (lsq_best_F_test,
             popt_best_F_test) = F_test_preparation(model, popt_res, xdata,
                                                    ydata, moddepth,
                                                    popt_best_F_test,
                                                    lsq_best_F_test, k)
        else:
            (lsq_best_F_test,
             popt_best_F_test) = F_test_preparation_global(model, popt_res,
                                                           xdata, ydata,
                                                           xdata2,
                                                           ydata2, moddepth,
                                                           popt_best_F_test,
                                                           lsq_best_F_test,
                                                           weight, k)
        # Condition for stopping Gaussian reduction
        if len(popt_best_F_test)-len(popt_res) > 3:
            break
    return return_result(popt_best_F_test, model, lsq_best_F_test, True)


def trust_region_reflective(xdata, ydata, moddepth, multigaussan=True,
                            minmethod=1, xdata2=None, ydata2=None, weight=0,
                            globalAna=False, suppresion=False, supstart=None,
                            supend=None):
    printline(True)
    print("Algorithm: "+exact_name[minmethod])
    if multigaussan:
        model = 1
        fun = 'PELDOR_Calculation'
        maxGaus = 5
        popt_best_F_test = np.zeros(11)
        ydata_tmp = ydata
        if globalAna:
            ydata_tmp = np.concatenate((ydata, np.sqrt(weight)*ydata2))
            fun = 'PELDOR_Calculation_mult_global'
        if suppresion:
            fun = 'PELDOR_Calculation_sup'
            if globalAna:
                fun = 'PELDOR_Calculation_Mult_global_sup'
    else:
        model = 2
        maxGaus = 4
        popt_best_F_test = np.zeros(12)
        fun = 'PELDOR_Calculation_TriModal'
        ydata_tmp = ydata
        if globalAna:
            ydata_tmp = np.concatenate((ydata, np.sqrt(weight)*ydata2))
            fun = 'PELDOR_Calculation_TriModal_global'
        if suppresion:
                fun = 'PELDOR_Calculation_TriModal_sup'
                if globalAna:
                    fun = 'PELDOR_Calculation_TriModal_global_sup'
    if suppresion:
            pass_args = (xdata, moddepth, supstart, supend, True)
            pass_args_f = (xdata, moddepth, supstart, supend, False)
            if globalAna:
                pass_args = (xdata, xdata2, weight, moddepth, supstart,
                             supend, True)
                pass_args_f = (xdata, xdata2, weight, moddepth, supstart,
                               supend, False)
    else:
            pass_args = (xdata, moddepth, True)
            pass_args_f = (xdata, moddepth, False)
            if globalAna:
                pass_args = (xdata, xdata2, weight, moddepth, True)
                pass_args_f = (xdata, xdata2, weight, moddepth, False)
    lsq_best_F_test = 0
    for i in range(0, 4):
        for k in range(maxGaus, 0, -1):
            init = make_init(k, model, popt_best_F_test)
            if minmethod == 5 and k == maxGaus and i > 0:
                print("\nStochastic sample number: "+str(i))
                init = sample_init(k, model)
            boundaries = make_boundaries(k, model)
            # Restore initial parameter in bounce by suppression
            if suppresion:
                dist, coeff, sigma = convert_init2dist_coeff_sigma(model, init)
                init = throw_in_bounce(model, dist, coeff, sigma, supend,
                                       supstart)
            try:
                try:
                    popt, pcov = curve_fit(eval(fun), pass_args, ydata_tmp,
                                           (init), method='trf',
                                           bounds=boundaries, verbose=0,
                                           max_nfev=800, ftol=5e-6)
                    distances, coef, sigma = return_result(np.abs(popt), model)
                    opt_init = restore_popt(distances, coef, sigma)
                except:
                    opt_init = init
                popt, pcov = curve_fit(eval(fun), pass_args_f, ydata_tmp,
                                       (opt_init), method='trf',
                                       bounds=boundaries, verbose=0,
                                       max_nfev=800, ftol=5e-6)
                distances, coef, sigma = return_result(np.abs(popt), model)
                popt_res = restore_popt(distances, coef, sigma)
            except RuntimeError:
                print("Trust-region reflective algorithm failed!!!")
                popt_res = init
            distances, coef, sigma = return_result(np.abs(popt_res), model)
            if suppresion:
                distances, coef, sigma = suppression_handler(model, distances,
                                                             coef, sigma,
                                                             supstart, supend)
            popt_res = restore_popt(distances, coef, sigma)
            if not globalAna:
                (lsq_best_F_test,
                 popt_best_F_test) = F_test_preparation(model, popt_res, xdata,
                                                        ydata_tmp, moddepth,
                                                        popt_best_F_test,
                                                        lsq_best_F_test, k)
            else:
                (lsq_best_F_test,
                 popt_best_F_test) = F_test_preparation_global(model, popt_res,
                                                               xdata, ydata,
                                                               xdata2, ydata2,
                                                               moddepth,
                                                               popt_best_F_test,
                                                               lsq_best_F_test,
                                                               weight, k)
            # Condition for stopping Gaussian reduction
            if len(popt_best_F_test)-len(popt_res) > 3:
                break
        if minmethod == 1:
            break
        # Stochastic sampling
        elif minmethod == 5:
            if i == 0:
                popt_best_stochastic = popt_best_F_test
                lsq_best_stochastic = lsq_best_F_test
            else:
                if lsq_best_F_test < lsq_best_stochastic:
                    popt_best_stochastic = popt_best_F_test
                    lsq_best_stochastic = lsq_best_F_test
    if minmethod == 5:
        popt_best_F_test = popt_best_stochastic
        lsq_best_F_test = lsq_best_stochastic

    return return_result(popt_best_F_test, model, lsq_best_F_test, True)


"""****************************************************************************
                RETURN FUNCTIONS
****************************************************************************"""


def return_result(popt, model, lsq=0, verbos=False):
    dist, coef, sigma_tmp = convert_init2dist_coeff_sigma(model, popt)
    if model == 1:
        sigma = np.ones(len(dist))*sigma_tmp
    else:
        sigma = sigma_tmp
    if verbos:
        print("\nResults:")
        print("Distance / nm \t Coefficient\t  sigma / nm")
        for i in range(0, len(dist)):
            value1 = str("%.4f" % dist[i])
            value2 = str("%.4f" % coef[i])
            value3 = str("%.4f" % sigma[i])
            print(value1+"\t         "+value2+"\t         "+value3)
        print("Least-squares = ", round(lsq, 6))
        printline()
    if model == 1:
        sigma = sigma_tmp
    return dist, coef, sigma


"""****************************************************************************
                STANDARD OBJECTIVE FUNCTIONS
****************************************************************************"""


def simple_errf(x, time, ydata, moddepth, pre=False):
    return sum(np.power((PELDOR_Calculation((time, moddepth, pre), *x)-ydata),
                        2))


def simple_errf_tri(x, time, ydata, moddepth, pre=False):
    return sum(np.power((PELDOR_Calculation_TriModal((time, moddepth, pre),
                                                     *x)-ydata), 2))


def simple_errf_sup(x, time, ydata, moddepth, supstart, supend, pre=False):
    return sum(np.power((PELDOR_Calculation_sup((time, moddepth, supstart,
               supend, pre), *x)-ydata), 2))


def simple_errf_tri_sup(x, time, ydata, moddepth, supstart, supend, pre=False):
    return sum(np.power((PELDOR_Calculation_TriModal_sup((time, moddepth,
               supstart, supend, pre), *x)-ydata), 2))


"""****************************************************************************
                GLOBAL OBJECTIVE FUNCTION
****************************************************************************"""


def simplex_errf_global_tri(x, time1, ydata1, time2, ydata2, weighting,
                            moddepth, pre=False):
    return (sum(np.power((PELDOR_Calculation_TriModal((time1, moddepth, pre),
                                                      *x)-ydata1), 2)) +
            weighting *
            sum(np.power((PELDOR_Calculation_TriModal((time2, moddepth, pre),
                                                      *x)-ydata2), 2)))


def simplex_errf_global_mult(x, time1, ydata1, time2, ydata2, weighting,
                             moddepth, pre=False):
    return (sum(np.power((PELDOR_Calculation((time1, moddepth, pre), *x) -
                          ydata1), 2)) +
            weighting*sum(np.power((PELDOR_Calculation((time2,
                                    moddepth, pre), *x)-ydata2), 2)))


def PELDOR_Calculation_TriModal_global(args, *x):
    time1 = args[0]
    time2 = args[1]
    moddepth = args[3]
    moddepth2 = np.sqrt(args[2])*args[3]
    pre = args[4]
    return (np.concatenate(((PELDOR_Calculation_TriModal((time1,
                                                          moddepth, pre), *x)),
                            PELDOR_Calculation_TriModal((time2,
                                                         moddepth2, pre),
                                                        *x))))


def PELDOR_Calculation_mult_global(args, *x):
    time1 = args[0]
    time2 = args[1]
    moddepth = args[3]
    moddepth2 = np.sqrt(args[2])*args[3]
    pre = args[4]
    return (np.concatenate(((PELDOR_Calculation((time1, moddepth, pre), *x)),
                            PELDOR_Calculation((time2, moddepth2, pre), *x))))


"""****************************************************************************
                GLOBAL OBJECTIVE FUNCTION WITH SUPPRESSION
****************************************************************************"""


def simplex_errf_global_mult_sup(x, time1, ydata1, time2, ydata2, weighting,
                                 moddepth, supstart, supend, pre=False):
    return (sum(np.power((PELDOR_Calculation_sup((time1, moddepth, supstart,
                                                  supend, pre),
                                                 *x)-ydata1), 2)) +
            weighting*sum(np.power((PELDOR_Calculation_sup((time2, moddepth,
                                    supstart, supend, pre), *x)-ydata2), 2)))


def simplex_errf_global_tri_sup(x, time1, ydata1, time2, ydata2, weighting,
                                moddepth, supstart, supend, pre=False):
    return (sum(np.power((PELDOR_Calculation_TriModal_sup((time1, moddepth,
            supstart, supend, pre), *x)-ydata1), 2))+weighting *
            sum(np.power((PELDOR_Calculation_TriModal_sup((time2, moddepth,
                         supstart, supend, pre), *x)-ydata2), 2)))


def PELDOR_Calculation_TriModal_global_sup(args, *x):
    time1 = args[0]
    time2 = args[1]
    moddepth = args[3]
    moddepth2 = np.sqrt(args[2])*args[3]
    supstart = args[4]
    supend = args[5]
    pre = args[6]
    return (np.concatenate(((PELDOR_Calculation_TriModal_sup((time1, moddepth,
                            supstart, supend, pre), *x)),
                            PELDOR_Calculation_TriModal_sup((time2, moddepth2,
                                                             supstart, supend,
                                                             pre), *x))))


def PELDOR_Calculation_Mult_global_sup(args, *x):
    time1 = args[0]
    time2 = args[1]
    moddepth = args[3]
    moddepth2 = np.sqrt(args[2])*args[3]
    supstart = args[4]
    supend = args[5]
    pre = args[6]
    return (np.concatenate(((PELDOR_Calculation_sup((time1, moddepth, supstart,
                                                     supend, pre), *x)),
                            PELDOR_Calculation_sup((time2, moddepth2, supstart,
                                                    supend, pre), *x))))


"""****************************************************************************
                SUPPRESSION HANDLING FUNCTION
****************************************************************************"""


def suppression_handler(model, dist, coef, sigma_tmp, supstart, supend):
    if model == 1:
        sigma = np.ones(len(dist))*sigma_tmp
    else:
        sigma = sigma_tmp
    for k in range(0, len(dist)):
        if dist[k] < dist_lb:
            dist[k] = dist_lb+0.01
        if dist[k] > dist_ub:
            dist[k] = dist_ub-0.01
        if dist[k]-2.5*sigma[k] < supend and dist[k]+2.5*sigma[k] > supstart:
            coef[k] = 0.0
    coef = coef/(sum(np.abs(coef))+0.00001)
    return dist, coef, sigma_tmp


"""****************************************************************************
                INITIAL PARAMETERS, BOUNDARIES, PARAM-CONVERSION
****************************************************************************"""


def restore_popt(distances, coef, sigma):
    coef = coef/(sum(np.abs(coef))+0.0000000001)
    popt = np.append(np.append(distances, coef), sigma)
    return popt


def throw_in_bounce(model, dist, coeff, sigma_tmp, supend, supstart):
    if model == 1:
        sigma = np.ones(len(dist))*sigma_tmp
    else:
        sigma = sigma_tmp
    for i in range(0, len(dist)):
        if dist[i]-2.5*sigma[i] < supend and dist[i]+2.5*sigma[i] > supstart:
            if abs(dist[i]-supend) > abs(dist[i]-supstart):
                dist[i] = supstart-2.6*sigma[i]
                if dist[i] < dist_lb:
                    dist[i] = supend+2.6*sigma[i]
            else:
                dist[i] = supend+2.6*sigma[i]
                if dist[i] > dist_ub:
                    dist[i] = supstart-2.6*sigma[i]
        if dist[i] < dist_lb:
            dist[i] = dist_lb+0.01
        if dist[i] > dist_ub:
            dist[i] = dist_ub-0.01
    init = np.append(np.append(dist, coeff), sigma_tmp)
    return init


def make_boundaries(k, model):
    bounds_coeff_down = np.zeros(k)
    bounds_coeff_up = np.ones(k)
    bounds_distances_down = np.ones(k)*dist_lb
    bounds_distances_up = np.ones(k)*dist_ub
    if model == 2:
        bounds_sigma_down = np.ones(k)*sigma_lb
        bounds_sigma_up = np.ones(k)*sigma_ub
    elif model == 1:
        bounds_sigma_down = sigma_lb
        bounds_sigma_up = sigma_ub
    boundaries_down = np.append(np.append(bounds_distances_down,
                                          bounds_coeff_down),
                                bounds_sigma_down)
    boundaries_up = np.append(np.append(bounds_distances_up,
                                        bounds_coeff_up), bounds_sigma_up)
    boundaries = np.array([boundaries_down, boundaries_up])
    return boundaries


def make_init(k, model, popt_best_F_test=0):
    if model == 2:
        if k == 4:
            distances_in = np.linspace(1.8, 6, k, endpoint=True)
            coef_in = np.ones(k)-0.5
            coef_in[k-1] = coef_in[k-1]-0.01
            sigma_in = np.zeros(k)+0.12

        else:
            popt_best_F_test_tmp = popt_best_F_test
            while True:
                number = len(popt_best_F_test_tmp)//3
                coeff_tmp = popt_best_F_test_tmp[number:2*number]
                sigma_tmp = popt_best_F_test_tmp[2*number:3*number]
                dist_tmp = popt_best_F_test_tmp[0:number]
                ind = np.argmin(coeff_tmp)
                distances_in = np.delete(dist_tmp, ind)
                sigma_in = np.delete(sigma_tmp, ind)
                coef_in = np.delete(coeff_tmp, ind)
                popt_best_F_test_tmp = np.append(np.append(distances_in,
                                                           coef_in), sigma_in)
                if len(sigma_in) == k:
                    break
    else:
        if k == 5:
            distances_in = np.linspace(1.8, 6, k, endpoint=True)
            coef_in = np.ones(k)-0.5
            coef_in[k-1] = coef_in[k-1]-0.01
            sigma_in = 0.12
        else:
            popt_best_F_test_tmp = popt_best_F_test
            while True:
                number = (len(popt_best_F_test_tmp)-1)//2
                coeff_tmp = popt_best_F_test_tmp[number:2*number]
                sigma_tmp = popt_best_F_test_tmp[-1]
                dist_tmp = popt_best_F_test_tmp[0:number]
                ind = np.argmin(coeff_tmp)
                distances_in = np.delete(dist_tmp, ind)
                sigma_in = sigma_tmp
                coef_in = np.delete(coeff_tmp, ind)
                popt_best_F_test_tmp = np.append(np.append(distances_in,
                                                           coef_in), sigma_in)
                if len(distances_in) == k:
                    break
    init = np.append(np.append(distances_in, coef_in), sigma_in)
    return init


def convert_init2dist_coeff_sigma(model, init):
    if model == 2:
        number = len(init)//3
        coeff = init[number:2*number]
        sigma = init[2*number:3*number]
        dist = init[0:number]
        for i in range(0, len(sigma)):
            if sigma[i] > 0.4:
                sigma[i] = 0.4
            if sigma[i] < 0.08:
                sigma[i] = 0.08
    else:
        number = (len(init)-1)//2
        coeff = init[number:2*number]
        sigma = init[-1]
        if sigma > sigma_ub:
            sigma = sigma_ub
        if sigma < sigma_lb:
            sigma = sigma_lb
        dist = init[0:number]
    return dist, coeff, sigma


def freq_to_dist(n):
    return np.power(327.0/n, 1.0/3.0)


def dist_to_freq(n):
    return (327.0/np.power(n, 3))


"""****************************************************************************
                 F-TEST (EVALUATION OF GAUSSIAN FUNCTIONS)
****************************************************************************"""


def F_test_preparation_global(model, popt, xdata1, ydata1, xdata2, ydata2,
                              moddepth, popt_best_F_test, lsq_best_F_test,
                              weighting, k=1):
    if model == 2:
        lsq = simplex_errf_global_tri(popt, xdata1, ydata1, xdata2, ydata2,
                                      weighting, moddepth, False)
        first = 4
    else:
        lsq = simplex_errf_global_mult(popt, xdata1, ydata1, xdata2, ydata2,
                                       weighting, moddepth, False)
        first = 5
    if k == first:
        lsq_best_F_test = lsq
        popt_best_F_test = popt
    else:
        len1 = len(xdata1)+len(xdata2)-len(popt)
        len2 = len(xdata1)+len(xdata2)-len(popt_best_F_test)
        dis, coe, sig = convert_init2dist_coeff_sigma(model, popt)
        dis2, coe2, sig2 = convert_init2dist_coeff_sigma(model,
                                                         popt_best_F_test)
        stop = F_test(lsq_best_F_test, lsq, len2, len1, len(dis), len(dis2))
        if stop:
            pass
        else:
            lsq_best_F_test = lsq
            popt_best_F_test = popt
    return lsq_best_F_test, popt_best_F_test


def F_test_preparation(model, popt, xdata, ydata, moddepth, popt_best_F_test,
                       lsq_best_F_test, k=1):
    if model == 2:
        lsq = simple_errf_tri(popt, xdata, ydata, moddepth)
        first = 4
    else:
        lsq = simple_errf(popt, xdata, ydata, moddepth)
        first = 5
    if k == first:
        lsq_best_F_test = lsq
        popt_best_F_test = popt
    else:
        len1 = len(xdata)-len(popt)
        len2 = len(xdata)-len(popt_best_F_test)
        dis, coe, sig = convert_init2dist_coeff_sigma(model, popt)
        dis2, coe2, sig2 = convert_init2dist_coeff_sigma(model,
                                                         popt_best_F_test)
        stop = F_test(lsq_best_F_test, lsq, len2, len1, len(dis), len(dis2))
        if stop:
            pass
        else:
            lsq_best_F_test = lsq
            popt_best_F_test = popt
    return lsq_best_F_test, popt_best_F_test


def F_test(lsq_best_F_test, lsq, len_full, len_red, ngaus, ngaus_accepted,
           p_critical=0.04):
    f_ratio = (((lsq-lsq_best_F_test)/(len_red-len_full)) /
               (lsq_best_F_test/(len_full/4.0)))
    p = stat.f.cdf(f_ratio, len_red/4.0, len_full/4.0)
    if p < p_critical:
        stop = False
        stop_str = "accepted"
    else:
        stop = True
        stop_str = "rejected"
    print("\nNumber of Gaussians in currently accepted/new hypothesis: " +
          str(ngaus_accepted)+"/"+str(ngaus))
    print("P-value (F-Test) ="+str(round(p, 5))+"       (Least-squares: " +
          str(round(lsq_best_F_test, 6))+" vs. "+str(round(lsq, 6))+")")
    print("Hypothesis "+stop_str)
    return stop


def F_test_model_comp(lsq_best_F_test, lsq, len_full, len_red,
                      p_critical=0.04):
    f_ratio = (((lsq-lsq_best_F_test)/(len_red-len_full)) /
               (lsq_best_F_test/(len_full/4.0)))
    p = stat.f.cdf(f_ratio, len_red/4.0, len_full/4.0)
    return p


def printline(adnew=False):
    if adnew:
        print("")
    print("*****************************************************************")
    return


"""****************************************************************************
               STOCHASTIC SAMPLING OF INPUT PARAMETER
****************************************************************************"""


def sample_init(k, model):
    if model == 2:
        distances_in = np.ones(k)*np.random.uniform(low=1.5, high=6.5, size=k)
        coef_in = np.ones(k)*np.random.uniform(low=0.2, high=0.5, size=k)
        sigma_in = np.ones(k)*np.random.uniform(low=0.1, high=0.2, size=k)
    else:
        distances_in = np.ones(k)*np.random.uniform(low=1.5, high=6.5, size=k)
        coef_in = np.ones(k)*np.random.uniform(low=0.2, high=0.5, size=k)
        sigma_in = np.random.uniform(low=0.1, high=0.2, size=1)
    init = np.append(np.append(distances_in, coef_in), sigma_in)
    return init
