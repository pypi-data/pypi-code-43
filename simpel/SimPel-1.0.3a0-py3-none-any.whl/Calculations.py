# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 17:20:25 2016

@author: Stephan Rein

Simulation kernel for PELDOR/DEER data

The program is distributed under a GPLv3 license
For further details see LICENSE.txt

Copyright (c) 2018, Stephan Rein
All rights reserved.
"""

# External libraries
import numpy as np
from scipy.special import fresnel


def calculate_time_trace(frequencies, time, moddepth, trapezoidal, superadap,
                         Jarasbutton, sigmas, userdef, r_usr=None,
                         Pr_usr=None):
    """"

    in:  frequencies        (vector with central distances, given as frequency)
         time               (time vector)
         moddepth           (overall modulation depth)
         trapezoidal        (integration method)
         superadap          (if True then use higher discretization rate)
         Jarasbutton        (object for the progress button)
         sigmas             (vector with standard deviations)
         userdef            (if True use a user defined dist. distribution)
         r_usr              (user defined distance vector)
         Pr_usr             (user defined distance distribution)

    out: spectrum           (PELDOR time trace)
         Fourier            (Fourier transform of the PELDOR time trace)
         Frequency_region   (x-axis of the Fourier transf. of the time trace)
         warning            (warning flag for short distances)

    The function converts the user defined information into a PELDOR time
    trace. Either a Gaussian model is used with up to 5 Gaussian functions,
    or a user-defined distance distribution is passed
    (loaded from a .txt file). The function takes the input and passes all
    information to either the internal_PELDOR_kernel() function or the
    PELDOR_matrix_kernel() function.
    """
    if userdef:
        spectrum = PELDOR_matrix_kernel(r_usr, Pr_usr, time, moddepth)
        warning = False
    else:
        frequencies = np.absolute(frequencies)
        frequencies = np.delete(frequencies, 10)
        freq = frequencies[0::2]
        coef = frequencies[1::2]
        coef = coef/np.sum(coef)
        sigma = max(sigmas)
        spectrum = np.zeros(len(time))
        steps = 19+int(round(sigma*100))
        if superadap:
            steps = steps*3
        if trapezoidal == 2:
            steps = steps*5
        if steps % 2 == 0:
            steps = steps+1
        warning = False
        # Check warning
        x_g = np.zeros((5, steps))
        for number_of_freq in range(0, 5):
            for gstep in range(0, steps):
                x_g[number_of_freq, gstep] = (freq[number_of_freq] +
                                              3.0*sigmas[number_of_freq] -
                                              (3.0*sigmas[number_of_freq] *
                                              (gstep-1.0)) /
                                              ((steps-1.0)/2.0))
                if x_g[number_of_freq, gstep] <= 0:
                    x_g[number_of_freq, gstep] = 1e-8
                    warning = True
        spectrum = internal_PELDOR_kernel(freq, coef, sigmas, moddepth, time,
                                          3, steps)
    # Fourier Decomposition
    stepsize = abs(time[0]-time[1])
    spectrumtmp = spectrum/max(spectrum)
    Fourierim = np.fft.fft(spectrumtmp, 10000)
    Frequency_region = np.fft.fftfreq(len(Fourierim), stepsize*0.001)
    Fourierim = np.fft.fftshift(Fourierim)
    Frequency_region = np.fft.fftshift(Frequency_region)
    Fourier = np.absolute(Fourierim)
    Fourier = Fourier/max(Fourier)
    stepsize = abs(time[0]-time[1])
    return spectrum, Fourier, Frequency_region, warning


def internal_PELDOR_kernel(dist, coef, sigma, moddepth, time, num,
                           steps):
    """
    PELDOR kernel matrix calculation


    Parameters
    ----------
    dist :     :class:`numpy.ndarray`
               Vector with 1-5 central distance(s) in nm.

    coef :     :class:`numpy.ndarray`
               Vector with 1-5 linear coefficients for the Gaussians.

    sigma :    :class:`numpy.ndarray`
               Vector with 1-5 central standard deviations in nm.

    moddepth : :class:`float`
               Modulation depth of the reduced form factor.

    num :      :class:`int`
               Factor for the evaluation ranges of the Gaussians (usually 3).

    steps :    :class:`int`
               Number of points for the discretization of Gaussians.

    Returns
    -------
    signal :   :class:`numpy.ndarray`
               PELDOR intensity vector, also called reduced form factor.

    Notes
    -----
    Kernel function for calculating PELDOR time traces from a distance
    distribution based on a linear combination of Gaussian functions.
    Note that the Fresnel integrals are evaluated by passing
    a three-dimensional array to the scipy.special.fresnel() function.
    """
    time = time/1000
    time_tmp_mat = np.ones((len(dist), steps, len(time)))
    time_tmp_mat = time_tmp_mat*(np.absolute(time))
    try:
        nozero = True
        indext0 = np.argwhere(np.abs(time) < 1e-6)[0][0]
    except:
        nozero = False
    y = np.zeros((steps, len(dist)))
    fr = np.zeros((steps, len(dist)))
    ditr = np.zeros((steps, len(dist)))
    for gau in range(0, len(dist)):
        y = (np.linspace(dist[gau]-num*sigma[gau], dist[gau] +
             num*sigma[gau], steps))
        ditr[:, gau] = np.exp(-0.5*np.power((dist[gau]-y), 2) /
                              (sigma[gau]*sigma[gau]))
        ditr[:, gau] = ditr[:, gau]/np.sum(ditr[:, gau])
        fr[:, gau] = (327.0/np.power(y, 3))
    # Fully vectorized Fresnel integral evaluation
    fi = np.transpose(np.abs(fr)*np.transpose(time_tmp_mat))
    b1 = np.sqrt(6/np.pi)*np.sqrt(fi)
    tmpfresnel = fresnel(b1)
    if nozero:
        b1[:, :, indext0] = 1.0
    integral = np.transpose((np.cos(fi)*tmpfresnel[1]+np.sin(fi) *
                            tmpfresnel[0])/(b1))*coef
    if nozero:
        integral[indext0, :, :] = coef
    signal = np.sum(np.sum((ditr*(integral)), axis=2), axis=1)
    if max(signal) < 1e-20:
        signal += 1e-8
    return (moddepth*(signal/max(signal)))


def PELDOR_matrix_kernel(r_usr, Pr_usr, time, moddepth):
    """
    PELDOR kernel matrix calculation


    Parameters
    ----------
    r_usr:   :class:`numpy.ndarray`
             User defined distance vector

    Pr_us:   :class:`numpy.ndarray`
             User defined distance distribution

    time :   :class:`numpy.ndarray`
             Time vector of the PELDOR trace in ns.

    moddepth : :class:`float`
               Modulation depth, used for the simulation

    Returns
    -------
    signal :     :class:`numpy.ndarray`
            PELDOR kernel matrix.


    Notes
    -----
    Calculates the PELDOR kernel matrix used in Tikhonov regularization
    for constructing a PELDOR time trac from a given distance
    distribution.
    Uses Fresnel integrals to numerically integrate the PELDOR function.
    """
    time = time/1000.0
    kernel = np.zeros((len(time), len(Pr_usr)))
    indext0 = np.argwhere(np.abs(time) < 1e-6)[0][0]
    for i in range(0, len(r_usr)):
        w = (327.0/(np.power(r_usr[i], 3)))
        z = np.sqrt((6*w*np.absolute(time))/np.pi)
        tmpfresnel = fresnel(z)
        kernel[indext0, :] = 1.0
        z[indext0] = 1
        kernel[:, i] = ((np.cos(w*np.absolute(time))/z)*tmpfresnel[1] +
                        (np.sin(w*np.absolute(time))/z)*tmpfresnel[0])
    kernel[indext0][:] = 1.0
    signal = kernel@Pr_usr
    return (moddepth*(signal/max(signal)))


def add_background(spectrum, time, bg_dim, bg_decay, moddepth):
    """
    Calculation of the background function

    Parameters
    ----------
    spectrum ::class:`numpy.ndarray`
               Real intensity vector of the uncorrected PELDOR trace.

    time :    :class:`numpy.ndarray`
              Time vector of the PELDOR trace in ns.

    bg_dim :  :class:`float`
              Background dimension. Can be a fractional between 1 and 6.

    bg_decay : :class:`int`
                Numerical value for a decay constant.

    moddepth : :class:`float`
               Modulation depth, used for the simulation

    Returns
    -------
    popt :    :class:`tuple`
              Tuple with 2 optimized parameters. The first element is the
              value of the determined modulation amplitude, the second
              element is the parameter k of the exponential decay.

    Notes
    -----
    The function uses the standard exponential function to simulate
    the bakcground decay:

        B(t) = (1-lambda)*exp(-k*|t|^(3/dim)) .

    The obtained values for lambda and k are returned.
    """
    spectrum_with_background = np.zeros((len(time)))
    background_decay = np.zeros((len(time)))
    bg_dim = bg_dim/3.0
    spectrum_with_background = ((spectrum+1-moddepth) *
                                np.exp(-np.power(np.absolute(time), (bg_dim)) *
                                bg_decay*0.0001)*moddepth)
    background_decay = ((1-moddepth) *
                        np.exp(-np.power(np.absolute(time), (bg_dim)) *
                        bg_decay*0.0001)*moddepth)
    return (spectrum_with_background, background_decay)


def add_noise(spectrum, noiselevel):
    """

    in:  spectrum                          (PELDOR time trace without noise)
         noiselevel                        (level of the signal-to-noise ratio)

    out: spectrum_with_noise               (PELDOR time trace with noise)
         noisefunction                     (function with additive noise)

    The function adds white noise to an existing PELDOR time trace.
    """
    spectrum_with_noise = np.zeros((len(spectrum)))
    noisefunction = np.zeros((len(spectrum)))
    for i in range(0, len(spectrum)):
        noisefunction[i] = np.random.normal(0, noiselevel)
    spectrum_with_noise = spectrum+noisefunction
    return (spectrum_with_noise, noisefunction)


def calculate_time(timescale, stepsize, t_min):
    time = np.arange(t_min, timescale+stepsize, stepsize)
    return time


def calculate_distance_distr(frequencies, sigmas, configs):
    """
    Calculates the distance distribution as a sum of Gaussian functions

    Parameters
    ----------
    frequencies : :class:`numpy.ndarray`
                  Dipolar frequencies and linear coeffieciens .

    sigmas :    :class:`numpy.ndarray`
                 5 standard deviations for the Gaussians in the distance
                 domain

    configs : :class:`dict`
              User definition of simulation parameters

    Returns
    -------
    Pr :    :class:`numpy.ndarray`
            Distance distribution vector

    r :     :class:`numpy.ndarray`
            Distance vector

    Notes
    -----
    Function that convertes the information about dipolar frequencies (here
    central distances),
    standard deviation and linear coefficients into a distance distribution
    """
    frequencies = np.absolute(frequencies)
    frequencies = np.delete(frequencies, 10)
    freq = frequencies[0::2]
    coef = frequencies[1::2]
    coef = coef/np.sum(coef)
    configs["points"] = int(configs["points"])
    Pr = np.zeros(configs["points"])
    r = np.linspace(configs["r_min"], configs["r_max"], configs["points"],
                    endpoint=True)
    for fr in range(0, 5):
        Pr += (coef[fr]*(1.0/(np.sqrt(2.0*np.pi)*sigmas[fr])) *
               np.exp(-0.5*(np.power((freq[fr]-r)/sigmas[fr], 2))))
    return (Pr, r)
