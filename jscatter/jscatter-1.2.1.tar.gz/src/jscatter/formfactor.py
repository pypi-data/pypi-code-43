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

r"""
**Particle solution**

The scattering of a particle solution with particle concentration :math:`c_p` is

.. math:: I(q)= c_p I_p(q) = c_p I_0 F(q)

In this module the scattering intensity :math:`I_p(q)` of a single particle with
real scattering length densities is calculated in units :math:`nm^2=10^{-14} cm^2`.

If the scattering length density is not defined as e.g. for beaucage model
the normalized particle form factor :math:`F(q)` with :math:`F(q=0)=1` is calculated.

Conversion of single particle scattering :math:`I_p(q)` to particle in solution
(units :math:`\frac{1}{cm}` with :math:`c` in mol/liter) is
:math:`I_{[1/cm]}(q)=N_A \frac{c_p}{1000} 10^{-14} I_{p,[nm^2]}(q)`.

**Particle form factors**

Particle form factor is (:math:`<>` indicates the ensemble average)

.. math:: F(q)=<F_a(q)F^*_a(q)>=<|F_a(q)|^2>

and particle scattering amplitude

.. math:: F_a(q)= \int_V b(r) e^{iqr} \mathrm{d}r  / \int_V b(r) \mathrm{d}r  = \sum_N b_i e^{iqr}  / \sum_N b_i

The forward scattering per particle is

.. math:: I_0=(\int_V b(r) \mathrm{d}r )^2= V_p^2(\rho_{particle}-\rho_{solvent})^2

Here :math:`V_p` is particle volume :math:`\rho` the average scattering length density.

For polymer like particles (e.g. Gaussian chain) of :math:`N` monomers with monomer partial volume
:math:`V_{monomer}` the particle volume is :math:`V_p=N V_{monomer}`.

The solution forward scattering :math:`c_pI_0` can be calculated from the monomer concentration as

.. math:: c_pI_0 = c_p V_p^2(\rho_{particle}-\rho_{solvent})^2 =
                  c_{monomer} N V_{monomer}^2(\rho_{monomer}-\rho_{solvent})^2



The scattering of **arbitrary shaped particles** can be calculated by :py:func:`~.cloudscattering.cloudScattering`
as a cloud of points representing the desired shape.

In the same way **distributions of particles** as e.g. clusters of particles or nanocrystals can be calculated.
Oriented scattering of e.g. oriented nanoclusters can be calculated by
:py:func:`~.cloudscattering.orientedCloudScattering`.

Methods to build clouds of scatterers e.g. a cube decorated with spheres at the corners can be
found in :ref:`Lattice` with examples. The advantage here is that there is no double counted overlap.

**Distribution of parameters**

Experimental data might be influenced by multimodal parameters (like multiple sizes)
or by one or several parameters distributed around a mean value.
See :ref:`Distribution of parameters`

------


Some **scattering length densities** as guide to choose realistic values for SLD and solventSLD :
 - neutron scattering  unit nm\ :sup:`-2`:
    - protonated polyethylene glycol = 0.71e-6 A\ :sup:`-2` = 0.71e-4 nm\ :sup:`-2`
    - protonated polyethylene        =-0.315e-6 A\ :sup:`-2` =-0.315e-4 nm\ :sup:`-2`
    - SiO2                           = 4.185e-6 A\ :sup:`-2` = 4.185e-4 nm\ :sup:`-2`
    - D2O                            = 6.335e-6 A\ :sup:`-2` = 6.335e-4 nm\ :sup:`-2`
    - H2O                            =-0.560e-6 A\ :sup:`-2` =-0.560e-4 nm\ :sup:`-2`
    - protein                        |ap| 2.0e-6 A\ :sup:`-2` |ap| 2.0e-4 nm\ :sup:`-2`
    - gold                           = 4.500e-6 A\ :sup:`-2` = 4.500e-4 nm\ :sup:`-2`

 - Xray scattering  unit nm^-2:
    - polyethylene glycol            = 1.11e-3 nm\ :sup:`-2` = 396 e/nm\ :sup:`3`
    - polyethylene                   = 0.85e-3 nm\ :sup:`-2` = 302 e/nm\ :sup:`3`
    - SiO2                           = 2.25e-3 nm\ :sup:`-2` = 796 e/nm\ :sup:`3`
    - D2O                            = 0.94e-3 nm\ :sup:`-2` = 332 e/nm\ :sup:`3`
    - H2O                            = 0.94e-3 nm\ :sup:`-2` = 333 e/nm\ :sup:`3`
    - protein                        |ap| 1.20e-3 nm\ :sup:`-2` |ap| 430 e/nm\ :sup:`3`
    - gold                           = 13.1e-3 nm\ :sup:`-2` =4662 e/nm\ :sup:`3`

Density SiO2 = 2.65 g/ml quartz; |ap| 2.2 g/ml quartz glass

Return values are dataArrays were useful. To get only Y values use .Y

"""
from __future__ import division

import inspect
import os
import sys
import warnings
import numbers

import numpy as np
import scipy
import scipy.constants as constants
import scipy.integrate
import scipy.special as special

from . import formel
from . import parallel
from . import structurefactor as sf
from .dataarray import dataArray as dA
from .dataarray import dataList as dL
from .cloudscattering import cloudScattering, orientedCloudScattering

_path_ = os.path.realpath(os.path.dirname(__file__))

# variable to allow printout for debugging as if debug:print 'message'
debug = False


def guinier(q, Rg=1, A=1):
    """
    Classical Guinier

    see genGuinier with alpha=0

    Parameters
    ----------
    q :array
    A : float
    Rg : float

    """
    return genGuinier(q, Rg=Rg, A=A, alpha=0)


def genGuinier(q, Rg=1, A=1, alpha=0):
    r"""
    Generalized Guinier approximation for low wavevector q scattering q*Rg< 1-1.3

    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array of float
        Wavevector
    Rg : float
        Radius of gyration in units=1/q
    alpha : float
        Shape [α = 0] spheroid,    [α = 1] rod-like    [α = 2] plane
    A : float
        Amplitudes

    Returns
    -------
    dataArray
        Columns [q,Fq]

    Notes
    -----
    Quantitative analysis of particle size and shape starts with the Guinier approximations.
     - For three-dimensional objects the Guinier approximation is given by
       :math:`I(q) = A e^{-Rg^2q^2/3}`
     - This approximation can be extended also to rod-like and plane objects by
       :math:`I(q) =(\alpha \pi q^{-\alpha})  A e^{-Rg^2q^2/(3-\alpha) }`

    If the particle has one dimension of length L that is much larger than
    the others (i.e., elongated, rod-like, or worm-like), then there is a q
    range such that qR_c < 1 <<  qL, where α = 1.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,300)
     spheroid=js.ff.genGuinier(q, Rg=2, A=1, alpha=0)
     rod=js.ff.genGuinier(q, Rg=2, A=1, alpha=1)
     plane=js.ff.genGuinier(q, Rg=2, A=1, alpha=2)
     p=js.grace()
     p.plot(spheroid,le='sphere')
     p.plot(rod,le='rod')
     p.plot(plane,le='plane')
     p.yaxis(scale='l',min=1e-4,max=1e4)
     p.xaxis(scale='l')
     p.legend(x=0.03,y=0.1)
     #p.save(js.examples.imagepath+'/genGuinier.jpg')

    .. image:: ../../examples/images/genGuinier.jpg
     :align: center
     :width: 50 %
     :alt: genGuinier


    References
    ----------
    .. [1] Form and structure of self-assembling particles in monoolein-bile salt mixtures
           Rex P. Hjelm, Claudio Schteingart, Alan F. Hofmann, and Devinderjit S. Sivia
           J. Phys. Chem., 99:16395--16406, 1995

    """
    q = np.atleast_1d(q)
    if alpha == 0:
        pre = 1
    elif alpha == 1 or alpha == 2:
        pre = alpha * np.pi * q ** -alpha
    else:
        raise TypeError('alpha needs to be in 0,1,2')
    I = pre * A * np.exp(-Rg ** 2 * q ** 2 / (3 - alpha))
    result = dA(np.c_[q, I].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.Rg = Rg
    result.A = A
    result.alpha = alpha
    result.modelname = sys._getframe().f_code.co_name
    return result


def beaucage(q, Rg=1, G=1, d=3):
    r"""
    Beaucage introduced a model based on the polymer fractal model.

    Beaucage used the numerical integration form (Benoit, 1957) although the analytical
    integral form was available [1]_. This is an artificial connection of Guinier and Porod Regime .
    Better use the polymer fractal model [1]_ used in gaussianChain.
    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array
        Wavevector
    Rg : float
        Radius of gyration in 1/q units
    G : float
        Guinier scaling factor, transition between Guinier and Porod
    d : float
        Porod exponent for large wavevectors

    Returns
    -------
    dataArray
        Columns [q,Fq]

    Notes
    -----
    Equation 9+10 in [1]_

    .. math:: I(q) &= G e^{-q^2 R_g^2 / 3.} + C q^{-d} \left[erf(qR_g / 6^{0.5})\right]^{3d}

                C &= \frac{G d}{R_g^d} \left[\frac{6d^2}{(2+d)(2+2d)}\right]^{d / 2.} \Gamma(d/2)

    with the Gamma function :math:`\Gamma(x)` .

    Polymer fractals:

    | d = 5/3    fully swollen chains,
    | d = 2      ideal Gaussian chains and
    | d = 3      globular e.g. collapsed chains. (volume scattering)
    | d = 4      surface scattering at a sharp interface/surface
    | d = 6-dim  rough surface area with a dimensionality dim between 2-3 (rough surface)
    | d < r      mass fractals (eg gaussian chain)

    The Beaucage model is used to analyze small-angle scattering (SAS) data from
    fractal and particulate systems. It models the Guinier and Porod regions with a
    smooth transition between them and yields a radius of gyration and a Porod
    exponent. This model is an approximate form of an earlier polymer fractal
    model that has been generalized to cover a wider scope. The practice of allowing
    both the Guinier and the Porod scale factors to vary independently during
    nonlinear least-squares fits introduces undesired artefact's in the fitting of SAS
    data to this model.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,5,300)
     d2=js.ff.beaucage(q, Rg=2, d=2)
     d3=js.ff.beaucage(q, Rg=2, d=3)
     d4=js.ff.beaucage(q, Rg=2,d=4)
     p=js.grace()
     p.plot(d2,le='d=2 gaussian chain')
     p.plot(d3,le='d=3 globular')
     p.plot(d4,le='d=4 sharp surface')
     p.yaxis(scale='l',min=1e-4,max=5)
     p.xaxis(scale='l')
     p.legend(x=0.15,y=0.1)
     #p.save(js.examples.imagepath+'/beaucage.jpg')

    .. image:: ../../examples/images/beaucage.jpg
     :align: center
     :width: 50 %
     :alt: beaucage



    .. [1] Analysis of the Beaucage model
            Boualem Hammouda  J. Appl. Cryst. (2010). 43, 1474–1478
            http://dx.doi.org/10.1107/S0021889810033856

    """
    q = np.atleast_1d(q)
    Rg = float(Rg)
    C = G * d / Rg ** d * (6 * d ** 2 / ((2. + d) * (2. + 2. * d))) ** (d / 2.) * special.gamma(d / 2.)
    I = G * np.exp(-q ** 2 * Rg ** 2 / 3.) + C / q ** d * (special.erf(q * Rg / 6 ** 0.5)) ** (3 * d)
    I[q == 0] = 1
    result = dA(np.c_[q, I].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.GuinierScalingfactor = G
    result.GuinierDimension = d
    result.Rg = Rg
    result.modelname = sys._getframe().f_code.co_name
    return result


def guinierPorod3d(q, Rg1, s1, Rg2, s2, G2, dd):
    r"""
    Generalized Guinier-Porod Model with high Q power law with 3 length scales.

    The model represents the most general case containing three Guinier regions [1]_.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/nm
    Rg1 : float
        Radii of gyration for the short size of scattering object in units nm.
    Rg2 : float
        Radii of gyration for the overall size of scattering object in units nm.
    s1 : float
        Dimensionality parameter for the short size of scattering object (s1=1 for a cylinder)
    s2 : float
        dimensionality parameter for the overall size of scattering object (s2=0 for a cylinder)
    G2 : float
        Intensity for q=0.
    dd : float
        Porod exponent

    Returns
    -------
    dataArray
        Columns [q,Iq]
         Iq scattering intensity

    Notes
    -----
    For a cylinder with length L and radius R (see [1]_)
    :math:`R_{g2} = (L^2/12+R^2/2)^{\frac{1}{2}}`  and :math:`R_{g1}=R/\sqrt{2}`


    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     I=js.ff.guinierPorod3d(q,Rg1=1,s1=1,Rg2=10,s2=0,G2=1,dd=4)
     p=js.grace()
     p.plot(I)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.yaxis(scale='l',label='I(q) / a.u.')
     #p.save(js.examples.imagepath+'/guinierPorod3d.jpg')

    .. image:: ../../examples/images/guinierPorod3d.jpg
     :align: center
     :width: 50 %
     :alt: guinierPorod3d

    References
    ----------
    .. [1]  A new Guinier/Porod Model
            B. Hammouda J. Appl. Cryst. (2010) 43, 716-719

    Author M. Kruteva JCNS 2019

    """
    q = np.atleast_1d(q)

    # define parameters for smooth transitions
    Q1 = (1 / Rg1) * ((dd - s1) * (3 - s1) / 2) ** 0.5
    Q2 = ((s1 - s2) / (2 / (3 - s2) * Rg2 ** 2 - 2 / (3 - s1) * Rg1 ** 2)) ** 0.5
    G1 = G2 / (np.exp(-Q2 ** 2 * (Rg1 ** 2 / (3 - s1) - Rg2 ** 2 / (3 - s2))) * Q2 ** (s2 - s1))
    D = G1 * np.exp(-Q1 ** 2 * Rg1 ** 2 / (3 - s1)) * Q1 ** (dd - s1)

    # define functions in different regions
    def _I1_3regions(q):
        res = G2 / q ** s2 * np.exp(-q ** 2 * Rg2 ** 2 / (3 - s2))
        return res

    def _I2_3regions(q):
        res = G1 / q ** s1 * np.exp(-q ** 2 * Rg1 ** 2 / (3 - s1))
        return res

    def _I3_3regions(q):
        res = D / q ** dd
        return res

    I = np.piecewise(q, [q < Q2, (Q2 <= q) & (q < Q1), q >= Q1], [_I1_3regions, _I2_3regions, _I3_3regions])

    result = dA(np.c_[q, I].T)
    result.columnname = 'q; Iq'
    result.setColumnIndex(iey=None)
    result.Rg1 = Rg1
    result.s1 = s1
    result.Rg2 = Rg2
    result.s2 = s2
    result.G1 = G1
    result.G2 = G2
    result.dd = dd
    result.modelname = sys._getframe().f_code.co_name
    return result


def guinierPorod(q, Rg, s, G, dd):
    """
    Generalized Guinier-Porod Model with high Q power law.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/nm
    Rg : float
        Radii of gyration in units nm.
    s : float
        Dimensionality parameter describing the low Q region.
    dd : float
        Porod exponent describing the high Q slope.
    G : float
        intensity

    Returns
    -------
    dataArray
        Columns [q,Iq]
        Iq    scattering intensity

    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     I=js.ff.guinierPorod(q,s=0,Rg=5,G=1,dd=4)
     p=js.grace()
     p.plot(I)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.yaxis(scale='l',label='I(q) / a.u.')
     #p.save(js.examples.imagepath+'/guinierPorod.jpg')

    .. image:: ../../examples/images/guinierPorod.jpg
     :align: center
     :width: 50 %
     :alt: guinierPorod

    References
    ----------
    .. [1]  A new Guinier/Porod Model
            B. Hammouda J. Appl. Cryst. (2010) 43, 716-719


    Author M. Kruteva JCNS 2019
    """
    q = np.atleast_1d(q)

    # define parameters for smooth transitions
    Q1 = (1 / Rg) * ((dd - s) * (3 - s) / 2) ** 0.5
    D = G * np.exp(-Q1 ** 2 * Rg ** 2 / (3 - s)) * Q1 ** (dd - s)

    # define functions in different regions
    def _I1_2regions(q):
        res = G / q ** s * np.exp(-q ** 2 * Rg ** 2 / (3 - s))
        return res

    def _I2_2regions(q):
        res = D / q ** dd
        return res

    I = np.piecewise(q, [q < Q1, q >= Q1], [_I1_2regions, _I2_2regions])

    result = dA(np.c_[q, I].T)
    result.columnname = 'q; Iq'
    result.setColumnIndex(iey=None)
    result.Rg = Rg
    result.s = s
    result.G = G
    result.D = D
    result.dd = dd
    result.modelname = sys._getframe().f_code.co_name
    return result


def _fa_sphere(qr):
    """
    scattering amplitude sphere with catching the zero
    """
    fa = lambda qr: 3 / qr ** 3 * (np.sin(qr) - qr * np.cos(qr))
    return np.piecewise(qr, [qr == 0], [1, fa])


def sphere(q, radius, contrast=1):
    r"""
    Scattering of a single homogeneous sphere.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/nm
    radius : float
        Radius in units nm
    contrast : float, default=1
        Difference in scattering length to the solvent = contrast

    Returns
    -------
    dataArray
        Columns [q,Iq]
        Iq    scattering intensity
        - .I0   forward scattering

    Notes
    -----
    .. math:: I(q)=  4\pi\rho^2V^2\left[\frac{3(sin(qR) - qr cos(qR))}{(qR)^3}\right]^2

    with contrast :math:`\rho` and sphere volume :math:`V=\frac{4\pi}{3}R^3`

    The first minimum of the form factor is at qR=4.493

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,5,300)
     p=js.grace()
     R=3
     sp=js.ff.sphere(q, R)
     p.plot(sp.X*R,sp.Y,li=1)
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1e5)
     p.xaxis(label='qR',scale='l',min=0.1*R,max=5*R)
     p.legend(x=0.15,y=0.1)
     #p.save(js.examples.imagepath+'/sphere.jpg')

    .. image:: ../../examples/images/sphere.jpg
     :align: center
     :width: 50 %
     :alt: sphere


    References
    ----------
    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955).

    """
    R = radius
    qr = np.atleast_1d(q) * R
    f0 = (4 / 3. * np.pi * R ** 3 * contrast) ** 2  # forward scattering q=0
    ffQR = f0 * _fa_sphere(qr) ** 2
    result = dA(np.c_[q, ffQR].T)
    result.columnname = 'q; Iq'
    result.setColumnIndex(iey=None)
    result.radius = radius
    result.I0 = f0
    result.contrast = contrast
    result.modelname = sys._getframe().f_code.co_name
    return result


def sphereFuzzySurface(q, R, sigmasurf, contrast):
    """
    Scattering of a sphere with a fuzzy interface.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/(R units)
    R : float
        The particle radius R represents the radius of the particle
        where the scattering length density profile decreased to 1/2 of the core density.
    sigmasurf : float
        Sigmasurf is the width of the smeared particle surface.
    contrast : float
        Difference in scattering length to the solvent = contrast

    Returns
    -------
    dataArray
        Columns [q, Iq]
        Iq    scattering intensity related to sphere volume.
        - .I0   forward scattering

    Notes
    -----
    The "fuzziness" of the interface is defined by the parameter sigmasurf. The particle
    radius R represents the radius of the particle where the scattering length density profile
    decreased to 1/2 of the core density. sigmasurf is the width of the smeared particle
    surface. The inner regions of the microgel that display a higher density are described by
    the radial box profile extending to a radius of approximately Rbox ~ R - 2(sigma). In
    dilute solution, the profile approaches zero as Rsans ~ R + 2(sigma).

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,5,300)
     p=js.grace()
     sFS=js.ff.sphereFuzzySurface(q, 3, 0.01, 1)
     p.plot(sFS,le='sigmasurf=0.01')
     sFS=js.ff.sphereFuzzySurface(q, 3, 0.5, 1)
     p.plot(sFS,le='sigmasurf=0.3')
     sFS=js.ff.sphereFuzzySurface(q, 3, 1, 1)
     p.plot(sFS,le='sigmasurf=1')
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1e5)
     p.xaxis(label='q / nm\S-1',scale='l')
     p.legend(x=0.15,y=0.1)
     #p.save(js.examples.imagepath+'/sphereFuzzySurface.jpg')

    .. image:: ../../examples/images/sphereFuzzySurface.jpg
     :align: center
     :width: 50 %
     :alt: sphereFuzzySurface


    References
    ----------
    .. [1] M. Stieger, J. S. Pedersen, P. Lindner, W. Richtering, Langmuir 20 (2004) 7283-7292

    """
    q = np.atleast_1d(q)
    f0 = (4 / 3. * np.pi * R ** 3 * contrast) ** 2  # forward scattering q=0

    def _ff(q):
        return f0 * (3 / (q * R) ** 3 * (np.sin(q * R) - q * R * np.cos(q * R)) *
                     np.exp(-sigmasurf ** 2 * q ** 2 / 2.) ) ** 2

    ffQR = np.piecewise(q, [q == 0], [f0, _ff])
    result = dA(np.c_[q, ffQR].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.HsRadius = R
    result.I0 = f0
    result.contrast = contrast
    result.sigmasurf = sigmasurf
    result.modelname = sys._getframe().f_code.co_name
    return result


def sphereGaussianCorona(q, R, Rg, Ncoil, coilequR, coilSLD=0.64e-4, sphereSLD=4.186e-4, solventSLD=6.335e-4, d=1):
    """
    Scattering of a sphere surrounded by gaussian coils as model for grafted polymers on particle e.g. a micelle.

    The additional scattering is uniformly distributed at the surface, which might fail for lower aggregation
    numbers as 1, 2, 3.
    Instead of aggregation number in [1]_ we use sphere volume and a equivalent volume of the gaussian coils.

    Parameters
    ----------
    q: array of float
        Wavevectors in unit 1/nm
    R : float
        Sphere radius in unit nm
    Rg : float
        Radius of gyration of coils in unit nm
    d : float, default 1
        Coils centre located d*Rg away from the sphere surface
    Ncoil : float
        Number of coils at the surface (aggregation number)
    coilequR : float
        Equivalent radius to calc volume of one coil if densely packed as a sphere.
        Needed to calculate absolute scattering of the coil.
    coilSLD : float
        Scattering length density of coil in bulk.  unit nm^-2.
        default hPEG = 0.64*1e-6 A^-2 = 0.64*1e-4 nm^-2
    sphereSLD : float
        Scattering length density of sphere.unit nm^-2.
        default SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of solvent. unit nm^-2.
        default D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2

    Returns
    -------
    dataArray
        Columns [q,Iq]
         - .coilRg
         - .sphereRadius
         - .numberOfCoils
         - .coildistancefactor
         - .coilequVolume
         - .coilSLD
         - .sphereSLD
         - .solventSLD

    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.1,5,100)
     p=js.grace()
     p.plot(js.ff.sphereGaussianCorona(q,4.4,2,30,2))
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1)
     p.xaxis(label='q / nm\S-1',scale='l')
     #p.save(js.examples.imagepath+'/sphereGaussianCorona.jpg')

    .. image:: ../../examples/images/sphereGaussianCorona.jpg
     :align: center
     :width: 50 %
     :alt: sphereGaussianCorona

    Notes
    -----
    The defaults result in a silica sphere with hPEG grafted at the surface in D2O.
     - Rg=N**0.5*b    with N monomers of length b
     - Vcoilsphere=N*monomerVolume=4/3.*np.pi*coilequR**3
     - coilequR=(N*monomerVolume/(4/3.*np.pi))**(1/3.)

    References
    ----------
    .. [1] Form factors of block copolymer micelles with spherical, ellipsoidal and cylindrical cores
           Pedersen J
           Journal of Applied Crystallography 2000 vol: 33 (3) pp: 637-640
    .. [2] Hammouda, B. (1992).J. Polymer Science B: Polymer Physics30 , 1387–1390

    """
    q = np.atleast_1d(q)
    Q = np.where(q == 0, q * 0 + 1e-10, q)
    # scattering amplitude gaussian coil
    cg = coilSLD - solventSLD
    coilVolume = (4 / 3. * np.pi * coilequR ** 3)
    fa_coil = coilVolume * cg * (1 - np.exp(-Rg * Q)) / (Rg * Q)  # fa_coil**2 is Debye function [2]..
    # amplitude sphere
    cs = sphereSLD - solventSLD
    QR = Q * R
    f0 = (4 / 3. * np.pi * R ** 3 * cs)  # forward scattering Q=0
    fa_sphere = f0 * (3 / QR ** 3 * (np.sin(QR) - QR * np.cos(QR)))
    # total scattering from one sphere and N coils
    #  (   fa_sphere + [ fa_coil + fa_coil+.....] )**2
    # sphere scattering
    res = fa_sphere ** 2
    # N * coil scattering
    res += Ncoil * fa_coil ** 2
    # N times interference between one coil and one sphere
    res += 2 * Ncoil * fa_sphere * fa_coil * np.sin(Q * (R + d * Rg)) / (Q * (R + d * Rg))
    # interference between one coils with distance R+d*Rg
    res += Ncoil * (Ncoil - 1) * (fa_coil * np.sin(Q * (R + d * Rg)) / (Q * (R + d * Rg))) ** 2

    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.coilRg = Rg
    result.sphereRadius = R
    result.numberOfCoils = Ncoil
    result.coildistancefactor = d
    result.coilequVolume = coilVolume
    result.coilSLD = coilSLD
    result.sphereSLD = sphereSLD
    result.solventSLD = solventSLD
    result.modelname = sys._getframe().f_code.co_name
    return result


def sphereCoreShellGaussianCorona(q, Rc, Rs, Rg, Ncoil, thicknessCoils, coilSLD=0.64e-4, coreSLD=4.186e-4,
                                  shellSLD=2e-4, solventSLD=6.335e-4, d=1):
    r"""
    Scattering of a core-shell particle surrounded by gaussian coils as model for grafted polymers on particle.

    The model is in analogy to the sphereGaussianCorona replacing the sphere by a core shell particle in [1]_.
    The additional scattering from the coils is uniformly distributed at the surface,
    which might fail for lower aggregation numbers as 1, 2, 3.
    Instead of aggregation number in [1]_ we use volume of the gaussian coils collapsed to the surface.

    Parameters
    ----------
    q: array of float
        Wavevectors in unit 1/nm.
    Rc,Rs : float
        Radius of core and shell in unit nm.
    Rg : float
        Radius of gyration of coils in unit nm.
    d : float, default 1
        Coils centre located d*Rg away from the sphere surface
        This might be equivalent to Rg
    Ncoil : float
        Number of coils at the surface (aggregation number)
    thicknessCoils : float
        Thickness of a layer if all coils collapsed on the surface as additional shell in nm.
        Needed to calculate absolute scattering of the expanded coils.
        The densely packed coil shell volume is :math:`V_{coils}= 4/3\pi((R_{s}+thicknessCoils)^3-R_s^3)` and
        the volume of a single polymer `V_m =V_{coils} / Ncoils`.
    coilSLD : float
        Scattering length density of coil in bulk as if collapsed on surface unit nm^-2.
        default hPEG = 0.64*1e-6 A^-2 = 0.64*1e-4 nm^-2
    coreSLD,shellSLD : float
        Scattering length density of core and shell in unit nm^-2.
        default :
         - core SiO2 =  4.186*1e-4 nm^-2
         - protein coating = 2*1e-4 nm^-2
    solventSLD : float
        Scattering length density of solvent. unit nm^-2.
        default D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2

    Returns
    -------
    dataArray
        Columns [q,Iq]
         - .coilRg
         - .Radii
         - .numberOfCoils
         - .coildistancefactor
         - .coilequVolume
         - .coilSLD
         - .coreshellSLD
         - .solventSLD

    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,500)
     p=js.grace()
     FF=js.ff.sphereCoreShellGaussianCorona(q,8,12,6,20,1.5)
     p.plot(FF,sy=[1,0.2],li=1)
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=10)
     p.xaxis(label='q / nm\S-1',scale='l')
     #p.save(js.examples.imagepath+'/sphereCoreShellGaussianCorona.jpg')

    .. image:: ../../examples/images/sphereCoreShellGaussianCorona.jpg
     :align: center
     :width: 50 %
     :alt: sphereCoreShellGaussianCorona

    Notes
    -----
    The defaults result in a silica sphere with protein coating and with hPEG grafted at the surface in D2O.
     - Rg=N**0.5*b    with N monomers of length b
     - Vcoilsphere=N*monomerVolume=4/3.*np.pi*coilequR**3
     - coilequR=(N*monomerVolume/(4/3.*np.pi))**(1/3.)

    References
    ----------
    .. [1] Form factors of block copolymer micelles with spherical, ellipsoidal and cylindrical cores
           Pedersen J
           Journal of Applied Crystallography 2000 vol: 33 (3) pp: 637-640
    .. [2] Hammouda, B. (1992).J. Polymer Science B: Polymer Physics30 , 1387–1390

    """
    q = np.atleast_1d(q)
    Q = np.where(q == 0, q * 0 + 1e-10, q)
    # scattering amplitude gaussian coil
    cg = coilSLD - solventSLD
    coilVolume = 4 / 3. * np.pi * ((Rs + thicknessCoils) ** 3 - Rs ** 3) / Ncoil
    fa_coil = coilVolume * cg * (1 - np.exp(-Rg * Q)) / (Rg * Q)  # fa_coil**2 is Debye function [2]_ .
    # amplitude core shell
    fa_coreshell = multiShellSphere(q, [Rc, Rs - Rc], [coreSLD, shellSLD], solventSLD=solventSLD)
    fa_coreshell.Y **= 0.5
    # total scattering from one sphere and N coils
    #  (   fa_coreshell + [ fa_coil + fa_coil+.....] )**2
    # core shell scattering
    res = fa_coreshell.Y ** 2
    # N * coil scattering
    res += Ncoil * fa_coil ** 2
    # N times interference between one coil and one sphere
    res += 2 * Ncoil * fa_coreshell.Y * fa_coil * np.sin(Q * (Rs + d * Rg)) / (Q * (Rs + d * Rg))
    # interference between one coils with distance R+d*Rg
    res += Ncoil * (Ncoil - 1) * (fa_coil * np.sin(Q * (Rs + d * Rg)) / (Q * (Rs + d * Rg))) ** 2

    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.coilRg = Rg
    result.Radiii = [Rc, Rs]
    result.numberOfCoils = Ncoil
    result.coildistancefactor = d
    result.coilVolume = coilVolume
    result.coilSLD = coilSLD
    result.coreshellSLD = [coreSLD, shellSLD]
    result.solventSLD = solventSLD
    result.modelname = sys._getframe().f_code.co_name
    return result


def sphereCoreShell(q, Rc, Rs, bc, bs, solventSLD=0):
    """
    Scattering of a spherical core shell particle.

    Parameters
    ----------
    q : float
        Wavevector  in units of 1/(R units)
    Rc,Rs : float
        Radius core and radius of shell
        Rs>Rc
    bc,bs : float
        Contrast to solvent scattering length density of core and shell.
    solventSLD : float, default =0
        Scattering length density of the surrounding solvent.
        If equal to zero (default) then in profile the contrast is given.

    Returns
    -------
    dataArray
        Columns [wavevector ,Iq ]

    Notes
    -----
    Calls multiShellSphere.

    Examples
    --------
    ::

     import jscatter as js
     q=js.loglist(0.01,5,500)
     p=js.grace()
     FF=js.ff.sphereCoreShell(q,6,12,-0.2,1)
     p.plot(FF,sy=[1,0.2],li=1)
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=10)
     p.xaxis(label='q / nm\S-1',scale='l')
     #p.save(js.examples.imagepath+'/sphereCoreShell.jpg')

    .. image:: ../../examples/images/sphereCoreShell.jpg
     :align: center
     :width: 50 %
     :alt: sphereCoreShell

    """
    return multiShellSphere(q, [Rc, Rs - Rc], [bc, bs], solventSLD=solventSLD)


def multiShellSphere(q, shellthickness, shellSLD, solventSLD=0):
    r"""
    Scattering of spherical multi shell particle including linear contrast variation in subshells.

    The results needs to be multiplied with the concentration to get the measured scattering.
    The resulting contrastprofile can be accessed as .contrastprofile

    Parameters
    ----------
    q : array
        Wavevectors to calculate form factor, unit e.g. 1/nm.
    shellthickness : list of float
        Thickness of shells starting from inner most, unit in nm.
        There is no limit for the number of shells.
    shellSLD : list of float or list
        List of scattering length densities of the shells in sequence corresponding to shellthickness. unit in nm**-2
         - Innermost shell needs to be constant shell.
         - If an element of the list is itself a list of SLD values it is interpreted as equal thick subshells
           with linear progress between SLD values in sum giving shellthickness.
           Here any shape can be approximated as sequence of linear pieces.
         - If subshell list has only one float e.g. [1e.4] the second value is the SLD of the following shell.
         - If empty list is given as [] the SLD of the previous and following shells are used as smooth transition.
    solventSLD : float, default=0
        Scattering length density of the surrounding solvent.
        If equal to zero (default) then in profile the contrast is given.
        Unit in 1/nm**2

    Returns
    -------
    dataArray
        Columns [wavevector, Iq]
        Iq                  scattering cross section in units nm**2
         - .contrastprofile     as radius and contrast values at edge points
         - .shellthickness      consecutive shell thickness
         - .shellcontrast       contrast of the shells to the solvent
         - .shellradii          outer radius of the shells
         - .slopes              slope of linear increase of each shell
         - .outerVolume         Volume of complete sphere
         - .I0                  forward scattering for Q=0

    Notes
    -----
    The scattering intensity for a multishell particle with several subshells is

    .. math:: I(q) = \left( \sum_i f_a(q) \right)^2

    The scattering amplitude of a subshell with inner and outer radius :math:`R_{i,o}` is

    .. math:: f_a(q) = 4\pi\int_{R_i}^{R_o} \rho(r) \frac{sin(qr)}{qr}r^2dr

    where we use always the scattering length density difference to the solvent (contrast)
    :math:`\rho(r) = \hat{\rho}(r) - \hat{\rho}_{solvent}`.



    - For **constant scattering length density** :math:`\rho(r) = \rho` we get

      .. math:: f_{a,const}(q) = \frac{4\pi}{3}r^3\rho
                                 \left. \frac{3(sin(qr)-qR cos(qr))}{(qr)^3}\right\rvert_{r=R_i}^{r=R_o}

      with forward scattering contribution

      .. math:: f_{a,const}(q=0) = \frac{4\pi\rho}{3} (R_i^{3} - R_o^{3})

    - For a **linear variation** as :math:`\rho(r)=\Delta\rho(r-R_i)/d + \rho_i` with
      :math:`\Delta\rho=\rho_o-\rho_i` and thickness :math:`d=(R_o-R_i)`
      we may sum a constant subshell as above with :math:`\rho(r)=\rho_i`
      and contribution of the linear increase :math:`\rho(r)=\Delta\rho(r-R_i)/d` resulting in

      .. math:: f_{a,lin}(q) =f_{a,const}(q) + \frac{4\pi\Delta\rho}{d}
                          \left. \frac{(q(2r-R_i))sin(qr)-(q^2r(r-R_i)-2)cos(qr)  }{q^4}
                          \right\rvert_{r=R_i}^{r=R_o}

      with the forward scattering contribution

      .. math:: f_{a,lin}(q=0)= f_{a,const}(q=0) + \frac{\pi \Delta\rho}{3 d}
                              \left(R_{i} - R_{o}\right)^{2} \left(R_{i}^{2} + 2 R_{i} R_{o} + 3 R_{o}^{2}\right)

    - The solution is unstable (digital resolution) for really low QR values, which are set to the I0 scattering.


    Examples
    --------
    Alternating shells with 5 alternating thickness 0.4 nm and 0.6 nm with h2o, d2o scattering contrast in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.05:10:0.01]
     ashell=js.ff.multiShellSphere(x,[0.4,0.6]*5,[-0.56e-4,6.39e-4]*5)
     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[0].plot(ashell)
     p[0].yaxis(label='I(q)',scale='l',min=1e-7,max=0.1)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.05,max=10)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs
     p[1].subtitle('contrastprofile')
     p[0].title('alternating shells')
     #p.save(js.examples.imagepath+'/multiShellSphere.jpg')

    .. image:: ../../examples/images/multiShellSphere.jpg
     :align: center
     :width: 50 %
     :alt: multiShellSphere

    Double shell with exponential decreasing exterior shell to solvent scattering::

     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,d1,d2,e3,sd1,sd2,sol):
        return js.ff.multiShellSphere(q,[d1,d2,e3*3],[sd1,sd2,((sd2-sol)*np.exp(-np.r_[0:3:9j]))+sol],solventSLD=sol)
     dde=doubleexpshells(x,0.5,0.5,1,1e-4,2e-4,0)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(dde)
     p[0].yaxis(scale='l')
     p[1].plot(dde.contrastprofile,li=1) # a contour of the SLDs


    """
    if isinstance(shellSLD, (numbers.Number)): shellSLD = [shellSLD]
    if isinstance(shellthickness, (numbers.Number)): shellthickness = [shellthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))
    Q = np.array(q)
    shelld = []     # list of shellthicknesses
    shelltype = []  # list of types
    SLDs = []       # constant scattering length density of inner radius to outer radius of shell
    Slopes = []     # linear slope from inside to outside of a shell
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, (numbers.Number)):  # a normal constant shell only ffsph will be used
            shelld.append(shellthickness[i])
            shelltype.append(0)
            SLDs.append(sld)
            Slopes.append(0)
        elif shellthickness[i] == 0:
            shelld.append(shellthickness[i])
            shelltype.append(0)
            SLDs.append(sld[0])
            Slopes.append(0)
        else:  # a sphere with lin progress
            if i == 0:
                raise Exception('innermost shell needs to be constant contrast even if it is small!!')
            if len(sld) == 0:  # linear between neighboring shells
                if i == 0:
                    raise Exception('A SLD at zero (first shell) should be defined')
                shelld.append(shellthickness[i])
                shelltype.append(1)
                SLDs.append(shellSLD[i - 1])
                Slopes.append((shellSLD[i + 1] - shellSLD[i - 1]) / shellthickness[i])
            elif len(sld) == 1:  # linear to following with starting value
                shelld.append(shellthickness[i])
                shelltype.append(1)
                SLDs.append(sld[0])
                Slopes.append((shellSLD[i + 1] - sld[0]) / shellthickness[i])
            else:
                shelld.append([shellthickness[i] / (len(sld) - 1)] * (len(sld) - 1))
                shelltype.append([1] * (len(sld) - 1))
                SLDs.append(sld[:-1])
                slda = np.array(sld)
                Slopes.append((slda[1:] - slda[:-1]) / (shellthickness[i] / (len(sld) - 1)))
    SLDs = np.hstack(SLDs)
    shelld = np.hstack(shelld)
    shelltype = np.hstack(shelltype)
    Slopes = np.hstack(Slopes)
    radii = np.cumsum(shelld)

    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD
    #  Volume  *  formfactor

    def ffsph(qr, r):
        # constant profile
        return 4 / 3. * np.pi * r * r * r * 3. * (np.sin(qr) - qr * np.cos(qr)) / qr / qr / qr

    def fflin(q, r, ri):
        # lin profile = drho*(r-Ri)/l
        qr=q[:, None]*r
        q2=q[:, None]**2
        return 4*np.pi/q2**2 * (q[:, None]*(2*r-ri)*np.sin(qr) + q2*r*(ri-r)*np.cos(qr) + 2*np.cos(qr))

    def _ff(QQ, r):
        # outer integration boundary r
        Pc = dSLDs * ffsph(QQ[:, None] * r, r)
        if len(r) > 1:  # subtract lower integration boundary
            # innermost shell has r==0 and is not calculated
            Pc[:, 1:] = Pc[:, 1:] - dSLDs[1:] * ffsph(QQ[:, None] * r[:-1], r[:-1])
        # look at slopes, innermost is not slope
        if len(r) > 1:
            # Ri is r[:-1] Rout is r[1:]
            Pl = Slopes[1:] * fflin(QQ, r[1:], r[:-1])
            # subtract lower integration boundary
            Pl = Pl - Slopes[1:] * fflin(QQ, r[:-1], r[:-1])
            Pc[:, 1:]+=Pl
        return Pc.sum(axis=1) ** 2

    # forward scattering Q=0 -------------
    # constant contribution
    dslds =4 / 3. * np.pi * radii ** 3 * dSLDs
    dslds[:-1] = dslds[:-1] - 4 / 3. * np.pi * radii[:-1] ** 3 * dSLDs[1:]
    # lin contribution
    Ro=radii[1:]
    Ri=radii[:-1]
    slr=np.zeros_like(Slopes)
    slr[1:] =np.pi/3.*Slopes[1:] *(Ri-Ro)**2*(Ri**2+2*Ri*Ro+3*Ro**2)

    f0 = (dslds + slr).sum() ** 2
    # ------------------------------------
    # the calculation shows up to be unstable for really small Qr as the binary resolution shows up in the lin part.
    # therefore we limit it to the f0 value below a threshold; the error is of order 1e-4
    PP = np.piecewise(Q, [Q < 5e-3 / max(radii)], [f0, _ff], radii)
    result = dA(np.c_[q, PP].T)
    result.columnname = 'q; Iq'
    result.shellthickness = shelld
    result.shellcontrast = SLDs
    result.shellradii = radii
    contrastprofile = np.c_[np.r_[radii - shelld, radii], np.r_[SLDs, SLDs + Slopes * shelld]].T
    result.contrastprofile = contrastprofile[:,
                             np.repeat(np.arange(len(SLDs)), 2) + np.tile(np.r_[0, len(SLDs)], len(SLDs))]
    result.slopes = Slopes
    result.outerVolume = 4. / 3 * np.pi * max(radii) ** 3
    result.I0 = f0
    result.shelltype = shelltype
    result.modelname = sys._getframe().f_code.co_name
    return result


def _fqdisc(q, R, D, angle):
    """
    disc form factor amplitude, save for q=0 and q<0 result is zero

    q : wavevectors
    D : thickness of discs , array
    R : Radii of discs, array
    angle : angle between axis and scattering vector q in rad

    q<0 result is zero needed in ellipsoidFilledCylinder

    """
    # deal with possible zero in q
    if isinstance(q, numbers.Number):
        q = np.r_[q]
    result = np.zeros((len(q), len(D)))
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1
    if D[0] > 0 and R[0] > 0:
        fq0 = 2. * np.pi * R ** 2 * D
        fqq = lambda q: fq0 * special.j1(q[:, None] * R * sina) / (q[:, None] * R * sina) * \
                        np.sinc(q[:, None] * D / 2. * cosa / np.pi)
    elif R[0] > 0:
        fq0 = 2. * np.pi * R ** 2 * 1
        fqq = lambda q: fq0 * special.j1(q[:, None] * R * sina) / (q[:, None] * R * sina)
    elif D[0] > 0:
        fq0 = 2. * D
        fqq = lambda q: fq0 * np.sinc(q[:, None] * D / 2. * cosa / np.pi)

    result[np.where(q > 0)[0], :] = fqq(q[np.where(q > 0)])
    result[np.where(q == 0)[0], :] = fq0 * 0.5
    return result


def multiShellDisc(q, radialthickness, shellthickness, shellSLD, solventSLD=0, alpha=None, nalpha=60):
    """
    Multi shell disc in solvent averaged over axis orientations.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    radialthickness : float, all >0
        Radial thickness of disc shells from inner to outer, units nm
        radii r=cumulativeSum(radialthickness)
    shellthickness : list of float or float, all >0
        Thickness of shells from inner to outer, units nm.
        Innermost thickness is only once.
        total thickness = shellthickness[0]+2*cumulativeSum(shellthickness[1:])
    shellSLD : list of float/list
        Scattering length density of shells in nm^-2.
        A shell can be divided in sub shells if instead of a single float a list of floats is given.
        These list values are used as scattering length of equal thickness subshells.
        E.g. [1,2,[3,2,1]] results in the last shell with 3 subshell of equal thickness.
        The sum of subshell thickness is the thickness given in shellthickness. See second example.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    alpha : float, [float,float] , unit rad
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .outerDiscVolume
         - .radii
         - .alpha
         - .discthickness
         - .shellSLD
         - .solventSLD
         - .modelname


    Examples
    --------
    Alternating shells with different thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     ashell=js.ff.multiShellDisc(x,[0.6,0.4]*2,[0.4,0.6]*2,[-0.56e-4,6.39e-4]*2)
     p=js.grace()
     p[0].plot(ashell)
     bshell=js.ff.multiShellDisc(x,2,2,6.39e-4)
     p[0].plot(bshell)
     p[0].yaxis(label='I(q)',scale='l',min=1e-8,max=0.001)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.05,max=10)
     #p.save(js.examples.imagepath+'/multiShellDisc.jpg')

    .. image:: ../../examples/images/multiShellDisc.jpg
     :align: center
     :width: 50 %
     :alt: multiShellDisc

    References
    ----------
    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)


    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    if isinstance(shellSLD, numbers.Number):
        shellSLD = [shellSLD]
    if isinstance(shellthickness, numbers.Number):
        shellthickness = [shellthickness]
    if isinstance(radialthickness, numbers.Number):
        radialthickness = [radialthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))
    Q = np.atleast_1d(q)
    shelld = []  # list of shellthicknesses
    radii = []  # list of radii
    SLDs = []  # constant scattering length density of inner to outer
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, (numbers.Number)):  # a normal constant shell only ffsph will be used
            shelld.append(abs(shellthickness[i]))
            radii.append(abs(radialthickness[i]))
            SLDs.append(sld)
        else:  # a shell with steps
            shelld.append([abs(shellthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            radii.append([abs(radialthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            SLDs.append(sld[:-1])
    SLDs = np.hstack(SLDs)
    shelld = np.cumsum(np.hstack([shelld[0] * 0.5, shelld[1:]]) * 2)
    radii = np.cumsum(np.hstack(radii))
    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD

    # disc scattering amplitude
    _fq = _fqdisc

    def _ff(QQ, R, D, angle):
        # formfactor of a cylinder with orientation angle alpha
        # outer integration boundary r
        QQ0 = np.r_[0, QQ]
        Pc = dSLDs * _fq(QQ0, R, D, angle)
        if len(R) > 1:  # subtract lower integration boundary
            #  r==0 is not calculated
            Pc[:, 1:] = Pc[:, 1:] - dSLDs[1:] * _fq(QQ0, R[:-1], D[:-1], angle)
        # cylinder without cap
        Pc2 = Pc.sum(axis=1) ** 2
        result = dA(np.c_[QQ, Pc2[1:] * np.sin(angle)].T)
        # store the forward scattering
        result.I0 = Pc2[0]
        return result

    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]
    if isinstance(alpha, numbers.Number):
        # single angle
        result = _ff(Q, radii, shelld, alpha)
    else:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        w = np.c_[0:np.pi/2:90j, np.sin(np.r_[0:np.pi/2:90j])].T
        result = formel.parQuadratureFixedGauss(_ff, alpha[0], alpha[1], 'angle', weights=w,
                                                n=nalpha, QQ=Q, R=radii, D=shelld)

    result.outerDiscVolume = np.pi * radii[-1] ** 2 * shelld[-1]
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.radii = radii[-1]
    result.discthickness = shelld
    result.alpha = alpha
    result.shellSLD = shellSLD
    result.solventSLD = solventSLD
    result.modelname = sys._getframe().f_code.co_name
    return result


def disc(q, R, D, SLD, solventSLD=0, alpha=None):
    """
    Disc form factor .

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    R : float
        Radius in nm
    D : float
        Thickness of shell
    SLD,solventSLD : float
        Scattering length density in nm^-2.
    alpha : float, [float,float] , unit rad
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2

    Notes
    -----

    See multiShellCylinder

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    return multiShellCylinder(q, D, [R], [SLD], solventSLD=solventSLD, alpha=alpha)


def cylinder(q, L, radius, SLD=1e-3, solventSLD=0, alpha=None, nalpha=90, h=None):
    r"""
    Cylinder form factor including cap.

    Based on multiShellCylinder (see there for detailed description of parameters).

    Parameters
    ----------
    L : float
        Length in nm.
    radius : float
        Radius in nm.
    h : float
        Cap geometry

    Notes
    -----
    Compared to SASview (5.0) this yields a factor 2 less intensity.
    Correctness can be checked as the forward scattering .I0 is independent of orientation
    and should be equal V² (V is volume) if SLD=1 and solvent SLD=0.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,8,500)
     p=js.grace()
     p.multi(1,2)
     R=2
     for L in [20,40,150]:
         cc=js.ff.cylinder(q,L=L,radius=R)
         p[0].plot(cc,li=-1,sy=0,le='L ={0:.0f} R={1:.1f}'.format(L,R))
     L=60
     for R in [1,2,4]:
         cc=js.ff.cylinder(q,L=L/R**2,radius=R)
         p[1].plot(cc,li=-1,sy=0,le='L ={0:.2f} R={1:.1f}'.format(L/R**2,R))
     p[0].yaxis(label='I(q)',scale='l',min=1e-6,max=10)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.01,max=6)
     p[1].yaxis(label='I(q)',scale='l',min=1e-7,max=1)
     p[1].xaxis(label='q / nm\S-1',scale='l',min=0.01,max=6)
     p[1].text(r'forward scattering I0\n=(SLD*L\xp\f{}R\S2\N)\S2\N = 0.035530',x=0.02,y=0.1)
     p.title('cylinder')
     p[0].legend(x=0.012,y=0.001)
     p[1].legend(x=0.012,y=0.0001)
     #p.save(js.examples.imagepath+'/cylinder.jpg')

    .. image:: ../../examples/images/cylinder.jpg
     :align: center
     :width: 50 %
     :alt: cylinder

    References
    ----------
    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Cylinder.html

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    return multiShellCylinder(q, L, [radius], [SLD], h=h, solventSLD=solventSLD, alpha=alpha, nalpha=nalpha)


def fuzzyCylinder(q, L, radius, sigmasurf, SLD=1e-3, solventSLD=0, alpha=None, nalpha=90):
    """
    Cylinder with a fuzzy surface as in fuzzySphere averaged over axis orientations.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    L : float
        Length of cylinder, units nm.
        L=0 infinite cylinder.
    radius : float
        Radius of the cylinder in nm.
    sigmasurf : float
        Sigmasurf is the width of the smeared particle surface in units nm.
    SLD : float, default about SiO2 in H2O
        Scattering length density of cylinder in nm^-2.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    alpha : float, [float,float], default [0,pi/2]
        Orientation, angle between the cylinder axis and the scattering vector q in units rad.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .cylinderVolume
         - .radius
         - .cylinderLength
         - .alpha
         - .SLD
         - .solventSLD
         - .modelname

    Notes
    -----


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,500)

     p=js.grace()
     for sig in [0.1,0.5,1]:
         fc=js.ff.fuzzyCylinder(q,L=100,radius=5,sigmasurf=sig)
         p[0].plot(fc,le='fuzzy layer sig={0:.1f}'.format(sig))
     cc=js.ff.cylinder(q,L=100,radius=5)
     p.plot(cc,li=[1,1,4],sy=0,le='cylinder')
     p.yaxis(label='I(q)',scale='l',min=1e-4,max=1e2)
     p.xaxis(label='q / nm\S-1',scale='l',min=0.01,max=6)
     p.title('fuzzy cylinder')
     p.legend(x=0.012,y=1)
     #p.save(js.examples.imagepath+'/fuzzyCylinder.jpg')

    .. image:: ../../examples/images/fuzzyCylinder.jpg
     :align: center
     :width: 50 %
     :alt: multiShellCylinder


    References
    ----------
    The models is derived from the fuzzy sphere model.
    Similar is used in for the core in
    .. [1] Lund et al, Soft Matter, 2011, 7, 1491

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    Q = np.atleast_1d(q)
    dSLD = SLD - solventSLD  # contrast

    def _ff(QQ, r, L, angle, sig):
        # formfactor of a cylinder with orientation angle alpha
        QQ0 = np.r_[0, QQ]
        Pc = dSLD * _fqcylinder(QQ0, np.r_[r], L, angle)[:, 0] * np.exp(-sig ** 2 * QQ0 ** 2 / 2.)**2
        result = dA(np.c_[QQ, Pc[1:]**2 ].T)
        # store the forward scattering
        result.I0 = Pc[0]**2
        return result

    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]

    if isinstance(alpha, numbers.Number):
        # single angle
        result = _ff(Q, radius, L, alpha, sig=sigmasurf)
    else:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        w = np.c_[0:np.pi/2:90j, np.sin(np.r_[0:np.pi/2:90j])].T
        result = formel.parQuadratureFixedGauss(_ff, alpha[0], alpha[1], 'angle', weights=w,
                                                n=nalpha, QQ=Q, r=radius, L=L, sig=sigmasurf)

    result.cylinderVolume = np.pi * radius ** 2 * L
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.radius = radius
    result.cylinderLength = L
    result.alpha = alpha
    result.SLD = SLD
    result.solventSLD = solventSLD
    result.sigmasurf=sigmasurf
    result.modelname = sys._getframe().f_code.co_name
    return result


def _fqcylinder(q, r, L, angle):
    """
    cylinder form factor amplitude, save for q=0 and q<0 result is zero

    q : wavevectors
    r : shell thickness , a list or array !!
    L : length of cylinder, L=0 is infinitely long cylinder
    angle : angle between axis and scattering vector q in rad

    q<0 result is zero needed in ellipsoidFilledCylinder

    """
    # deal with possible zero in q
    if isinstance(q, numbers.Number):
        q = np.r_[q]
    result = np.zeros((len(q), len(r)))
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1
    if L > 0 and r[0] > 0:
        fq0 = 2. * np.pi * r ** 2 * L
        fqq = lambda qq: fq0 * special.j1(qq[:, None] * r * sina) / (qq[:, None] * r * sina) * \
                        np.sinc(qq[:, None] * L / 2. * cosa / np.pi)
    elif r[0] > 0:
        fq0 = 2. * np.pi * r ** 2 * 1
        fqq = lambda qq: fq0 * special.j1(qq[:, None] * r * sina) / (qq[:, None] * r * sina)
    elif L > 0:
        fq0 = 2. * L
        fqq = lambda qq: fq0 * np.sinc(qq[:, None] * L / 2. * cosa / np.pi)
    result[np.where(q > 0)[0], :] = fqq(q[np.where(q > 0)])
    result[np.where(q == 0)[0], :] = fq0 * 0.5
    return result


def _fqcylindercap(q, r, L, angle, h, n=21):
    # Equ 1 in Kaya & Souza  J. Appl. Cryst. (2004). 37, 508±509  DOI: 10.1107/S0021889804005709
    # integrate by fixed Gaussian at positions t and weights w
    j1 = special.j1
    x, w = formel._cached_p_roots(n)
    x = np.real(x)
    if isinstance(q, (numbers.Number)):
        q = np.r_[q]
    if angle != 0:
        sina = np.sin(angle)
        cosa = np.cos(angle)
    else:
        sina = 1
        cosa = 1
    R = (h ** 2 + r ** 2) ** 0.5
    lowlimit = -h / R
    uplimit = 1
    t = ((uplimit - lowlimit) * (x[:, None, None] + 1) / 2.0 + lowlimit)  # first axis for x
    result = np.zeros((len(t), len(q), len(r)))
    cap = lambda q: 4 * np.pi * r ** 3 * np.cos(q[:, None] * cosa * (r * t + h + L / 2)) * \
                    (1 - t ** 2) * (j1(q[:, None] * r * sina * (1 - t ** 2) ** 0.5)) / \
                    (q[:, None] * r * sina * (1 - t ** 2) ** 0.5)
    cap0 = 4 * np.pi * r ** 3 * (1 - t ** 2)

    result[:, np.where(q > 0)[0], :] = (uplimit - lowlimit) / 2.0 * cap(q[np.where(q > 0)])
    result[:, np.where(q == 0)[0], :] = (uplimit - lowlimit) / 2.0 * cap0 * 0.5

    # multiply by weight and sum over weights
    return (result * w[:, None, None]).sum(axis=0)


def multiShellCylinder(q, L, shellthickness, shellSLD, solventSLD=0, alpha=None, h=None, nalpha=60, ncap=31):
    """
    Multi shell cylinder with caps in solvent averaged over axis orientations.

    Each shell has a constant SLD and may have a cap with same SLD sequence.
    Caps may be globular (barbell) or small (like lenses).
    For zero length L a lens shaped disc or  a double sphere like shape is recovered.

    Parameters
    ----------
    q : array
        Wavevectors, units 1/nm
    L : float
        Length of cylinder, units nm
        L=0 infinite cylinder if h=None.
    shellthickness : list of float or float, all >0
        Thickness of shells in sequence, units nm.
        radii r=cumulativeSum(shellthickness)
    shellSLD : list of float/list
        Scattering length density of shells in nm^-2.
        A shell can be divided in sub shells if instead of a single float a list of floats is given.
        These list values are used as scattering length of equal thickness subshells.
        E.g. [1,2,[3,2,1]] results in the last shell with 3 subshell of equal thickness.
        The sum of subshell thickness is the thickness given in shellthickness. See second example.
        SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2
    solventSLD : float
        Scattering length density of surrounding solvent in nm^-2.
        D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2
    h : float, default=None
        Geometry of the caps with cap radii R=(r**2+h**2)**0.5
        h is distance of cap center with radius R from the flat cylinder cap and r as radii of the cylinder shells.

        - None No caps, flat ends as default.
        - 0 cap radii equal cylinder radii (same shellthickness as cylinder shells)
        - >0 cap radius larger cylinder radii as barbell
        - <0 cap radius smaller cylinder radii as lens caps
    alpha : float, [float,float] , unit rad
        Orientation, angle between the cylinder axis and the scattering vector q.
        0 means parallel, pi/2 is perpendicular
        If alpha =[start,end] is integrated between start,end
        start > 0, end < pi/2
    nalpha : int, default 30
        Number of points in Gauss integration along alpha.
    ncap : int, default=31
        Number of points in Gauss integration for cap.

    Returns
    -------
    dataArray
        Columns [q ,Iq ]
         - .outerCylinderVolume
         - .Radius
         - .cylinderLength
         - .alpha
         - .shellthickness
         - .shellSLD
         - .solventSLD
         - .modelname
         - .contrastprofile
         - .capRadii

    Notes
    -----
    Multishell of types:
     - flat cap cylinder      L>0, radii>0, h=None
     - lens cap cylinder      L>0, radii>0, h<0
     - globular cap cylinder  L>0, radii>0, h>0
     - lens                   L=0, radii>0, h<0
     - barbell no cylinder    L=0, radii>0, h>0
     - infinite flat disc     L=0. h=None

    .. image:: barbell.png
     :align: center
     :height: 150px
     :alt: Image of barbell

    Compared to SASview this yields a factor 2 less. See :py:func:`~.ff.cylinder`

    Examples
    --------
    Alternating shells with different thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     ashell=js.ff.multiShellCylinder(x,20,[0.4,0.6]*5,[-0.56e-4,6.39e-4]*5)
     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[0].plot(ashell)
     p[0].yaxis(label='I(q)',scale='l',min=1e-7,max=1)
     p[0].xaxis(label='q / nm\S-1',scale='l',min=0.05,max=10)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs
     p[1].subtitle('contrastprofile')
     p[0].title('alternating shells')
     #p.save(js.examples.imagepath+'/multiShellCylinder.jpg')

    .. image:: ../../examples/images/multiShellCylinder.jpg
     :align: center
     :width: 50 %
     :alt: multiShellCylinder

    Double shell with exponential decreasing exterior shell to solvent scattering::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,L,d1,d2,e3,sd1,sd2,sol):
        # The third layer will have 9 subshells with combined thickness of e3.
        # The scattering length decays to e**(-3) in last subshell.
        return js.ff.multiShellCylinder(q,L,[d1,d2,e3],[sd1,sd2,((sd2-sol)*np.exp(-np.r_[0:3:9j])+sol)],solventSLD=sol)
     dde=doubleexpshells(x,10,0.5,0.5,3,1e-4,2e-4,0)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(dde)
     p[1].plot(dde.contrastprofile,li=1) # a contour of the SLDs

    Cylinder with cap::

     x=np.r_[0.1:10:0.01]
     p=js.grace()
     p.title('Comparison of dumbbell cylinder with simple models')
     p.subtitle('thin lines correspond to simple models as sphere and dshell sphere')
     p.plot(js.ff.multiShellCylinder(x,0,[10],[1],h=0),sy=[1,0.5,2],le='simple sphere')
     p.plot(js.ff.sphere(x,10),sy=0,li=1)
     p.plot(js.ff.multiShellCylinder(x,0,[2,1],[1,2],h=0),sy=[1,0.5,3],le='double shell sphere')
     p.plot(js.ff.multiShellSphere(x,[2,1],[1,2]),sy=0,li=1)
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=-5),sy=[1,0.5,4],le='thin lens cap cylinder=flat cap cylinder')
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=None),sy=0,li=[1,2,1],le='flat cap cylinder')
     p.plot(js.ff.multiShellCylinder(x,10,[3],[20],h=-0.5),sy=0,li=[3,2,6],le='thick lens cap cylinder')
     p.yaxis(scale='l')
     p.xaxis(scale='l')
     p.legend(x=0.15,y=0.01)

    References
    ----------
    Single cylinder

    .. [1] Guinier, A. and G. Fournet, "Small-Angle Scattering of X-Rays", John Wiley and Sons, New York, (1955)
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Cylinder.html

    Double cylinder

    .. [3] Use of viscous shear alignment to study anisotropic micellar structure by small-angle neutron scattering,
           J. B. Hayter and J. Penfold J. Phys. Chem., 88:4589--4593, 1984
    .. [4] http://www.ncnr.nist.gov/resources/sansmodels/CoreShellCylinder.html

    Barbell, cylinder with small end-caps, circular lens

    .. [5] Scattering from cylinders with globular end-caps
           Kaya (2004). J. Appl. Cryst. 37, 223-230]     DOI: 10.1107/S0021889804000020
           Scattering from capped cylinders. Addendum
           H. Kaya and Nicolas-Raphael de Souza
           J. Appl. Cryst. (2004). 37, 508-509  DOI: 10.1107/S0021889804005709

    """
    if alpha is None:
        alpha = [0, np.pi / 2]
    if isinstance(shellSLD, (numbers.Number)): shellSLD = [shellSLD]
    if isinstance(shellthickness, (numbers.Number)): shellthickness = [shellthickness]
    if len(shellSLD) != len(shellthickness):
        raise Exception('shellSLD and shellthickness should be of same length but got:%i!=%i'
                        % (len(shellSLD), len(shellthickness)))
    Q = np.atleast_1d(q)
    shelld = []  # list of shellthicknesses
    SLDs = []  # constant scattering length density of inner radius to outer radius of shell
    for i, sld in enumerate(shellSLD):
        if isinstance(sld, (numbers.Number)):  # a normal constant shell only ffsph will be used
            shelld.append(abs(shellthickness[i]))
            SLDs.append(sld)
        else:  # a shell with lin progress
            shelld.append([abs(shellthickness[i]) / (len(sld) - 1)] * (len(sld) - 1))
            SLDs.append(sld[:-1])
    SLDs = np.hstack(SLDs)
    shelld = np.hstack(shelld)
    radii = np.cumsum(shelld)
    # subtract solvent to have in any case the contrast to the solvent
    dSLDs = SLDs - solventSLD

    # cylinder scattering amplitude
    _fq = _fqcylinder
    _fc = _fqcylindercap

    def _ff(QQ, r, L, angle):
        # formfactor of a cylinder with orientation angle alpha
        # outer integration boundary r
        QQ0 = np.r_[0, QQ]
        Pc = dSLDs * _fq(QQ0, r, L, angle)
        if h is not None and np.all(r > 0):
            # calc cap contribution
            Pcap = dSLDs * _fc(QQ0, r, L, angle, h, ncap)
        if len(r) > 1:  # subtract lower integration boundary
            #  r==0 is not calculated
            Pc[:, 1:] = Pc[:, 1:] - dSLDs[1:] * _fq(QQ0, r[:-1], L, angle)
            if h is not None and np.all(r > 0):
                # calc cap contribution
                Pcap[:, 1:] = Pcap[:, 1:] - dSLDs[1:] * _fc(QQ0, r[:-1], L, angle, h, ncap)
        if h is not None and np.all(r > 0):
            # this avoids the infinite thin disc to be added
            if L > 0:
                Pc2 = (Pc + Pcap).sum(axis=1) ** 2
            else:
                Pc2 = Pcap.sum(axis=1) ** 2
        else:
            # cylinder without cap
            Pc2 = Pc.sum(axis=1) ** 2
        result = dA(np.c_[QQ, Pc2[1:]].T)
        # store the forward scattering
        result.I0 = Pc2[0]
        return result

    # test if alpha is angle or range
    if isinstance(alpha, (list, set, tuple)) and alpha[0] == alpha[1]:
        alpha = alpha[0]
    if isinstance(alpha, (numbers.Number)):
        # single angle
        result = _ff(Q, radii, L, alpha)

    else:
        # integrate over range
        alpha[1] = min(alpha[1], np.pi / 2.)
        alpha[0] = max(alpha[0], 0.)
        w = np.c_[0:np.pi/2:90j, np.sin(np.r_[0:np.pi/2:90j])].T
        result = formel.parQuadratureFixedGauss(_ff, alpha[0], alpha[1], 'angle', weights=w,
                                                n=nalpha, QQ=Q, r=radii, L=L)

    result.outerCylinderVolume = np.pi * radii[-1] ** 2 * L
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.Radius = radii[-1]
    result.cylinderLength = L
    result.alpha = alpha
    result.shellthickness = np.abs(shellthickness)
    result.shellSLD = shellSLD
    result.solventSLD = solventSLD
    if h is not None:
        result.capRadii = radii * (1 + h ** 2) ** 0.5
        if h != 0:
            result.capRadii *= np.sign(h)
    contrastprofile = np.c_[np.r_[radii - shelld, radii], np.r_[SLDs, SLDs]].T
    result.contrastprofile = contrastprofile[:,
                             np.repeat(np.arange(len(SLDs)), 2) + np.tile(np.r_[0, len(SLDs)], len(SLDs))]
    result.modelname = sys._getframe().f_code.co_name
    return result

#: incomplete Gamma function
_iG = lambda a, x: special.gamma(a) * special.gammainc(a, x)


def gaussianChain(q, Rg, nu=0.5):
    r"""
    General formfactor of a gaussian polymer chain with excluded volume parameter.

    For nu=0.5 this is the Debye model for Gaussian chain in theta solvent.
    nu>0.5 for good solvents,nu<0.5 for bad solvents.
    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array
        Scattering vector, unit eg  1/A or 1/nm
    Rg : float
        Radius of gyration,  units in 1/unit(q)
    nu : float, default=0.5
        ν is the excluded volume parameter,
        which is related to the Porod exponent d as ν = 1/d and [5/3 <= d <= 3].

    Returns
    -------
    dataArray
        Columns [q,Fq]
         - .radiusOfGyration
         - .nu excluded volume parameter

    Notes
    -----
     - :math:`Rg^2=l^2 N^{2\nu}` with monomer length l and monomer number N.
     - calcs

       .. math:: F(Q) = \frac{1}{\nu U^{\frac{1}{2\nu}}} \gamma_{inc}(\frac{1}{2\nu}, U) -
                        \frac{1}{\nu U^{\frac{1}{\nu}}} \gamma_{inc}(\frac{1}{\nu}, U)

       with :math:`U=(qR_g)^2` and :math:`\gamma_{inc}` as lower incomplete gamma function.
     - The absolute scattering is proportional to :math:`b^2 N^2=b^2 (R_g/l)^{1/\nu}` with monomer number :math:`N`
       and monomer scattering length :math:`b`.
     - From [1]_: "Note that this model describing polymer chains with excluded volume applies only in
       the mass fractal range ([5/3 <= d <= 3]) and does not apply to surface fractals ([3 < d < 4]).
       It does not reproduce the rigid-rod limit (d = 1) because it assumes chain flexibility from the outset,
       nor does it describe semi-flexible chains ([1 < d < 5/3]). "
     - This model should be favoured compared to the Beaucage model as it is not an artificial
       connection between two regimes.


    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,8,100)
     p=js.grace()
     for nu in np.r_[0.3:0.61:0.05]:
        iq=js.ff.gaussianChain(q,2,nu)
        p.plot(iq,le='nu= $nu')
     p.yaxis(label='I(q)',scale='l',min=1e-3,max=1)
     p.xaxis(label='q / nm\S-1',scale='l')
     p.legend(x=0.2,y=0.1)
     p.title('Gaussian chains')
     #p.save(js.examples.imagepath+'/gaussianChain.jpg')

    .. image:: ../../examples/images/gaussianChain.jpg
     :align: center
     :width: 50 %
     :alt: gaussianChain

    References
    ----------
    .. [1] Analysis of the Beaucage model
            Boualem Hammouda  J. Appl. Cryst. (2010). 43, 1474–1478
            http://dx.doi.org/10.1107/S0021889810033856
    .. [2] SANS from homogeneous polymer mixtures: A unified overview.
           Hammouda, B. in Polymer Characteristics 87–133 (Springer-Verlag, 1993). doi:10.1007/BFb0025862


    """

    nu2 = nu * 2.
    q = np.atleast_1d(q)
    U = q ** 2 * Rg ** 2 * (nu2 + 1) * (nu2 + 2) / 6.
    gu = lambda x: 1 / (nu * x ** (1. / nu2)) * _iG(1 / nu2, x) - 1 / (nu * x ** (1. / nu)) * _iG(1 / nu, x)
    res = np.piecewise(U, [U == 0], [1, gu])
    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.radiusOfGyration = Rg
    result.nu = nu
    result.modelname = sys._getframe().f_code.co_name
    return result


def ringPolymer(q, Rg):
    r"""
    General formfactor of a polymer ring in theta solvent.

    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    q : array
        Scattering vector, unit eg  1/A or 1/nm
    Rg : float
        Radius of gyration,  units in 1/unit(q)

    Returns
    -------
    dataArray
        Columns [q,Fq]
         - .radiusOfGyration

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.1,8,100)
     p=js.grace()
     p.multi(1,2)
     iq=js.ff.ringPolymer(q,5)
     p[0].plot(iq)
     p[0].yaxis(scale='l',label='I(q) / a.u.')
     p[0].xaxis(scale='l',label='q / nm\S-1')
     p[1].plot(iq.X,iq.Y*iq.X**2)
     p[1].yaxis(scale='l',label=[r'I(q)q\S2\N / a.u.',1,'opposite'],ticklabel=['power',0,1,'opposite'],min=1e-2,max=0.2)
     p[1].xaxis(scale='l',label='q / nm\S-1')
     p[1].legend(x=0.2,y=0.5)
     p[1].subtitle('Kratky plot')
     p[0].subtitle('ring polymer')
     #p.save(js.examples.imagepath+'/ringPolymer.jpg')

    .. image:: ../../examples/images/ringPolymer.jpg
     :align: center
     :width: 50 %
     :alt: ringPolymer

    References
    ----------
    .. [1] SANS from homogeneous polymer mixtures: A unified overview.
           Hammouda, B. in Polymer Characteristics 87–133 (Springer-Verlag, 1993). doi:10.1007/BFb0025862

    """
    U = q * Rg / 2.
    res = special.dawsn(U) / U
    result = dA(np.c_[q, res].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.radiusOfGyration = Rg
    result.modelname = sys._getframe().f_code.co_name
    return result


def wormlikeChain(q, N, a, R=None, SLD=1, solventSLD=0, rtol=0.02):
    r"""
    Scattering of a wormlike chain, which correctly reproduces the rigid-rod and random-coil limits.

    The forward scattering is :math:`I0=V^2(SLD-solventSLD)^2` with volume :math:`V=\pi R^2 N`.

    Parameters
    ----------
    q : array
        Wavevectors in 1/nm.
    N : float
        Length of the chain in units nm.
        Number of chain segments is N/l=N/(2a). We follow here the notation of [1]_.
    a : float
        Persistence length *a* with Kuhn length l=2a (segment length), units of nm.
    R : float
        Radius in units of nm.
    SLD : float
        Scattering length density segments.
    solventSLD :
        Solvent scattering length density.
    rtol : float
        Maximum relative tolerance in integration.

    Returns
    -------
    dataArray
        Columns [q, Iq]
         - .chainRadius
         - .chainLength
         - .persistenceLength
         - .Rg
         - .volume
         - .contrast

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     p.multi(2,1)
     p.title('figure 3 (2 scaled) of ref Kholodenko Macromolecules 26, 4179 (1993)',size=1)
     q=js.loglist(0.01,10,100)
     for a in [1,2.5,5,20,50,1000]:
         ff=js.ff.wormlikeChain(q,200,a)
         p[0].plot(ff.X,200*ff.Y*ff.X**2,legend='a=%.4g' %ff.persistenceLength)
         p[1].plot(ff.X,ff.Y,legend='a=%.4g' %ff.persistenceLength)
     p[0].legend()
     p[0].yaxis(label=r'Nk\S2\NS(k)')
     p[1].xaxis(label='k',scale='l')
     p[1].yaxis(label='S(k)',scale='l')
     #p.save(js.examples.imagepath+'/wormlikeChain.jpg')

    .. image:: ../../examples/images/wormlikeChain.jpg
     :align: center
     :width: 50 %
     :alt: wormlikeChain

    ::

     p=js.grace()
     p.multi(2,1)
     p.title('figure 4 of ref Kholodenko Macromolecules 26, 4179 (1993)',size=1)
     # fig 4 seems to be wrong scale in [1]_ as for large N with a=1 fig 2 and 4 should have same plateau.
     a=1
     q=js.loglist(0.01,4./a,100)
     for NN in [1,20,50,150,500]:
         ff=js.ff.wormlikeChain(q,NN,a)
         p[0].plot(ff.X*a,NN*a*ff.Y*ff.X**2,legend='N=%.4g' %ff.chainLength)
         p[1].plot(ff.X,ff.Y,legend='a=%.4g' %ff.persistenceLength)
     p[0].legend()
     p[0].yaxis(label=r'(N/a)(ka)\S2\NS(k)')
     p[0].xaxis(label='ka')
     p[1].xaxis(label='k',scale='l')
     p[1].yaxis(label='S(k)',scale='l')

    Notes
    -----
    From [1]_ :
        The Kratky plot (Figure 4 ) is not the most convenient
        way to determine a as was pointed out in ref 20. Figure
        5 provides an alternative way of measuring a by plotting
        the experimentally measurable combination Nk2S(k)
        versus a for fixed wavelength k. As Figure 5 indicates,
        this plot is rather insensitive to the chain length N and
        therefore is universal. The numerical analysis of eq 17
        shows that this remains true for as long as k is not too
        small. Taking into account that the excluded-volume
        effects leave S(k) practically unchanged (e.g., see Figures
        2 and 4 of ref 231, the plot of Figure 5 can serve as a useful
        alternative to the Kratky plot which, in addition, does not
        suffer from the polydispersity effects

    - Rg is calculated according to equ 20 in [2]_ and [3]_.

    References
    ----------
    .. [1] Analytical calculation of the scattering function for polymers of arbitrary
           flexibility using the dirac propagator A. L. Kholodenko, Macromolecules, 26:4179--4183, 1993
    .. [2] The structure factor of a wormlike chain and the random-phase-approximation solution
           for the spinodal line of a diblock copolymer melt Zhang X et. al. Soft Matter 10, 5405 (2014)
    .. [3] Models of Polymer Chains
           Teraoka I. in Polymer Solutions: An Introduction to Physical Properties
           pp: 1-67, New York, John Wiley & Sons, Inc.


    """
    a2 = 2. * float(a)  # Kuhn length
    q = np.atleast_1d(q)  # row vector
    limit = 100  # limit to avoid exp overflow
    x = 3 * N / a2
    z = np.c_[0:x:1000 * 1j]  # column vector

    EF = np.sqrt(np.sign(a2 * q / 3. - 1) * ((a2 * q / 3.) ** 2 - 1))
    EFiszero = (EF == 0)
    EF[EFiszero] = 1  # to avoid EF=0

    # fz is [ z , q ] matrix
    def FZ(qq, zz):
        mfz = np.zeros((zz.shape[0], qq.shape[0]))
        # now fill it
        mfz[(0 < zz) & (zz < limit) & (a2 * qq <= 3)] = (
                np.sinh(zz[(0 < zz) & (zz < limit), None] * EF[None, a2 * qq <= 3]) / np.sinh(
                zz[(0 < zz) & (zz < limit), None]) / EF[None, a2 * qq <= 3]).flatten()
        # for to large zz we avoid expz>limit and use sinh(EF*zz)/sinh(zz)=exp(zz*(Ef-1)) for zz>limit
        mfz[(zz >= limit) & (a2 * qq <= 3)] = (
                np.exp(zz[zz >= limit, None] * (EF[None, a2 * qq <= 3] - 1)) / EF[None, a2 * qq <= 3]).flatten()
        mfz[(0 < zz) & (zz < limit) & (a2 * qq > 3)] = (
                np.sin(zz[(0 < zz) & (zz < limit), None] * EF[None, a2 * qq > 3]) / np.sinh(
                zz[(0 < zz) & (zz < limit), None]) / EF[None, a2 * qq > 3]).flatten()
        # mfz[(zz>limit          ) & (a2*qq >3)] = 0    # default is zero
        # for zz=0  limes is  1 in both cases
        mfz[zz[:, 0] == 0, :] = 1
        if np.any(EFiszero):
            # catch fz  when EF is zero and assigned correct value
            mfz[(0 < zz) & (zz < limit) & EFiszero] = (
                    zz[(0 < zz) & (zz < limit)] / np.sinh(zz[(0 < zz) & (zz < limit)]))
        return mfz

    # integrate I1 and I2 from above matrix
    fz = FZ(q, z)
    I1 = scipy.integrate.simps(fz, z, axis=0)
    I2 = scipy.integrate.simps(fz * z, z, axis=0)
    P0 = 2. / x * (I1 - I2 / x)

    while True:
        # adaptive integration to increase accuracy stepwise
        nz = np.c_[0:x:(2 * len(z) - 1) * 1j]
        nfz = np.zeros((nz.shape[0], q.shape[0]))
        nfz[::2, :] = fz
        nfz[1::2, :] = FZ(q, nz[1::2])  # each second is new element
        I1 = scipy.integrate.simps(nfz, nz, axis=0)
        I2 = scipy.integrate.simps(nfz * nz, nz, axis=0)
        nP0 = 2. / x * (I1 - I2 / x)
        if max(abs(nP0 - P0) / abs(nP0)) < rtol:
            P0 = nP0
            break
        else:
            z = nz
            fz = nfz
            P0 = nP0
    # now do the volume and sld
    if R is not None:
        Pcs = (2 * special.j1(q * R) / q / R) ** 2
        V = np.pi * R * R * N
        sld = SLD - solventSLD
    else:
        Pcs = 1
        R = 0
        V = 1
        sld = 1
    result = dA(np.c_[q, V ** 2 * sld ** 2 * P0 * Pcs].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.chainRadius = R
    result.chainLength = N
    result.persistenceLength = a
    # in [2]_ a is Kuhn length (here a2)
    result.Rg = np.sqrt(
        (a2 * N / 6.) * (1 - 1.5 * a2 / N + 1.5 * (a2 / N) ** 2 - 0.75 * (a2 / N) ** 3 * (1 - np.exp(-2 * N / a2))))
    result.volume = V
    result.contrast = sld
    result.columnname = 'q; Iq'
    result.modelname = sys._getframe().f_code.co_name
    return result


def cuboid(q, a, b=None, c=None, SLD=1, solventSLD=0, N=30):
    r"""
    Formfactor of cuboid with different edge lengths.

    Parameters
    ----------
    q : array
        Wavevector in 1/nm
    a,b,c : float, None
        Edge length, for a=b=c its a cube, Units in nm.
        If b=None b=a.
        If c=None c=b.
    SLD : float, default =1
        Scattering length density of cuboid.unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    N : int
        Order for Gaussian integration over both phi and theta.

    Returns
    -------
    dataArray
        Columns [q,Iq]
         - .I0 forward scattering
         - .edges
         - .contrast

    Notes
    -----

    .. math:: I(q)=\rho^2V_{cube}^2 \int_{0}^{2\pi}\int_{0}^{\pi} \lvert sinc(q_xa/2 )
              sinc(q_yb/2) sinc(q_zc/2)\rvert^2 \sin\theta d\theta d\phi

    with :math:`q = (q_x,q_y,q_z) = (q\sin\theta\cos\phi,q\sin\theta\sin\phi,q\cos\theta)`
    and contrast :math:`\rho` [1]_.

    In [1]_ the edge length is only half of it.

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.1:5:0.01]
     p=js.grace()
     p.plot(js.ff.cuboid(q,60,4,6))
     p.plot(js.ff.cuboid(q,10,4,60))
     p.plot(js.ff.cuboid(q,11,11,11),li=1)
     p.yaxis(scale='l',label='I(q)')
     p.xaxis(scale='l',label='q / nm\S-1')
     p.title('cuboid')
     #p.save(js.examples.imagepath+'/cuboid.jpg')

    .. image:: ../../examples/images/cuboid.jpg
     :width: 50 %
     :align: center
     :alt: cuboid


    References
    ----------
    .. [1] Analysis of small-angle scattering data from colloids and polymer solutions:
           modeling and least-squares fitting
           Pedersen, Jan Skov Advances in Colloid and Interface Science 70, 171 (1997)
           http://dx.doi.org/10.1016/S0001-8686(97)00312-6

    """
    if b is None:
        b = a
    if c is None:
        c = b
    sld = SLD - solventSLD
    V = a * b * c
    q = np.atleast_1d(q)
    sin = np.sin
    cos = np.cos
    sinc = np.sinc
    pi2 = np.pi * 2
    f = lambda q, p, t: (sinc(q * a * sin(t) * cos(p) / pi2) *
                         sinc(q * b * sin(t) * sin(p) / pi2) *
                         sinc(q * c * cos(t) / pi2)) ** 2 * sin(t)

    # integrate by Gauss quadrature rule
    ff = lambda q, t: formel.pQFG(f, 0, np.pi / 2, 'p', q=q, t=t, n=N)
    fff = formel.pQFG(ff, 0, np.pi / 2, 't', q=q, n=N) * 8 / (4 * np.pi)

    I0 = V ** 2 * sld ** 2

    result = dA(np.c_[q, I0 * fff].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = sys._getframe().f_code.co_name
    result.I0 = I0
    result.edges = [a, b, c]
    result.contrast = sld
    return result


def pearlNecklace(Q, N, Rc=None, l=None, A1=None, A2=None, A3=None, ms=None, mr=None, vmonomer=None, monomerlength=None):
    r"""
    Formfactor of a pearl necklace (freely jointed chain of pearls connected by rods)

    The formfactor is normalized to 1.
    For absolute scattering see introduction :ref:`formfactor (ff)`.

    Parameters
    ----------
    Q : array
        Wavevector in nm.
    Rc : float
        Pearl radius in nm.
    N : float
        Number of pearls (homogeneous spheres).
    l : float
        Physical length of the rods in nm
    A1, A2, A3 : float
        Amplitudes of pearl-pearl, rod-rod and pearl-rod scattering.
        Can be calculated with the number of chemical monomers in a pearl ms and rod mr
        (see below for further information)
        If ms and mr are given A1,A2,A3 are calculated from these.
    ms : float, default None
        Number of chemical monomers in each pearl.
    mr : float, default None
        Number of chemical monomers in rod like strings.
    vmonomer : float
        Monomer specific volume :math:`v_0` in cubic nm.
        Used to calculate Rc as :math:`Rc= (\frac{ms v_03}{4\pi})^{1/3}`.
        Increasing vmonomer compard to the bulk simulates swelling due to solvent inclusion.
    monomerlength : float
        Monomer length a in nm to calculate :math:`l=m_r a`.

    Returns
    -------
    dataArray
        Columns [q, Iq]
         - .pearlRadius
         - .A1 = ms²/(M*mr+N*ms)²
         - .A2 = mr²/(M*mr+N*ms)²
         - .A3 = (mr*ms)/(M*mr+N*ms)²
         - .numberPearls N
         - .numberRods M = (N-1) number of rod like strings
         - .mr
         - .ms
         - .stringLength
         - .numberMonomers : :math:`Nm_s + Mm_r`

    Notes
    -----

    Author: L. S. Fruhner, RB, FZJ Juelich 2016

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     q=js.loglist(0.01,5,300)
     p=js.grace()
     for l in [2,20,50]:
         p.plot(js.ff.pearlNecklace(q, Rc=2, N=5, ms=200-l, mr=l,monomerlength=0.1),le='l=$stringLength mr=$mr')
     p.yaxis(scale='l',label='I(q)',min=0.0001)
     p.xaxis(scale='l',label='q / nm\S-1')
     p.legend(x=0.2,y=0.01)
     p.title('pearl necklace with 5 parls')
     p.subtitle('increasing string length reducing pearls')
     #p.save(js.examples.imagepath+'/pearlNecklace.jpg')

    .. image:: ../../examples/images/pearlNecklace.jpg
     :width: 50 %
     :align: center
     :alt: pearlNecklace



    References
    ----------
    .. [1] Particle scattering factor of pearl necklace chains
           R. Schweins, K. Huber, Macromol. Symp., 211, 25-42, 2004.



    """

    N = np.float(N)  # always float
    M = N - 1
    if isinstance(ms, numbers.Number) and isinstance(mr, numbers.Number):
        A1 = ms ** 2 / (M * mr + N * ms) ** 2
        A2 = mr ** 2 / (M * mr + N * ms) ** 2
        A3 = (mr * ms) / (M * mr + N * ms) ** 2
    if isinstance(monomerlength, numbers.Number) and l is None:
        l=monomerlength*mr
    if isinstance(vmonomer, numbers.Number) and Rc is None:
        Rc = (ms*vmonomer*3/4/np.pi)**(1/3)

    # distance between centers of neighbouring spheres
    A = l + 2 * Rc
    QA = Q * A
    # sphere form factor
    Y1 = 3 * (np.sin(Q * Rc) - (Q * Rc) * np.cos(Q * Rc)) / (Q * Rc) ** 3
    # S_ss equ 13 in [1]_
    Z1 = 2 * Y1 ** 2 * (N / (1 - np.sinc(QA)) - N / 2 - (1 - np.sinc(QA)**N) / (1 - np.sinc(QA))**2 * np.sinc(QA))

    # infinitely thin rod equ 16 selfterm ii
    Y2 = special.sici(Q * l)[0] / (Q * l)
    # rods mixed terms ij
    Y3 = (special.sici(Q * (A - Rc))[0] -special.sici(Q * Rc)[0]) / (Q * l)

    # S_rr equ 15 in [1]_
    Z2 = M * (2 * Y2 - np.sinc(Q * l / 2)**2) \
         + 2 * M * Y3**2 / (1 - np.sinc(QA)) \
         - 2 * Y3**2 * (1 - np.sinc(QA)**M)/(1 - np.sinc(QA))**2

    # S_rs equ 21 in [1]
    Z3 = Y3*Y1*4 * ((N - 1) / (1 - np.sinc(QA)) - (1 - np.sinc(QA)**(N - 1)) / (1 - np.sinc(QA))**2 * np.sinc(QA))

    # add the different contributions
    YY = A1 * Z1 + A2 * Z2 + A3 * Z3
    result = dA(np.c_[Q, YY].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Fq'
    result.pearlRadius = Rc
    result.A1 = A1
    result.A2 = A2
    result.A3 = A3
    result.numberPearls = N
    result.numberRods = M
    result.mr = mr
    result.ms = ms
    try:
        result.numberMonomers=ms*N + mr*(N-1)
    except:
        pass
    result.stringLength = l
    return result


def linearPearls(q, N, R, l, ms, mc, n=1, relError=0, rms=0, ffpolydispersity=0, ncpu=0):
    r"""
    Linear arranged pearls connected by gaussian chains in between them.

    Large pearls are aligned in a line and connected by polymer chain approximated as Gaussian coils.
    Increasing the number of connecting coils (reducing individual mass) result in a approximated linear connector.
    The model uses cloudscattering.
    The formfactor is normalized to 1. For absolute scattering see introduction :ref:`formfactor (ff)`.

    This model might be used as template to make models with with inhomogeneous pearls like
    hollow spheres or Gaussian coils as pearls just by changing the sphere formfactor and adjusting the geometry.

    Parameters
    ----------
    q : array, ndim= Nx1
         Radial wavevectors in 1/nm
    N : int
        Number of pearls
    R : float
        Radius of uniform pearls in units nm.
    l : float
        Length of connectors in units nm.
        The distance between pearls center of mass is 2R+l
    ms : float
        Number of chemical monomers in each pearl.
    mc : float
        Number of chemical monomers in each connector.
    n : int
        Number of Gaussians coils in connector.
        The coils are equal distributed on pearl connecting lines with Rg=l/2/n that coils touch with a distance 2Rg
        and touch the radius of the pearls. Zero means no connector but pearls separated by l.
    relError : float
        Determines calculation method.
         - relError>1   Explicit calculation of spherical average with Fibonacci lattice on sphere
                        of 2*relError+1 points. Already 150 gives good results (see Examples)
         - 0<relError<1 Monte Carlo integration on sphere until changes in successive iterations
                        become smaller than relError.
                        (Monte carlo integration with pseudo random numbers, see sphereAverage).
                        This might take long for too small error.
         - relError=0   The Debye equation is used (no asymmetry factor beta, no rms, no ffpolydispersity).
                        Computation is of order :math:`N^2` opposite to above which is order :math:`N`.
                        For about 1000 particles same computing time,for 500 Debye is 4 times faster than above.
                        If beta, rms or polydispersity is needed use above.
    rms : float, default=0
        Root mean square displacement :math:`\langle u^2 \rangle^{0.5}` of the positions in line as
        random (Gaussian) displacements in nm. See cloudscattering
    ffpolydispersity : float
        Polydispersity of the spheres in relative units.
        See cloudscattering.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
        See cloudscattering

    Returns
    -------
    dataArray :
        Columns [q,Pq,beta]
         - .I0 :          :math:`=I(q=0)=(\sum_N b_i)^2 = (Nm_s+(N-1)m_c)^2`
         - .sumblength :  :math:`=Nm_s+(N-1)m_c`
         - .formfactoramplitude   : formfactor amplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :  corresponding q values
         - beta only for relErr>0

    Notes
    -----
    This model is unique to Jscatter as connectors are included (at 2019).
    For linear pearls without connector use [1]_ as reference which is basically the same.

    The forward scattering of a linearPearl can be calculated as :math:`I(q=0) = b_{monomer}^2V_{monomer}^2  .I0`.

    The scattering length density in a pearl is :math:`\rho=ms b_{monomer}/V_{pearls}`.
    This may include the contrast relative to the solvent and swelling of the pearl material by solvent.

    We calculate the scattering amplitude :math:`F(q)` for :math:`N` particles in a volume :math:`V` with scattering
    amplitude :math:`b_i(q)`

    .. math:: F(q)= \sum_N b_i(q) e^{i\mathbf{qr_i}}  / \sum_N b_i(q=0)

    with the  form factor :math:`P(Q)` after explicit orientational average or using the Debye function :math:`<>`

    .. math:: P(Q)=< F(q) \cdot F^*(q) >=< |F(q)|^2 >

    Here we use :math:`b_i(q)` of spheres and Gaussians to describe the pearls and linear connectors.



    Examples
    --------
    ::

     import jscatter as js

     q=js.loglist(0.01,5,300)
     p=js.grace(1.5,1)
     for n in [0,1,5,15,30]:
         fq=js.ff.linearPearls(q,N=5,R=2,l=2,ms=100,mc=n,n=1)
         p.plot(fq,li=[1,2,-1],le='mc={0:.0f}'.format(n))
     p.plot(fq.formfactoramplitude_q,fq.formfactoramplitude[0],le='single sphere')
     p.plot(fq.formfactoramplitude_q,fq.formfactoramplitude[1],le='single gaussian')
     p.yaxis(scale='l',label='I(Q)')
     p.xaxis(label='q / nm\S-1')
     p.legend(x=0.02,y=0.001)
     p.title('linear pearls with gaussian connector with mass mc')
     #p.save(js.examples.imagepath+'/linearPearls.jpg')

    .. image:: ../../examples/images/linearPearls.jpg
     :width: 50 %
     :align: center
     :alt: cuboid



    References
    ----------
    For linear pearls without connector

    .. [1] Cascade of Transitions of Polyelectrolytes in Poor Solvents
           A. V. Dobrynin, M. Rubinstein, S. P. Obukhov
           Macromolecules 1996, 29, 2974-2979


    """
    M=N-1  # number connectors
    line=np.zeros((N+M*n, 5))              # N pearls and (N-1)*n gaussians in connectors
    # pearls
    line[:N, 0]=np.r_[0:1:N*1j]*N*(2*R+l)  # position on x axis
    line[:N, 3]=ms                         # scattering amplitude
    line[:N, 4]=1                          # index formfactor
    # formfactors, these will be normalized inside of cloudscattering
    # columns will be [q, sphere.Y, gaussianchain.Y]
    ffs = sphere(q, R)
    # connectors as n Gaussian coils
    if n>0:
        for m in range(M):
            line[N+m*n:N+(m+1)*n, 0]=line[m, 0] + R + l*np.r_[1:n+1]/(n+1)
        line[N:, 3] = mc/n
        line[N:, 4] = 2
        ffg = gaussianChain(q, l/2./n)
        ff = ffs.addColumn(1, ffg.Y)

    result = cloudScattering(q, line, relError=relError, formfactor=ff,
                             rms=rms, ffpolydispersity=ffpolydispersity, ncpu=ncpu)
    result.setColumnIndex(iey=None)
    result.modelname = sys._getframe().f_code.co_name

    return result


def ellipsoid(q, Ra, Rb, SLD=1, solventSLD=0, alpha=None, tol=1e-6):
    r"""
    Form factor for a simple ellipsoid (ellipsoid of revolution).

    Parameters
    ----------
    q : float
        Scattering vector unit e.g.  1/A or 1/nm  1/Ra
    Ra : float
        Radius rotation axis   units in 1/unit(q)
    Rb : float
        Radius rotated axis    units in 1/unit(q)
    SLD : float, default =1
        Scattering length density of unit nm^-2
        e.g. SiO2 = 4.186*1e-6 A^-2 = 4.186*1e-4 nm^-2 for neutrons
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
        e.g. D2O = 6.335*1e-6 A^-2 = 6.335*1e-4 nm^-2 for neutrons
    alpha : [float,float] , default [0,90]
        Angle between rotation axis Ra and scattering vector q in unit grad
        Between these angles orientation is averaged
        alpha=0 axis and q are parallel, other orientation is averaged
    tol : float
        relative tolerance for integration between alpha

    Returns
    -------
    dataArray
        Columns [q; Iq; beta ]
         - .RotationAxisRadius
         - .RotatedAxisRadius
         - .EllipsoidVolume
         - .I0         forward scattering q=0
         - beta is asymmetry factor according to [3]_.
           :math:`\beta = |<F(Q)>|^2/<|F(Q)|^2>` with scattering amplitude :math:`F(Q)` and
           form factor :math:`P(Q)=<|F(Q)|^2>`

    Examples
    --------
    Simple ellipsoid in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.1:10:0.01]
     Rp=6.
     Re=8.
     ashell=js.ff.multiShellEllipsoid(x,Rp,Re,1)
     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[1].subtitle('contrastprofile')
     p[0].plot(ashell)
     p[0].yaxis(scale='l',label='I(q)',min=0.01,max=100)
     p[0].xaxis(scale='l',label='q / nm\S-1',min=0.1,max=10)
     p[0].title('ellipsoid')
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs
     #p.save(js.examples.imagepath+'/ellipsoid.jpg')

    .. image:: ../../examples/images/ellipsoid.jpg
     :width: 50 %
     :align: center
     :alt: ellipsoid


    References
    ----------
    .. [1] Structure Analysis by Small-Angle X-Ray and Neutron Scattering
           Feigin, L. A, and D. I. Svergun, Plenum Press, New York, (1987).
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Ellipsoid.html
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if alpha is None:
        alpha = [0, 90]
    result = multiShellEllipsoid(q, Ra, Rb, shellSLD=SLD, solventSLD=solventSLD, alpha=alpha, tol=tol)
    attr = result.attr
    result.EllipsoidVolume = result.outerVolume
    result.RotationAxisRadius = Ra
    result.RotatedAxisRadius = Rb
    result.contrast = result.shellcontrast
    result.angles = alpha
    attr.remove('columnname')
    attr.remove('I0')
    for at in attr:
        delattr(result, at)
    result.modelname = sys._getframe().f_code.co_name
    return result


def multiShellEllipsoid(q, poleshells, equatorshells, shellSLD, solventSLD=0, alpha=None, tol=1e-6):
    """
    Scattering of multi shell ellipsoidal particle with varying shell thickness at pole and equator.

    Shell thicknesses add up to form complex particles with any combination of axial ratios and shell thickness.
    A const axial ratio means different shell thickness at equator and pole.

    Parameters
    ----------
    q : array
        Wavevectors, unit 1/nm
    equatorshells : list of float
        Thickness of shells starting from inner most for rotated axis Re making the equator. unit nm.
        The absolute values are used.
    poleshells : list of float
        Thickness of shells starting from inner most for rotating axis Rp pointing to pole. unit nm.
        The absolute values are used.
    shellSLD : list of float
        List of scattering length densities of the shells in sequence corresponding to shellthickness. unit nm^-2.
    solventSLD : float, default=0
        Scattering length density of the surrounding solvent. unit nm^-2
    alpha : [float,float], default [0,90]
        Angular range of rotated axis to average over. Default is no preferred orientation.
    tol : float
        Absolute tolerance for above adaptive integration of alpha.

    Returns
    -------
    dataArray
        Columns[q, Iq]
         Iq                    scattering cross section in units nm**2
          - .contrastprofile       as radius and contrast values at edge points of equatorshells
          - .equatorshellthicknes  consecutive shell thickness
          - .poleshellthickness
          - .shellcontrast         contrast of the shells to the solvent
          - .equatorshellradii     outer radius of the shells
          - .poleshellradii
          - .outerVolume           Volume of complete sphere
          - .I0                    forward scattering for Q=0

    Examples
    --------
    Simple ellipsoid in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     Rp=2.
     Re=1.
     ashell=js.ff.multiShellEllipsoid(x,Rp,Re,1)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(ashell)
     p[1].plot(ashell.contrastprofile,li=1) # a contour of the SLDs

    Alternating shells with thickness 0.3 nm h2o and 0.2 nm d2o in vacuum::

     import jscatter as js
     import numpy as np
     x=np.r_[0.1:10:0.01]
     shell=np.r_[[0.3,0.2]*3]
     sld=[-0.56e-4,6.39e-4]*3
     # constant axial ratio for all shells but nonconstant shell thickness
     axialratio=2
     ashell=js.ff.multiShellEllipsoid(x,axialratio*shell,shell,sld)
     # shell with constant shellthickness of one component and other const axialratio
     pshell=shell[:]
     pshell[0]=shell[0]*axialratio
     pshell[2]=shell[2]*axialratio
     pshell[4]=shell[4]*axialratio
     bshell=js.ff.multiShellEllipsoid(x,pshell,shell,sld)
     #plot it
     p=js.grace()
     p.new_graph(xmin=0.24,xmax=0.5,ymin=0.2,ymax=0.5)
     p[1].subtitle('contrastprofile')
     p[0].plot(ashell,le='const. axial ratio')
     p[1].plot(ashell.contrastprofile,li=2) # a contour of the SLDs
     p[0].plot(bshell,le='const shell thickness')
     p[1].plot(bshell.contrastprofile,li=2) # a contour of the SLDs
     p[0].yaxis(scale='l',label='I(q)',min=1e-9,max=0.0002)
     p[0].xaxis(scale='l',label='q / nm\S-1')
     p[0].legend(x=0.12,y=1e-5)
     p[0].title('multi shell ellipsoids')
     #p.save(js.examples.imagepath+'/multiShellEllipsoid.jpg')

    .. image:: ../../examples/images/multiShellEllipsoid.jpg
     :width: 50 %
     :align: center
     :alt: multiShellEllipsoid

    double shell with exponential decreasing exterior shell to solvent scattering::

     import jscatter as js
     import numpy as np
     x=np.r_[0.0:10:0.01]
     def doubleexpshells(q,d1,ax,d2,e3,sd1,sd2,sol):
        shells =[d1   ,d2]+[e3]*9
        shellsp=[d1*ax,d2]+[e3]*9
        sld=[sd1,sd2]+list(((sd2-sol)*np.exp(-np.r_[0:3:9j])))
        return js.ff.multiShellEllipsoid(q,shellsp,shells,sld,solventSLD=sol)
     dde=doubleexpshells(x,0.5,1,0.5,1,1e-4,2e-4,0)
     #plot it
     p=js.grace()
     p.multi(2,1)
     p[0].plot(dde)
     p[1].plot(dde.contrastprofile,li=1) # a countour of the SLDs

    References
    ----------
    .. [1] Structure Analysis by Small-Angle X-Ray and Neutron Scattering
           Feigin, L. A, and D. I. Svergun, Plenum Press, New York, (1987).
    .. [2] http://www.ncnr.nist.gov/resources/sansmodels/Ellipsoid.html
    .. [3] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if alpha is None:
        alpha = [0, 90]
    if isinstance(shellSLD, (numbers.Number)): shellSLD = [shellSLD]
    if isinstance(poleshells, (numbers.Number)): poleshells = [poleshells]
    if isinstance(equatorshells, (numbers.Number)): equatorshells = [equatorshells]
    if len(shellSLD) != len(equatorshells) or len(equatorshells) != len(poleshells):
        raise Exception(
            'shellSLD and equatorshells should be of same length but got:%i!=%i' % (len(shellSLD), len(equatorshells)))
    alpha = np.deg2rad(alpha) / np.deg2rad(90)  # set alpha so [0,1] interval which is [0,90]
    requ = np.cumsum(np.abs(equatorshells))  # returns array with absolute values
    rpol = np.cumsum(np.abs(poleshells))
    dSLDs = np.r_[shellSLD] - solventSLD  # subtract solvent to have in any case the contrast to the solvent

    # forward scattering Q=0 -------------
    Vr = 4 / 3. * np.pi * requ ** 2 * rpol
    dslds = Vr * dSLDs
    dslds[:-1] = dslds[:-1] - Vr[:-1] * dSLDs[1:]  # subtract inner shell
    fa0 = dslds.sum()

    # scattering amplitude in general
    def _ellipsoid_ffamp(Q, x, Re, Rp):
        axialratio = Rp / Re
        z = lambda q, Re, x: q * Re * np.sqrt(1 + x ** 2 * (axialratio ** 2 - 1))
        f = lambda z: 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
        return f(z(Q, Re, x))

    def _ffa(q, x, re, rp):
        # avoid zero
        Q = np.where(q == 0, q * 0 + 1e-10, q)
        # scattering amplitude multishell Q and R are column and row vectors
        # outer shell radius
        fa = Vr * dSLDs * _ellipsoid_ffamp(Q[:, None], x, re, rp)
        if len(re) > 1:
            # subtract inner radius for multishell, innermost shell has r=0
            fa[:, 1:] = fa[:, 1:] - Vr[:-1] * dSLDs[1:] * _ellipsoid_ffamp(Q[:, None], x, re[:-1], rp[:-1])
        # sum over radii and square for intensity
        fa = fa.sum(axis=1)
        # restore zero
        Fa = np.where(q == 0, fa0, fa)
        Fq = Fa ** 2
        # return scattering intensity and scattering amplitude for beta
        return np.c_[Fq, Fa]

    # integration over orientations for all q
    res = formel.parQuadratureAdaptiveGauss(_ffa, alpha[0], alpha[1], 'x', tol=tol, miniter=30, q=q, re=requ, rp=rpol)
    # calc beta
    res[1] = res[1] ** 2 / res[0]
    result = dA(np.c_[q, res.T].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq; beta'
    result.equatorshellsthickness = equatorshells
    result.poleshellthickness = poleshells
    result.shellcontrast = shellSLD
    result.equatorshellradii = requ
    result.poleshellradii = rpol
    contrastprofile = np.c_[np.r_[requ - equatorshells, requ], np.r_[shellSLD, shellSLD]].T
    result.contrastprofile = contrastprofile[:,
                             np.repeat(np.arange(len(shellSLD)), 2) + np.tile(np.r_[0, len(shellSLD)], len(shellSLD))]
    result.outerVolume = 4. / 3 * np.pi * max(requ) ** 2 * max(rpol)
    result.I0 = fa0 ** 2
    result.modelname = sys._getframe().f_code.co_name
    return result


def _ellipsoid_ff_amplitude(q, x, Ra, Rb):
    """
    Ellipsoidal form factor amplitude for internal usage only. save for q=0
    q in nm
    x in rad
    Ra,Rb in nm

    If x is an array of len N the output is shape N+1,len(q) with 0 as q and 1:N+1 as result

    """
    Q = np.where(q == 0, q * 0 + 1e-10, q)
    nu = Ra / float(Rb)
    z = lambda q, Rb, x: q[:, None] * Rb * np.sqrt(1 + x ** 2 * (nu ** 2 - 1))
    f = lambda z: 3 * (np.sin(z) - z * np.cos(z)) / z ** 3
    fa = f(z(Q, Rb, x))
    fa = np.where(q[:, None] == 0, 1, fa)
    return dA(np.c_[q, fa].T)


def ellipsoidFilledCylinder(q=1, R=10, L=0, Ra=1, Rb=2, eta=0.1, SLDcylinder=0.1, SLDellipsoid=1, SLDmatrix=0, alpha=90,
                            epsilon=None, fPY=1, dim=3):
    r"""
    Scattering of a single cylinder filled with ellipsoidal particles .

    A cylinder filled with ellipsoids of revolution with cylinder formfactor and ellipsoid scattering
    as described by Siefker [1]_.
    Ellipsoids have a fluid like distribution and hard core interaction leading to Percus-Yevick
    structure factor between ellipsoids. Ellipsoids can be oriented along cylinder axis.
    If cylinders are in a lattice, the  ellipsoid scattering (column 2) is observed in the diffusive scattering and
    the dominating cylinder contributes only to the bragg peaks as a form factor.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm
    R : float
        Cylinder radius in nm
    L : float
        Length of the cylinder in nm
        If zero infinite length is assumed, but absolute intensity is not valid, only relative intensity.
    Ra : float
        Radius rotation axis   units in nm
    Rb : float
        Radius rotated axis    units in nm
    eta : float
        Volume fraction of ellipsoids in cylinder for use in Percus-Yevick structure factor.
        Radius in PY corresponds to sphere with same Volume as the ellipsoid.
    SLDcylinder : float,default 1
        Scattering length density cylinder material in nm**-2
    SLDellipsoid : float,default 1
        Scattering length density of ellipsoids in cylinder in nm**-2
    SLDmatrix : float
        Scattering length density of the matrix outside the cylinder in nm**-2
    alpha : float, default 90
        Orientation of the cylinder axis to wavevector in degrees
    epsilon : [float,float], default [0,90]
        Orientation range of ellipsoids rotation axis relative to cylinder axis in degrees.
    fPY : float
        Factor between radius of ellipsoids Rv (equivalent volume) and radius used in structure factor Rpy
        Rpy=fPY*(Ra*Rb*Rb)**(1/3)
    dim : 3,1, default 3
        Dimensionality of the Percus-Yevick structure factor
        1 is one dimensional stricture factor, anything else is 3 dimensional (normal PY)

    Returns
    -------
    dataArray
        Columns [q,n*conv(ellipsoids,cylinder)*sf_b + cylinder,
                 n *conv(ellipsoids,cylinder)*sf_b,
                 cylinder, n * ellipsoids,
                 sf, beta_ellipsoids]
         - Each contributing formfactor is given with its absolute contribution
           :math:`V^2contrast^2` (NOT normalized to 1)
         - The observed structurefactor is :math:`sf\_b = S_{\beta}(q)=1+\beta (S(q)-1)`.
         - beta_ellipsoids :math:`=\beta(q)` is the asymmetry factor of Kotlarchyk and Chen [2]_.
         - conv(ellipsoids,cylinder) -> ellipsoid formfactor convoluted with cylinder formfactor
         - .ellipsoidNumberDensity  -> n ellipsoid number density in cylinder volume
         - .cylinderRadius
         - .cylinderLength
         - .cylinderVolume
         - .ellipsoidRa
         - .ellipsoidRb
         - .ellipsoidRg
         - .ellipsoidVolume
         - .ellipsoidVolumefraction
         - .ellipsoidNumberDensity  unit 1/nm**3
         - .alpha orientation range
         - .ellipdoidAxisOrientation

    Examples
    --------
    ::

     import jscatter as js
     p=js.grace()
     q=js.loglist(0.01,5,800)
     ff=js.ff.ellipsoidFilledCylinder(q,L=100,R=5.4,Ra=1.63,Rb=1.63,eta=0.4,alpha=90,epsilon=[0,90])
     p.plot(ff.X,ff[2],legend='convolution cylinder x ellipsoids')
     p.plot(ff.X,ff[3],legend='cylinder formfactor')
     p.plot(ff.X,ff[4],legend='ellipsoid formfactor')
     p.plot(ff.X,ff[5],legend='structure factor ellipsoids')
     p.plot(ff.X,ff.Y,legend='conv. ellipsoid + filled cylinder')
     p.legend(x=2,y=9e5)
     p.yaxis(scale='l',label='I(q)',min=1e-4,max=1e6)
     p.xaxis(scale='n',label='q / nm\S-1')
     p.title('ellipsoid filled cylinder')
     p.subtitle('the convolution cylinder x ellipsoids shows up in diffusive scattering')
     #p.save(js.examples.imagepath+'/ellipsoidFilledCylinder.jpg')

    .. image:: ../../examples/images/ellipsoidFilledCylinder.jpg
     :width: 50 %
     :align: center
     :alt: ellipsoidFilledCylinder

    Angular averaged formfactor ::

     def averageEFC(q,R,L,Ra,Rb,eta,alpha=[alpha0,alpha1],fPY=fPY):
         res=js.dL()
         alphas=np.deg2rad(np.r_[alpha0:alpha1:13j])
         for alpha in alphas:
             ffe=js.ff.ellipsoidFilledCylinder(q,R=R,L=L,Ra=Ra,Rb=Rb,eta=ata,alpha=alpha,)
             res.append(ffe)
         result=res[0].copy()
         result.Y=scipy.integrate.simps(res.Y,alphas)/(alpha1-alpha0)
         return result

    References
    ----------
    .. [1]  Confinement Facilitated Protein Stabilization As Investigated by Small-Angle Neutron Scattering.
            Siefker, J., Biehl, R., Kruteva, M., Feoktystov, A., & Coppens, M. O. (2018)
            Journal of the American Chemical Society, 140(40), 12720–12723. https://doi.org/10.1021/jacs.8b08454
    .. [2] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).

    """
    if epsilon is None:
        epsilon = [0, 90]
    q = np.atleast_1d(q)
    sldc = SLDmatrix - SLDcylinder
    slde = SLDellipsoid - SLDcylinder
    alpha = np.deg2rad(np.r_[alpha])
    epsilon = np.deg2rad(epsilon) / np.deg2rad(90)
    Ra = abs(Ra)
    Rb = abs(Rb)

    # nu = Ra / float(Rb)
    Vell = 4 * np.pi / 3. * Ra * Rb * Rb
    if L == 0:
        Vcyl = np.pi * R ** 2 * 1
    else:
        Vcyl = np.pi * R ** 2 * L
    # matrix with q and x for later integration
    Rge = (Ra ** 2 + 2 * Rb ** 2) ** 0.5
    # RgL = (R ** 2 / 2. + L ** 2 / 12) ** 0.5
    # catch if really low Q are tried
    lowerlimit = min(0.01 / Rge, min(q) / 5.)
    upperlimit = min(100 / Rge, max(q) * 5.)
    qq = np.r_[0, formel.loglist(lowerlimit, upperlimit, 200)]
    # width dq between Q values for integration;
    dq = qq * 0
    dq[1:] = ((qq[1:] - qq[:-1]) / 2.)
    dq[0] = (qq[1] - qq[0]) / 2.  # above zero
    dq[-1] = qq[-1] - qq[-2]  # assume extend to inf

    # generate ellipsoid orientations
    points = formel.fibonacciLatticePointsOnSphere(1000)
    pp = points[(points[:, 2] > epsilon[0]) & (points[:, 2] < epsilon[1])]
    v = formel.rphitheta2xyz(pp)
    # assume cylinder axis as [0,0,1], rotate the ellipsoid distribution to alpha cylinder axis around [1,0,0]
    RotM = formel.rotationMatrix([1, 0, 0], alpha)
    pxyz = np.dot(RotM, v.T).T
    # points in polar coordinates still with radius 1, theta component is for average formfactor amplitude
    theta = formel.xyz2rphitheta(pxyz)[:, 2]
    # use symmetry of _ellipsoid_ff_amplitude
    theta[theta > np.pi / 2] = np.pi / 2 - theta[theta > np.pi / 2]
    theta[theta < 0] = -theta[theta < 0]
    # get all ff_amplitudes interpolate and get mean
    eangles = np.r_[0:np.pi / 2:45j]
    fee = _ellipsoid_ff_amplitude(qq, eangles / np.deg2rad(90), Ra, Rb)[1:].T
    feei = scipy.interpolate.interp1d(eangles, fee)
    femean_qq = feei(theta).mean(axis=1)
    febetamean_qq = (feei(theta) ** 2).mean(axis=1)

    def _sfacylinder(q, R, L, angle):
        """
        single cylinder form factor amplitude for all angle
        q : wavevectors
        r : cylinder radius
        L : length of cylinder, L=0 is infinitely long cylinder
        angle : angle between axis and scattering vector q in rad
        for q<0 we get zero as a feature!!
        """
        # deal with possible zero in q and sin(angle)
        sina = np.sin(angle)
        qsina = q[:, None] * sina
        qsina[:, sina == 0] = q[:, None]
        qsina[q == 0, :] = 1  # catch later
        result = np.zeros_like(qsina)
        if L > 0:
            qcosa = q[:, None] * np.cos(angle)
            fqq = lambda qsina, qcosa: 2 * special.j1(R * qsina) / (R * qsina) * special.j0(L / 2. * qcosa)
            result[q > 0, :] = fqq(qsina[q > 0, :], qcosa[q > 0, :])
            result[q == 0, :] = 1
        else:
            fqq = lambda qsina: 2 * special.j1(R * qsina) / (R * qsina)
            result[q > 0, :] = fqq(qsina[q > 0, :])
            result[q == 0, :] = 1
        return result

    def fc2(q, R, L, angle):
        # formfactor cylinder ; this is squared!!!
        if angle[0] == angle[1]:
            res = _sfacylinder(q, R, L, np.r_[angle[0]]) ** 2
        else:
            pj = (angle[1] - angle[0]) // 0.05
            if pj == 0: pj = 2
            al_angle = np.r_[angle[0]:angle[1]:pj * 1j]
            val = _sfacylinder(q, R, L, al_angle)
            res = np.trapz(val ** 2, al_angle, axis=1)
        return res

    def fefcconv(q, angle):
        # convolution of cylinder and ellipsoid;
        val = [(femean_qq * _sfacylinder(q_ - qq, R, L, np.r_[angle]).T[0] * dq).sum() / dq[
            qq <= q_].sum() if q_ > 0 else 1 for q_ in qq]
        res = np.interp(q, qq, np.r_[val])
        return res

    # structure factor ellipsoids
    if dim == 1:
        R1dim = (Ra * Rb * Rb) ** (1 / 3.)
        Sq = sf.PercusYevick1D(q, fPY * R1dim, eta=fPY * eta)
        density = eta / (2 * R1dim)  # in unit 1/nm
    else:
        Sq = sf.PercusYevick(q, fPY * (Ra * Rb * Rb) ** (1 / 3.), eta=fPY ** 3 * eta)
        # particle number in cylinder volume
        density = Sq.molarity * constants.Avogadro / 10e24  # unit 1/nm**3
    nV = density * Vcyl
    # contribution form factors
    ffellipsoids = nV * (slde * Vell) ** 2 * np.interp(q, qq, femean_qq ** 2)
    ffellipsoidsbeta = np.interp(q, qq, (femean_qq ** 2 / febetamean_qq))  # ala Kotlarchyk

    ffcylinder = (sldc * Vcyl) ** 2 * fc2(q, R, L, [alpha[0], alpha[0]])[:, 0]
    # convoluted  form factor of ellipsoids
    # and structure factor correction as in Chen, Kotlarchyk
    ffconv = nV * (slde * Vell) ** 2 * fefcconv(q, alpha[0]) ** 2 * (1 + ffellipsoidsbeta * (Sq.Y - 1))

    result = dA(np.c_[q, ffconv + ffcylinder, ffconv, ffcylinder, ffellipsoids, Sq.Y, ffellipsoidsbeta].T)
    result.cylinderRadius = R
    result.cylinderLength = L
    result.cylinderVolume = Vcyl
    result.ellipsoidRa = Ra
    result.ellipsoidRb = Rb
    result.ellipsoidRg = R
    result.ellipsoidVolume = Vell
    result.ellipsoidVolumefraction = eta
    result.ellipsoidNumberDensity = density  # unit 1/nm**3
    result.alpha = np.rad2deg(alpha[0])
    result.ellipdoidAxisOrientation = np.rad2deg(epsilon)
    result.setColumnIndex(iey=None)
    result.columnname = 'q; ellipsoidscylinder; convellicyl; cylinder; ellipsoids; structurefactor; betaellipsoids'
    result.modelname = sys._getframe().f_code.co_name
    return result


def teubnerStrey(q, xi, d, eta2=1):
    """
    Phenomenological model for the scattering intensity of a two-component system using the Teubner-Strey model [1]_.

    Often used for  bi-continuous micro-emulsions.

    Parameters
    ----------
    q : array
        wavevectors
    xi : float
        correlation length
    d : float
        characteristic domain size, periodicity
    eta2 : float, default=1
        squared scattering length density contrast

    Returns
    -------
    dataArray
        Columns [q, Iq]

    Notes
    -----
    - :math:`q_{max}=((2\pi/d)^2-\\xi^{-2})^{1/2}`

    Examples
    --------
    Teubner-Strey with background and a power law for low Q
    ::

     import jscatter as js
     import numpy as np

     def tbpower(q,B,xi,dd,A,beta,bgr):
         # Model Teubner Strey  + power law and background
         tb=js.ff.teubnerStrey(q=q,xi=xi,d=dd)
         # add power law and background
         tb.Y=B*tb.Y+A*q**beta+bgr
         tb.A=A
         tb.bgr=bgr
         tb.beta=beta
         return tb

     q=js.loglist(0.01,5,600)
     p=js.grace()
     data=tbpower(q,1,10,20,0.00,-3,0.)
     p.plot(data,legend='no bgr, no power law')
     data=tbpower(q,1,10,20,0.002,-3,0.1)
     p.plot(data,legend='xi=10')
     data=tbpower(q,1,20,20,0.002,-3,0.1)
     p.plot(data,legend='xi=20')
     p.xaxis(scale='l',label=r'Q / nm\S-1')
     p.yaxis(scale='l',label='I(Q) / a.u.')
     p.legend(x=0.02,y=1)
     p.title('TeubnerStrey model with power law and background')
     #p.save(js.examples.imagepath+'/teubnerStrey.jpg')

    .. image:: ../../examples/images/teubnerStrey.jpg
     :width: 50 %
     :align: center
     :alt: teubnerStrey



    References
    ----------
    .. [1] M. Teubner and R. Strey,
           Origin of the scattering peak in microemulsions,
           J. Chem. Phys., 87:3195, 1987
    .. [2] K. V. Schubert, R. Strey, S. R. Kline, and E. W. Kaler,
           Small angle neutron scattering near lifshitz lines:
           Transition from weakly structured mixtures to microemulsions,
           J. Chem. Phys., 101:5343, 1994

    """
    q = np.atleast_1d(q)
    qq = q * q
    k = 2 * np.pi / d
    a2 = (k ** 2 + xi ** -2) ** 2
    b = k ** 2 - xi ** -2
    Iq = 8 * np.pi * eta2 / xi / (a2 - 2 * b * qq + qq * qq)
    result = dA(np.c_[q, Iq].T)
    result.correlationlength = xi
    result.domainsize = d
    result.SLD2 = eta2
    result.setColumnIndex(iey=None)
    result.columnname = 'q; Iq'
    result.modelname = sys._getframe().f_code.co_name

    return result


def superball(q, R, p, SLD=1, solventSLD=0, nGrid=15, returngrid=False):
    """
    A superball is a general mathematical shape that can be used to describe rounded cubes, sphere and octahedron's.

    The numerical integration is done by a pseudorandom grid of scatterers.
    The integration is valid at low Q. Validity can be increased if nGrid is increased.

    Parameters
    ----------
    q : array
        Wavevector in 1/nm
    R : float, None
        2R = edge length
    p : float, 0<p<100
        Parameter that describes shape
        | p=0       empty space
        | p<0.5     concave octahedron's
        | p=0.5     octahedron
        | 0.5<p<1   convex octahedron's
        | p=1       spheres
        | p>1       rounded cubes
        | p->inf    cubes
    SLD : float, default =1
        Scattering length density of cuboid. unit nm^-2
    solventSLD : float, default =0
        Scattering length density of solvent. unit nm^-2
    nGrid : int
        Number of gridpoints is nGrid**3.
        relError=nGrid*4 is used for Fibonacci lattice with 2*relError+1 orientations in spherical average.
    returngrid : bool
        Return grid.

    Returns
    -------
    dataArray
        Columns [q,Iq, beta]

    Examples
    --------
    Compare to extreme cases of sphere (p=1) and cube (p->inf , use here 100) ::

     import jscatter as js
     import numpy as np
     #
     q=np.r_[0:3.5:0.02]
     R=6;
     p=js.grace()
     p.multi(2,1)
     p[0].yaxis(scale='l',label='I(q)')
     ss=js.ff.superball(q,R,p=1,returngrid=1)
     p[0].plot(ss,legend='superball p=1')
     ss=js.ff.superball(q,R,p=1,returngrid=1,nGrid=20)
     p[0].plot(ss,legend='superball p=1 nGrid=20')
     p[0].plot(js.ff.sphere(q,R),li=1,sy=0,legend='sphere ff')
     p[0].legend(x=2,y=5e5)
     #
     p[1].yaxis(scale='l',label='I(q)')
     p[1].xaxis(scale='n',label='q / nm\S-1')
     cc=js.ff.superball(q,R,p=100,nGrid=15)
     p[1].plot(cc,sy=[1,0.3,4],legend='superball p=100 nGrid=15')
     cc=js.ff.superball(q,R,p=100,nGrid=20)
     p[1].plot(cc,sy=[1,0.3,5],legend='superball p=100 nGrid=20')
     p[1].plot(js.ff.cuboid(q,2*R),li=4,sy=0,legend='cuboid')
     p[1].legend(x=2,y=2e5)
     p[0].title('Superball with transition from sphere to cuboid')
     p[0].subtitle('p=1 sphere; p>1 round cube; p>20 cube  ')
     #
     # visualisation
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     # cubic grid points
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     q=np.r_[0:5:0.1]
     R=3
     pxyz=js.ff.superball(q,R,p=200,nGrid=10,returngrid=True).grid
     pxyz=pxyz[pxyz[:,0]>0]
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-3,3])
     ax.set_ylim([-3,3])
     ax.set_zlim([-3,3])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)
     #p.save(js.examples.imagepath+'/superball.jpg')

    .. image:: ../../examples/images/superball.jpg
     :width: 50 %
     :align: center
     :alt: superball


    References
    ----------
    .. [1] Periodic lattices of arbitrary nano-objects: modeling and applications for self-assembled systems
           Yager, K.G.; Zhang, Y.; Lu, F.; Gang, O.
           Journal of Applied Crystallography 2014, 47, 118–129. doi: 10.1107/S160057671302832X
    .. [2] http://gisaxs.com/index.php/Form_Factor:Superball

    """
    p2 = abs(2. * min(p, 200.))
    R = abs(R)
    q = np.atleast_1d(q)
    contrast = SLD - solventSLD
    # volume according to Soft Matter, 2012, 8, 8826-8834, DOI: 10.1039/C2SM25813G
    V = 8 * R ** 3 * special.gamma(1 + 1 / p2) ** 3 / special.gamma(1 + 3 / p2)

    # superball surface radius for a point, a definition of radius in p2 but normal length unit
    r = lambda xyz: (np.abs(xyz[:, :3]) ** p2).sum(axis=1) ** (1. / p2)

    def _inside(xyz, R, dR=None):
        # points inside superball or in surface layer [R,R+dR]
        if dR is None:
            rr = r(xyz)
            inside = rr <= R
        else:
            rr = r(xyz)
            inside = (rr > R) & (rr < R + dR)
        return inside

    # surrounding pseudorandom grid
    gridb = formel.randomPointsInCube(nGrid ** 3, 3)
    gridb = gridb * 2 * R - R  # move to zero center
    insidegrid = np.array(gridb[_inside(gridb, R)])

    # calc scattering
    result = cloudScattering(q, insidegrid, relError=nGrid * 4)
    result.columnname = 'q; Iq; beta'
    result.Y = result.Y * V ** 2 * contrast ** 2
    result.modelname = sys._getframe().f_code.co_name
    result.R = R
    result.Volume = V
    result.rounding_p = p2 / 2.
    result.contrast = contrast
    result.I0 = V ** 2 * contrast ** 2
    if returngrid:
        result.grid = insidegrid
    return result


def _mVD(Q, kk, N):
    # in the paper N and n are both the same.
    q = Q  # np.float128(Q) # less numeric noise at low Q with float128 but 4 times slower
    K = kk  # np.float128(kk)
    K2 = K * K
    K3 = K2 * K
    K4 = K3 * K
    K5 = K4 * K
    K6 = K5 * K
    K7 = K6 * K
    K8 = K7 * K
    NN = N * N
    NNN = N * N * N
    K2m1 = K2 - 1
    K2p1 = K2 + 1
    KN2 = K ** (N + 2)
    D = (-6. * K2m1 * K2p1 * (K4 + 5 * K2 + 1) * NN + (-6 * K8 - 12 * K6 + 48 * K4 + 48 * K2 + 6) * N + (
            3 * K8 + 36 * K6 + 24 * K4 - 18 * K2 - 3.)) * np.sin(q * (2 * N + 1))
    D += ((3 * K8 - 12 * K6 - 45 * K4 - 24 * K2 - 3) * NN + (6 * K8 - 12 * K6 - 72 * K4 - 48 * K2 - 6) * N + (
            3 * K8 + 18 * K6 - 24 * K4 - 36 * K2 - 3.)) * np.sin(q * (2 * N - 1))
    D += ((3 * K8 + 24 * K6 + 45 * K4 + 12 * K2 - 3) * NN + 6 * K2 * (3 * K2 + 2) * N + 3 * K2 * (
            4 * K4 - K2 - 6.)) * np.sin(q * (2 * N + 3))
    D += (18 * K4 * K2p1 * NN + 6 * K2 * (6 * K4 + 3 * K2 - 2) * N + 3 * K2 * (6 * K4 + K2 - 4.)) * np.sin(
        q * (2 * N - 3))
    D += (-18 * K2 * K2p1 * NN - 6 * K4 * (2 * K2 + 3) * N - 3 * K4) * np.sin(q * (2 * N + 5))
    D += (3 * K4 * NN + 6 * K4 * N + 3 * K4) * np.sin(q * (2 * N - 5))
    D += (-3 * K4 * NN) * np.sin(q * (2 * N + 7))
    D += (6 * K3 * (3 * K4 + 10 * K2 + 5) * NN + 6 * K3 * (3 * K4 + 8 * K2 + 3) * N - 12 * K * K2m1 * (
            K4 + 3 * K2 + 1.)) * np.sin(q * 2 * N)
    D += (K * (-12 * K6 - 12 * K4 + 12 * K2 + 6) * NN - 6 * K * (2 * K2 + 3) * (2 * K4 - 2 * K2 - 1) * N + K * (
            -12 * K6 - 12 * K4 + 36 * K2 + 12.)) * np.sin(q * (2 * N - 2))
    D += (K * (-30 * K4 - 60 * K2 - 18) * NN + K * (-42 * K4 - 72 * K2 - 18) * N + K * (
            -12 * K6 - 36 * K4 + 12 * K2 + 12.)) * np.sin(q * (2 * N + 2))
    D += (-6 * K3 * (2 * K2 + 1) * NN - 6 * K3 * (4 * K2 + 1.) * N - 12 * K5) * np.sin(q * (2 * N - 4))
    D += (-6 * K * (K6 + 2 * K4 - 2 * K2 - 2) * NN + 6 * K3 * (K4 + 4 * K2 + 2.) * N + 12 * K3) * np.sin(
        q * (2 * N + 4))
    D += (6 * K3 * (K2 + 2.) * NN + 6 * K5 * N) * np.sin(q * (2 * N + 6))

    D += (6 * K2m1 * K2p1 * (K4 + 4 * K2 + 1) * NNN + 3 * (K4 - 4 * K2 - 3) * (3 * K4 + 8 * K2 + 1) * NN + (
            3 * K8 - 36 * K6 - 120 * K4 - 60 * K2 - 3) * N + 42 * K2 * (K4 - 4 * K2 + 1.)) * np.sin(q)
    D += (-2 * K2m1 * K2p1 * (K4 - K2 + 1) * NNN + (-3 * K8 + 9 * K6 + 3 * K2 + 3) * NN + (
            -K8 + 7 * K6 + 5 * K2 + 1) * N + 6 * K2 * (-4 * K4 + 11 * K2 - 4.)) * np.sin(3 * q)
    D += (-6 * K2 * K2m1 * K2p1 * NNN - 3 * K2 * (K4 - 8 * K2 - 5) * NN + 3 * K2 * (K4 + 8 * K2 + 3) * N + 6 * K2 * (
            K4 - K2 + 1.)) * np.sin(5 * q)
    D += (-6 * K * K2m1 * (2 * K2 + 1) * (K2 + 2) * NNN + K * (-12 * K6 + 48 * K4 + 102 * K2 + 24) * NN + K * (
            66 * K4 + 84 * K2 + 12) * N + 24 * K3 * K2p1) * np.sin(2 * q)
    D += (6 * K * K2m1 * K2p1 * K2p1 * NNN + 6 * K * K2p1 * (K4 - 5 * K2 - 2) * NN - 6 * K * K2p1 * (
            5 * K2 + 1) * N - 12 * K3 * K2p1) * np.sin(4 * q)
    D += (2 * K3 * K2m1 * NNN - 6 * K3 * NN - 2 * K3 * (K2 + 2.) * N) * np.sin(6 * q)

    D += KN2 * K2m1 * np.sin(q * N + 0) * K * (-72 - 12 * N * (3 * K2 + 4))
    D += KN2 * K2m1 * np.sin(q * (N - 1)) * (12 * (3 * K2 - 2) - 12 * N * (K2 + 2.))
    D += KN2 * K2m1 * np.sin(q * (N + 1)) * (-12 * (2 * K2 - 3) + 12 * N * (4 * K2 + 3.))
    D += KN2 * K2m1 * np.sin(q * (N - 2)) * K * (48 + 6 * N * (4 * K2 + 7.))
    D += KN2 * K2m1 * np.sin(q * (N + 2)) * K * (48 + 12 * N * (2 * K2 + 1.))
    D += KN2 * K2m1 * np.sin(q * (N - 3)) * (-6 * (4 * K2 - 1) - 6 * N * (2 * K2 - 1.))
    D += KN2 * K2m1 * np.sin(q * (N + 3)) * (6 * (K2 - 4) - 6 * N * (7 * K2 + 4.))
    D += KN2 * K2m1 * np.sin(q * (N - 4)) * K * (-12 - 6 * N * (K2 + 2.))
    D += KN2 * K2m1 * np.sin(q * (N + 4)) * K * (-12 - 6 * N * (K2 - 2.))
    D += KN2 * K2m1 * np.sin(q * (N - 5)) * K2 * (6. + 6 * N)
    D += KN2 * K2m1 * np.sin(q * (N + 5)) * (6 + 6 * N * (2 * K2 + 1.))
    D += KN2 * K2m1 * np.sin(q * (N + 6)) * K * (-6. * N)

    return D  # np.float64(D)


def multilayer(q, layerd, SLD, gaussw=None, solventSLD=0):
    r"""
    Form factor of a multilayer with rectangular/Gaussian density profiles perpendicular to the layer.

    To describe smeared interfaces or complex profiles use more layers.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    layerd : list of float
        Thickness of layers in units nm.
        List gives consecutive layer thickness from center to outside.
    gaussw : list of float, default None
        Width of Gaussian in a layer. If float>0 a gaussian profile with this width is assumed.
        [1,None,1] is box in center and Gaussian width of 1 for outer layers.
    SLD : list of float
        Scattering length density of layers in nm^-2.
    solventSLD : float, default=0
        Solvent scattering length density in nm^-2.

    Returns
    -------
    dataArray
        Columns [q,Fq]
         - Fq is multilayer scattering per layer area.
         - To get the scattering intensity of a volume the result needs to be multiplied with the layer area [2]_.
         - .contrastprofile    contrastprofile relative to layer center (contrast to solvent)
         - .layerthickness

    Notes
    -----
    The scattering amplitude :math:`F_a` is the Fourier transform of the density profile :math:`\rho(r)`

    .. math:: F_a(q)=\int \rho(r)e^{iqr}dr

    For a rectangular profile [1]_ of thickness :math:`d_i` centered at :math:`a_i` and
    layer scattering length density :math:`\rho_i` we find

    .. math:: F_{a,box}(q)= \rho_i d_i sinc(qd_i/2)e^{iqa_i}

    For a Gaussian profile [2] :math:`\rho(r)=\rho_ie^{-r^2/d_i^2/2}`
    with same area as the rectangular profile we find

    .. math:: F_{a,gauss}(q)= \rho_i d_i e^{-(q^2d_i^2/2)}e^{iqa_i}

    The scattering amplitude for a multi box/gauss profile is :math:`F_a(q)=\sum_i F_a(q,i)`

    The formfactor :math:`F(q)` of this multi layer profile is in time average :math:`<>`

    .. math:: F(q)=<\sum_{ij} F_a(q,i)F_a^*(q,j)>

    resulting e.g. for a profile of rectangular boxes in

    .. math:: F_{box}(q)=\sum_{i,j} \rho_i\rho_j d_i d_j sinc(qd_i)sinc(qd_j)cos(q(a_i-a_j))

    To get the 3D orientational average one has to add a Lorentz correction :math:`q^{-2}`
    to describe the correct scattering in isotropic average (see [2]_) or use *multilamellarVesicles* which includes a
    full structure factor and also size averaging.

    **Restricting parameters for Fitting**
     If the model is used during fits one has to consider dependencies between the parameters and restrict them somehow.
     For example the scattering length densities scale all with the particle concentration. This requires that
     maybe one is fixed. Symmetry in the layers may also be used to restrict the parameter space.


    Examples
    --------
    Some symmetric membranes in comparison.
    Gaussian profiles correspond roughly to a box width of the Gaussian :math:`FWHM= 2\sqrt{2 log(2)}\sigma`.
    ::

     import jscatter as js
     import numpy as np
     q=np.r_[0.01:5:0.001]
     p=js.grace()
     p.multi(2,1)
     p[0].title('multilayer membranes')
     p[0].subtitle('fractions choosen to result in same forward scattering at q=0')
     profile=np.r_[2,1,2]
     #
     pf1=js.ff.multilayer(q,[1,5,1],profile)
     p[0].plot(pf1,sy=[1,0.3,1],le='box')
     p[1].plot(pf1.contrastprofile,li=[1,2,1],le='box')
     #
     f=2*(2*np.log(2))**0.5 # factor between sigma and FWHM
     pf2=js.ff.multilayer(q,np.r_[1,5,1],profile*f,gaussw=np.r_[1,5,1]/f)
     p[0].plot(pf2,sy=[2,0.3,2],le='gauss')
     p[1].plot(pf2.contrastprofile,li=[1,2,2],le='gauss')
     #
     pf3=js.ff.multilayer(q,np.r_[1,5,1],profile*np.r_[f,1,f],gaussw=np.r_[1/f,0,1/f])
     p[0].plot(pf3,sy=[3,0.3,3],le='gauss-box-gauss')
     p[1].plot(pf3.contrastprofile,li=[1,2,3],le='gauss-box-gauss')
     #
     p[0].yaxis(scale='n',min=0.001,max=90,label='I(Q)',charsize=1)#,ticklabel=['power',0,1]
     p[0].xaxis(label='',charsize=1)
     p[1].yaxis(label='contrast profile ()')
     p[1].xaxis(label='Q / nm\S-1')
     p[0].legend(x=3,y=50)
     #p.save(js.examples.imagepath+'/multilayer.jpg')

    .. image:: ../../examples/images/multilayer.jpg
     :width: 50 %
     :align: center
     :alt: multilayer membrane

    **How to use in a fit model**.
    Due to the large number of possible models, smearing and so on one has to define what seems to be important.
    Also complex profiles are possible. ::

     # define new model
     def membrane3(q,d1,d2,d3,s1,s2,s3,dd):
        # define your model
        #outer layers have half the scattering length density and thickness dd
        result=js.ff.multilayer(q,[dd,d1,d2+dd2,d3,dd],[s1/2,s1,s2,s3,s3/2])


    References
    ----------
    Multi box profile
     .. [1] Modelling X-ray or neutron scattering spectra of lyotropic lamellar phases :
            interplay between form and structure factors
            F. Nallet, R. Laversanne, D. Roux  Journal de Physique II, EDP Sciences, 1993, 3 (4), pp.487-502
            https://hal.archives-ouvertes.fr/jpa-00247849/document

    Gaussian profile
     .. [2] X-ray scattering from unilamellar lipid vesicles
            Brzustowicz and Brunger, J. Appl. Cryst. (2005). 38, 126–131
     .. [3] Structural information from multilamellar liposomes at full hydration:
            Full q-range fitting with high quality X-ray data.
            Pabst, G., Rappolt, M., Amenitsch, H. & Laggner, P.
            Phys. Rev. E - Stat. Physics, Plasmas, Fluids, Relat. Interdiscip. Top. 62, 4000–4009 (2000).

    """
    layerd = np.abs(np.atleast_1d(layerd))
    if gaussw is None:
        gaussw = [0] * layerd.shape[0]
    gaussw = np.atleast_1d([gw if isinstance(gw, (numbers.Number)) else 0 for gw in gaussw])
    # layers center positions with geometric center at zero
    edges = np.r_[0, np.cumsum(layerd)]
    edges = edges - edges[-1] / 2.  # center at zero
    pos = edges[:-1] + np.diff(edges) / 2  # pos is centers of layers
    # contrast
    sld = np.atleast_1d(SLD) - solventSLD
    # 3d array of phases and sum up over layers jk
    phase = np.cos(q[:, None, None] * (pos - pos[:, None])) * sld * sld[:, None]
    # for contrastprofile
    x = np.r_[np.min(edges) * 1.5:np.max(edges) * 1.5:100j]
    if np.alltrue(gaussw <= 0):
        # only box layers
        aq = np.sinc(q[:, None] * layerd / 2. / np.pi) * layerd
        contrastprofile = np.c_[[formel.box(x, [a, e]).Y * s for a, e, s in zip(edges[:-1], edges[1:], sld)]]
    elif np.alltrue(gaussw > 0):
        # only gaussian layers
        aq = np.exp(-q[:, None] ** 2 * gaussw ** 2 / 2.) * np.abs(gaussw)
        contrastprofile = np.c_[[formel.gauss(x, a, e).Y * s for a, e, s in zip(pos, gaussw, sld)]]
    else:
        aq = np.zeros((q.shape[0], layerd.shape[0]))
        # box contributions
        aq[:, gaussw <= 0] = np.sinc(q[:, None] * layerd[gaussw <= 0] / 2. / np.pi) * layerd[gaussw <= 0]
        # gaussian contributions
        aq[:, gaussw > 0] = np.exp(-q[:, None] ** 2 * gaussw[gaussw > 0] ** 2 / 2.) * np.abs(gaussw[gaussw > 0])
        contrastprofile = np.r_[[formel.box(x, [a, e]).Y * s for a, e, s in
                                 zip(edges[:-1][gaussw <= 0], edges[1:][gaussw <= 0], sld[gaussw <= 0])],
                                [formel.gauss(x, a, e).Y * s for a, e, s in
                                 zip(pos[gaussw > 0], gaussw[gaussw > 0], sld[gaussw > 0])]
                                ]
    # calc fomfactor
    Fq = np.einsum('ij,ijk,ik->i', aq, phase, aq)

    result = dA(np.c_[q, Fq].T)

    result.contrastprofile = dA(np.c_[x, np.sum(contrastprofile, axis=0)].T)
    result.layerthickness = layerd
    return result


def _mVSzero(q, N):
    S = 0.5 + 3. / (4 * N * (N + 0.5) * (N + 1)) * (
            np.cos(2 * q * (N + 1)) * ((N + 1) ** 2 - (N + 1) / (np.sin(q) ** 2)) +
            np.sin(2 * q * (N + 1)) / np.tan(q) * (-(N + 1) ** 2 + 1 / (2 * np.sin(q) ** 2)))
    return S / N ** 2 / q ** 2


def _mVSone(q, N):
    S = 3. / (N ** 3 * (N + 0.5) * (N + 1)) * (-0.5 * np.cos(q * (N + 0.5)) * (N + 0.5) +
                                               0.25 * np.sin(q * (N + 0.5)) / np.tan(q / 2.)) ** 2
    return S / (q * np.sin(q / 2)) ** 2


def _mVS(Q, R, displace, N):
    q = Q * R / N
    if N == 1:
        # a single shell ; see Frielinghaus below equ. 5
        return np.sinc(Q * R / np.pi) ** 2
    if displace == 0:
        return _mVSone(q, N)
    # for N > 1
    Sq = np.ones_like(Q)
    K = _fa_sphere(Q * displace)

    # booleans to decide which solution
    limit = 1e-3
    kzerolimit = limit * 0.5 * (6 * N ** 5 + 15 * N ** 4 + 10 * N ** 3 - N) / (6. * N ** 5 - 10 * N ** 3 + 4 * N)
    konelimit = limit * (420. / 36 * (4. * N ** 6 + 12 * N ** 5 + 13 * N ** 4 + 6 * N ** 3 + N ** 2) /
                         (10. * N ** 7 + 36. * N ** 6 + 21. * N ** 5 - 35 * N ** 4 - 35 * N ** 3 + 4 * N))
    kone = K > 1 - konelimit
    try:
        # above minimum Q with K <kzerolimit always use the kzero solution to get smooth solution
        Qmin = np.min(Q[K < kzerolimit])
    except ValueError:
        # This happens when kzerolimit is not in Q range and kzero should be always False
        Qmin = np.max(Q) + 1
    kzero = Q > Qmin
    kk = ~(kzero | kone)
    # cases as described in Frielinghaus equ 12 and 13 and full solution (kk)
    S0 = _mVSzero(q, N)
    Sq[kzero] = S0[kzero]
    Sq[kone] = _mVSone(q[kone], N)
    qkk = q[kk]
    D = _mVD(qkk, K[kk], N)
    divisor = (-48. * np.sin(qkk) ** 3 * (K[kk] ** 2 + 1 - 2 * K[kk] * np.cos(qkk)) ** 4 * qkk ** 2)
    sq = D * 3. / (N ** 3 * (N + 0.5) * (N + 1)) / divisor
    # for some values divisor and D become both small (machine precision) introducing errors
    # these are approximated by _mVSzero which has minima at the same positions
    qsing = (np.abs(D) < 1e-7) & (np.abs(divisor) < 1e-7) & (S0[kk] < 1e-4)
    sq[qsing] = _mVSzero(qkk[qsing], N)

    Sq[kk] = sq
    return Sq  # ,_mVD( q, K,N),(-48.*np.sin(q)**3 * (K**2 + 1 - 2*K * np.cos(q))**4 * q**2),_mVSone(q,N)


def _discrete_gaussian_kernel(mean, sig, Nmax):
    # generates a truncated discrete gaussian distribution with integrated probabilities in the interval's
    if sig < 0.4:
        # some default values for a single shell
        return [mean], [1], mean, 0
    if Nmax == 0:
        b = 10  # 10 sigma is large enough and >5*sig
    else:
        b = (Nmax - mean) / sig
    nn = np.floor(np.r_[mean - 5 * sig:mean + 5 * sig])
    nn = nn[nn > 0]
    cdf = scipy.stats.truncnorm.cdf(np.r_[nn - 0.5, nn[-1] + 0.5], a=(0.5 - mean) / sig, b=b, loc=mean, scale=sig)
    m, v = scipy.stats.truncnorm.stats(a=(0.5 - mean) / sig, b=10, loc=mean, scale=sig, moments='mv')
    pdf = np.diff(cdf)
    take = pdf > 0.005
    return nn[take], pdf[take] / np.sum(pdf[take]), m, v ** 0.5


def multilamellarVesicles(Q, R, N, phi, displace=0, dR=0, dN=0, layers=0, gaussw=None, ds=0, SLD=1, solventSLD=0,
                          nGauss=100):
    r"""
    Scattering intensity of a multilamellar vesicle with random displacements of the inner vesicles [1]_.

    The result contains the full scattering, the structure factor of the lamella and a multilayer formfactor of the
    lamella layer structure. Other layer structures as mentioned in [2].
    Multilayer formfactor is described in :py:func:`~.formfactor.multilayer`.

    Parameters
    ----------
    Q : float
        Wavevector in 1/nm.
    R : float
        Outer radius of the Vesicle in units nm.
    dR : float
        Width of outer radius distribution in units nm.
    displace : float
        Displacements of the vesicle centers in units nm.
        This describes the displacement steps in a random walk of the centers.
        displace=0 it is concentric, all have same center. displace< R/N.
    N : int
        Number of lamella.
    dN : int, default=0
        Width of distribution for number of lamella. (dN< 0.4 is single N)
        A zero truncated normal distribution is used with N>0 and N<R/displace.
        Check .Ndistribution and .Nweight = Nweight for the resulting distribution.
    phi : float
        Volume fraction :math:`\phi` of layers inside of vesicle.
    layers: list of float, default=0
        Thickness of layer sequence in a lamella in units nm.
        Zero assumes infinite thin lamella with constant formfactor.
        List gives consecutive layer thickness from center to outside.
    gaussw : list of float, default None
        Width of Gaussian in a layer. If float>0 a gaussian profile with this width is assumed.
        [1,None,1] is box in center and Gaussian width of 1 for outer layers.
        A gaussian needs a layers thickness of about the FWHM=2.35*sigma of the gaussian.
        See :py:func:`~.formfactor.multilayer`.
    SLD : list of float
        Scattering length density of layers in lamella in nm^-2.
    ds : float
        Thickness fluctuation of central layer in above lamella in nm.
        The variation is calculated as Gaussian distribution of the central layer
        (inner most one for even number of layers).
    solventSLD
        Solvent scattering length density in nm^-2.
    nGauss : int, default 100
        Number of Gaussian quadrature points in integration over dR distribution.

    Returns
    -------
    dataArray
        Columns [q,I(q),S(q),F(q)]
         - I(q)=S(q)F(q)  scattering intensity
         - S(q) multilamellar vesicle structure factor
         - F(q) lamella formfactor
         - .columnname='q;Iq;Sq;Fq'
         - .outerShellVolume
         - .Ndistribution
         - .Nweight
         - .displace
         - .phi
         - .layerthickness
         - .SLD
         - .solventSLD
         - .shellfluctuations=ds
         - .preFactor=phi*Voutershell**2


    Notes
    -----
    The left shows a concentric lamellar structure.
    The right shows the random path of the consecutive centers of the spheres.
    See :ref:`Multilamellar Vesicles` for resulting scattering curves.

    .. image:: MultiLamellarVesicles.png
     :align: center
     :height: 200px
     :alt: Image of MultiLamellarVesicles


    The function returns I(Q) as (see [1]_ equ. 17 )

    .. math:: I(Q)=\phi V_{outershell} S(Q) F(Q)

    with the multishell structure factor :math:`S(Q)` as described in [1]_.
    For a single layer we have the formfactor F(Q)

    .. math:: F(Q)= ( \sum_i \rho_i d_i sinc( Q d_i) )^2

    with :math:`\rho_i` as scattering length density and thickness :math:`d_i`.
    For a complex multilayer we find (see :py:func:`multilayer`)

    .. math:: F(Q)= \sum_{i,j} \rho_i\rho_j d_i d_j sinc(qd_i)sinc(qd_j)cos(q(a_i-a_j))

    with :math:`a_i` as positions of the layers.

    - The amphiphile concentration phi
      is roughly given by phi = d/a, with d being the bilayer thickness
      and a being the spacing of the shells. The spacing of the
      shells is given by the scattering vector of the first correlation
      peak, i.e., a = 2pi/Q. Once the MLVs leave considerable
      space between each other then phi < d/a holds. This condition
      coincides with the assumption of dilution of the Guinier law. (from [1]_)
    - Structure factor part is normalized that :math:`S(0)=\sum_{j=1}^N (j/N)^2`
    - To use a different shell form factor the structure factor is given explicitly.
    - Comparing a unilamellar vesicle (N=1) with multiShellSphere shows that
      R is located in the center of the shell::

        Q=js.loglist(0.0001,5,1000)#np.r_[0.01:5:0.01]
        ffmV=js.ff.multilamellarVesicles
        p=js.grace()
        p.multi(1,2)
        # comparison single layer
        mV=ffmV(Q=Q, R=100., displace=0, dR=0,N=1,dN=0, phi=1,layers=6, SLD=1e-4)
        p[0].plot(mV)
        p[0].plot(js.ff.multiShellSphere(Q,[97,6],[0,1e-4]),li=[1,1,3],sy=0)
        # triple layer
        mV1=ffmV(Q=Q, R=100., displace=0, dR=0,N=1,dN=0, phi=1,layers=[1,4,1], SLD=[0.07e-3,0.6e-3,0.07e-3])
        p[1].plot(mV1,sy=[1,0.5,2])
        p[1].plot(js.ff.multiShellSphere(Q,[97,1,4,1],[0,0.07e-3,0.6e-3,0.07e-3]),li=[1,1,4],sy=0)
        p[1].yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
        p[0].yaxis(label='S(Q)',scale='l',min=1e-10,max=1e6,ticklabel=['power',0])
        p[1].xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])
        p[0].xaxis(label='Q / nm\S-1',scale='l',min=1e-3,max=5,ticklabel=['power',0])

    Examples
    --------
    See :ref:`Multilamellar Vesicles`
    ::

     import jscatter as js
     import numpy as np

     ffmV=js.ff.multilamellarVesicles
     Q=js.loglist(0.01,5,500)
     dd=1.5
     dR=5
     nG=100
     R=50
     N=3
     st=[1.5,3.5,1.5]
     p=js.grace(1,1)
     p.title('Lipid bilayer in SAXS/SANS')
     # SAXS
     sld=[0.07e-3,0.6e-3,0.07e-3]
     saxm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=N,dN=0, phi=0.2,layers=st, SLD=sld,solventSLD=0.94e-3,nGauss=nG)
     p.plot(saxm,sy=[1,0.3,1],le='SAXS multilamellar')
     saxu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,layers=st, SLD=sld,solventSLD=0.94e-3,nGauss=100)
     p.plot(saxu,sy=0,li=[3,2,1],le='SAXS unilamellar')
     # SANS
     sld=[0.3e-4,1.5e-4,0.3e-4]
     sanm=ffmV(Q=Q, R=R, displace=dd, dR=dR,N=N,dN=0, phi=0.2,layers=st, SLD=sld,solventSLD=6.335e-4,nGauss=nG)
     p.plot( sanm,sy=[1,0.3,2],le='SANS multilamellar')
     sanu=ffmV(Q=Q, R=R, displace=0, dR=dR,N=1,dN=0, phi=0.2,layers=st, SLD=sld,solventSLD=6.335e-4,nGauss=100)
     p.plot(sanu,sy=0,li=[3,2,2],le='SANS unilamellar')
     #
     p.legend(x=0.015,y=1e-1)
     p.subtitle('R=50 nm, N=5, layerthickness=[1.5,3.5,1.5] nm, dR=5')
     p.yaxis(label='S(Q)',scale='l',min=1e-5,max=1e5,ticklabel=['power',0])
     p.xaxis(label='Q / nm\S-1',scale='l',min=1e-2,max=5,ticklabel=['power',0])
     #p.save(js.examples.imagepath+'/multilamellarVesicles.jpg')

    .. image:: ../../examples/images/multilamellarVesicles.jpg
     :width: 70 %
     :align: center
     :alt: multilamellarVesicles


    References
    ----------
    .. [1] Small-angle scattering model for multilamellar vesicles
           H. Frielinghaus Physical Review E 76, 051603 (2007)
    .. [2] Small-Angle Scattering from Homogenous and Heterogeneous Lipid Bilayers
           N. Kučerka Advances in Planar Lipid Bilayers and Liposomes 12, 201-235 (2010)
    """
    if isinstance(layers, (numbers.Number)): layers = [layers]

    # formfactor
    shelld = np.atleast_1d(layers)
    sld = np.atleast_1d(SLD) - solventSLD
    shellmax = np.sum(shelld)

    if shellmax == 0 or phi == 0:
        # if layers is zero no formfactor
        Soutershell = 1
        phi = 1
        Fq = np.ones_like(Q)
    else:
        if ds > 0:
            # integrate over normal distribution with width ds
            x, w = formel.gauss(np.r_[-2 * ds:2 * ds:23j], 0, ds).array
            ns = len(shelld) // 2
            if gaussw is None: gaussw = [0] * shelld.shape[0]
            if gaussw[ns] <= 0:
                # central layer is box
                fq = dL([multilayer(q=Q, layerd=np.r_[shelld[:ns], shelld[ns] + xx, shelld[ns + 1:]], SLD=sld,
                                    gaussw=gaussw, solventSLD=0) for xx, ww in zip(x, w)])
            else:
                # central layer is Gauss
                fq = dL([multilayer(q=Q, layerd=np.r_[shelld[:ns], shelld[ns] + xx, shelld[ns + 1:]], SLD=sld,
                                    gaussw=np.r_[gaussw[:ns], gaussw[ns] + xx, gaussw[ns + 1:]], solventSLD=0) for
                         xx, ww in zip(x, w)])
            Fq = (fq.Y.array * w[:, None]).sum(axis=0) / w.sum()
        else:
            Fq = multilayer(Q, shelld, sld, gaussw, 0).Y
        Soutershell = 4 * np.pi * R ** 2  # outer shell surface
    if N * (displace + shellmax) > R:
        warnings.warn("--->> Warning: layers dont fit inside!!! N=%.3g displace=%.3g R=%.3g" % (N, displace, R))

    # get discrete distribution over N with width dN
    # for small dN this is a single N and N>0
    Nmax = R / displace if displace != 0 else 0
    Ndistrib, Nweight, Nmean, Nsigma = _discrete_gaussian_kernel(N, dN, Nmax)
    if len(Ndistrib) == 0:
        warnings.warn("--->> Warning: layers dont fit inside!!!")
        return -1

    # define sum over N distribution
    SqR = lambda RR: np.c_[[Nw * _mVS(Q, RR, displace, NN) for NN, Nw in zip(Ndistrib, Nweight)]].sum(axis=0)

    # integrate over dR
    # Sq = np.c_[[Nw * _mVS(Q, R, displace, NN) for NN, Nw in zip(Ndistrib, Nweight)]].sum(axis=0)
    if dR == 0:
        Sq = np.c_[[Nw * _mVS(Q, R, displace, NN) for NN, Nw in zip(Ndistrib, Nweight)]].sum(axis=0)
    else:
        # fixed Gaussian integral over +-3dR
        weight = formel.gauss(np.r_[R - 3 * dR:R + 3 * dR:37j], R, dR).array
        Sq = formel.pQFG(SqR, R - 3 * dR, R + 3 * dR, 'RR', n=nGauss, weights=weight)

    # layer thickness thickness is included in Fq
    result = dA(np.c_[Q, phi * Soutershell ** 2 * Fq * Sq, Sq, Fq].T)
    # result = dA(np.c_[Q, Sq].T)
    result.modelname = sys._getframe().f_code.co_name
    result.setColumnIndex(iey=None)
    result.columnname = 'q;Iq;Sq;Fq'
    result.outerShellVolume = Soutershell * shellmax
    result.Ndistribution = Ndistrib
    result.Nweight = Nweight
    result.displace = displace
    result.phi = phi
    result.shellthickness = layers
    result.SLD = SLD
    result.solventSLD = solventSLD
    result.preFactor = phi * result.outerShellVolume ** 2
    return result


def decoratedCoreShell(q, Rcore, Rdrop, Ndrop, Hdrop, coreSLD, shellthickness=None, shellSLD=None, dropSLD=None,
                       solventSLD=0, typ='drop', distribution='fibonacci', ndrop=5, show=False):
    r"""
    Scattering of a sphere or coreshell particle decorated with droplets or disc-like particles.

    The model described a core shell particle decorated with drops or discs.
     - Drops may be added only at the outer surface extending the volume or extending into the inner volume.
     - Discs are only located in the shell describing e.g. liposomes with patches of different lipids or proteins.
     - Using a zero shellthickness drops decorate a sphere like the raspberry model for pickering emulsions.
     - For zero core the disc describes cones.
     - The model might be used to describe a sphere with surface roughness.

    The model uses cloudscattering and the source can be used as a template for more specific models as e.g.
    a bilayer membrane considering head and tail layers or decorated discs larger than the outer shell.

    Parameters
    ----------
    q : array
        Wavevectors in units 1/nm.
    Rcore : float
        Core radius in nm.
    shellthickness : float
        Thickness of the shell in units nm.
        Might be zero.
    Rdrop : float
        Radius of small drops or discs decorating the shell in units nm.
    Ndrop : int
        Number of drops on shell.
    Hdrop : float
        Center of mass position of drops relative to Rcore+shellthickness. Not used for discs.
    coreSLD,shellSLD,dropSLD : float
        Scattering length of core, shell or drops in unit nm^-2.
    solventSLD : float
        Solvent scattering length density in unit nm^-2.
    typ : 'drop','cutdrop','disc'
        Type of the drops
         - 'drop' extending to inside, drop volume has SLD dropSLD
         - 'cutdrop' the drop is cut at the outer shell and the shell has always shellSLD.
         - 'disc' a disc is cut from the shell and has dropSLD.
    distribution : 'fibonacci','quasirandom'
        Distribution of drops as :
         - 'fibonacci' A Fibonacci lattice on the sphere with Ndrop points.
                       For even Ndrop the point [0,0,1] is removed
         - 'quasirandom' quasirandom distribution of Ndrop drops on sphere surface.
    ndrop : int
        Number of points in grid on length Rdrop. Determines resolution of the droplets.
        Large ndrop increase the calculation time by ndrop**3.
        To small give wrong scattering length contributions in shell and core.
    show : bool
        Show a 3D image using matplotlib.

    Returns
    -------
    dataArray :
        Columns [q, Fq, Fq coreshell]
         - attributes from call
         - .dropSurfaceFraction :math:`=N_{drop}R_{drop}^2/(4(R_{core} + shellthickness + H_{drop})^2)`


    Notes
    -----
    The models uses cloudscattering with multicomponent particle distribution.
     - At the center is a multiShellSphere with core and shell located.
     - At the positions of droplets/disc a grid of small particles describe the respective shape as disc or drop.
     - According to the 'typ' each particle gets a respective scattering length to
       result in the correct scattering length density including the overlap with the central core-shell particle.
     - cloudscattering is used to calculate the respective scattering including all cross terms.
     - If drops overlap the overlap volume is only counted once.
       For large Ndrop the drop layer might be full, check *.dropSurfaceFraction*. In this case the disc represents
       the shell, while the drops represent still some surface roughness.
       The Rdrop is explicitly not limited to allow this.


    As described in cloudscattering for high q a bragg peak will appear showing the particle bragg peaks.
    This is far outside the respective SAS scattering. The validity of this model is comparable to
    :ref:`A nano cube build of different lattices`.
    For higher q the ndrop resolution parameter needs to be increased.


    Examples
    --------
    Comparing the models with arbitrary values. ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     drop = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=1, shellthickness=1, shellSLD=2,dropSLD=5,show=0,typ='drop')
     cutdrop = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=1, shellthickness=1, shellSLD=2,dropSLD=5,show=0,typ='cutdrop')
     disc = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=1, shellthickness=1, shellSLD=2,dropSLD=5,show=0,typ='disc')
     p=js.grace()
     p.plot(drop,li=1,le='drop')
     p.plot(disc,li=1,le='disc')
     p.plot(cutdrop,li=1,le='cutdrop')
     p.plot(drop.X,drop._cs_fq,li=1,sy=0,le='coreshell')
     p.yaxis(scale='l',min=1e4,max=1e10)
     p.xaxis(scale='l')
     p.legend(x=0.02,y=1e6)


    Comparing the coreshell with the drop decorated version
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     drop = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=0, shellthickness=1, shellSLD=2,dropSLD=0.5,show=0,typ='drop')
     fig = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=0, shellthickness=1, shellSLD=2,dropSLD=0.5,show=1,typ='drop')
     bb=fig.axes[0].get_position()
     fig.axes[0].set_title('raspberry: drops on core shell')
     fig.axes[0].set_position(bb.shrunk(0.5,0.9))
     ax1=fig.add_axes([0.58,0.1,0.4,0.85])
     ax1.plot(drop.X,drop.Y, label='coreshell with drops')
     ax1.plot(drop.X,drop[3],'--', label='core shell')
     ax1.set_yscale('log')
     ax1.set_xscale('log')
     ax1.legend()
     fig.set_size_inches(8,4)
     #fig.savefig(js.examples.imagepath+'/raspberry.jpg')

    .. image:: ../../examples/images/raspberry.jpg
     :width: 70 %
     :align: center
     :alt: cuboid


    Comparing the coreshell with the disc decorated version
    ::

     import jscatter as js
     q=js.loglist(0.01,5,300)
     drop = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=0, shellthickness=1, shellSLD=2,dropSLD=0.5,show=0,typ='disc')
     fig = js.ff.decoratedCoreShell(q=q,Rcore=20, Rdrop=4, Ndrop=20, Hdrop=0,
                     coreSLD=0, shellthickness=1, shellSLD=2,dropSLD=0.5,show=1,typ='disc')
     bb=fig.axes[0].get_position()
     fig.axes[0].set_title('liposome with patches')
     fig.axes[0].set_position(bb.shrunk(0.5,0.9))
     ax1=fig.add_axes([0.58,0.1,0.4,0.85])
     ax1.plot(drop.X,drop.Y, label='liposome with patches')
     ax1.plot(drop.X,drop[3],'--', label='core shell')
     ax1.set_yscale('log')
     ax1.set_xscale('log')
     ax1.legend()
     fig.set_size_inches(8,4)
     #fig.savefig(js.examples.imagepath+'/coreshellwithdisc.jpg')

    .. image:: ../../examples/images/coreshellwithdisc.jpg
     :width: 70 %
     :align: center
     :alt: cuboid


    """
    # use contrasts
    coreSLD = coreSLD - solventSLD
    if shellSLD is None:
        shellSLD = 0
    else:
        shellSLD = shellSLD - solventSLD
    if dropSLD is None:
        dropSLD = 0
    else:
        dropSLD = dropSLD - solventSLD

    if shellthickness is None: shellthickness=0

    # fq of coreshell and particles (root and norm is taken in cloudscattering)
    # this might be extended to complicated multishellSpheres
    if shellthickness ==0 or shellSLD ==0:
        fq = sphere(q, Rcore, coreSLD)
    elif Rcore ==0:
        fq = sphere(q, shellthickness, shellSLD)
    else:
        fq = multiShellSphere(q, [Rcore, shellthickness], [coreSLD, shellSLD], solventSLD=0)
    fq = fq.addColumn(1, 1)  # constant fa for points

    # a hcp grid for the droplets
    dnn=Rdrop/ndrop  # resolution for droplets
    size=(Rcore+shellthickness+Hdrop+Rdrop*2)/dnn  # overall size
    grid=sf.hcpLattice(ab=dnn, size=size)
    grid.set_b(0)  # set all b to zero

    # center of mass of droplets
    if distribution[0] == 'f':
        NN=int(Ndrop/2)
        points=formel.fibonacciLatticePointsOnSphere(NN=NN, r=Rcore+shellthickness+Hdrop)
        if points.shape[0]>Ndrop:
            points=np.delete(points, int(NN/2), 0)
        pointsxyz=formel.rphitheta2xyz(points)
    elif distribution[0] == 'q':
        points=formel.randomPointsOnSphere(NN=int(Ndrop), r=Rcore+shellthickness+Hdrop)
        pointsxyz=formel.rphitheta2xyz(points)

    # generate droplet grids
    V = grid.unitCellVolume
    if typ == 'drop':
        # all drop volume has SDL of drop
        for point in pointsxyz:
            grid.inSphere(Rdrop, center=point, b=dropSLD*V)
        grid.prune(grid._points[:, 3]>0)  # prune all except spheres
        # correct overlap not to count it twice in core and shell
        grid.inSphere(Rcore + shellthickness, b=(dropSLD-shellSLD)*V)
        grid.inSphere(Rcore, b=(dropSLD-coreSLD)*V)
        grid.prune(grid._points[:, 3]>0)  # prune all except spheres
    elif typ == 'cutdrop':
        # the drop is just an extension of core and shell to the outside
        for point in pointsxyz:
            grid.inSphere(Rdrop, center=point, b=1)
        grid.prune(grid._points[:, 3]>0)  # prune all except spheres
        # set b to zero
        grid.inSphere(Rcore + shellthickness, b=0)
        # grid.inSphere(Rcore, b=0)
        grid.prune(grid._points[:, 3]>0)  # prune all except spheres
        grid.set_b(dropSLD * V)
    elif typ == 'disc':
        # disc cuts in shell
        for point in pointsxyz:
            grid.alongLine(v=point, R=Rdrop, a=[0, 0, 0], direction=1, b=1)
        grid.prune(grid._points[:, 3]>0)  # prune all except cylinders/cone
        grid.inSphere(Rcore + shellthickness, b=0, invert=True)
        grid.inSphere(Rcore, b=0, invert=False)
        grid.prune(grid._points[:, 3]>0)
        grid.set_b((dropSLD-shellSLD) * V)
    if show:
        fig=grid.show()
        # add two transparent spheres
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = np.outer(np.cos(u), np.sin(v))
        y = np.outer(np.sin(u), np.sin(v))
        z = np.outer(np.ones(np.size(u)), np.cos(v))
        # Plot the surface
        fig.axes[0].plot_surface(x*Rcore, y*Rcore, z*Rcore,
                                 color='red', alpha=0.8)
        fig.axes[0].plot_surface(x*(Rcore+shellthickness), y*(Rcore+shellthickness), z*(Rcore+shellthickness),
                                 color='grey', alpha=0.2)
        return fig

    # complete the grid adding coreshell formfactor at center with respective scattering amplitude
    points = np.vstack([np.c_[grid.array, np.ones(grid.numberOfAtoms())*2], [0, 0, 0, fq.I0**0.5, 1]])
    res = cloudScattering(q, points, relError=200, formfactor=fq, ncpu=0)
    result=res.addColumn(1, fq.Y)
    result[1]=result[1]*result.I0
    result.columnname+='; cs_fq'
    result.setColumnIndex(iey=None)
    result.modelname = sys._getframe().f_code.co_name
    del result.rms
    del result.ffpolydispersity
    result.Rcore=Rcore
    result.Ndrops=Ndrop
    result.Rdrop=Rdrop
    result.Hdrop =Hdrop
    result.coreSLD =coreSLD
    result.shellthickness=shellthickness
    result.shellSLD=shellSLD
    result.dropSLD=dropSLD
    result.solventSLD=solventSLD
    result.dropSurfaceFraction=Ndrop*Rdrop**2/(4*(Rcore+shellthickness+Hdrop)**2)
    result.typ=typ
    result.distribution=distribution


    return result
















