#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 09:58:57 2017

@author: Stephan Rein

Subfunction for regularization analysis.
Second order Tikhnonov regularization using the discretized second order
derivative operator, First order Thikonov regularization, using the
discretized first order derivative operator as well as a hybrid functional
are available.
Convex optimization (using the cvxopt package and the quadratic programming
solver) is used for minimization of the Tikhonov functional.


The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2017, Stephan Rein, M.Sc., University of Freiburg
2017-12-15
"""

import numpy as np
from scipy.special import fresnel
from numpy import hstack, inf, ndarray, ones
from osqp import OSQP
from scipy.sparse import csc_matrix, vstack
from warnings import warn

cvxoptinstalled = True
try:
    try:
        import cvxopt as cvo
    except ImportError:
        import sys
        systr = "C:\Program Files (x86)\Python\lib\site-packages\cvxopt"
        sys.path.append(systr)
        import cvxopt as cvo
except:
    cvxoptinstalled = False
    pass


global Npoints
Npoints = 130

global Nl
Nl = 20

global DFreq    # Dipolar frequency factor in angular frequencies
DFreq = 52.04*2*np.pi


def regularization(time, spectrum, method=1, L_curve=True, L_number=6,
                   globalana=False, time2=None, spectrum2=None,
                   weight=None, suppression=False, supstart=None,
                   supend=None, Adaptive=False, Large_kernel=False):
    """regularization()

    input: -time: vector (1xM), time vector
           -spectrum: vector (1XM), experimental time trace
           OPTIONAL
           -method: integer (1,2,3), Tikhonov functional choice
           -L_curve: boolean, calculate L-curve if true
           -L_number: integer, L-curve number (Tikhonov without full L-Curve)
           -globalana: boolean, global analysis if set to true
           -time2: vector (1xM2), time vector of data set 2
           -spectrum2: vector (1XM2), experimental time trace of data set 2
           -weight: numeric, weighting factor for global analysis
           -suppression: boolean, enables suppression if set to true
           -supstart: numerci, start of the suppressed region
           -supend: numeric, end of suppressed region in nm
           -Adaptive: boolean, medium size kernel with 261 elements
           -Large_kernel: boolean, large kernel with 521 elements

    output:
           -kdist: vector (1xN), distance vector
           -sol: matrix (NlXN), distance distribution obtained with Tikhonov
           -TT: matrix (NlxM), data set 1 time traces obtained with Tikhonov
           -TT2: matrix (NlxM2), data set 2 time traces obtained with Tikhonov
           -Lcurvex: vector (1xNl), values for the x-axis of the L-curve
           -Lcurvey: vector (1xNl), values for the y-axis of the L-curve

    Main function for regularization of PELDOR time traces. Different
    regularization methods as well as different disretization grids are
    available. Details about the Tikhonov alogrithm are noted in the Tikhonov
    function.

    Regularization:
        -1: Tikhonov with discretized second derivative operator
        -2: Tikhonov with discretized first derivative operator
        -3: Hybrid Tikhonov functional as linear combination of a second
        order derivative operator and a unity matrix

    Kernels:
        -1: 131 points (standard)
        -2: 261 points (adaptive)
        -3: 521 points (large)

    Much optional arguments are due to either suppression of defined
    distance regions or global analysis of two datasets.
    All regularizations are carried out with a solver for convex optimization
    problems implemented in the open source CVXOPT library.

    (c) Stephan Rein, 09.12.2017
    """
    # *************************************************************************
    # User settings for regularization
    # *************************************************************************
    if not cvxoptinstalled:
        print("CVXOPT is not installed! OSQP is used as solver")
    if not Adaptive:
        if not Large_kernel:
            points = Npoints
        else:
            points = Npoints*4
    else:
        points = Npoints*2
    kernel, kdist = kernel_matrix(time, points)
    kernel_tmp = kernel
    if globalana:
        kernel2, kdist = kernel_matrix(time2, points)
        TT2 = np.zeros((len(time2), Nl))
        kernel2_tmp = kernel2
    # Define number of points
    points = len(kdist)
    # Setting Tikhonov differential operators
    diff_mat = second_order_diffential_operator(points)
    diff_mat1 = first_order_diffential_operator(points)
    # Allocate time traces and DD for Nl L-curve values
    TT = np.zeros((len(time), Nl))
    sol = np.zeros((points, Nl))
    # Set temporary used differential operators to final ones
    diff_mat_tmp = diff_mat
    diff_mat_tmp1 = diff_mat1
    # *************************************************************************
    # MAIN LOOP FOR REGULARIZATION (ALWAYS CARRIED OUT WHEN BUTTON PRESSED)
    # *************************************************************************

    if L_curve:
        printline()
        if method == 1:
            print("Using Tikhonov regularization with discretized" +
                  " second order derivative operator")
        elif method == 2:
            print("Using Tikhonov regularization with discretized" +
                  " first order derivative operator")
        elif method == 3:
            print("Using hybrid Tikhonov functional")
        Lcurvex = np.zeros(Nl)
        Lcurvey = np.zeros(Nl)
        alpha_cross = np.zeros(Nl)
        alpha_aic = np.zeros(Nl)
        for k in range(0, Nl):
            if not globalana:
                if method == 1:
                    sol_tmp2, alpha1, alpha2 = Thikonov(kernel_tmp,
                                                        diff_mat_tmp, spectrum,
                                                        k, True)
                elif method == 2:
                    sol_tmp2, alpha1, alpha2 = Thikonov(kernel_tmp,
                                                        diff_mat_tmp1,
                                                        spectrum, k, True)
                elif method == 3:
                    sol_tmp2, fac, alpha1, alpha2 = Hybrid_Thik(kernel_tmp,
                                                                diff_mat_tmp,
                                                                spectrum, k,
                                                                True)
                sol_tmp = np.asarray(sol_tmp2).reshape(points,)
                TT_tmp = 0.5*np.dot(kernel, sol_tmp)
                if method == 1:
                    Lcurvey[k] = np.real(np.log10(np.power(
                                np.linalg.norm(np.dot(diff_mat, sol_tmp)), 2)))
                elif method == 2:
                    Lcurvey[k] = np.real(np.log10(np.power(np.linalg.norm(
                                np.dot(diff_mat1, sol_tmp)), 2)))
                elif method == 3:
                    Lcurvey[k] = np.real(np.log10(np.power(np.linalg.norm(
                            np.absolute(np.dot(diff_mat, sol_tmp))+fac *
                            np.absolute(np.dot(np.eye(points), sol_tmp))), 2)))
                Lcurvex[k] = np.real(np.log10(np.power(np.linalg.norm((
                                    TT_tmp-np.transpose(spectrum))), 2)))
                sol[:, k] = sol_tmp
                TT[:, k] = TT_tmp
            if globalana:
                if method == 1:
                    sol_tmp2, alpha1, alpha2 = Thikonov(kernel, diff_mat_tmp,
                                                        spectrum, k, True,
                                                        True, kernel2_tmp,
                                                        spectrum2, weight)
                elif method == 2:
                    sol_tmp2, alpha1, alpha2 = Thikonov(kernel, diff_mat_tmp1,
                                                        spectrum, k, True,
                                                        True, kernel2_tmp,
                                                        spectrum2, weight)
                elif method == 3:
                    sol_tmp2, fac, alpha1, alpha2 = Hybrid_Thik(kernel,
                                                                diff_mat_tmp,
                                                                spectrum, k,
                                                                True, True,
                                                                kernel2_tmp,
                                                                spectrum2,
                                                                weight)
                sol_tmp = np.asarray(sol_tmp2).reshape(points,)
                TT_tmp = 0.5*np.dot(kernel, sol_tmp)
                TT_tmp2 = 0.5*np.dot(kernel2, sol_tmp)
                if method == 1:
                    Lcurvey[k] = np.real(np.log10(np.power(
                                np.linalg.norm(np.dot(diff_mat, sol_tmp)), 2)))
                elif method == 2:
                    Lcurvey[k] = np.real(np.log10(np.power(np.linalg.norm(
                                np.dot(diff_mat1, sol_tmp)), 2)))
                elif method == 3:
                    Lcurvey[k] = np.real(np.log10(np.power(np.linalg.norm(
                            np.absolute(np.dot(diff_mat, sol_tmp))+fac *
                            np.absolute(np.dot(np.eye(points), sol_tmp))), 2)))
                Lcurvex[k] = np.real(np.log10(np.power(np.linalg.norm(
                          TT_tmp-np.transpose(spectrum))+weight *
                          np.linalg.norm(TT_tmp2-np.transpose(spectrum2)), 2)))
                sol[:, k] = sol_tmp
                TT[:, k] = TT_tmp
                TT2[:, k] = TT_tmp2
            # Values for cross validation and Information criterion
            alpha_cross[k] = alpha1
            alpha_aic[k] = alpha2
        if not globalana:
            return kdist, sol, TT, Lcurvex, Lcurvey, alpha_cross, alpha_aic
        elif globalana:
            return (kdist, sol, TT, TT2, Lcurvex, Lcurvey, alpha_cross,
                    alpha_aic)
    else:
        if not globalana:
            points = len(diff_mat[0, :])
            if method == 1:
                sol2 = Thikonov(kernel_tmp, diff_mat_tmp, spectrum, L_number,
                                False)
            elif method == 2:
                sol2 = Thikonov(kernel_tmp, diff_mat_tmp1, spectrum, L_number,
                                False)
            elif method == 3:
                sol2, fac = Hybrid_Thik(kernel_tmp, diff_mat_tmp,
                                        spectrum, L_number, False)
            TT2 = 0.5*np.dot(kernel, sol2)
            return kdist, np.asarray(sol2).reshape(points,), TT2
        else:
            if method == 1:
                sol2 = Thikonov(kernel, diff_mat_tmp, spectrum, L_number,
                                False, True, kernel2_tmp, spectrum2, weight)
            elif method == 2:
                sol2 = Thikonov(kernel, diff_mat_tmp1, spectrum, L_number,
                                False, True, kernel2_tmp, spectrum2, weight)
            elif method == 3:
                sol2, fac = Hybrid_Thik(kernel, diff_mat_tmp, spectrum,
                                        L_number, False, True, kernel2_tmp,
                                        spectrum2, weight)
            TT2 = 0.5*np.dot(kernel, np.asarray(sol2))
            return kdist, np.asarray(sol2).reshape(points,), TT2


# *****************************************************************************
# SUBFUNCTIONS FOR REGULARIZATION
# *****************************************************************************


def first_order_diffential_operator(points=131):
    """
    Calculates the discrete first derivative operator

    Parameters
    ----------
    points :   :class:`int`
               Number of points in the distance domain.

    Returns
    -------
    D_matrix : :class:`numpy.ndarray`
               Discrete second derivative matrix.

    Notes
    -----
    The function creates the discretized second order derivative operator
    as a matrix (points x points) that may be used in the Tikhonov functional.
    """
    D_matrix = np.eye(points, points)*(1)-np.eye(points, points, k=-1)
    D_matrix = 0.5*D_matrix
    return D_matrix


def second_order_diffential_operator(points=131):
    """
    Calculates the discrete second derivative operator

    Parameters
    ----------
    points :   :class:`int`
               Number of points in the distance domain.

    Returns
    -------
    D_matrix : :class:`numpy.ndarray`
               Discrete second derivative matrix.

    Notes
    -----
    The function creates the discretized second order derivative operator
    as a matrix (points x points) used in the Tikhonov penalty expression.
    """
    D_matrix = (np.eye(points, points)*(-2)+np.eye(points, points, k=-1) +
                np.eye(points, points, k=1))
    return D_matrix


def kernel_matrix(time, points=131):
    """
    PELDOR kernel matrix calculation


    Parameters
    ----------
    time :   :class:`numpy.ndarray`
             Time vector of the PELDOR trace in ns.

    points : :class:`int`
             Number of points in the distance domain.

    Returns
    -------
    K :     :class:`numpy.ndarray`
            PELDOR kernel matrix.

    Kdist : :class:`numpy.ndarray`
            Distance vector used for the distance domain.

    Notes
    -----
    Calculates the PELDOR kernel matrix used in Tikhonov regularization.
    Uses Fresnel integrals to numerically integrate the PELDOR function.
    Currently, the distance domain is fixed to a range of 1.5 < r < 8.0 nm.
    """
    Kdist = np.zeros(points)
    K = np.zeros((len(time), points))
    Kdist = np.linspace(1.5, 8.0, points, endpoint=True)
    time = time/1000.0
    for i in range(0, points):
        w = (DFreq/(np.power(Kdist[i], 3)))
        z = np.sqrt((6*w*time)/np.pi)
        tmpfresnel = fresnel(z)
        K[0, :] = 1.0
        z[0] = 1
        K[:, i] = ((np.cos(w*time)/z)*tmpfresnel[1] +
                   (np.sin(w*time)/z)*tmpfresnel[0])
    K[0][:] = 1.0
    return K, Kdist


def Thikonov(kernel, diff_mat, spectrum, k, do_cross=False, globalana=False,
             kernel2=None, spectrum2=None, weight=None):
    """
    Thikonov(kernel, diff_mat, spectrum,k ,do_cross =False, globalana = False,
             kernel2 = None, spectrum2 = None, weight = None)

    input: REQUIRED
           - kernel:   matrix (NxM), containing the kernel integrals
           - diff_mat: matrix (NxN), with first or second derivative elements
           - spectrum: vector (1xM), experimental data set
           - k: integer, L-Curve number
           OPTIONAL
           - do_cross: boolean, do cross validation
           - globalana: boolean, do global regularization
           - kernel2: matrix (NxM2), second kernel for global regularization
           - spectrum2: vector(1xM2), second experimental data set
           - weight: numeric, weighting factor for global analysis

    output:
           -x: vector (1xN), contains the distance distribution
           -alpha_sel: numeric, value from generalized cross validation
           -alpha_sel2: numeric, value from  AIC criterion

    DESCRIPTION
    The alogithm for Tikhonov regularization with non-negative constraints is
    based on the iterative minimization of the Tikhonov functional with the
    contraint that all elements of the solution has to be >= 0.
    For the description of the algorithm, kernel = K, diffmat = D,
    spectrum = S, 2^k/400.0 = alpha, x = P.

    Algorithm (one dataset):
        1. Calculate P_0 = (K^TK+alpha^2*D^TD)^-1 * K^TS
        2. Set all P_0(i) < 0 elements to zero
        3. Set A = -2*K^TS
        4. Set B = (K^TK+alpha^2*D^TD)
        5. Minimize ||P^TBP+P^TB|| with respect to P as convex optimization
        6. Return the optimal P

     The alogrithm works identical for global analysis. Here a linear
     combination of the functionals is created, weighted with the weighting
     factor.
     """
    points = len(diff_mat)
    if points < Npoints+1:
        s = 2
    elif points < 2*Npoints+2:
        s = 4*2
    else:
        s = 8*4
    lambda_reg = s*np.power(2, k)/400.0
    if not globalana:
        Preresult = (np.dot(np.transpose(kernel), kernel) +
                     (lambda_reg**2)*np.dot(np.transpose(diff_mat), diff_mat))
        Direct_sol = np.dot(np.linalg.inv(Preresult),
                            np.dot(np.transpose(kernel), spectrum))
        Direct_sol = Direct_sol.clip(min=0)
        Bmatrix = Preresult
        Amatrix = -2*np.dot(np.transpose(kernel),
                            np.transpose(spectrum))
    elif globalana:
        Preresult = (np.dot(np.transpose(kernel), kernel) +
                     weight*np.dot(np.transpose(kernel2), kernel2) +
                     (lambda_reg**2)*(1+weight) *
                     np.dot(np.transpose(diff_mat), diff_mat))
        Direct_sol = np.dot(np.linalg.inv(Preresult),
                            (np.dot(np.transpose(kernel), spectrum) +
                            weight*np.dot(np.transpose(kernel2), spectrum2)))
        Bmatrix = Preresult
        Amatrix = -2*(np.dot(np.transpose(kernel),
                             np.transpose(spectrum)) +
                             weight*np.dot(np.transpose(kernel2),
                             np.transpose(spectrum2)))
    Direct_sol = Direct_sol.clip(min=0)
    G = -1000*np.eye(points, points)
    lb = np.zeros(points)
    x = run_solver(Bmatrix, Amatrix, G, lb, Direct_sol, points)
    if not do_cross:
        return x
    else:
        x_tmp = np.asarray(x).reshape(points,)
        TT_tmp = 0.5*np.dot(kernel, x_tmp)
        if not globalana:
            pre = np.linalg.inv(Preresult)@np.transpose(kernel)
            Influennce_mat_tr = np.sum(np.transpose(kernel)*pre)
            lsq_norm = np.linalg.norm((spectrum-TT_tmp))**2
            n = len(spectrum)
            alpha_sel = (lsq_norm)/((1-Influennce_mat_tr/n)**2)
            we = (2*n)/(n-Influennce_mat_tr-1)
            alpha_sel2 = n*np.log(lsq_norm/n)+we*Influennce_mat_tr
        else:
            Preresult1 = (np.dot(np.transpose(kernel), kernel) +
                          (lambda_reg**2)*np.dot(np.transpose(diff_mat),
                          diff_mat))
            Preresult2 = (weight*np.dot(np.transpose(kernel2), kernel2) +
                          (lambda_reg**2)*(1+weight) *
                          np.dot(np.transpose(diff_mat), diff_mat))
            pre1 = np.linalg.inv(Preresult1)@np.transpose(kernel)
            Influennce_mat_tr1 = np.sum(np.transpose(kernel)*pre1)
            pre2 = np.linalg.inv(Preresult2)@np.transpose(kernel2)
            Influennce_mat_tr2 = np.sum(np.transpose(kernel2)*pre2)
            n1 = len(spectrum)
            n2 = len(spectrum2)
            TT_tmp2 = 0.5*np.dot(kernel2, x_tmp)
            lsq_norm1 = np.linalg.norm((spectrum-TT_tmp))**2
            lsq_norm2 = weight*np.linalg.norm((spectrum2-TT_tmp2))**2
            we1 = (2*n1)/(n1-Influennce_mat_tr1-1)
            we2 = (2*n2)/(n2-Influennce_mat_tr2-1)
            alpha_sel = ((lsq_norm1)/((1-Influennce_mat_tr1/n1)**2) +
                         (lsq_norm2)/((1-Influennce_mat_tr2/n2)**2))
            alpha_sel2 = (n1*np.log(lsq_norm1/n1)+we1*Influennce_mat_tr1 +
                          n2*np.log(lsq_norm2/n2)+we2*Influennce_mat_tr2)
        return x, alpha_sel, alpha_sel2


def Hybrid_Thik(kernel, diff_mat, spectrum, k, do_cross=False, globalana=False,
                kernel2=None, spectrum2=None, weight=None):
    """
    Hybrid_Thikonov(kernel, diff_mat, spectrum,k ,do_cross = False,
                    globalana = False, kernel2 = None, spectrum2 = None,
                    weight = None)

    input: REQUIRED
           - kernel:   matrix (NxM), containing the kernel integrals
           - diff_mat: matrix (NxN), with first or second derivative elements
           - spectrum: vector (1xM), experimental data set
           - k: integer, L-Curve number
           OPTIONAL
           - do_cross: boolean, do cross validation
           - globalana: boolean, do global regularization
           - kernel2: matrix (NxM2), second kernel for global regularization
           - spectrum2: vector(1xM2), second experimental data set
           - weight: numeric, weighting factor for global analysis

    output:
           -x: vector (1xN), contains the distance distribution
           -alpha_sel: numeric, value from generalized cross validation
           -alpha_sel2: numeric, value from  AIC criterion

    DESCRIPTION
    Same algorithm as implemented in the Tikhonov function except that
    instead of a single derivative operator a linear combination of a unit
    matrix and a derivative operator is used as functional (hybrid functional)
    """
    points = len(diff_mat)
    lambdafac = 0.2
    if points < Npoints+1:
        s = 1
    elif points < 2*Npoints+2:
        s = 4
        lambdafac = 0.04
    else:
        s = 8
        lambdafac = 0.008
    unity = np.eye(points)
    lambda_reg = s*np.power(2, k)/1000.0
    if not globalana:
        Preresult = (np.dot(np.transpose(kernel), kernel)+(lambda_reg**2) *
                     np.dot(np.transpose(diff_mat), diff_mat)+lambdafac *
                     0.2*(lambda_reg**2)*np.dot(np.transpose(unity), unity))
        Direct_sol = np.dot(np.linalg.inv(Preresult),
                            np.dot(np.transpose(kernel), spectrum))
        Bmatrix = Preresult
        Amatrix = -2*np.dot(np.transpose(kernel),
                            np.transpose(spectrum))
    elif globalana:
        Preresult = (np.dot(np.transpose(kernel), kernel)+weight *
                     np.dot(np.transpose(kernel2), kernel2)+(lambda_reg**2) *
                     (1+weight)*(np.dot(np.transpose(diff_mat), diff_mat) +
                     lambdafac*0.2*np.dot(np.transpose(unity), unity)))
        Direct_sol = np.dot(np.linalg.inv(Preresult),
                            (np.dot(np.transpose(kernel), spectrum) +
                            weight*np.dot(np.transpose(kernel2), spectrum2)))
        Direct_sol = Direct_sol.clip(min=0)
        Bmatrix = Preresult
        Amatrix = -2*(np.dot(np.transpose(kernel),
                      np.transpose(spectrum))+weight *
                      np.dot(np.transpose(kernel2),
                      np.transpose(spectrum2)))
    Direct_sol = Direct_sol.clip(min=0)
    G = -1000*np.eye(points, points)
    lb = np.zeros(points)
    x = run_solver(Bmatrix, Amatrix, G, lb, Direct_sol, points)
    if not do_cross:
        return x, lambdafac*0.2
    else:
        x_tmp = np.asarray(x).reshape(points,)
        TT_tmp = 0.5*np.dot(kernel, x_tmp)
        if not globalana:
            pre = np.linalg.inv(Preresult)@np.transpose(kernel)
            Influennce_mat = kernel@pre
            lsq_norm = np.linalg.norm((spectrum-TT_tmp))**2
            n = len(spectrum)
            alpha_sel = (lsq_norm)/((1-np.trace(Influennce_mat)/n)**2)
            we = (2*n)/(n-np.trace(Influennce_mat)-1)
            alpha_sel2 = n*np.log(lsq_norm/n)+we*np.trace(Influennce_mat)
        else:
            Preresult1 = (np.dot(np.transpose(kernel), kernel) +
                          (lambda_reg**2)*np.dot(np.transpose(diff_mat),
                          diff_mat)+lambdafac*0.2*(lambda_reg**2) *
                          np.dot(np.transpose(unity), unity))
            Preresult2 = (weight*np.dot(np.transpose(kernel2), kernel2) +
                          (lambda_reg**2)*(1+weight) *
                          np.dot(np.transpose(diff_mat), diff_mat)+lambdafac *
                          0.2*(lambda_reg**2)*np.dot(np.transpose(unity),
                          unity))
            pre1 = np.linalg.inv(Preresult1)@np.transpose(kernel)
            Influennce_mat1 = kernel@pre1
            pre2 = np.linalg.inv(Preresult2)@np.transpose(kernel2)
            Influennce_mat2 = kernel2@pre2
            n1 = len(spectrum)
            n2 = len(spectrum2)
            TT_tmp2 = 0.5*np.dot(kernel2, x_tmp)
            lsq_norm1 = np.linalg.norm((spectrum-TT_tmp))**2
            lsq_norm2 = np.linalg.norm((spectrum2-TT_tmp2))**2
            we1 = (2*n1)/(n1-np.trace(Influennce_mat1)-1)
            we2 = (2*n2)/(n2-np.trace(Influennce_mat2)-1)
            alpha_sel = ((lsq_norm1)/((1-np.trace(Influennce_mat1)/n1)**2) +
                         weight *
                         (lsq_norm2)/((1-np.trace(Influennce_mat2)/n2)**2))
            alpha_sel2 = (n1*np.log(lsq_norm1/n1) +
                          we1*np.trace(Influennce_mat1) +
                          n2*np.log(lsq_norm2/n2) +
                          we2*np.trace(Influennce_mat2))
        return x, lambdafac*0.2, alpha_sel, alpha_sel2


def run_solver(Bmatrix, Amatrix, G, lb, Direct_sol, points):
    G = -1000*np.eye(points, points)
    lb = np.zeros(points)
    if cvxoptinstalled:
        Amatrix = cvo.matrix(Amatrix)
        Bmatrix = cvo.matrix(Bmatrix)
        lb = cvo.matrix(lb)
        G = cvo.matrix(G)
        cvo.solvers.options['show_progress'] = False
        x = cvo.solvers.qp(Bmatrix, Amatrix, G, lb,
                           initvals=cvo.matrix(Direct_sol))['x']
    else:
        x = solve_qp(Bmatrix, Amatrix, G, lb, None, None, Direct_sol)
    return x


def Thikonov_direct(kernel, diff_mat, spectrum, k):
    """
    Thikonov(kernel, diff_mat, spectrum, k)

    Direct Tikhonov solution without non-negative constraints. Calculated
    via direct matrix inversion.
    """
    s = 2
    lambda_reg = s*np.power(2, k)/400.0
    Preresult = (np.dot(np.transpose(kernel), kernel) +
                 (lambda_reg**2)*np.dot(np.transpose(diff_mat), diff_mat))
    Direct_sol = np.dot(np.linalg.inv(Preresult),
                        np.dot(np.transpose(kernel), spectrum))
    return Direct_sol


def kernel_matrix_ff(time, maxdist, points):
    """kernel_matrix()

    input:
           -time: (1xn) time vector in ns units
           -maxdist: float, maximal distance in nm
           -points: integer, defines the number of points in the distance dom.

    The function creates a PELDOR kernel matrix for arbitrary time vectors with
    the limitation of nonegative times.
    The distance domain is flexible what is different to the kernel_matrix()
    function.
    """
    kdist = np.zeros(points)
    kernel = np.zeros((len(time), points))
    kdist = np.linspace(1.5, maxdist, points, endpoint=True)
    time = time/1000.0
    for i in range(0, points):
        w = (327.0/(np.power(kdist[i], 3)))
        z = np.sqrt((6*w*time)/np.pi)
        tmpfresnel = fresnel(z)
        kernel[0, :] = 1.0
        z[0] = 1
        kernel[:, i] = ((np.cos(w*time)/z)*tmpfresnel[1] +
                        (np.sin(w*time)/z)*tmpfresnel[0])
    kernel[0][:] = 1.0
    return kernel, kdist


def form_fac_fit(time, spectrum):
    maxdist = abs(np.cbrt(max(time)*1e-3*52.04))*0.6+3
    points = 70
    kernel, kdist = kernel_matrix_ff(time, maxdist, points)
    diff_mat = second_order_diffential_operator(points)
    # Fit_tmp = Thikonov_direct(kernel, diff_mat, spectrum, 5)
    # Fit_final = kernel@Fit_tmp
    Fit = Thikonov(kernel, diff_mat, spectrum, 5)
    Fit_tmp = np.asarray(Fit).reshape(points,)
    Fit_final = 0.5*kernel@Fit_tmp
    lsq = np.sum((Fit_final-spectrum)**2)
    return lsq


def printline(adnew=False):
    if adnew:
        print("")
    print("*****************************************************************")
    return



def solve_qp(P, q, G=None, h=None, A=None, b=None, initvals=None):
    """
    !!!THIS FUNCTION IS COPIED FROM THE QPSOVERS PACKAGE!!!

    Solve a Quadratic Program defined as:

        minimize
            (1/2) * x.T * P * x + q.T * x

        subject to
            G * x <= h
            A * x == b

    using OSQP <https://github.com/oxfordcontrol/osqp>.

    Parameters
    ----------
    P : scipy.sparse.csc_matrix
        Symmetric quadratic-cost matrix.
    q : numpy.array
        Quadratic cost vector.
    G : scipy.sparse.csc_matrix
        Linear inequality constraint matrix.
    h : numpy.array
        Linear inequality constraint vector.
    A : scipy.sparse.csc_matrix, optional
        Linear equality constraint matrix.
    b : numpy.array, optional
        Linear equality constraint vector.
    initvals : numpy.array, optional
        Warm-start guess vector.

    Returns
    -------
    x : array, shape=(n,)
        Solution to the QP, if found, otherwise ``None``.

    Note
    ----
    OSQP requires `P` to be symmetric, and won't check for errors otherwise.
    Check out for this point if you e.g. `get nan values
    <https://github.com/oxfordcontrol/osqp/issues/10>`_ in your solutions.
    """
    l = -inf * ones(len(h))
    if type(P) is ndarray:
        P = csc_matrix(P)
    if A is not None:
        if A.ndim == 1:
            A = A.reshape((1, A.shape[0]))
        qp_A = vstack([G, A]).tocsc()
        qp_l = hstack([l, b])
        qp_u = hstack([h, b])
    else:  # no equality constraint
        if type(G) is ndarray:
            G = csc_matrix(G)
        qp_A = G
        qp_l = l
        qp_u = h
    osqp = OSQP()
    osqp.setup(P=P, q=q, A=qp_A, l=qp_l, u=qp_u, verbose=False)
    if initvals is not None:
        osqp.warm_start(x=initvals)
    res = osqp.solve()
    return res.x