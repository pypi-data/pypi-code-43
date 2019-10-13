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

"""
This module allows **smearing/desmearing** of SAXS/SANS data and
provides the **sasImage** class to read and analyse 2D detector images from SAXS cameras.

* **Smearing** is for line collimation as in Kratky SAXS cameras and for point collimation as SAXS/SANS data.
  For point collimation the resolution smearing a la Pedersen is realised.
  This can also be used for SAXS instruments in pinhole geometry collimation with smaller pinholes and distances.
  **Smearing as decorator of model allows simultaneous fit of smeared data from SANS/SAXS at different collimations.**

* **Desmearing** uses the Lake algorithm as an iterative procedure to desmear measured data.
  We follow here the improvements according to Vad using a convergence criterion and smoothing.

* 2D SAXS data can be read into **sasImage** to do typical tasks as transmission correction, masking,
  beamcenter location, 2D background subtraction, radial average (also for sectors).

* As **references** the waterXray scattering and a AgBe reference spectrum are available.

* For form factors and structure factors see the respective modules. Conversion of sasImage to
  dataArray allows 2D fit of scattering patterns (see :ref:`Fitting the 2D scattering of a lattice`)


"""
from __future__ import print_function
from __future__ import division

import copy
import fnmatch
import numbers
import os
import re
import shutil
import sys
import functools
import inspect
import xml.etree.ElementTree

import math
import numpy as np
import scipy

from scipy import interpolate, special, constants
from scipy.integrate import simps as integrate
import scipy.signal

from .graceplot import GracePlot as grace
from .dataarray import zeros
from .dataarray import dataArray as dA
from .dataarray import dataList as dL
from .formel import voigt, Elements, felectron, waterdensity, watercompressibility, loglist, smooth

from .sasimagelib import *

_beamProfType = {0: 'no', 1: 'sig', 2: 'trap'}


def _gauss(x, A, mean, sigma, bgr):
    """Normalized gaussian function. """
    return A * np.exp(-0.5 * (x - mean) ** 2 / sigma ** 2) / sigma / np.sqrt(2 * np.pi) + bgr


def readpdh(pdhFileName):
    """
    Opens and reads a SAXS data file in the .pdh (Primary Data Handling) format.

    If data contain X values <0 it is assumed that the primary beam is included as for SAXSpace instruments.
    Use js.sas.transmissionCorrection to subtract dark counts and do transmission correction.
    
    Parameters
    ----------
    pdhFileName : string
        File name

    Returns
    -------
        dataArray

    Notes
    -----
    Alternatively the files can be read ignoring the information in the header (it is stored in the comments)
    ::

     data=dA(pdhFileName,lines2parameter=[2,3,4])

    **PDH format** used in the  PCG SAXS software suite developed by the Glatter group
    at the University of Graz, Austria.
    This format is described in the appendix of the PCG manual (below from version 4.05.12 page 159).

    In the PDH format, lines 1-5 contain header information, followed by the SAXS data.
    ::

     line 1:  format A80             -> description
     line 2:  format 16(A4,1X)       -> description in 16x4 character groups (1X = space separated)
     line 3:  format 8(I9,1X)        -> 8 integers (1X = space separated)
     line 4:  format 5(E14.6,1X)     -> 5 float (1X = space separated)
     line 5:  format 5(E14.6,1X      -> 5 float(1X = space separated)
     line 6+  format 3(E14.6,1X)     - SAXS data x,y,error (1X = space separated)

    with:
     - line 3 field 0 : number of points
     - line 4 field 4 : normalization constant (default 1, never zero!!)

    Anything else can have different meanings.

    The SAXSpace and SAXSess (AntonPaar) format add:
     - line 4 field 2 : detector distance in mm
     - line 4 field 5 : wavelength
     - line 5 field 2 : detector slit length (equivalent to width of integration area) in q units

    Additional xml parameter as in the SAXSPACE format appended can be extracted to attributes by addXMLParameter.
    Mainly this is "Exposure" time.

    Example data for SAXSpace
    ::

     <emptyline>
     SAXS BOX
           2057         0         0         0         0         0         0         0
       0.000000E+00   3.052516E+02   0.000000E+00   1.000000E+00   1.541800E-01
       0.000000E+00   1.332843E+00   0.000000E+00   0.000000E+00   0.000000E+00
     -1.033335E-01   2.241656E+03   1.024389E+00
     -1.001430E-01   2.199972E+03   1.052537E+00
     ...


    """
    pdhs=dL()
    for pdhname in glob.glob(pdhFileName):
        data = dA(pdhname, lines2parameter=[2, 3, 4])
        if np.isnan(data.eY.min()) or np.all(data.eY == -1):
            data.setColumnIndex(iey=None)
        # forth line
        if data.line_3[4] != 0: data.wavelength = data.line_3[4]
        if data.line_3[1] != 0: data.detDist = data.line_3[1]
        # detector slit length (equivalent to width of integration area
        if data.line_4[1] != 0: data.dIW = data.line_4[3]
        pdhs.append(data)
    if len(pdhs) ==1:
        return pdhs[0]
    else:
        return pdhs


def fitDarkCurrent(darkfile):
    """
    Fits dark current with 5th order polynom + cosine.

    This is dangerous as the darkcurrent has a noise that is not random but depends on
    used detector and count time.

    """
    dark = dA(darkfile, lines2parameter=[2, 3, 4])
    darkp = dark.prune(0.01, 6.3, 100)
    # modeldark=lambda x,a0,a1,a2,a3,a4,a5,b0,b1,b2: a0+a1*x+a2*x**2+a3*x**3+a4*x**4+a5*x**4  +  b0*np.cos(((x-b1)/b2))
    modeldark = lambda x, a0, a1, a2, a3, a4, a5, b0, b1, b2: a0 + a1 * (x - b1) + a2 * (x - b1) ** 2 + a3 * (
                x - b1) ** 3 + a4 * (x - b1) ** 4 + a5 * (x - b1) ** 5 + b0 * np.cos(((x - b1) / b2))
    darkp.setlimit(a0=[2010, 2050], b2=[0, 10], b0=[0, 100], b1=[2, 4])
    darkp.fit(modeldark,
              {'a0': 2030, 'a1': 4.5, 'a2': 5.5, 'a3': -1, 'b0': 36, 'b1': 2.9, 'b2': 0.88},
              {'a4': 0, 'a5': 0, },
              mapNames={'x': 'X'})
    newdark = darkp.modelValues(x=dark.X)
    newdark.setattr(dark)
    return newdark


# smearing Functions  ####################################################################

def _wBLength(beam):
    """
    Weight at beam length y due to detector integration width.

    The relevant integration width is detected automatically from beamProfile.

    Parameters
    ----------
    beam : beamProfile
        Beam profile with attributes, see prepareBeamProfile

    Returns 
    -------
        Weight at Beam Length position y after integration over detector integration width dIW
        as array [y,weight]

    """
    dIW = beam.dIW
    if beam.a == 0 and dIW == 0:
        return None
    if beam.beamProfType[0] == 'm':
        # a measured beam profile stored in beam
        y = np.r_[0:3 * abs(beam.X).max():100j]  # estimate
        if dIW == 0:
            weight = beam.interp(y)
        else:
            interval = (beam.X[:, None] > y - dIW / 2) & (beam.X[:, None] < y + dIW / 2)
            weight = np.trapz(np.repeat(beam.Y[:, None], interval.shape[1], axis=1) * (interval * 1), interval, axis=0)
    elif beam.beamProfType[0] == 't':
        # a trapezoidal profile
        y = np.r_[0:3 * abs(beam.X).max():100j]  # estimate
        if dIW == 0:
            weight = beam.interp(y)
        else:
            def _integral(yy):
                # define trapez respecting integration boundaries
                ymi = yy - dIW / 2.  # integration boundaries
                yma = yy + dIW / 2.
                X = beam.X.copy()
                Y = beam.Y.copy()
                ibmi = np.searchsorted(X, ymi) - 1  # index position in beam
                ibma = np.searchsorted(X, yma)
                if ibmi >= len(X) or ibma == 0:
                    return 0.
                X[X < ymi] = ymi  # set the boundary x value
                Y[X < ymi] = 0.  # values outside are zero
                Y[ibmi] = beam.interp(ymi)  # set boundary y value as interpolated value at boundary
                X[X > yma] = yma  # same for other side
                Y[X > yma] = 0.
                if ibma < len(Y):
                    Y[ibma] = beam.interp(yma)
                w = np.trapz(Y, X)  # integrate
                return w

            weight = [_integral(yy) for yy in y]
    else:
        raise TypeError('No beam profile given.')

    # normalize
    normweight = weight / integrate(weight, y)
    # return only the nonzero values
    return np.c_[y[normweight > 1e-5], normweight[normweight > 1e-5]].T


def _wBWidth(beam):
    """
    weighting  beam width
    from +-2.5*sigma for Gaussian
    The integral is 0.99958
    """

    if isinstance(beam.bxw, numbers.Number):
        if beam.bxw == 0:
            return None
        # normalized Gaussian
        sigma = beam.bxw / np.sqrt(2 * np.log(2.0))  # sigma from hwhm
        # points with maximum width 2.5*sigma
        x = np.r_[-2.5 * sigma:2.5 * sigma:21j]
        return np.c_[x, _gauss(x, 1, 0, sigma, 0)].T
    elif hasattr(beam.bxw, '_isdataArray'):
        # experimental data interpolated
        x = np.r_[beam.bxw.X[0]:beam.bxw.X[-1]:27j]
        return np.c_[x, beam.bxw.interp(x)].T


def _smear(q, data):
    """
    Calculates smeared intensity for q array for line-collimated SAXS (Kratky camera).

    Defining a cubic spline representing the unsmeared scattering curve,
    Integrates all of the contributions to the observed scattering intensity at a nominal q-value
    
    Parameters
    ----------
    q : array
        Wavevectors
    data : dataset
        Here the beam parameters a,b,dIW are taken from data.beamProfile.

    Notes
    -----
    Contributions of scattering of other q-values are determined by
    the beam geometry and the detector slit width.

    """
    tckUnsm = data.tckUnsm  # spline coefficients of data
    q = np.atleast_1d(q)  # guarantee a ndarray
    # get weighting functions as arrays
    wx = _wBWidth(data.beamProfile)
    wy = _wBLength(data.beamProfile)
    # for qxy>q.max() the spline delivers wrong extrapolated results, so we use there a mean average from the largest q
    # generate mean value for qxy > q.max as last 10 values
    qmaxmean = interpolate.splev(q[-10:], tckUnsm, der=0).mean()
    if wx is None:
        if wy is None:
            # there is no smearing! Just return interpolated value
            valq = interpolate.splev(q, tckUnsm, der=0)
        else:
            # smear only y
            qy = np.sqrt((q[:, None] ** 2) + wy[0] ** 2)
            val = interpolate.splev(qy.flatten(), tckUnsm, der=0).reshape(qy.shape)
            val[qy > q.max()] = qmaxmean
            valwy = val * wy[1][None, :]
            valq = integrate(valwy, wy[0], axis=-1)
    else:
        # smear x
        if wy is None:
            # only x
            qx = q[:, None] + wx[0]
            val = interpolate.splev(qx.flatten(), tckUnsm, der=0).reshape(qx.shape)
            val[qx > q.max()] = qmaxmean
            valwx = val * wx[1][:, None]
            valq = integrate(valwx, wx[0], axis=-1)
        else:
            # smear over both x and y
            qxy = np.sqrt(((q[:, None] + wx[0]) ** 2)[:, :, None] + wy[0] ** 2)
            val = interpolate.splev(qxy.flatten(), tckUnsm, der=0).reshape(qxy.shape)
            val[qxy > q.max()] = qmaxmean
            valwxwy = val * wx[1][:, None] * wy[1][None, None, :]
            valwx = integrate(valwxwy, wy[0], axis=-1)
            valq = integrate(valwx, wx[0], axis=-1)
    return valq


def smear(unsmeared=None, *, beamProfile=None, **smkwargs):
    r"""
    Smearing model/data for point collimation SANS/SAXS or line-collimated SAXS (Kratky camera).

    The beamProfile parameter has to be given as keyword argument ``beamProfile=mybeam``.

    Smearing at detector edges involves evaluation of the model at extrapolated q values.
     * For model functions smear is used as decorator ``@smear`` and the q range is automatically extended.
     * If a model has beamProfile as parameter and gets a valid beamProfile during function call
       this is used. This allows fitting with different profiles if the corresponding data contain .beamProfile
       as attribute. See Notes.
     * For explicit given data extrapolation at each edge needs to be chosen according
       to the observed behaviour at the edge (eg power law at low q or constant at high q).
       See prepareBeamProfile for the options.
    Call only with keyword arguments. See Notes for details.

    Parameters
    ----------
    unsmeared : function or dataArray
        Model function or explicit data to be smeared.
        **The scattering vector in the model function should have name starting with one of 'qQ'.**
        If used as a decorator the function is inserted automatically by the @smear syntax and should not be given.
        If any smearing related parameter is None as *detDist=None* smearing is bypassed.
    beamProfile : beamProfile or 'trap', 'SANS', 'explicit', dataArray
        Beamprofile that determines smearing as prepared from prepareBeamProfile.
        **Always use as keyword argument**
        If no beamProfile is given input and smkwargs are used in prepareBeamProfile to define beamprofile.
        Measured Profile is also treated by prepareBeamProfile.
    smkwargs :
        See prepareBeamProfile for kwargs.
    
    Returns 
    -------
    dataArray :
        - for line collimation: smeared data
        - other: dataArray with columns
                 [q, smeared data, original data, half width smearing function]
                 and additional attributes as defined in the respective beamProfiles and smeared model.
    
    Notes
    -----
    **Smearing a model function as decorator** (like @smear ) for fitting.

    Decorators modify functions. Here the model is smeared according to the provided beamprofile
    extending the q range at edges.

    **The model scattering vector must have a name starting with one of "qQ".**

    * Beamprofile parameters as *detDist* are updated for smearing during the function call.
      This allows that during fitting of datasets with different *detDist* always the correct smearing is used.
      Setting any of the beamprofile parameters to *None* bypasses smearing.

      Use as : ::

       # define resolution
       resol2m = js.sas.prepareBeamProfile('SANS', detDist=2000,collDist=2000.,wavelength=0.4,wavespread=0.10,
                                           collAperture=10, sampleAperture=6, dpixelWidth=10, dringwidth=1)

       # decorate model to automatically smear it (dont use `unsmeared` argument as it is added automatically)
       @js.sas.smear(beamProfile=resol2m)
       def sphere(q,R,bgr,detDist=3000,collDist=2000.,c=1):
           sp = js.ff.sphere(q=q,radius=R,contrast=c)
           sp.Y=sp.Y+bgr
           return sp

       # also for fitting with attribute detDist and collDist in fitted data for different detector distances
       sp=sphere(q=q,R=13,detDist=8000,collDist=8000.)

      The above decorator is equivalent to the following. Use `smearedsphere` as smeared model function.
      ::

       def sphere(q,R,bgr,detDist=3000,collDist=2000.,contrast=1):
           sp = js.ff.sphere(q,R,contrast)
           sp.Y=sp.Y+bgr
           return sp
       smearedsphere=js.sas.smear(sphere,beamProfile=resol2m)

    * To **fit SAXS and SANS data together** (also with different collimation)
      use the parameter beamProfile in the model.
      If calling the smeared model with a valid beamProfile this is used instead of the one defined in @smear
      One may remind that also pinhole SAXS has a smearing even if it is small.
      Ask your instrument responsible for reasonable values or do a measurement of the primary beam.

      This allows fitting with different profiles if the corresponding data contain
      .beamProfile as attribute. See :ref:`Fitting multiple smeared data together`.
      ::

       fbeam = js.sas.prepareBeamProfile(0.02)
       fbeam2 = js.sas.prepareBeamProfile(0.01)

       # define smeared model with beamProfile as parameter
       @js.sas.smear(beamProfile=fbeam)
       def sphere(q,R,bgr,contrast=1, beamProfile=None):
           sp = js.ff.sphere(q=q,radius=R,contrast=contrast)
           sp.Y=sp.Y+bgr
           return sp

       # call as
       sphere(q=q,R=13,bgr=0,beamProfile=fbeam2)

       # to fit data add corresponding beamProfile attributeto each dataArray in a dataList
       dll[0].beamProfile=fbeam
       dll[1].beamProfile=fbeam2
       dll.fit(sphere,.....)


    **Smear explicit data**

    Explicit data show artifacts due to smearing at the edges if extrapolation is done wrong.
    The default is a constant value from the edge which is good for a low q plateau or a high q flat background.
    For the above model smearing this is not important as the q range is automatically extended.
    For desmearing e.g. of multi detector distance SANS data this is important
    if detector edges are within a nonconstant region.
    ::

     import jscatter as js
     #define beamprofile
     resol8m = js.sas.prepareBeamProfile('SANS', detDist=8000,collDist=8000.,wavelength=0.4,wavespread=0.10,
                                         collAperture=15, sampleAperture=5, dpixelWidth=10, dringwidth=1,)
     resol8m2 = js.sas.prepareBeamProfile('SANS', detDist=8000,collDist=8000.,wavelength=0.4,wavespread=0.10,
                                         collAperture=15, sampleAperture=5, dpixelWidth=10, dringwidth=1,
                                         extrapolfunc=['guinier',None])
     # create some data
     q=js.loglist(0.01,1,300)
     sp=js.ff.sphere(q,radius=13)
     #  smear data
     spsmeared=js.sas.smear(sp,beamProfile=resol8m)
     # smear in a limited range, default is extrapolation with constant edge value
     spsmeared2=js.sas.smear(sp[:,sp.X>0.2],beamProfile=resol8m)
     # guinier like extrapolation
     spsmeared2ex=js.sas.smear(sp[:,sp.X>0.2],beamProfile=resol8m2)

     # plot it
     p=js.grace(1,1)
     p.plot(sp)
     p.plot(spsmeared,li=[1,3,1],sy=0)
     p.plot(spsmeared2,li=[1,3,2],sy=0,le='low edge underestimate')
     p.plot(spsmeared2ex,li=[1,3,3],sy=0,le='low edge improved')
     p.yaxis(scale='log',min=10000,max=1e8)
     p.legend(x=0.2,y=1e5)
     p.new_graph(xmin=0.5,xmax=0.9,ymin=0.55,ymax=0.9)
     xs=(spsmeared.X>0.18) & (spsmeared.X<0.25)
     p[1].plot(spsmeared[:,xs],li=[1,3,1],sy=0)
     xs=(spsmeared2.X>0.18) & (spsmeared2.X<0.25)
     p[1].plot(spsmeared2[:,xs],li=[1,3,2],sy=0)
     p[1].plot(spsmeared2ex[:,xs],li=[1,3,3],sy=0)
     p[1].yaxis(scale='log',min=8e6,max=2e7)
     p[0].title('Examine smearing at edge')

    - If *unsmeared* has attributes a, b, dIW, bxw, detDist these are used for the beamProfile,
      if not given in function call.
    - If wavelength is missing in data a default of 0.155418 nm for Xray :math:`K_{\alpha}` line is assumed.
      For SANS 0.6 A.
    - During smearing for Kratky camera an integration over the beam width and beam length are performed.
      In this integration :math:`q_{w,l}= ((q+q_{w})^2)+q_{l}^2)^{1/2}` is used with :math:`q_{w}` along the
      beam width and :math:`q_{l}` along the beam length. in regions :math:`q_{w,l} > max(q_{data})`
      we estimate the measured scattering intensity by the mean of the last 10 points of the measured
      spectra to allow for a maximum in :math:`q` range.
      The strictly valid q range can be estimated by calculating :math:`q_{x,y} < max(q)`
      with 2 times the used beam width and beam length.
      As the smearing for larger :math:`q`  has no real effect the estimate might be still ok.

    Examples
    --------
    For more examples see
    :ref:`How to build a more complex model`,
    :ref:`How to fit SANS data including the resolution for different detector distances` and
    :ref:`Smearing and desmearing of SAX and SANS data`.
    ::

     import jscatter as js
     q=js.loglist(0.01,4,300)

     def sphere(q,R,bgr,contrast=1):
         sp = js.ff.sphere(q,R,contrast)
         sp.Y=sp.Y+bgr
         return sp
     #
     # prepare different beamprofiles
     beam=js.sas.readpdh(js.examples.datapath+'/BeamProfile.pdh')
     mbeam = js.sas.prepareBeamProfile(beam , bxw=0.01, dIW=1.)
     tbeam = js.sas.prepareBeamProfile('trapez', a=mbeam.a, b=mbeam.b, bxw=0.01, dIW=1)
     Sbeam1 = js.sas.prepareBeamProfile('SANS', detDist=1000,wavelength=0.4,wavespread=0.1)
     Sbeam2 = js.sas.prepareBeamProfile('SANS', detDist=10000,wavelength=0.4,wavespread=0.1)
     # Gbeam = js.sas.prepareBeamProfile(measurement,explicit=3)

     # smear data
     data=sphere(q,R=13,bgr=1000)
     datasm= js.sas.smear(unsmeared=data,beamProfile=mbeam)
     datast= js.sas.smear(unsmeared=data,beamProfile=tbeam)
     datasS1= js.sas.smear(unsmeared=data,beamProfile=Sbeam1)
     datasS2= js.sas.smear(unsmeared=data,beamProfile=Sbeam2)
     # datasG= js.sas.smear(unsmeared=data,beamProfile=Gbeam)

     p=js.grace()
     for dat in [data,datasm,datast,datasS1,datasS2,]:
        p.plot(dat)
     p.yaxis(scale='l')
     p.xaxis(scale='l')

    """

    if beamProfile is None:
        raise TypeError('beamProfile not defined. Only use keyword arguments by calling smear.')

    if unsmeared is None or formel._getFuncCode(unsmeared):
        # smear is used as a decorator for a model function and we wrap with smearing

        # in case it was not a preparedBeamProfile (prepareBeamProfile return unchanged profiles)
        beamProfile = prepareBeamProfile(beamProfile, **smkwargs)

        def _smeared(model):
            # arguments of model function
            usarg =model.usarg = inspect.getfullargspec(model)
            # get attribute starting with q or Q
            qarg = model.qarg = next((v for i, v in enumerate(usarg.args) if v[0] in 'qQ'), None)

            # functools.wraps presents arguments and doc of model to the outside
            # the original function is in __wrapped__
            @functools.wraps(model)
            def _smearer(*args, **kwargs):
                # check if explicit beamProfile is in kwargs, otherwise use from decorator
                if 'beamProfile' in kwargs and hasattr(kwargs['beamProfile'], 'isBeamProfile'):
                    _beamProfile = kwargs['beamProfile']
                else:
                    _beamProfile = beamProfile

                if _beamProfile.beamProfType[0] == 'S':
                    # SANS like (2 pinholes)
                    # update beamProfileAttr if attr are in kwargs
                    _beamProfileAttr=_beamProfile.resFunctAttr
                    # remove one needless attribute
                    _=_beamProfileAttr.pop('extrapolfunc', None)

                    # update beamProfileAttr by current kwargs
                    for _k in dict(_beamProfileAttr):
                        if _k in kwargs:
                            _beamProfileAttr.update({_k: kwargs[_k]})

                    if None in _beamProfileAttr.values():
                        # None in beamProfileAttr bypasses smearing
                        return model(**_callargs)

                    # get dict with model call arguments
                    _callargs = inspect.getcallargs(model, *args, **kwargs)
                    # get qarg values, get frame and extend range, then update
                    _q=_callargs[qarg]
                    _xexl, _xexh =_estimateFrame(_q, **_beamProfileAttr)
                    _lqh = np.r_[_xexl, _q, _xexh]
                    _callargs.update({qarg: _lqh})

                    # calc model values in extended range
                    _data = model(**_callargs)

                    # smear it with additional frame
                    _dataa = resFunct(_data, extrapolfunc='NO', **_beamProfileAttr)
                    _dataa.setColumnIndex(iey=None)
                    _dataa.beamProfile = _beamProfile
                    # return with original size
                    return _dataa[:, len(_xexl):-len(_xexh)]

                elif _beamProfile.beamProfType[0] == 'e':
                    # explicit given sigma
                    _nn = 8
                    # get dict with model call arguments
                    _callargs = inspect.getcallargs(model, *args, **kwargs)
                    # get qarg values, get frame and increase, then update
                    _q=_callargs[qarg]
                    _xexl = loglist(max(0, _q.min() - 3 * _beamProfile.Y.min()), _q.min(), 3 * _nn)[:-1]  # low q
                    _xexh = loglist(_q.max(), _q.max() + 3 * _beamProfile.Y.max(), 3 * _nn)[:-1]  # high q
                    _lqh = np.r_[_xexl, _q, _xexh]
                    _callargs.update({qarg: _lqh})

                    # calc model values in extended range
                    _data = model(**_callargs)

                    # smear it with borders
                    _dataa = resFunctExplicit(_data, _beamProfile, extrapolfunc='NO')
                    _dataa.setColumnIndex(iey=None)
                    _dataa.beamProfile = _beamProfile
                    # return with original size
                    return _dataa[:, len(_xexl):-len(_xexh)]
                else:
                    # trapz (Kratky Camera)
                    # get dict with model call arguments
                    _callargs = inspect.getcallargs(model, *args, **kwargs)
                    # calc model values in extended range
                    _dataa = model(**_callargs)
                    _dataa.tckUnsm = interpolate.splrep(_dataa.X, _dataa.Y, s=0)
                    _dataa.beamProfile = _beamProfile
                    _dataa.Y = _smear(_dataa.X, _dataa)
                    return _dataa

            return _smearer

        if unsmeared is None:
            # called as decorator
            return _smeared
        else:
            # called as function
            return _smeared(unsmeared)

    else:
        # its just data and we smear it
        dataa = copy.copy(unsmeared)
        dataa.beamProfile = prepareBeamProfile(beamProfile, **smkwargs)
        #  smear data
        if dataa.beamProfile.beamProfType[0] == 'S':
            # calculate parameters for cubic spline representation of the data
            dataa.tckUnsm = interpolate.splrep(dataa.X, dataa.Y, s=0)
            dataa = resFunct(dataa, **beamProfile.resFunctAttr)
        elif dataa.beamProfile.beamProfType[0] == 'e':
            # explicit given sigma
            dataa = resFunctExplicit(dataa, beamProfile)
        else:
            # calculate parameters for cubic spline representation of the data
            dataa.tckUnsm = interpolate.splrep(dataa.X, dataa.Y, s=0)
            dataa.Y = _smear(dataa.X, dataa)
        dataa.setColumnIndex(iey=None)
        return dataa


def desmear(Ios, beamProfile, NIterations=-15, windowsize=4, qmax=4, output=True, **kwargs):
    """
    Desmearing of measured data according to Lake algorithm with possibility to stop recursion at best desmearing.
    
    For negative NIterations the iterations are stopped if a convergence criterion reaches
    a minimum as described by Vad [2]_.
    In each step a smoothing based on the ratio desmeared/observed as described in [2]_
    is used (point average with windowsize).

    Parameters
    ----------
    Ios : dataArray
        Original smeared data
    beamProfile : dataArray
        Beam profile as prepared with prepareBeamProfile
    NIterations : int, default=-15
        Number of iterations to stop.
        Negative values indicate to stop when convergence criterion increases again (as described by Vad [2]_)
        and abs(NIterations) is maximum number of iterations.
    qmax : float, default=4
        Maximum in scattering vector q up to where the convergence criterion is evaluated.
        This reduces the influence of the noise at larger a.
    windowsize : odd int , default=4
        Window size for smoothing in each step of desmearing (running average).
    output : bool
        Print output.

    Returns
    -------
        dataArray
    
    References
    ----------
    .. [1] Lake, J. A. (1967). Acta Cryst. 23, 191–194.
    .. [2] Comparison of iterative desmearing procedures for one-dimensional small-angle scattering data
           Vad and Sager, J. Appl. Cryst. (2011) 44,32-42
    
    """
    beamProfile = prepareBeamProfile(beamProfile, **kwargs)
    # lists of desmeared data start from os (original smeared) for iterations
    Idesmeared = dL(Ios.copy())
    Idesmeared[-1].convergence = 1
    Idesmeared[-1].decreasing = True
    Idesmeared[-1].chi2 = 1
    # Iterations of Lake desmearing
    if output:
        print('Steps, current meangamma, minimal meangamma')
    while True:
        Idesmeared.append(Idesmeared[-1].copy())  # just generate new dataArray
        Ismeared = smear(unsmeared=Idesmeared[-2], beamProfile=beamProfile)  # smear it
        gamman = Idesmeared[0].Y / Ismeared.Y  # generate convergence criterion
        Idesmeared[-1].Y = Idesmeared[0].Y * smooth(Idesmeared[-2].Y / Idesmeared[0].Y,
                                                    windowsize) * gamman  # calc iteration with smoothing
        meangamma = np.abs(gamman[Idesmeared[0].X < qmax].mean() - 1)  # calc convergence criterion
        Idesmeared[-1].chi2 = ((Ismeared.Y - Idesmeared[0].Y) ** 2).mean()  # chi**2 distance
        # does convergence increase again then we finish and stop
        Idesmeared[-1].decreasing = (meangamma <= Idesmeared.convergence.array.min())
        Idesmeared[-1].convergence = meangamma  # store convergence criterion close to zero
        # smooth the last step in iteration

        if output:
            print('{0:3} {1:8.5g} {2:8.5g} '.format(len(Idesmeared), meangamma, Idesmeared.convergence.array.min(),),
              Idesmeared[-1].decreasing)
        if len(Idesmeared) >= abs(NIterations):
            if output:
                print('len(Idesmeared) = NIterations', len(Idesmeared))
            return Idesmeared[-1]
        if (NIterations < 0) and (not Idesmeared[-1].decreasing and not Idesmeared[-2].decreasing):
            return Idesmeared[Idesmeared.convergence.array.argmin()]
    return 'Error'  # this is never reached


# noinspection PyIncorrectDocstring
def prepareBeamProfile(data=None, **kwargs):
    r"""
    Prepare beamProfile from beam profile measurement or according to given parameters.
    
    Parameters
    ----------
    data : dataArray,'trapez','SANS', float
        Contains measured beam profile, explicit Gaussian width list or type 'SANS', 'trapz'.
         - dataArray: Beam profile measurement for **line collimation** as measured during adjustment of a Kratky camera.
           The beam profile looks like a trapez. The measured beam profile will be smoothed and made symmetric.
         - dataArray + keyword 'explicit': Explicit given **Gaussian width for each Q* value (see below).
           Missing values will be interpolated.
           The explicit given width should have same units as scattering vector q in the data.
           Needs additional parameter *explicit* set. E.g. all data from KWS2@MLZ have this in 4th column of data.
         - float : A beam profile (similar to 'explicit') with a **single Gaussian width** will be used.
           The explicit given width should have same units as scattering vector q in the data.
           This can be used for explicit measured beam profile from the attenuated primary beam
           in SAXS/SANS if it looks Gaussian.
         - 'trapez' : **Line collimation** with trapezoidal parameters
                      Needs: a, b, bxw, dIW.
         - 'SANS' : **Smearing a la Pedersen**; see resFunct for parameters
                     - Needs:  collDist, collAperture, detDist, sampleAperture, wavelength, wavespread,
                       dpixelWidth, dringwidth, extrapolfunc
                     - This can also be used for SAXS with appropriate values for wavespread and aperture sizes.
    collDist,collAperture,detDist,sampleAperture : float
        Parameters as described in resFunct for SANS.
        These are determined from the experimental setup.
    wavelength,wavespread,dpixelWidth,dringwidth,extrapolfunc : float
        Parameters as described in resFunct for SANS.
        These are determined from the experimental setup.
    explicit : int
        For explicit given Gaussian width the index of the column with the width.
        For merged dataFiles of KWS2@MLZ this is the forth column with index 3.
        The width should have same units as q.
    a : float
        Larger full length of trapezoidal profile in detector q units.
        Ignored for measured profile.
    b : float
        Shorter full length of trapezoidal profile in detector q units
        If a=b ==> a=a*(1+1e-7), b=b*(1-1e-7)
        Ignored for measured profile.
    bxw : float,dataArray
        Beam width profile.
        Use getBeamWidth to cut the primary beam and fit a Gaussian.
        A float describes the beam half-width at half maximum (hwhm of Gaussian).
        If bxw is the profile prepared by getBeamWidth the experimental profile is used.
    dIW : float
        Detector slit width in detector q units.
        Length on detector to integrate parallel to beam length for line collimation.
        On my SAXSpace this is 1.332 as given in the header of the file (20 mm in real coordinates).
    wavelength : float,
        Wavelength in nm
        default 0.155418 nm for SAXS 0.5 nm for SANS
    detDist : float, default 305.3558
        Detector distance in units mm
        Default is detector distance of SAXSpace


    Returns
    -------
       beamProfile as dataArray

    Notes
    -----
     - For measured beam profiles in line collimation parameters a,b
       are determined from the flanks for trapezoidal profile.
     - Detector q units are equivalent to the pixel distance as expressed in a corrected measurement.
     - For 'explicit' Gaussian width a SANS measurement as on KWS2 can be used which has sigma as 4th column.
       Missing values are interpolated.

    Examples
    --------
    ::

     # use as
     # a single width for all e.g. primary beam measurement
     fbeam= js.sas.prepareBeamProfile(0.01)
     # prepare measured beamprofile for line collimation
     mbeam = js.sas.prepareBeamProfile(beam, bxw=0.01, dIW=1.)
     # prepare profile with trapezoidal shape (a,b are fitted above)
     tbeam = js.sas.prepareBeamProfile('trapz', a=mbeam.a, b=mbeam.b, bxw=0.01, dIW=1)
     # prepare profile SANS (missing parameters get defaults)
     Sbeam = js.sas.prepareBeamProfile('SANS', detDist=2000,wavelength=0.4,wavespread=0.15)
     # prepare profile with explicit given Gaussian width in column 3 as e.g. KWS2@MLZ
     Gbeam = js.sas.prepareBeamProfile(measurement,explicit=3)


    """
    if hasattr(data, 'isBeamProfile'):
        # fast return if it is already beamprofile
        return data
    elif hasattr(data, '_isdataArray') and 'explicit' in kwargs:
        # a column in data contains explicit sigma values for all q
        beam = data[np.r_[0, kwargs['explicit']]]
        beam.beamProfType = 'explicit'
    elif hasattr(data, '_isdataArray'):
        # data is line collimation measurement of beam profile
        beam = data[:2].prune(number=100)  # cut 3rd column as it contains NANs for SAXSpace
        beam.beamProfType = 'measured'
    elif isinstance(data,numbers.Number):
        # a single width is given
        beam = dA(np.c_[[0.1, 1], [data, data]].T)
        beam.beamProfType = 'explicit'
    else:
        # an empty array data ist string 'SANS' or 'trapz'
        beam = zeros((2, 6))
        beam.beamProfType = data
    for attr in ['collDist', 'collAperture', 'detDist', 'sampleAperture', 'wavespread', 'dpixelWidth',
                 'dringwidth', 'extrapolfunc', 'wavelength', 'a', 'b', 'dIW', 'bxw']:
        if attr in kwargs:
            setattr(beam, attr, kwargs[attr])
    if beam.beamProfType == 'measured':
        # make it symmetric as it was measured line collimation
        if not hasattr(beam, 'wavelength'): beam.wavelength = 0.155418  # K_alpha in nm as default
        if not hasattr(beam, 'detDist'):    beam.detDist = 305.3558  # distance for SAXSpace in mm
        if not hasattr(beam, 'dIW'): beam.dIW = 0
        if not hasattr(beam, 'bxw'): beam.bxw = 0
        beam.qscale = 2 * np.pi / beam.wavelength / beam.detDist  # factor for q units
        beam.Y = beam.Y - beam.Y.min()
        center = beam.X[beam.Y > (beam.Y.max() * 0.8)].mean()
        beam.X -= center
        ml = min((beam.X < 0).sum(), (beam.X > 0).sum())
        if (beam.X < 0).sum() > (beam.X > 0).sum():
            beam.Y[-2 * ml:] = (beam.Y[-2 * ml:] + beam.Y[-2 * ml:][::-1]) / 2.
        else:
            beam.Y[:2 * ml] = (beam.Y[:2 * ml] + beam.Y[:2 * ml][::-1]) / 2.
        # normalize to integral=1
        beam.Y = beam.Y / np.trapz(beam.Y, beam.X)
        highflanc = beam.where(lambda a: (a.Y < beam.Y.max() * 0.9) & (a.X > 0))
        top = beam.where(lambda a: (a.Y > beam.Y.max() * 0.9))
        topmean = top.where(lambda a: abs(a.X) < abs(a.X).max() * 0.9).Y.mean()
        pf = np.polyfit(highflanc.X, highflanc.Y, 1)
        beam.a = -2 * pf[1] / pf[0]
        beam.b = 2 * (topmean - pf[1]) / pf[0]
    elif beam.beamProfType == 'trapez':
        # For trapezoidal beam profile, make sure that a > b
        if not hasattr(beam, 'wavelength'): beam.wavelength = 0.155418  # K_alpha in nm as default
        if not hasattr(beam, 'detDist'):    beam.detDist = 305.3558  # distance for SAXSpace in mm
        if not hasattr(beam, 'dIW'): beam.dIW = 0
        if not hasattr(beam, 'bxw'):
            beam.bxw = 0
        elif hasattr(beam.bxw, '_isdataArray'):
            # use the extracted parameter from measured data
            beam.bxw = beam.bxw.hwhm
        beam.qscale = 2 * np.pi / beam.wavelength / beam.detDist  # factor for q units
        if beam.a == beam.b:
            beam.a *= 1 + 1e-7
            beam.b *= 1 - 1e-7
        if beam.a < beam.b:
            beam.a, beam.b = beam.b, beam.a
        beam.X = [-beam.a, -beam.a / 2., -beam.b / 2., beam.b / 2., beam.a / 2., beam.a]
        beam.Y = [0, 0, 1, 1, 0, 0]
        beam.Y = beam.Y /np.trapz(beam.Y, beam.X)
    elif beam.beamProfType == 'SANS':
        # SANS with Pedersen smearing, only parameters needed
        beam.resFunctAttr = dict()
        for attr in ['collDist', 'collAperture', 'detDist', 'sampleAperture', 'wavelength', 'wavespread', 'dpixelWidth',
                     'dringwidth', 'extrapolfunc']:
            if attr in kwargs:
                beam.resFunctAttr[attr] = kwargs[attr]
    elif beam.beamProfType == 'explicit':
        pass
    else:
        raise TypeError('beam profile type not recognized!')
    beam.isBeamProfile = True
    return beam


def getBeamWidth(empty, minmax='auto', show=False):
    """
    Extract primary beam of empty cell or buffer measurement for semitransparent beam stops. Used for Kratky camera.

    The primary beam is searched and cut between the next minima found, then normalized.
    Additionally a Gaussian fit is done and hwhm is included in result profile.

    Parameters
    ----------
    empty : dataArray
        Empty cell measurement with the transmitted beam included.
    minmax : 'auto',[float,float]
        Automatic or interval for search of primary beam.
        E.g. [-0.03,0.03] allow for explicitly setting the interval.
    show : bool
        Show the fit result


    Returns
    -------
        dataArray with beam width profile
         .sigma sigma of fit with Gaussian
         .hwhm  half width half maximum

    """

    if minmax[0] == 'a':  # auto
        # for normal empty cell or buffer measurement the primary beam is the maximum
        imax = imin = empty.Y.argmax()
        while empty.Y[imax + 1] < empty.Y[imax]:      imax += 1
        while empty.Y[imin - 1] < empty.Y[imin]:      imin -= 1
        xmax = empty.X[imax]
        xmin = empty.X[imin]
    else:
        xmin = minmax[0]
        xmax = minmax[1]
    primarybeam = empty.prune(lower=xmin, upper=xmax)
    primarybeam.Y -= primarybeam.Y.min()
    norm = scipy.integrate.simps(primarybeam.Y, primarybeam.X)
    primarybeam.Y = primarybeam.Y /norm
    try:
        primarybeam.eY = primarybeam.eY /norm
    except AttributeError:
        pass
    # estimate for width and A
    width=0.015
    A=(primarybeam.Y.max()-primarybeam.Y.min())*width*2
    primarybeam.fit(_gauss,
                    {'mean': 0, 'sigma': width, 'bgr': empty.Y.min(), 'A': A}, {},
                    {'x': 'X'},output=show)
    primarybeam.hwhm = primarybeam.sigma * np.sqrt(np.log(2.0))
    primarybeam.peakmax = primarybeam.modelValues(x=primarybeam.mean).Y[0]
    if show:
        primarybeam.showlastErrPlot()
    return primarybeam


def plotBeamProfile(beam, p=None):
    """
    Plots beam profile and weight function according to parameters in beam. Used for Kratky camera.

    Parameters
    ----------
    beam
        beam with parameters
    p : GracePlot instance
        Reuse the given plot

    """

    wY = _wBLength(beam)
    wX = _wBWidth(beam)

    if p is None:
        p = grace()
        p.multi(2, 1)

    p[0].plot(wY, li=[1, 3, 1], sy=0, legend='Y profile a=%.3g  b=%.3g ' % (beam.a, beam.b))
    p[0].plot(wX[0], wX[1] / (wX[1].max()), li=[1, 3, 2], sy=0,
              legend='X profile hw=%.4g max %.3g ' % (beam.bxw, wX[1].max()))
    p[1].plot(beam, li=[1, 3, 2], sy=0, legend='weight function ')

    p[0].yaxis(label='weight')
    p[0].xaxis(label='x,y')
    p[1].yaxis(label='profile')
    p[1].xaxis(label='x,y')
    p[0].title("Beam Length Profile and Weighting Function")
    p[0].legend(x=1, y=0.9)
    p[1].legend(x=4, y=beam.Y.max())
    return p


# noinspection PyProtectedMember
def AgBeReference(q, wavelength, n=np.r_[1:10], ampn=None, domainsize=100, udw=0.1, asym=0, lg=1):
    """
    The scattering intensity expected from AgBe as a reference for wavelength calibration.

    The intensities assume a d-spacing of 5.8378 nm and a reduction of the intensity as q**-2.
    The domain size determines the width according to Scherrer equation [2]_. The first peak is at 1.076 1/nm.
    The result needs to be convoluted with the instrument resolution by resFunct or smear.

    Parameters
    ----------
    q : array
        Wavevector
    wavelength : float
        Wavelength
    n : array of int
        Order of the peaks.
    ampn : list of float
        Amplitudes of the peaks
    domainsize : float
        Domainsize of AgBe crystals in nm.
        default 100 nm as is given in [1]_.
    udw : float
        Displacement u in Debye Waller factor exp(-u**2*q**2/3)
    asym : float
        Factor asymmetry in Voigt function describing the peaks.
    lg : float
        Lorenzian/gaussian fraction of both FWHM, describes the contributions of gaussian and lorenzian shape.
        See Voigt for details.

    Returns
    -------
    dataArray

    References
    ----------
    .. [1] T. C. Huang, H. Toraya, T. N. Blanton and Y. Wu
           X-ray Powder Diffraction Analysis of Silver Behenate, a Possible Low-Angle Diffraction Standard
           J. Appl.Cryst.(1993).26,180-184
    .. [2] Patterson, A.
           The Scherrer Formula for X-Ray Particle Size Determination
           Phys. Rev. 56 (10): 978–982 (1939)
           doi:10.1103/PhysRev.56.978.

    """
    if ampn is None:
        ampn = [1] * 10
    dspacing = 5.8378  # nm
    braggAngle = 2 * np.arcsin(n * wavelength / 2. / dspacing)  # as 2*Theta
    theta = lambda q: 2 * np.arcsin(q / 4 / np.pi * wavelength)
    # Scherer equation for broadening due to finite size
    beta = 0.9 * wavelength / (domainsize * np.cos(braggAngle))  # beta is FWHM in rad
    # the peaks are described as Gaussians in theta
    peaks = np.c_[[voigt(theta(q), center=m, lg=lg, fwhm=fw, asym=asym).Y * a for m, fw, a in
                   zip(braggAngle, beta, ampn)]].sum(axis=0) / q ** 2 * np.exp(-q ** 2 * udw ** 2 / 3.)
    result = dA(np.c_[q, peaks].T)
    result.setColumnIndex(iey=None)
    result.columnname = 'wavevector; intensity'
    result.rf_modelname = sys._getframe().f_code.co_name
    return result


def _estimateFrame(X, collDist=8000., collAperture=10, detDist=8000., sampleAperture=10, wavelength=0.5,
                   wavespread=0.2, dpixelWidth=10, dringwidth=1, nn=8):
    """
    Estimate width of resolution function of q independent contributions and additional values at edges
    for convolution.

    Parameters
    ----------
    X : array
        Original q values
    nn : int
        Additional points per sigma
    collDist, collAperture, detDist, sampleAperture, dpixelWidth, dringwidth, wavelength : float
        See resFunct

    Returns :
        xexl, xexh
        with
        xexl : extended x values lower X
        xexh : extended x values higher X


    """
    if detDist == 0 or collDist == 0:
        return [],[]
    L = collDist
    r1 = collAperture
    l = detDist
    r2 = sampleAperture
    dq = dpixelWidth * dringwidth / l
    # wave vector of incomming neutrons
    k0 = 2 * np.pi / wavelength
    # maximum angles of aperture edge
    a1 = r1 / (L + l)
    a2 = r2 / l
    # dbeta estimate at low q for extrapolation to low q
    if a1 >= a2:
        dbeta = 2 * r1 / L
    else:
        dbeta = 2 * r2 * (1 / L + 1 / l)

    # for extrapolation at edges we need an estimate of sigma
    # sigma squared width from q independent part at low q + maximum wavespread
    # + finite collimation + detector resolution dq
    sigma = (((k0 * dbeta) ** 2 + (k0 * dq) ** 2) / 8 / math.log(2) + (X.max() * wavespread) ** 2 / (
                8 * math.log(2))) ** 0.5

    # extent by 3 sigma to low and high q
    xexl = loglist(max(0, X.min() - 3 * sigma), X.min(), 3 * nn)[:-1]  # low q
    xexh = loglist(X.max(), X.max() + 3 * sigma, 3 * nn)[:-1]  # high q

    return xexl, xexh


def _extrapolateY(S, xexl, xexh, extrapolfunc=None):
    """
    Extrapolate data for given values.
    Returns new Y values
    """
    if isinstance(extrapolfunc, type('')):
        # no extrapolation
        return S.Y
    # extrapolate the Y values in xexl region
    if extrapolfunc is None or extrapolfunc == 0:
        extrapolfunc = [None, None]
    if isinstance(extrapolfunc, (numbers.Number)):
        extrapolfunc = [extrapolfunc, extrapolfunc]
    if len(xexl) ==0:
        pass
    elif extrapolfunc[0] is None or extrapolfunc[0] == 0:
        # this uses smallest value to extrapolate
        Y = np.r_[np.interp(xexl, S.X, S.Y), S.Y]
    elif isinstance(extrapolfunc[0], (numbers.Number)):
        q = extrapolfunc[0]
        # apply inverse power and reverse it after polyfit
        Y = np.r_[S.prune(upper=S.X.min() * 3).polyfit(xexl, 1, lambda yy: yy ** (1 / q)).Y ** q, S.Y]
    else:
        # Guinier like after log it should be quadratic
        Y = np.r_[np.exp(S.prune(upper=S.X.min() * 3).polyfit(xexl, 2, np.log).Y), S.Y]
    # extrapolate the Y values in xexh region
    if len(xexh) == 0:
        pass
    elif extrapolfunc[1] is None:
        # this uses largest value to extrapolate
        Y = np.r_[Y, np.interp(xexh, S.X, S.Y)]
    elif isinstance(extrapolfunc[1], (numbers.Number)):
        q = extrapolfunc[1]
        # apply inverse power and reverse it after polyfit
        Y = np.r_[Y, S.prune(lower=S.X.max() - sigma).polyfit(xexh, 1, lambda yy: yy ** (1 / q)).Y ** q]
    return Y


def resFunct(S, collDist=8000., collAperture=10, detDist=8000., sampleAperture=10,
             wavelength=0.5, wavespread=0.2, dpixelWidth=10, dringwidth=1, extrapolfunc=None):
    """
    Resolution smearing of small angle scattering for SANS/SAXS according to Pedersen
    for radial averaged data.

    :math:`I(q_0)= \int R(q,q_0)S(q)dq`  with  Kernel :math:`R(q,q0)` of equ. 33 in [1]_ including wavelength spread,
    finite collimation and detector resolution. Default parameters are typical for a SANS machine like KWS2@JCNS with
    rectangular apertures.

    To smear model functions (also for fitting) please use *smear* directly,
    which handles extrapolation at edges automatically.

    **If explicit data are smeared (not a model) edges can be extrapolated as power law, Guinier like or constant.**
    Best practice is to calculate the used model for extended Q range, smear it and prune to the needed data range.
    This is demonstrated in example 2.

    Parameters
    ----------
    S : array like
        Model scattering function as dataArray with X. and .Y
        q in 1/nm  .Y can be arbitrary unit.
    collDist : float, default 8000
        Collimation distance in mm. If 0 unsmeared data are returned.
    collAperture : float, default 10
        Collimation aperture rectangular size in mm
    detDist : float, default 8000
         Detector distance in mm. If 0 unsmeared data are returned.
    sampleAperture : float, default 10
        Sample  aperture rectangular size in mm
    wavelength : float, default 0.5
        Wavelength in nm
    wavespread : float, default 0.1
        FWHM wavelengthspread dlambda/lambda
    dpixelWidth : float, default 10
        Detector pixel width in mm
    dringwidth : integer, default 1
        Number of pixel for averaging
    extrapolfunc : list , default None
        Type of extrapolation at low and high X edges as list for [low edge,high edge].
        If a singe value is given this is used for both.
         - '' : no interpolation
         - Low edge towards zero
          - float :   Power law extrapolation
          - None :    A constant value as Y(X.min()).
          - anything else : Low X data are log scaled, then X**2 extrapolated as Guinier like extrapolation.
         - High edge towards infinity
          - float :   Power law extrapolation of low X e.g. a=-4 for  q**a for Porod scaling.
          - None :    A constant value as Y(X.max()).

    Returns
    -------
    dataArray ['wavevector; smeared scattering; unsmeared scattering; half width smearing function']

    Notes
    -----
     - HalfWidthSmearingFunction is the FWHM the Gaussian used for smearing including all effects.
     - The resolution is assumed to be equal in direction parallel and perpendicular to q on a 2D detector as
       described in chap. 2.5 in [1]_.
     - We neglect additional smearing due to radial averaging (last paragraph in chap 2.5 of [1]_).
     - Defaults correspond to a typical medium resolution measurement.
     - extrapolfunc allows extrapolation at both edges to reduce edge effects.
       The best values depends on the measured signal shape at the edge.
       The optimal way is to calculate the used model for the whole Q range, smear it and prune to the needed range.
       This is demonstrated in example 2.
       If at low *q* only a power law is observed use the corresponding extrapolation. Same for high *q*.
     - An example for SANS fitting with resFunc is given in example_SANSsmearing.py.

    Examples
    --------
    Reproducing Table 1 of [1]_ ::

     import jscatter as js
     q=js.loglist(0.1,10,500)
     S=js.ff.sphere(q,6)
     # this is the direct call of resFunc, use smear instead as shown in next example
     Sr=js.sas.resFunct(S, collDist=2000.0, collAperture=20, detDist=2000.0, sampleAperture=10, wavelength=0.5,
                                                  wavespread=0.2,dpixelWidth=0,dringwidth=0)
     # plot it
     p=js.grace()
     p.plot( S,sy=[1,0.3],li=1,legend='sphere')
     p.plot( Sr,sy=[2,0.3,2],li=2,legend='smeared sphere')
     p.plot(Sr.X,Sr[-1],li=4,sy=0,legend='FWHM in nm\S-1 ')
     p.yaxis(min=1e-3,scale='l',charsize=1.5,label='I(q) / a.u.',tick=[10,9])
     p.yaxis(min=1e-1,tick=[10,9])
     p.xaxis(scale='l',charsize=1.5,label='q / nm\S-1',tick=[10,9])
     p.legend(x=0.8,y=5e5)

    Example 2:

    Smear model over full range and interpolate to needed data.
    This is a way to smear a model for fitting, but is not possible for desmearing of measured data.
    *smear* extends the q range according to the width and does proper integration without interpolation.
    *smear* the preferred method.
    ::

     meas=js.dA('measureddata.dat')     # load data
     # define profile
     resol2m = js.sas.prepareBeamProfile('SANS', detDist=2000,collDist=2000.,wavelength=0.4,wavespread=0.15)
     q=np.r_[0.01:5:0.01]
     #  or extend q range as np.r_[0:meas.X.min():0.01,meas.X,meas.X.max():meas.X.max()*2:0.1]
     # calc model
     temp=js.ff.ellipsoid(q,2,3)
     # smear it
     smearedmodel=js.sas.smear(temp,resol2m).interpolate(X=meas.X)



    References
    ----------
    .. [1] Analytical Treatment of the Resolution Function for Small-Angle Scattering
           JAN SKOV PEDERSEN, DORTHE POSSELTAND KELL MORTENSEN J. Appl. Cryst. (1990). 23, 321-333

    """
    if detDist == 0 or collDist == 0:
        result = dA(np.c_[S.X, S.Y, S.Y, S.X*0].T)
        result.setattr(S)
        return result
    L = collDist
    r1 = collAperture
    l = detDist
    r2 = sampleAperture
    dq = dpixelWidth * dringwidth / l
    # wave vector of incomming neutrons
    k0 = 2 * np.pi / wavelength
    # maximum angles of aperture edge
    a1 = r1 / (L + l)
    a2 = r2 / l

    if isinstance(extrapolfunc, type('')):
        # no extrapolation
        xexl, xexh = [], []
        Y = S.Y
    else:
        # for extrapolation at edges we need an estimate of sigma and additional x values at lower and higher edges
        xexl, xexh = _estimateFrame(S.X, L, r1, l, r2, wavelength, wavespread, dpixelWidth, dringwidth)
        # do the extrapolation
        Y=_extrapolateY(S, xexl, xexh, extrapolfunc)

    # make this 2dim for later
    XT = np.r_[xexl, S.X, xexh][:, None]

    # calc th full width of the resolution function
    # now the full dbeta 1+2
    # 8*math.log(2) scales as FWHM**2= 8*math.log(2) * sigma**2
    # 2*theta
    theta2 = 2 * np.arcsin(S.X / (2 * k0))
    cos2theta = np.cos(theta2)
    # dbeta
    if a1 >= a2:
        dbeta1 = 2 * r1 / L - 0.5 * r2 * r2 / (r1 * l * l * L) * cos2theta ** 4 * (L + l / cos2theta ** 2) ** 2
        # dbeta2 = 2 * r1 / L - 0.5 * r2 * r2 / (r1 * l * l * L) * cos2theta ** 2 * (L + l / cos2theta) ** 2
    else:
        dbeta1 = 2 * r2 * (1 / L + cos2theta ** 2 / l) - 0.5 * r1 * r1 / r2 * l / L / (
                    cos2theta ** 2 * (L + l / cos2theta ** 2))
        # dbeta2 = 2 * r2 * (1 / L + cos2theta / l) - 0.5 * r1 * r1 / r2 * l / L / (cos2theta * (L + l / cos2theta))
    # sigmas finite collimation
    sigma2c1 = k0 ** 2 * np.cos(theta2 / 2) ** 2 * dbeta1 ** 2 / (8 * math.log(2))
    # sigma2c2=k0**2*dbeta2**2/(8*math.log(2))
    # sigmas detector resolution
    sigma2d1 = k0 ** 2 * np.cos(theta2 / 2) ** 2 * cos2theta ** 2 * dq ** 2 / (8 * math.log(2))
    # sigma2d2=k0**2*cos2theta**2*dq**2/(8*math.log(2))
    # wavelength dependent part of sigma**2 + collimation part + detector resolution
    sigma2 = (S.X * wavespread) ** 2 / (8 * math.log(2)) + sigma2c1 + sigma2d1

    # R is Kernel for convolution as 2D matrix
    # equation 33 in [1]_ for all q
    # with  axis=1 for q_average and axis=0 for the q integration over gaussian resolution with width sigma
    # modified Bessel function of first kind zeroth order    =>>>    scipy.special.i0e exp scaled
    # np.abs(XT*S.X/sigma2) is related to rescale the exp scaled bessel func
    R = (XT / sigma2) * np.exp(-0.5 * ((XT ** 2 + S.X ** 2) / sigma2) + np.abs(XT * S.X / sigma2)) * \
        special.i0e(XT * S.X / sigma2)  # this consumes the main computing time 385 ms of 410ms
    # width dx between Q values for integration;
    # first and last are taken full as kind of extrapolation with value of border
    dx = XT * 0
    dx[1:-1] = ((XT[2:] - XT[:-2]) / 2.)
    dx[0] = (XT[1] - XT[0]) / 2  # above zero
    dx[-1] = XT[-1] - XT[-2]  # assume extend to inf

    # integrate over kernel dx*R*Y and normalize integral dx*R
    SR = (dx * R * Y[:, None]).sum(axis=0) / (R * dx).sum(axis=0)

    result = dA(np.c_[S.X, SR, S.Y, 2 * (2 * math.log(2)) ** 0.5 * sigma2 ** 0.5].T)
    result.setattr(S)
    result.setColumnIndex(iey=None)
    result.columnname = 'wavevector; smeared scattering; unsmeared scattering; half width smearing function'
    result.rf_collDist = collDist
    result.rf_collAperture = collAperture
    result.rf_detDist = detDist
    result.rf_sampleAperture = sampleAperture
    result.rf_detectorResolution = dq
    result.rf_modelname = sys._getframe().f_code.co_name
    result.rf_extrapolX = XT.T[0]
    result.rf_extrapolY = Y
    result.rf_wavelength = wavelength
    result.rf_wavespread = wavespread
    result.rf_extrapolfunc = str(extrapolfunc)
    return result


# noinspection PyProtectedMember
def resFunctExplicit(S, beamprofile, extrapolfunc=None):
    """
    Resolution smearing of small angle scattering for SANS/SAXS according to explict given Gaussian width.
    Used in smear.

    :math:`I(q_0)= \int R(q,q_0)S(q)dq`  with  Gaussian kernel :math:`R(q,q0)` in equ. 33 in [1]_.
    E.g. for merged dataFiles of KWS2@MLZ the explicit width is given in the 4th column.

    To smear model functions (also for fitting) please use *smear* directly,
    which handles extrapolation at edges automatically.

    Parameters
    ----------
    S : array like
        Scattering function (model) as dataArray with X. and .Y
        q in 1/nm, .Y can be arbitrary unit
    beamprofile : beamProfile prepared by 'explicit' or float
        Beam profile as prepared from prepareBeamProfile with 'explicit' given values for all q
        or with a single width for all q. See prepareBeamProfile.
    extrapolfunc : list , default None
        Type of extrapolation at low and high X edges for handling of the border as list for [low edge,high edge].
        If a singe value is given this is used for both.
         - '' : no interpolation
         - Low edge
          - float :   Power law extrapolation of low X e.g. a=-4 for  q**a for Porod scaling.
          - None :    A constant value as Y(X.min()).
          - anything else : Low X data are log scaled, then X**2 extrapolated as Guinier like extrapolation.
         - High edge
          - float :   Power law extrapolation of low X e.g. a=-4 for  q**a for Porod scaling.
          - None :    A constant value as Y(X.max()).

    Returns
    -------
    dataArray
        columns ['wavevector; smeared scattering; unsmeared scattering; half width smearing function']

    Notes
    -----
     - HalfWidthSmearingFunction is the FWHM the Gaussian used for smearing including all effects.

    """
    # number of points to extrapolate per sigma
    nn = 8

    if isinstance(extrapolfunc, type('')):
        # no extrapolation
        xexl, xexh = [], []
        Y = S.Y
    else:
        # extent by 3 sigma to low and high q
        xexl = loglist(max(0, S.X.min() - 3 * beamprofile.Y.min()), S.X.min(), 3 * nn)[:-1]  # low q
        xexh = loglist(S.X.max(), S.X.max() + 3 * beamprofile.Y.max(), 3 * nn)[:-1]  # high q
        # do the extrapolation
        Y=_extrapolateY(S, xexl, xexh, extrapolfunc)

    # make this 2dim for later
    XT = np.r_[xexl, S.X, xexh][:, None]

    # R is Kernel for convolution as 2D matrix
    # with  axis=1 for q_average and axis=0 for the q integration over gaussian resolution with width sigma
    sigma = beamprofile.interp(S.X)
    R = np.exp(-0.5 * ((XT - S.X) ** 2 / sigma**2)) / (np.sqrt(2 * np.pi) * sigma)  # consumes the main computing time
    # width dx between Q values for integration; first and
    # last are taken full as kind of extrapolation with value of border
    dx = XT * 0
    dx[1:-1] = ((XT[2:] - XT[:-2]) / 2.)
    dx[0] = (XT[1] - XT[0]) / 2  # above zero
    dx[-1] = XT[-1] - XT[-2]  # assume extend to inf

    # integrate over kernel dx*R*Y and normalize integral dx*R
    SR = (dx * R * Y[:, None]).sum(axis=0) / (R * dx).sum(axis=0)

    result = dA(np.c_[S.X, SR, S.Y, sigma].T)
    result.setattr(S)
    result.setColumnIndex(iey=None)
    result.columnname = 'wavevector; smeared scattering; unsmeared scattering; sigma smearing function'
    result.rf_modelname = sys._getframe().f_code.co_name
    result.rf_extrapolX = XT.T[0]
    result.rf_extrapolY = Y
    result.rf_extrapolfunc = str(extrapolfunc)
    return result


# noinspection PyAugmentAssignment
def waterXrayScattering(composition='h2o1', T=293, units='mol'):
    """
    Absolute scattering of water with components (salt, buffer) at Q=0 as reference for X-ray.

    According to [2]_ a buffer of water with components might be used.
    Ions need to be given separatly as ['55.51h2o1','0.15Na1','0.15Cl1'] for 0.15 M NaCl solution.
    It is accounted for the temperature dependence of water density and compressibility.

    Parameters
    ----------
    composition : string
        Buffer composition as in scatteringLengthDensityCalc
        give dissociated ions separatly as ['1Na','1Cl'] with concentration in mol prepended
        the additional scattering as ionic liquid of the ions in water is taken into account see [2]_
        mass in g; 1000g water are 55.508 mol
    T : float
        Temperature in °K
    units : 'mol'
        Anything except 'mol' prepended unit is mass fraction.
        'mol' prepended units is mol and mass fraction is calculated as :math:`mass=[mol] mass_{molecule}`
        e.g. 1l Water with 123 mmol NaCl   ['55.508H2O1','0.123Na1','0.123Cl1']

    Returns
    -------
        float absolute scattering length in Units 1/cm

    References
    ----------
    .. [1] SAXS experiments on absolute scale with Kratky systems using water as a secondary standard
           Doris Orthaber et al. J. Appl. Cryst. (2000). 33, 218±225
    .. [2] A high sensitivity pinhole camera for soft condensed matter
           T. Zemb, O. Tache, F. Né, and O. Spalla, J. Appl. Crystallogr. 36, 800 (2003).

    Notes
    -----
    :math:`I(0)=(\sigma_{water}^2f_e^2 n_{ew}^2 k_B T \chi + \sum_{ci} n_i N_A 1000 n_{ei}^2 f_e^2 )/100`

    with

     - :math:`\sigma_{water}` water density
     - :math:`\chi`           compressibility
     - :math:`n_{ew}`     number of electrons per water molecule
     - :math:`f_e`        cross section of electron in nm
     - :math:`k_B`        Boltzmann constant
     - :math:`n_i`        concentration component i
     - :math:`n_{ei}`     number of electrons per molecule component i in Mol
     - :math:`\sum_{ci}`   is done for all ions separately if given

    """
    # Units is MMTK
    # k_MMTK=0.00831447086363271 # in  kJ/mol/K
    k = 1.3806488e-23  # J/K
    mw = 18.01528
    I0 = 0
    ch2o = 0
    cd2o = 0
    if isinstance(composition, str):
        composition = [composition]
    for compo in composition:
        compo = compo.lower()
        # decompose in numbers and characters
        decomp = re.findall('\d+\.\d+|\d+|\D+', compo)
        if not re.match('\d+\.\d+|\d+', decomp[-1]):
            raise KeyError('last %s Element missing following number ' % decomp[-1])
        if not re.match('\d', decomp[0]):  # add a 1 as concentration in front if not there
            decomp = [1] + decomp
        mass = np.sum([Elements[ele][1] * float(num) for ele, num in zip(decomp[1:][::2], decomp[1:][1::2])])
        nei = np.sum([Elements[ele][0] * float(num) for ele, num in zip(decomp[1:][::2], decomp[1:][1::2])])
        if units.lower() == 'mol':
            ci = float(decomp[0])
        else:
            # if units!=mol we convert here from  mass to mol fraction
            ci = float(decomp[0]) / mass
        if ''.join(decomp[1:]) == 'h2o1':
            ch2o += ci
        elif ''.join(decomp[1:]) == 'd2o1':
            cd2o += ci
        else:
            # units in m
            I0 += ci * constants.N_A * 1000 * (felectron * 1e-9) ** 2 * nei ** 2  # in mol/m**3...
    dhfraction = cd2o / (ch2o + cd2o) if ch2o + cd2o != 0 else 0
    I0 = I0 /(ch2o + cd2o) / (1000 / mw)
    #  from g/ml to  m**-3
    water_density = waterdensity(['%.4f' % (1 - dhfraction) + 'h2o1', '%.4f' % dhfraction + 'd2o1'],
                                 T=T) * 1e6 / mw * constants.N_A
    chi = watercompressibility(d2ofract=dhfraction, T=T, units='bar') * 1e-5  # in 1/Pa
    I0 += water_density ** 2 * (felectron * 1e-9 * 10) ** 2 * k * T * chi
    return I0 / 100.  # in 1/cm


def _find_peak(beam, edge):
    imax = imin = beam.Y[beam.X < edge].argmax()
    transmission = beam.Y[imax - 2:imax + 3].mean()
    # search for minima around transmission peak
    while beam.Y[imax + 1] < beam.Y[imax]:       imax += 1
    while beam.Y[imin - 1] < beam.Y[imin]:       imin -= 1
    temp = beam[:, imin:imax]
    centerTransmissionPeak = (temp.X * temp.Y / temp.Y.sum()).mean()
    return centerTransmissionPeak, transmission


def transmissionCorrection(data, dark, emptybeam=None, edge=0.03, exposure=None):
    r"""
    Subtract dark current, find primary beam, get transmission and normalize by transmission and exposure time.
    IN PLACE.

    For measurements including the primary beam from a semitransparent beamstop as from SAXSpace.
    Transmission is the maximum of the primary beam peak after dark subtraction.
    Allows easier comparison of measurements  with aged source (primary intensity change).


    Parameters
    ----------
    data : dataArray
        A measurement from a SAXSpace instrument read by js.dA('filename.pdh',lines2parameter=[2,3,4])
    dark : dataArray
        Dark current measurement.
    emptybeam : dataArray,default=None
        Empty beam measurement to subtract from measurement. dark will be subtracted of empty beam.
    edge : float, default 0.03
        Wavevector value below beam stop edge. The primary beam is searched below this value.
    exposure : float, default None
        Exposure time in unit 's'.
        If not given the xml description at the end of the file is examined.

    Returns
    -------
        None

    Notes
    -----
    Files from SAXSpace instrument (.pdh) can be read by
    ::

     js.dA('filename.pdh',lines2parameter=[2,3,4])

    **Correction**

    Brulet at al [1]_ describe the data correction for SANS, which is in principle also valid for SAXS,
    if incoherent contributions are neglected.

    The difference is, that SAXS has typical transmission around ~0.3 for 1mm water sample in quartz cell
    due to absorption, while in SANS typical values are around ~0.9 for D2O.
    Larger volume fractions in the sample play a more important rule for SANS as hydrogenated ingredients
    reduce the transmission significantly, while in SAXS still the water and the cell (quartz) dominate.

    One finds for a sample inside of a container with thicknesses (:math:`z`)
    for sample, buffer (solvent), empty cell and empty beam measurement (omitting the overall q dependence):

    .. math:: I_s = \frac{1}{z_S}\big((\frac{I_S-I_{dark}}{T_S}-I_{b}T_S\big) -
                                \big(\frac{I_{EC}-I_{dark}}{T_{EC}}-I_{b}T_{EC})\big) -
                    \frac{1}{z_B}\big((\frac{I_B-I_{dark}}{T_B}-I_{b}T_B\big) -
                                \big(\frac{I_{EC}-I_{dark}}{T_{EC}}-I_{b}T_{EC})\big)

    where
     - :math:`I_s`      is the interesting species
     - :math:`I_S`      is the sample of species in solvent (buffer)
     - :math:`I_B`      is the pure solvent (describing a constant background)
     - :math:`I_{dark}` is the dark current measurement
     - :math:`I_b`      is the empty beam measurement
     - :math:`I_{EC}`   is the empty cell measurement
     - :math:`z_x`      corresponding sample thickness
     - :math:`T_x`      corresponding transmission

    The recurring pattern :math:`\big((\frac{I-I_{dark}}{T}-I_{b}T\big)` shows that the the beam tail
    (border of primary beam not absorbed by the beam stop) is attenuated by the corresponding sample.

    For equal sample thickness :math:`z` the empty beam is included in subtraction of  :math:`I_B`:

    .. math:: I_s = \frac{1}{z} \big((\frac{I_S-I_{dark}}{T_S}-I_{b}T_S) - (\frac{I_B-I_{dark}}{T_B}-I_{b}T_B)\big)

    **The simple case**

    If the transmissions are nearly equal as for e.g. protein samples with low concentration (:math:`T_S \approx T_B`)
    we only need to subtract the transmission and dark current corrected buffer measurement from the sample.

    .. math:: I_s = \frac{1}{z} \big((\frac{I_S-I_{dark}}{T_S}) - (\frac{I_B-I_{dark}}{T_B}\big)

    **Higher accuracy for large volume fractions**

    For larger volume fractions :math:`\Phi` the transmission might be different and we have to take into account that
    only :math:`1-\Phi` of solvent contributes to :math:`I_S`.
    We may incorporate this in the sense of an optical density changing the effective thickness
    :math:`\frac{1}{z_B}\rightarrow\frac{1-\Phi}{z_B}` resulting in different thicknesses :math:`z_S \neq z_B`


    **Transmission**

    The transmission is measured as the ratio :math:`T=\frac{I(q=0)_{sample}}{I(q=0)_{emptybeam}}` with :math:`I(q=0)`
    as the primary beam intensity.

    If the primary beam tail is neglected in the above equation :math:`I(q=0)_{emptybeam}`
    only gives a common scaling factor and can be omitted if arbitrary units are used.
    Alternatively one can scale to the EC transmission with :math:`T_{EC}=1`
    For absolute calibration the same needs to be done.
    One finds :math:`T_{sample in cell}=T_{empty cell}T_{sample without cell}`.



    References
    ----------
    .. [1] Improvement of data treatment in small-angle neutron scattering
           Brûlet et al Journal of Applied Crystallography 40, 165-177 (2007)


    """
    if hasattr(data, 'transmission'):
        print('data has .transmission. It was already corrected and is not changed.')
        return
    if emptybeam is None or hasattr(emptybeam, 'transmission'):
        pass
    else:
        transmissionCorrection(emptybeam, dark, emptybeam=None, edge=edge, exposure=None)

    if data.X.min() > 0:
        raise Exception('data seem to have no transmission peak ')
    if exposure is None:
        addXMLParameter(data)
    else:
        data.Exposure = [exposure, 's']
    if not hasattr(data, 'Exposure'):
        raise Exception('No exposure time found or given.')

    # dark subtraction
    data.Y -= dark.Y
    try:
        data.eY = (data.eY ** 2 + dark.eY ** 2) ** 0.5
    except AttributeError:
        pass

    # get transmission and peak
    tp, bt = _find_peak(data, edge)
    data.centerTransmissionPeak = tp
    data.transmission = bt

    # normalize by exposure and transmission
    data.Y = data.Y / data.Exposure[0] / data.transmission
    data.eY = data.eY / data.Exposure[0] / data.transmission
    # scale and subtract emptybeam if given
    if emptybeam is not None:
        try:
            # subtract emptybeam
            data.Y -= (data.transmission * emptybeam.Y)
            data.eY = (data.eY ** 2 + (data.transmission * emptybeam.eY) ** 2) ** 0.5
        except AttributeError:
            pass


def _w2f(word):
    """converts string word if possible to float"""
    try:
        return float(word)
    except (ValueError, TypeError):
        return word


def autoscaleYinoverlapX(dataa, key=None, keep='lowest'):
    """
    Scales elements of data to have same mean .Y value in the overlap region of .X .

    Parameters
    ----------
    dataa : dataList
        Data to scale
    key : string
        Data are grouped into unique values of attribute key before scaling.
        E.g. to do it for a series of concentrations for each concentration individually.
    keep : default 'l'
        If 'l' the lowest X are kept and higher X are scaled successively to next lower X.
        Anything else highest X are kept and other are scaled to next higher.

    Returns
    -------
    dataList
        new scaled dataList

    Notes
    -----
    First data are sorted along .X.mean()
    scaling value is stored in .autoscalefactor

    """
    result = dL()
    if key is not None and hasattr(dataa, key):
        values = np.unique(getattr(dataa, key))
    else:
        values = [None]
    for uniquevalues in values:
        if uniquevalues is not None:
            data = dataa.filter(lambda a: getattr(a, key) == uniquevalues).copy()
        else:
            data = dataa.copy()
        data.sort(key=lambda ee: ee.X.mean())
        if keep[0] in ('l', 0):
            d = -1
            for i in range(len(data) - 1, 0, -1):
                meani0 = data[i].where(lambda a: a.X < data[i + d].X.max()).Y.mean()
                meani1 = data[i + d].where(lambda a: a.X > data[i].X.min()).Y.mean()
                data[i + d][1] *= meani0 / meani1
                data[i + d].autoscalefactor = meani0 / meani1
            data[-1].autoscalefactor = 1
        else:
            d = 1
            for i in range(len(data) - 1):
                meani0 = data[i].where(lambda a: a.X > data[i + d].X.min()).Y.mean()
                meani1 = data[i + d].where(lambda a: a.X < data[i].X.max()).Y.mean()
                data[i + d][1] *= meani0 / meani1
                data[i + d].autoscalefactor = meani0 / meani1
            data[0].autoscalefactor = 1
        result.append(data)
    return result


def removeSpikesMinmaxMethod(dataa, order=7, sigma=2, nrepeat=1, removePoints=None):
    """
    Takes a dataset and removes single spikes from data by substitution with spline.

    Find minima and maxima of data including double point spikes; no 3 point spikes
    scipy.signal.argrelextrema with np.greater and np.less are used to find extrema

    Parameters
    ----------
    dataa : dataArray
        Dataset with eY data.
    order : int
        Number of points see scipy.signal.argrelextrema.
        Distance between extrema.
    sigma : float
        Deviation factor from std dev; from eY.
        If datapoint -spline> sigma*std its a spike.
    nrepeat : int
        Repeat the procedure nrepeat times.
    removePoints : list of integer
        Instrument related points to remove because of dead pixels.
        'JCNS' results in a list for SAXSPACE at JCNS Jülich.

    Returns
    -------
    data with spikes removed

    """
    SAXSPACE = [0, 1, 134, 135, 530, 539, 540, 1011, 1012, 1091, 1092, 1287, 1312, 1451, 1452, 1502, 1503, 1606, 1607,
                1810, 1811, 1893, 1912, 1913, 1933, 1934]
    if removePoints == 'JCNS':
        removePoints = SAXSPACE
    elif not isinstance(removePoints, list):
        removePoints = []
    # make copy
    data = dataa.copy()
    takepoints = np.array([i not in removePoints for i in range(len(data.Y))])
    data = data[:, takepoints]

    def getpeaklist(data, order=7):
        """
        find minima and maxima of data including double spikes
        no 3 point spikes
        """
        # find minima and maxima
        llgreater = scipy.signal.argrelextrema(data.Y, np.greater, order=order, mode='wrap')[0]
        llless = scipy.signal.argrelextrema(data.Y, np.less, order=order, mode='wrap')[0]
        doubles = []  # list of neighbouring pixel
        # check in between llgreater intervals if edges are also spikes
        for i, j in zip(llgreater[:-1], llgreater[1:]):
            intervalmax = scipy.signal.argrelextrema(data.Y[i + 1:j], np.greater, order=order, mode='wrap')[0]
            if len(intervalmax) > 0:  # if an max is found check edges
                if min(intervalmax) == 0:
                    doubles.append(min(intervalmax) + i + 1)
                if max(intervalmax) == len(data.Y[i + 1:j]):
                    doubles.append(max(intervalmax) + i + 1)
        for i, j in zip(llless[:-1], llless[1:]):
            intervalmax = scipy.signal.argrelextrema(data.Y[i + 1:j], np.less, order=order, mode='wrap')[0]
            if len(intervalmax) > 0:
                if min(intervalmax) == 0:
                    doubles.append(min(intervalmax) + i + 1)
                if max(intervalmax) == len(data.Y[i + 1:j]):
                    doubles.append(max(intervalmax) + i + 1)
        return np.r_[llgreater, llless, np.array(doubles)]

    def reldif2(data, spline, sigma=1):
        # check if distance is larger than sigma
        return abs((data.Y - spline(data.X)) / data.eY) > sigma

    while nrepeat > 0:
        peaklist = getpeaklist(data, order=order)
        # which point is peak
        peaks = np.array([i in peaklist for i in range(len(data.Y))])
        # spline without the peaks '~' is 'not'
        spline = scipy.interpolate.UnivariateSpline(data.X[~peaks], data.Y[~peaks], s=0)
        # remove the spikes and substitute with spline of surrounding if  peak and > sigma
        # removeSpikes=lambda data,n,sigma:np.where(reldif2(data,spline,n,sigma=sigma) &
        #  peaks,meansurrounding(data,n),data.Y)
        removespikes = lambda data, sigma: np.where(reldif2(data, spline, sigma=sigma) & peaks, spline(data.X), data.Y)
        data.Y = removespikes(data, sigma=sigma)
        nrepeat -= 1
    return data


def removeSpikes(dataa, xmin=None, xmax=None, medwindow=5, SGwindow=None, sigma=0.2, SGorder=2):
    """
    Takes a dataset and removes single spikes.

    A median filter is used to find single spikes.
    If abs(data.Y-medianY)/data.eY>sigma then the medianY value is used.
    If SGwindow!=None  Savitzky-Golay filtered values are used.
    If sigma is 0 then new values (median or Savitzky-Golay filtered) are used everywhere.

    Parameters
    ----------
    xmin,xmax : float
        Minimum and maximum X values
    dataa : dataArray
        Dataset with eY data
    medwindow : odd integer
        window size of scipy.signal.medfilt
    SGwindow : odd int, None
        Savitzky-Golay filter see scipy.signal.savgol_filter
        without the spikes; window should be smaller than instrument resolution
    SGorder : int
        Polynomial order of scipy.signal.savgol_filter
        needs to be smaller than SGwindow
    sigma : float
        Relative deviation from eY
        If datapoint-median> sigma*eY its a spike

    Returns
    -------
    Filtered and smoothed dataArray

    """
    # make copy
    data = copy.deepcopy(dataa)
    if not isinstance(sigma, numbers.Number):
        sigma = 0.
    if xmin is None: xmin = min(data.X)
    if xmax is None: xmax = max(data.X)
    if SGwindow == 0: SGwindow = None
    # median filter to remove spikes
    Ynew = scipy.signal.medfilt(data.Y, medwindow)
    # decide where a spike is found --> if difference is larger than sigma
    spikesat = abs(data.Y - Ynew) / data.eY > sigma
    # logical limits
    limits = np.logical_and(data.X > xmin, data.X < xmax)
    if isinstance(SGwindow, numbers.Integral):
        # Savgol as smoothed signal
        # window smaller than resolution
        Ynew = scipy.signal.savgol_filter(np.where(spikesat, Ynew, data.Y), SGwindow, order)
    else:
        # remove only the spikes and substitute with Ynew
        Ynew = np.where(spikesat, Ynew, data.Y)
    # data.Y=np.where(np.logical_and(spikesat,limits),Ynew,data.Y)
    data.Y = np.where(limits, Ynew, data.Y)
    data.smoothed_SGwindow = SGwindow
    data.smoothed_sigma = sigma
    data.smoothed_medwindow = medwindow
    data.smoothed_SGorder = SGorder
    return data


def addXMLParameter(data):
    """
    Adds the parameters stored in xml part of a .pdh file as eg. in SAXSPACE .pdh files.

    Parameters
    ----------
    data : dataArray
        Already read pdh file.
        XML content is found in comments of the read files and starts with '<'.


    """
    if hasattr(data, '_isdataArray'):
        datalist = [data]
    elif hasattr(dataa, '_isdataList'):
        datalist = data
    else:
        raise Exception(data, ' is not dataArray or dataList')
    for dat in datalist:
        lines = [c for c in dat.comment if c.startswith('<')]
        try:
            root = xml.etree.ElementTree.fromstringlist(lines)
            for par in root.iter('parameter'):
                setattr(dat, par[2].text, [_w2f(par[ii].text) for ii in (3, 1)])
        except:
            raise Warning('No xml data found. Go on.')


def locateFiles(pattern, root=os.curdir):
    """
    Locate all files matching supplied filename pattern in and below supplied root directory.

    Parameters
    ----------
    pattern : file pattern
        Pattern used in fnmatch.filter
    root : directory, default is os.curdir
        Directory where to start

    Returns
    -------
        File list

    """
    matchfiles = []
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            matchfiles.append(os.path.join(path, filename))
    return matchfiles


def copyFiles(pattern, root=os.curdir, destination='copy', link=False):
    """
    Copies all files matching pattern in tree below root to destination directory

    Parameters
    ----------
    pattern : file pattern
        Pattern used in fnmatch.filter
    root : directory, default is os.curdir
        Directory where to start
    destination : dirname
        Destination
    link : bool
       If True links are created.


    """
    files = locateFiles(pattern, root=root)
    if not os.path.exists(destination):
        os.mkdir(destination)
    for ff in files:
        newname = os.path.join(destination, os.path.basename(ff))
        print(newname)
        if not link:
            shutil.copy2(ff, newname)
        else:
            os.symlink(ff, newname)
    return


def moveSAXSPACE(pattern, root='./', destination='./despiked', medwindow=5, SGwindow=5, sigma=0.2,
                 order=2):
    """
    Read SAXSPACE .pdh files and removes spikes by removeSpikes.

    This is mainly for use at JCNS SAXSPACE with CCD camera as detector :-))))

    Parameters
    ----------
    pattern : string
        Search pattern for filenames
    root : string
        Root path
    destination : string
        Where to save the files
    medwindow : odd integer
        Window size of scipy.signal.medfilt
    SGwindow : odd int, None
        Savitzky-Golay filter see scipy.signal.savgol_filter
    order : int
        Polynominal order of scipy.signal.savgol_filter
    sigma : float
        Deviation factor of eY
        If datapoint-median> sigma*std its a spike

    Notes
    -----
    Default values are adjusted to typical SAXSPACE measurement.

    """
    files = locateFiles(pattern, root=root)
    if not os.path.exists(destination):
        os.mkdir(destination)
    for file1 in files:
        if 'BeamProfile' in file1: continue
        newname = os.path.join(destination, os.path.basename(file1))
        print(file1, '->', newname)
        f = open(file1, 'rU')
        filecontent = f.readlines()
        f.close()
        header = filecontent[:2 + 3]
        nlines = int(header[2].split()[0])
        numbers = filecontent[2 + 3:2 + 3 + nlines]
        footer = filecontent[2 + 3 + nlines:]
        data = dA(numbers)
        datanew = removeSpikes(data, xmin=None, medwindow=medwindow, SGwindow=SGwindow, sigma=sigma, SGorder=order)
        f = open(newname, 'w')
        f.writelines(header)
        np.savetxt(f, datanew.T, delimiter='   ', fmt='%10.6E')
        f.writelines(footer)
        f.close()
    return
