# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 17:35:37 2017

@author: Stephan Rein

Subfunction for pre-processing of experimental time traces

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2017, Stephan Rein, M.Sc., University of Freiburg
"""

import numpy as np
from scipy.optimize import curve_fit


def make_FT(time, normalizedpc):
    """
    make_FT(time, normalizedpc)

    in:  time                 (vector, time vecotr)
         normalizedpc         (vector, normalized and bg correctoed time trace)

    out: Fourier              (Fourier transform of the signal)
         Frequency_region     (Frequency domain axis of the Fourier transform)

    The function calculates the Fourier transform of the background corrected
    and normalized time trace.
    """
    stepsize = abs(time[0]-time[1])
    spectrumtmp = normalizedpc/max(normalizedpc)
    Fourierim = np.fft.fft(spectrumtmp, 10000)
    Frequency_region = np.fft.fftfreq(len(Fourierim), stepsize*0.001)
    Fourierim = np.fft.fftshift(Fourierim)
    Frequency_region = np.fft.fftshift(Frequency_region)
    Fourier = np.absolute(Fourierim)
    Fourier = Fourier/max(Fourier)
    return (Fourier, Frequency_region)


# Normalizing the time trace and zero-time determination
def normalize(cheapreal, cheapimag, time, zerotime=0, boolean=False,
              normfac=0, dozerotime=True):
    """
    normalize(cheapreal, cheapimag, time, zerotime=0, boolean=False,
              normfac=0, dozerotime=True)

    in:  cheapreal             (vector, real part of the time trace)
         cheapimag             (vector, imaginary part of the time trace)
         time                  (vector, time vector)
         zerotime              (value for the "real" zero-time)
         boolean               (boolean value, if true carry out normalization)
         normfac               (float, normalization facotr)
         dozerotime            (boolean, if true do zero-time determination)

    out: normalized_spc        (real part of the normalized PELDOR time trace)
         normalized_imag       (imag. part of the normalized PELDOR time trace)
         zerotime              (determined zero-time)

    The function determines the zero-time as well as the normalizing factor
    by fitting a symmetrical function the time trace about the maximal value
    of the time trace. If the fitting procedure fails the normalization falls
    back to a normalization to the maximum value of the time trace.
    """
    normfac = normfac*0.001
    if boolean:
        try:
            cheapimag = cheapimag/max(cheapreal)
            cheapreal = cheapreal/max(cheapreal)
            if time[0] < -100:
                mintime = -100
                if time[0] < -140 and time[1]-time[0] > 15:
                    mintime = -140
                indices = np.where(time > mintime)[0][0]
                indices2 = np.where(time > abs(mintime))[0][0]
            else:
                mintime = time[0]
                indices = np.where(time > mintime)[0][0]
                indices = 0
                indices2 = np.where(time > abs(mintime))[0][0]
            begtime = time[indices:indices2:1]
            begreal = cheapreal[indices:indices2]

            def fxn_zero_fit(begtime, x0, x2, x3, x4):
                begtime = (begtime/1000.0)
                return (x0-x3*np.power(begtime-x4, 2) *
                        np.exp(np.absolute(begtime-x4)*x2))
            popt, pcov = curve_fit(fxn_zero_fit, begtime,
                                   begreal, (1, 1, 1, 0),
                                   bounds=(-10000, 10000))
            if dozerotime:
                zerotime = round(popt[3]*1000)
            normalized_spc = cheapreal/(popt[0])+normfac
            normalized_imag = cheapimag/(popt[0])
            return normalized_spc, normalized_imag, zerotime
        except:
            normalized_spc = cheapreal/max(cheapreal)+normfac
            normalized_imag = cheapimag/max(cheapreal)
            return normalized_spc, normalized_imag, zerotime


def normalize_Mod(spectrum1, spectrum2, time1, time2):
    """
    normalize_Mod(spectrum1, spectrum2, time1, time2)

    in:  spectrum1       (vector, PELDOR time trace 1)
         spectrum2       (vector, PELDOR time trace 2)
         time1           (vector, time vector 1)
         time2           (vector,  time vector 2)

    out: spectrumorg     (time trace after applying the relative normalization)

    The function carries out a relative normalization of two time traces
    according to their modulation depths. The time trace is streched and
    shifted by a linear factor to reduce the sum of least-squares between
    a zero-line and the difference between the two time traces.
    """
    spectrumorg = spectrum1
    stepsize1 = time1[1]-time1[0]
    stepsize2 = time2[1]-time2[0]
    stepsize = 1
    if stepsize1 < stepsize2:
        stepsize = int(stepsize2/stepsize1)
        spectrum1_tmp = spectrum1[0:len(spectrum1):stepsize]
        spectrum2_tmp = spectrum2[0:len(spectrum1_tmp)]
    elif stepsize1 > stepsize2:
        stepsize = int(stepsize1/stepsize2)
        spectrum2_tmp2 = spectrum2[0:len(spectrum2):stepsize]
        spectrum2_tmp = spectrum2_tmp2[0:len(spectrum1)]
        spectrum1_tmp = spectrum1
    else:
        spectrum2_tmp = spectrum2[0:len(spectrum1)]
        spectrum1_tmp = spectrum1
    zeroline = np.zeros(len(spectrum1_tmp))
    fnorm = max(spectrum1_tmp)

    def fxn_readjustmoddepth(args, x):
        tmp = (x+args[1])
        tmp = (tmp/max(tmp))*args[2]-args[0]
        return tmp
    for i in range(0, 5):
        try:
            popt1, pcov1 = curve_fit(fxn_readjustmoddepth,
                                     (spectrum2_tmp, spectrum1_tmp, fnorm),
                                     zeroline, -0.1, bounds=(-1.0, 1.0))
            spectrumorg = spectrumorg+popt1
            spectrumorg = spectrumorg/max(spectrumorg)
            spectrumorg = spectrumorg*fnorm
            spectrum1_tmp = spectrum1_tmp+popt1
            spectrum1_tmp = spectrum1_tmp/max(spectrum1_tmp)
            spectrum1_tmp = spectrum1_tmp*fnorm
        except:
            pass
    return spectrumorg


def bg_correction(spectrum, time, start, dim=3, exclude_vol=None):
    """
    bg_correction(spectrum, time, start, dim=3, exclude_vol=None)

    in:  spectrum              (vector, PELDOR time trace)
         time                  (vector, time vector)
         start                 (integer,start for background function in ns)
         dim                   (float, background diimension(between 1-6))
         exclude_vol           (integer spherical radius for ex. volume)

    out: popt                  (tuple with obtained paramters for k and lambda)

    The function determines the parameters for the background function needed
    for background correction of the PELDOR signal. The used model function
    is given by:

        B(t) = (1-lambda)*exp(-k*|t|^(3/dim))

    The obtained parameters for lambda and k are returned.
    """
    if exclude_vol is not None:
        dictionary = ditionary_excluded_vol(exclude_vol)
        dim = dictionary
    try:
        time_tmp = [i for i in time if i >= start]
        spectrum_tmp = spectrum[(len(time)-len(time_tmp)):]
    except:
        return

    def fxn_bg_fit(args, lambdaa, k):
        time_tmp = args[0]
        dim = args[1]
        return (1-lambdaa)*np.exp(-(np.power((np.absolute(time_tmp)/1000),
                                  dim/3.0)*k))
    popt, pcov = curve_fit(fxn_bg_fit, (time_tmp, dim), spectrum_tmp,
                           (0.2, 0.3), bounds=(0, 1000000))
    return popt


def bg_correction_fit_dim(spectrum, time, start, dim=3, exclude_vol=None,
                          lamb=0.2, k_init=0.2):
    """
    bg_correction(spectrum, time, start, dim=3, exclude_vol=None)

    in:  spectrum                 (vector, PELDOR time trace)
         time                     (vector, time vector)
         start                    (integer,start for background function in ns)
         dim                      (float, background diimension(between 1-6))
         exclude_vol              (integer spherical radius for ex. volume)
         lamb                     (float, inital value for lambda)
         k_init                   (float, inital value for k)

    out: popt                     (obtained paramters for k, dim and lambda)

    The function determines the parameters for the background function needed
    for background correction of the PELDOR signal. The used model function
    is given by:

        B(t) = (1-lambda)*exp(-k*|t|^(3/dim))

    The obtained parameters for lambda, dim and k are returned.
    """
    if exclude_vol is not None:
        dictionary = ditionary_excluded_vol(exclude_vol)
        dim = dictionary
    try:
        time_tmp = [i for i in time if i >= start]
        spectrum_tmp = spectrum[(len(time)-len(time_tmp)):]
    except:
        return

    def fxn_bg_fit(args, lambdaa, k, dim):
        time_tmp = args[0]
        return (1-lambdaa)*np.exp(-(np.power((np.absolute(time_tmp)/1000),
                                    dim/3.0)*k))
    popt, pcov = curve_fit(fxn_bg_fit, (time_tmp, dim), spectrum_tmp,
                           (lamb, k_init, 3), bounds=(0, 1000000))
    return popt


def bg_subtraction(spectrum, time, popt, zerotime=0, dim=3,
                   globalbg_fun=None, exclude_vol=None):
    """
    bg_subtraction(spectrum, time, popt, zerotime=0, dim=3,
                   globalbg_fun=None, exclude_vol=None)

    in:  spectrum                 (vector, PELDOR time trace)
         time                     (vector, time vector)
         popt                     (tuple,paramters for k and lambda)
         zerotime                 (integer, determined zero-time in ns)
         dim                      (float, background diimension(between 1-6))
         globalbg_fun             (tuple, global values for k and lambda)
         exclude_vol              (integer spherical radius for ex. volume)
         lamb                     (float, inital value for lambda)
         k_init                   (float, inital value for k)

    out: bg_corr                  (background corrected time trace)
         bg_time                  (time vector)
         bg_function              (background function)

    The function subtracts the background function from the time trace
    to extract the dipolar evolution time trace.
    """
    if exclude_vol is not None:
        dictionary = ditionary_excluded_vol(exclude_vol)
        dim = dictionary
    if globalbg_fun is None:
        lambdaa = popt[0]
        k = popt[1]
    else:
        lambdaa = globalbg_fun[0]
        k = globalbg_fun[1]
    try:
        bg_time = [i for i in time if i >= zerotime]
        bg_time = bg_time-min(bg_time)
        spectrum_tmp = spectrum[(len(time)-len(bg_time)):]
    except:
        return

    def fxn_bg_fit(bg_time, lambdaa, k, dim):
        return (1-lambdaa)*np.exp(-(np.power((np.absolute(bg_time)/1000),
                                    dim/3.0)*k))
    bg_corr = (((spectrum_tmp-fxn_bg_fit(bg_time, lambdaa, k, dim)) /
               fxn_bg_fit(bg_time, lambdaa, k, dim))*(1-lambdaa))
    return bg_corr, bg_time, fxn_bg_fit(bg_time, lambdaa, k, dim)


# Automatic zeroth and first order phase correction
def AutomaticPc(real, imag, time, zerotime=0):
    """
    AutomaticPc(real, imag, time, zerotime=0)

    in:  real                 (vector, real part of the PELDOR time trace)
         imag                 (vector, imaginary part of the PELDOR time trace)
         time                 (vector, time vector)
         zerotime             (integer, determined zero-time in ns)

    out: real                 (real part after phase correction)
         imag                 (imaginary part after phase correction)
         order0               (0-th order phase angle in degree)
         order1               (1-th order phase angle in degree)

    The function carries out an automatic 0-th oder phase correction of
    the PELDOR time trace. The 1-th order phase correction is temporarily
    disabled. Therefore the rotation function is given by:

        S(t) = (Re(S(t))+Im(S(t)))*e^(-a*i),

    where a is the phase angle. The signal is rotated in the complex plane
    until the least-square deviation between the imaginary part and a
    zero-line is minimal. If the signal has a phase shift of pi the algorithm
    detects this and rotates the phase corrected signal about 180 degree.
    """
    time_tmp = time[time >= zerotime+len(time)/20]
    real_im = real+1j*imag
    real_im_tmp = real_im[len(time)-len(time_tmp):len(real_im)]
    zeroline = np.zeros(len(time_tmp))

    def fxn_0_orderPC(real_im, k1):
        return np.imag(np.exp(1j*k1)*real_im)

    def fxn_1_orderPC(args, k1):
        return np.imag((np.exp(1j*k1*np.real(args[1]/1000))*args[0])*args[1])
    # 0-Order
    popt0, pcov0 = curve_fit(fxn_0_orderPC, real_im_tmp, zeroline, (0.0),
                             bounds=(-0.2, 0.2))
    real = np.real(np.exp(1j*popt0[0])*real_im)
    imag = np.imag(np.exp(1j*popt0[0])*real_im)
    real_im = real+1j*imag
    real_im_tmp = real_im[len(time)-len(time_tmp):len(real_im)]
    order0 = (popt0[0])*(180.0/np.pi)
    order1 = 0
    if max(abs(real)) == -min(real):
        real *= -1
    return real, imag, order0, order1


def make_distance_dist(dist, coef, sigma, multigaussian=True):
    """
    make_distance_dist(dist, coef, sigma, multigaussian=True)

    in:  dist                      (vector, coefficients for central distances)
         coef                      (vector, linear coefficients)
         sigma                     (vector, standard deviations)
         multigaussian             (boolean, determines which model)

    out: Pr                        (distance distribution vector)
         r                         (distance vector)

    The function creates a distance distribution from the coefficients obtained
    for Gaussian modelling.
    """
    Pr = np.zeros(400)
    r = np.zeros(400)
    r = np.linspace(1.4, 8.1, 400)
    if multigaussian:
        for fr in range(0, len(dist)):
                Dist_tmp = (coef[fr] *
                            np.exp(-0.5*(np.power((dist[fr]-r)/sigma, 2))))
                Pr = Pr+Dist_tmp
        return (Pr, r)
    else:
        r = np.linspace(1.4, 8.1, 400)
        for fr in range(0, len(dist)):
                Dist_tmp = ((1/(sigma[fr]*np.sqrt(2*np.pi)))*coef[fr] *
                            np.exp(-0.5*(np.power((dist[fr]-r)/sigma[fr], 2))))
                Pr = Pr+Dist_tmp
        return (Pr, r)


# Fractional exponentials obtained from fitting Heaviside function for a
# specific excluded volume
def ditionary_excluded_vol(i):
    dictionary = (3.00, 3.00, 3.00, 3.05, 3.29, 3.67, 4.14, 4.58,
                  4.98, 5.26, 5.43, 5.59, 5.68, 5.75, 5.80, 5.83)
    return dictionary[i]
