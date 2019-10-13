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
Cloud can represent any object described by a cloud of (different) scatterers with
scattering amplitudes as constant, sphere scattering amplitude,
Gaussian scattering amplitude or explicitly given ones.

The scattering of a cloud can represent the scattering of a **cluster of particles** with polydispersity
and position distortion according to root mean square displacements (rms).
Polydispersity and rms displacements are randomly changed within the explicit orientational average to represent
an ensemble average (opposite to the time average of a single cluster).

The cloud can represent a **particle lattice** in a nano particle to describe the Bragg peaks or be used as a kind
of volume integrations for **arbitrary shaped particles**.
Additional complex objects composed of different types of subparticles can be created.
E.g a hollow sphere decorated by Gaussian chains. See `cloudscattering examples` below.

The scattering is calculated by explicit calculation with a spherical average to allow inclusion of
polydispersity, position distortion and because its faster for large numbers of particles (>1000).
For small number of particles the Debye equation can be used but without polydispersity and position distortion.
See :py:func:`~.cloudscattering.cloudScattering`

Note:
    Models that are build by positioning of differently shaped particles might depict
    approximations of the real scattering as overlaps are not considered or
    changes of specific configurations due to the presence of another particle might change.
    As an example we look at  :py:func:`~.formfactor.sphereGaussianCorona`. The Gaussian coils have overlap
    with the inner sphere and for high aggregation numbers the coil overlap is not described correctly.

    Nevertheless these approximations might be useful to describe general features of a scattering pattern.
    Additional one might consider that analytic models as a e.g. a sphere are approximations itself neglecting
    surface roughness, interfaces, deviations from symmetry or anisotropy and
    break down if a length scale of internal building blocks as e.g. atoms is reached.

**Cloudscattering examples**

Check the source
 - :py:func:`~.formfactor.decoratedCoreShell`
 - :py:func:`~.formfactor.linearPearls`
 - :py:func:`~.formfactor.superball`
 - :py:func:`~.structurefactor.latticeStructureFactor`
 - :ref:`A nano cube build of different lattices`

Cloudscattering results are normalized by :math:`I_0=(\sum b_i)^2` to equal one for q=0
(except for polydispersity).

===============

"""
from __future__ import division

import inspect

import numpy as np
import numbers

from . import formel
from . import parallel

from .dataarray import dataArray as dA
from .dataarray import dataList as dL


try:
    from . import fscatter
    useFortran = True
except ImportError:
    useFortran = False


def _fa_sphere(qr):
    """
    scattering amplitude sphere with catching the zero
    """
    fa = lambda qr: 3 / qr ** 3 * (np.sin(qr) - qr * np.cos(qr))
    return np.piecewise(qr, [qr == 0], [1, fa])


def _scattering(point, r, q, blength, iff, formfactoramp=None, rms=0, ffpolydispersity=0):
    """
    Coherent scattering of objects at positions r in direction point on sphere with length (radius) q

    Parameters
    ----------
    point : point on unit sphere 3 x 1
    q : float
        q vector length
    r : array  N x 3
        vector of objekt positions
    blength : array N
        scattering length of objects
    iff : Nxinteger
        indices of form factors
    formfactoramp ixN array
        formfactoramp of all objects
    rms: float
        position rms
    ffpolydispersity : float
        size rms by scaling of size

    Returns
    -------
    F(Q)*F(Q).conj() , F(Q).sum()

    pure numpy way as option
    """
    if useFortran:
        # speedup 2.41 : 1.1  for  cloudScattering(q,insidegrid) on ncpu=1 comparing this fortran and below
        # speedup  38.5 : 4.75   for  ncpu=6 and 9261 points with rms>0
        ret = fscatter.cloud.ffq(point, r, q, blength, iff, formfactoramp, rms, ffpolydispersity)
        # print(ret,point,r.shape)
        return ret[0], ret[1], ret[2]
    else:
        if ffpolydispersity > 0:
            # normal distribution of size factor
            sizerms = np.random.randn(r.shape[0]) * ffpolydispersity + 1
            # corresponding relative volume change
            volrmsfactor = sizerms ** 3
            volrmsfactor[sizerms <= 0] = 0
            # interpolate with volume change weight
            fa=np.zeros_like(blength)
            for i in range(len(formfactoramp[1, :]), 1):
                chose = iff==i
                fa[chose] = volrmsfactor[chose] * np.interp(q * sizerms[chose], formfactoramp[0, :], formfactoramp[i, :])
        else:
            # interpolate the formfactoramp
            fa = np.array([np.interp(q, formfactoramp[0, :], amp) for amp in formfactoramp[1:]])
            fa=fa[iff-1]
        qx = q * point
        if rms > 0:
            r += np.random.randn(r.shape[0], 3) * rms
        iqr = np.einsum('i,ji', qx, r) * 1j  # 454 µs        iqr.shape 26135
        beiqrsum = np.einsum('i,i', blength * fa, np.exp(iqr))
        Sq = beiqrsum * beiqrsum.conj()  # 2 µs
        return q, Sq.real, beiqrsum.real


def _sphaverage_scattering(q, r, blength, iff, formfactoramp=None, rms=0, ffpolydispersity=0, relError=50):
    """
    Coherent scattering of objects at positions r in after oriental average.

    Parameters
    ----------
    q : float
        q vector length
    r : array  N x 3
        vector of objekt positions
    blength : array N
        scattering length of objects
    formfactoramp 2xN array
        formfactoramp of all objects
    rms: float
        position rms
    ffpolydispersity : float
        size rms by scaling of size
    relError : int
        determines number of points on Fibonacci lattice on sphere

    Returns
    -------
    Q, <F(Q)*F(Q).conj()> , <F(Q).sum()>

    """
    # call Fortran sphere average for ffq
    ret = fscatter.cloud.sphereaverage_ffq(q, r, blength, iff, formfactoramp, rms, ffpolydispersity, relError)
    return ret[0], ret[1], ret[2]


def _scattering_Debye(q, r, blength, iff, formfactoramp):
    """
    Debye equation  definition as in _scattering
    """
    iff1=iff-1
    if q == 0:
        return blength.sum() ** 2
    # interpolate the formfactoramp
    fa = np.array([np.interp(q, formfactoramp[0, :], amp) for amp in formfactoramp[1:]])

    # ()**2.sum()**0.5 to get absolute value |ri-rj|
    qrij = q * ((r[:, np.newaxis] - r) ** 2).sum(axis=2) ** 0.5  # 137 ms r.shape (1856, 3)
    np.fill_diagonal(qrij, 1)  # 19 µs
    sinoq = np.sin(qrij) / qrij  # 47.7 ms   still faster than np.sinc
    np.fill_diagonal(sinoq, 1)  # 19.4 µs
    Sq = np.einsum('i,j,ij->', blength*fa[iff1], blength*fa[iff1], sinoq)  # 10.3 ms
    return Sq


def cloudScattering(q, cloud, relError=50, formfactor=None, V=None, rms=0, ffpolydispersity=0, ncpu=0):
    r"""
    Scattering of a cloud of scatterers with variable scattering length. Uses multiprocessing.

    Cloud can represent any object described by a cloud of scatterers with scattering amplitudes
    as constant, sphere scattering amplitude, Gaussian scattering amplitude or explicitly given one.
    The result is normalized by :math:`I_0=(\sum b_i)^2` to equal one for q=0 (except for polydispersity).

    - .I0 represents the forward scattering if :math:`b_i=b_vV_{unit cell}` with :math:`b_v` as
      scattering length density in the unit cell.
    - Remember that the atomic bond length are on the order 0.1-0.2 nm.
    - Methods to build clouds of scatterers e.g. a cube decorated with spheres at the corners can be
      found in :ref:`Lattice` with examples.
    - By default explicit spherical average is done. If rms and polydispersity are not needed the Debye-function
      can be used (for particle numbers<1000 it is faster).

    Parameters
    ----------
    q : array, ndim= Nx1
         Radial wavevectors in 1/nm
    cloud : array Nx3 or Nx4 or Nx5
        - Center of mass positions (in nm) of the N scatterers in the cloud.
        - If given cloud[3] is the scattering length :math:`b_i` at positions cloud[:3], otherwise :math:`b=1`.
        - Ff given cloud[4] is the column index in formfactor for a specific scatterer.
        - To compare with material scattering length density :math:`b_v` use :math:`b=b_vV_{unit cell}` with
          :math:`b_v` as scattering length density and :math:`V_{unit cell}` as cloud unit cell volume.
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
        Root mean square displacement :math:`\langleu^2\rangle^{0.5} of the positions in cloud as
        random (Gaussian) displacements in nm.
        Displacement u is random for each orientation in sphere scattering.
        rms results in a Debye-Waller factor.
    formfactor : None,'gauss','sphere', array
        Gridpoint scattering amplitudes F_a(q) are described by:
         - None    : const scattering amplitude.
         - 'sphere': Sphere scattering amplitude according to [3]_ equal for all cloud points.
                     Parameter V is needed to determine :math:`R`.
                     The sphere radius is :math:`R=(\frac{3V}{4\pi})^{1/3}`
         - 'gauss' : Gaussian function  :math:`b_i(q)=b V exp(-\pi V^{2/3}q^2)` according to [2]_
                     equal for all cloud points. The Gaussian shows no artificial minima compared to the sphere.
                     Parameter V needed to determine :math:`b_i`.
         - Explicit isotropic formfactor as array with [q,ff1(q),ff2(q),ff3(q),....].
            - If multiple formfactors are given the formfactor for a cloud point needs to be given in cloud[4]
            - The normalized scattering amplitude fa for each cloud point is calculated as fa=ffi**0.5/fai(0).
              Missing values are linear interpolated (np.interp), q values outside interval are mapped to qmin or qmax.
            - Explicit formfactors are assumed to be isotropic.
    V : float, default=None
        Volume of the scatterers to determine scattering amplitude (see formfactor).
        Only needed for formfactor 'sphere' and 'gauss'.
    ffpolydispersity : float
        Polydispersity of the gridpoints in relative units for sphere, gauss, explicit.
        Assuming F(q*R) for each gridpoint F is scaled as F(q*f*R)  with f as normal distribution
        around 1 and standard deviation ffpolydispersity. The scattering length :math:`b` is scaled according
        to the respective volume change by f**3. (f<0 is set to zero) assuming a volume scatterer.
        This results in a change of the forward scattering because of the stronger weight of larger objects.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
    dataArray
        Columns [q, Pq, beta]
         - .I0 :          :math:`=I(q=0)=(\sum_N b_i)^2`
         - .sumblength :  :math:`=\sum_N b_i`
         - .formfactoramplitude   : formfactor amplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :  corresponding q values

    Notes
    -----
    We calculate the scattering amplitude :math:`F(q)` for :math:`N` particles in a volume :math:`V` with scattering
    length density :math:`b(r)`

    .. math:: F(q)= \int_V b(r) e^{i\mathbf{qr}} \mathrm{d}r  / \int_V b(r) \mathrm{d}r  =
                    \sum_N b_i(q) e^{i\mathbf{qr}}  / \sum_N b_i(0)

    with the  form factor :math:`P(Q)` after explicit orientational average :math:`<>`

    .. math:: P(Q)=< F(q) \cdot F^*(q) >=< |F(q)|^2 >

    The scattering intensity of a single object represented by the cloud is

    .. math:: I(Q)=P(Q) \cdot (\int_V b(r) \mathrm{d}r)^2

    beta is the asymmetry factor [1]_ :math:`beta =|< F(q) >|^2 / < |F(q)|^2 >`

    One has to expect a peak at :math:`q \approx 2\pi/d_{NN}` with :math:`d_{NN}` as the next
    neighbour distance between particles.

    :math:`b_i(q)` is a particle formfactor amplitude of the particles as e.g. q dependent Xray
    scattering amplitude or the formfactors in a cloud of different particles,
    but may also be constant as for neutron scattering atomic formfactors.

    Random displacements :math:`u_i` lead to :math:`r_i=r_i+u_i` and to the Debye-Waller factor for Bragg peaks
    and diffusive scattering at higher q. See :ref:`A nano cube build of different lattices` .

    The explicit orientational average can be simplified using the **Debye scattering equation** [4]_

     .. math::  I(Q)=\sum_i \sum_j b_i(q) b_j(q) \frac{\sin(qr_{ij})}{qr_{ij}}
                     =\sum_i b_i(q)^2 + 2\sum_i \sum_{j>i} b_i(q) b_j(q) \frac{\sin(qr_{ij})}{qr_{ij}}

    Here no rms or ffpolydispersity are included. The calculation of :math:`beta` requires an additional calculation.

    The scattering of a cloud can represent the scattering of a *cluster of particles* with polydispersity
    and position distortion according to root mean square displacements (rms).
    Polydispersity and rms displacements are randomly changed within the orientational average to represent
    an ensemble average (opposite to the time average of a single cluster).

    **Examples**
     - See :py:func:`~.structurefactor.latticeStructureFactor` for nanocubes.
     - :ref:`A nano cube build of different lattices` .
     - The model :py:func:`~.formfactor.linearPearls` uses cloudscattering.
       Look into the source code as example how to create a complex model.


    Examples
    --------
    The example compares to the analytic solution for an ellipsoid then for a cube.
    For other shapes the grid may be better rotated away from the object symmetry or a random grid should be used.
    The example shows a good approximation with NN=20. Because of the grid peak at :math:`q=2\pi/d_{NN}`
    the grid scatterer distance :math:`d_{NN}` should be :math:`d_{NN} < \frac{1}{3} 2\pi/q_{max}` .

    Inspecting :ref:`A nano cube build of different lattices` shows other possibilities building a grid.
    Also a pseudo random grid can be used :py:func:`~.structurefactor.pseudoRandomLattice` .

    ::

     # ellipsoid with grid build by mgrid
     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     # cubic grid points
     R=3;NN=20;relError=50
     grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-2*R:2*R:2j*NN].reshape(3,-1).T
     # points inside of sphere with radius R
     p=1;p2=1*2 # p defines a superball with 1->sphere p=inf cuboid ....
     inside=lambda xyz,R1,R2,R3:(np.abs(xyz[:,0])/R1)**p2+(np.abs(xyz[:,1])/R2)**p2+(np.abs(xyz[:,2])/R3)**p2<=1
     insidegrid=grid[inside(grid,R,R,2*R)]
     q=np.r_[0:5:0.1]
     p=js.grace()
     p.title('compare form factors of an ellipsoid')
     ffe=js.ff.cloudScattering(q,insidegrid,relError=relError)
     p.plot(ffe,legend='cloud ff explicit')
     ffa=js.ff.ellipsoid(q,2*R,R)
     p.plot(ffa.X,ffa.Y/ffa.I0,li=1,sy=0,legend='analytic formula')
     p.legend()
     # show only each 20th point
     js.mpl.scatter3d(insidegrid[::10,:])

    ::

     # cube
     # grid points generated by cubic grid
     import jscatter as js
     import numpy as np
     q=np.r_[0.1:5:0.1]
     p=js.grace()
     R=3;N=10;relError=0.01  # random points on sphere
     grid= js.sf.scLattice(R/N,N)
     ffe=js.ff.cloudScattering(q,grid,relError=relError)
     p.plot(ffe,legend='cloud ff explicit 10')
     # each point has a cube around it including the border
     ffa=js.ff.cuboid(q,2*R+R/N)
     p.plot(ffa.X,ffa.Y/ffa.I0,li=1,sy=0,legend='analytic formula')
     p.yaxis(scale='l')
     p.title('compare form factors of an cube')
     p.legend(x=2,y=0.1)


    An objekt with **explicit given formfactor** for each gridpoint.
    ::

     # 5 coreshell particles in line with polydispersity
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 4
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)
     ffe = js.ff.cloudScattering(q, rod0, formfactor=cs,relError=100,ffpolydispersity=0.1)
     p=js.grace()
     p.plot(ffe)

    Using cloudScattering as **fit model**.

    We have to define a model that parametrizes the building of the cloud that we get fit parameters.
    As example we use two overlapping spheres. The model can be used to fit some data.
    The build of the model is important as it describes how the overlap is treated e.g. as average.

    We have to consider some points:
     - It is important that the model is continuous in its parameters to avoid steps as
       any fit algorithm cannot handle this.
     - We have to limit some parameters that make giant grids.
       Fit algorithm make first a small step then a large one to estimate a good step size for parameter changes.
       If in the dumbbell example the radii R1 or R2 is increased to >1000 then the grid size burst the RAM
       and we get a Memory Error. Use hard limits for the radii to a reasonable value as shown below (see setlimit).
     - The argument "factor" limits the initial step size. Reduce it (default 100 -> [0.1..100]).
     - In the below example the first fit is fast but bad as we find a local minimum.
       A global fit algorithm takes quite long but finds the correct solution.

    ::

     import jscatter as js
     import numpy as np
     #
     #: test if distance from point on X axis
     isInside=lambda x,A,R:((x-np.r_[A,0,0])**2).sum(axis=1)**0.5<R
     #: model
     def dumbbell(q,A,R1,b1,bgr=0,dx=0.3,relError=50):
         # D sphere distance
         # R1, R2 radii
         # b1,b2  scattering length
         # bgr background
         # dx grid distance not a fit parameter!!
         R2=R1
         b2=b1
         mR=max(R1,R2)
         # xyz coordinates
         grid=np.mgrid[-A/2-mR:A/2+mR:dx,-mR:mR:dx,-mR:mR:dx].reshape(3,-1).T
         insidegrid=grid[isInside(grid,-A/2.,R1) | isInside(grid,A/2.,R2)]
         # add blength column
         insidegrid=np.c_[insidegrid,insidegrid[:,0]*0]
         # set the corresponding blength; the order is important as here b2 overwrites b1
         insidegrid[isInside(insidegrid[:,:3],-A/2.,R1),3]=b1
         insidegrid[isInside(insidegrid[:,:3],A/2.,R2),3]=b2
         # and maybe a mix ; this depends on your model
         insidegrid[isInside(insidegrid[:,:3],-A/2.,R1) & isInside(insidegrid[:,:3],A/2.,R2),3]=(b2+b1)/2.
         # calc the scattering
         result=js.ff.cloudScattering(q,insidegrid,relError=relError)
         result.Y=result.Y*result.I0+bgr
         # add attributes for later usage
         result.A=A
         result.R1=R1
         result.b1=b1
         result.dx=dx
         result.insidegrid=insidegrid
         return result
     #
     # test it
     q=np.r_[0.01:5:0.02]
     data=dumbbell(q,3,2,1)

     # show result configuration
     js.mpl.scatter3d(data.insidegrid[:,0],data.insidegrid[:,1],data.insidegrid[:,2])
     #
     # Fit your data like this.
     # It may be a good idea to use not the highest resolution in the beginning because of speed.
     # If you have a good set of starting parameters you can decrease dx.
     data2=data.prune(number=100)
     data2.makeErrPlot(yscale='l')

     data2=data.prune(number=100)
     data2.makeErrPlot(yscale='l')
     data2.setLimit(R1=[None,None,1,4],A=[None,None,1,10])

     # this results in a fast but bad fit result
     # a local minima is found but the basics is working.
     data2.fit(model=dumbbell,
                freepar={'A':3,'R1':2.4,'b1':1},
                fixpar={'dx':0.3,'bgr':0},
                mapNames={'q':'X'},factor=1)

     # To get a good result we need to find the global minimum by a different algorithm ('differential evolution')
     # The limits are used as border to search in an limited area.
     # The fit takes about 3500 iterations (1000s on Ryzen 1600X 6 cores)
     data2.fit(model=dumbbell,method='differential_evolution',
                freepar={'A':3,'R1':2.4,'b1':1},
                fixpar={'dx':0.3,'bgr':0},
                mapNames={'q':'X'})

    Fit a sphere formfactor.

    The quality of the grid approximation (number of gridpoints) may
    improve the correct description of higher order minima.
    ::

     import numpy as np
     import jscatter as js

     # a function to discriminate what is inside of the sphere
     # basically a superball p2=2 is a sphere
     inside=lambda xyz,R1,p2:(np.abs(xyz[:,0]))**p2+(np.abs(xyz[:,1]))**p2+(np.abs(xyz[:,2]))**p2<=R1**2

     def test(q,R,b,p2=2,relError=20):
         # make cubic grid with right size (increase NN for better approximation)
         NN=20
         grid= np.mgrid[-R:R:1j*NN, -R:R:1j*NN,-R:R:1j*NN].reshape(3,-1).T
         # cut the edges to get a sphere
         insidegrid=grid[inside(grid,R,p2)]
         # add scattering length for points
         # the average scattering length density is sum(b)/sphereVolume
         insidegrid=np.c_[insidegrid,insidegrid[:,0]*0]
         insidegrid[:,3]=b
         # calc formfactor (normalised) for a single sphere
         ffs=js.ff.cloudScattering(q,insidegrid,relError=relError)
         # the total scattering is sumblength**2
         ffs.Y*=ffs.sumblength**2
         # save radius and the grid for later
         ffs.R=R
         ffs.insidegrid=insidegrid
         return ffs

     ####main
     q=np.r_[0:3:0.01]
     sp=js.formfactor.sphere(q,3,1)

     sp.makeErrPlot(yscale='l')   # show intermediate results
     sp.setlimit(R=[0.3,10])      # set some reasonable limits for R
     sp.fit(model=test,
         freepar={'b':6,'R':2.1},
         fixpar={},
         mapNames={'q':'X'})

     # show the resulting sphere grid
     resultgrid=sp.lastfit.insidegrid
     js.mpl.scatter3d(resultgrid[:,0],resultgrid[:,1],resultgrid[:,2])

    Here we compare explicit calculation with the Debye equation as the later gets quite slow for larger numbers.
    ::

     import jscatter as js
     import numpy as np
     R=6;NN=20
     q=np.r_[0:5:0.1]
     grid=js.formel.randomPointsInCube(10000)*R-R/2
     ffe=js.ff.cloudScattering(q,grid,relError=150)    # takes about  1.3 s on six core
     ffd=js.ff.cloudScattering(q,grid,relError=0)      # takes about 11.4 s on six core
     grid=js.formel.randomPointsInCube(500)*R-R/2
     ffe=js.ff.cloudScattering(q,grid,relError=150)    # takes about 132 ms on six core
     ffd=js.ff.cloudScattering(q,grid,relError=0)      # takes about  33 ms on six core

     p=js.grace()
     p.plot(ffe)
     p.plot(ffd)
     p.yaxis(scale='l')


    References
    ----------
    .. [1] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    .. [2] An improved method for calculating the contribution of solvent to
           the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694
    .. [3] X-ray diffuse scattering by proteins in solution. Consideration of solvent influence
           B. A. Fedorov, O. B. Ptitsyn and L. A. Voronin
           J. Appl. Cryst. (1974). 7, 181-186 doi: 10.1107/S0021889874009137
    .. [4] Zerstreuung von Röntgenstrahlen
           Debye P. Annalen der Physik 1915 vol: 351 (6) pp: 809-823 DOI: 10.1002/andp.19153510606

    """

    if cloud.shape[1] == 5:
        # last columns are scattering length and iff
        blength = cloud[:, 3]
        iff = cloud[:, 4].astype(int)  # index in formfactor
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 4:
        # last column is scattering length
        blength = cloud[:, 3]
        cloud = cloud[:, :3]
        iff =np.ones(cloud.shape[0], dtype=int)
    else:
        blength = np.ones(cloud.shape[0])
        iff =np.ones(cloud.shape[0], dtype=int)
    sumblength = blength.sum()
    relError = abs(relError)

    if isinstance(formfactor, str):
        if formfactor.startswith('g'):
            # gaussian shape
            formfactoramp = np.c_[q, np.exp(-q ** 2 * V ** (2 / 3.) * np.pi)].T
            formfactor = 'gaussian'
            iff = np.ones(cloud.shape[0], dtype=int)
        elif formfactor.startswith('s'):
            # sphere
            R = (3. * V / 4. / np.pi) ** (1 / 3.)
            formfactoramp = np.c_[q, _fa_sphere(q * R)].T
            formfactor = 'sphere'
            iff = np.ones(cloud.shape[0], dtype=int)
    elif isinstance(formfactor, np.ndarray):
        formfactoramp=formfactor.copy()
        formfactoramp[1:] = formfactor[1:] ** 0.5 / formfactor[1:, :1] ** 0.5
        formfactor = 'explicit'
    else:
        # const form factor as default
        formfactoramp = np.c_[q, np.ones_like(q)].T
        formfactor = 'constant'
        iff = np.ones(cloud.shape[0], dtype=int)

    if relError == 0:
        # Debye equation
        # no asymmetry factor beta, no rms, no ffpolydispersity
        if useFortran:
            # about 4 timesfaster than below python version on single core
            res = fscatter.cloud.scattering_debye(q, cloud, blength, iff, formfactoramp, ncpu)
            result = dA(np.c_[res[0], res[1] / sumblength ** 2].T)
        else:
            #res=[_scattering_Debye(qx, cloud, blength, iff, formfactoramp) for qx in q]
            res=parallel.doForList(_scattering_Debye, q,
                                   r=cloud, blength=blength, iff=iff, formfactoramp=formfactoramp,
                                   ncpu=ncpu, loopover='q', output=False)

            result = dA(np.c_[q, res/ sumblength ** 2].T)
        result.columnname = 'q; Pq'
    elif relError > 0:
        # explicit average
        # allows asymmetry factor beta, rms, ffpolydispersity
        if useFortran:
            res = parallel.doForList(_sphaverage_scattering, q,
                                     r=cloud, blength=blength, iff=iff, formfactoramp=formfactoramp, rms=rms,
                                     ffpolydispersity=ffpolydispersity,
                                     ncpu=ncpu, relError=relError, loopover='q', output=False)
        else:
            # in _scattering there is a choice to use pure python; the above instant fortran call is 20% faster
            res = parallel.doForList(formel.sphereAverage, q, _scattering,
                                     r=cloud, blength=blength, iff=iff, formfactoramp=formfactoramp, rms=rms,
                                     ffpolydispersity=ffpolydispersity,
                                     ncpu=ncpu, relError=relError, loopover='q', output=False)

        res = np.array(res).T
        # the third row is F(Q) but will be asymmetry factor beta according to Chen
        #  which is beta=|<F(Q)>|²/<|F(Q)|²>   and scattering amplitude F(Q)
        res[2] = (res[2] * res[2].conj())
        if sumblength != 0:
            # prevent division by zero in some cases (matching)
            res[1] = res[1] / sumblength ** 2
            res[2] = res[2] / res[1]

        result = dA(res[:3], dtype=np.float)
        result.columnname = 'q; Pq; beta'
    result.sumblength = sumblength
    result.I0 = sumblength ** 2
    result.formfactoramplitude_q = formfactoramp[0]
    result.formfactoramplitude = formfactoramp[1:]
    result.formfactor = formfactor
    result.rms = rms
    result.ffpolydispersity = ffpolydispersity
    result.setColumnIndex(iey=None)

    result.modelname = inspect.currentframe().f_code.co_name
    return result


def _coneAverage(qlist, qxzw, qrpt, qfib, r, blength,iff, formfactoramp, rms):
    q, ilist = qlist  # ilist is index in qxzw of the qxzw with same q value

    fa = np.array([np.interp(q, formfactoramp[0, :], amp) for amp in formfactoramp[1:]])
    fa = blength * fa[iff - 1]

    qfib[:, 0] = q  # cone points around [0,0,1] direction
    fibpoints = formel.rphitheta2xyz(qfib)  # cartesian coordinates of fibonacci lattice with radius q
    # do the average for all in ilist
    res = {}
    pi_2 = np.pi / 2
    for il in ilist:
        # get angles
        _, p, t = qrpt[il]
        # rotate fibpoints to angles
        R = formel.rotationMatrix(formel.rphitheta2xyz(np.r_[1, p - pi_2, pi_2]), t)
        Rfibpoints = np.einsum('ij,jk->ki', R, fibpoints.T)
        # take mean of rotated fibpoints
        if useFortran:
            res[il] = np.mean([fscatter.cloud.ffx(point, r, fa, rms) for point in Rfibpoints])
        else:
            res[il] = np.mean([_sqx(point, r, fa, rms) for point in Rfibpoints])

    return res


def _sqx(qx, r, fa, rms=0):
    """
    coherent scattering of equal objects at positions r in direction point on
    sphere with length (radius) q

    Parameters
    ----------
    qx :  array 3 x 1
        point on unit sphere within oriented cone
    r : array  N x 3
        vector of objekt positions
    fa : float
        blength*formfactor(q)
    rms : float
        < random displacements >

    Returns
    -------
    F(Q)*F(Q).conj()

    pure numpy way
    """
    if rms > 0:
        r += np.random.randn(r.shape[0], 3) * rms
    iqr = np.einsum('i,ji', qx, r) * 1j
    beiqrsum = np.einsum('i,i', fa, np.exp(iqr))
    Sq = beiqrsum * beiqrsum.conj()
    return Sq.real


def orientedCloudScattering(qxzw, cloud, rms=0, coneangle=10, nCone=50, V=None, formfactor=None, ncpu=0):
    r"""
    2D scattering of an oriented cloud of scatterers with equal or variable scattering length. Using multiprocessing.

    Cloud can represent an object described by a cloud of isotropic scatterers with orientation averaged in a cone.
    Scattering amplitudes may be constant, sphere scattering amplitude, Gaussian scattering amplitude
    or explicitly given form factor. Remember that the atomic bond length are on the order 0.1-0.2 nm
    and one expects Bragg peaks.

    Parameters
    ----------
    qxzw : array, ndim= Nx3
         3D wavevectors in 1/nm
         If 2D the 3rd dim is set to zero. Wavevectors may represent a line, a plane or any other 3D distribution in
         reciprocal space.
    cloud : array Nx3, Nx4, Nx5
        - Center of mass positions (in nm) of the N scatterers in the cloud.
        - If given cloud[3] is the scattering length :math:`b` at positions cloud[:3], otherwise :math:`b=1`.
        - If given cloud[4] is the column index in formfactor for a specific scatterer.
    coneangle : float
        Cone angle in units degrees.
    rms : float, default=0
        Root mean square displacement :math:`\langleu^2\rangle^{0.5} of the positions in cloud as random
        displacements in nm. The displacement u is randomly chosen for each orientation in cone.
        rms can be used to simulate a Debye-Waller factor. Larger nCone is advised yield reasonable average.
    nCone : int
        Cone average as average over nCone Fibonacci lattice points in cone.
    formfactor : None,'gauss','sphere','cube'
        Scattering amplitudes :math:`F_a(q)` of scatterers are described as:
         - None    : const scattering amplitude.
         - 'sphere': Sphere scattering amplitude according to [3]_.
                     Parameter V needed to determine :math:`R`.
                     The sphere radius is :math:`R=(\frac{3V}{4\pi})^{1/3}`.
                     The scattering length per particle is :math:`b_i = V* contrast`
         - 'gauss' : Gaussian function  :math:`b_i(q)=b V exp(-\pi V^{2/3}q^2)` according to [2]_.
                     The Gaussian shows no artificial minima compared to spheres.
                     The scattering length per particle is :math:`b_i = V* contrast`
         - Explicit isotropic formfactor as array with [q,ff1(q),ff2(q),ff3(q),....].
            - If multiple formfactors are given the formfactor for a cloud point needs to be given in cloud[4]
            - The normalized scattering amplitude fa for each cloud point is calculated as fa=ffi**0.5/fai(0).
              Missing values are linear interpolated (np.interp), q values outside interval are mapped to qmin or qmax.
            - Explicit formfactors are assumed to be isotropic.
    V : float, default=None
        Volume of the scatterers to determine scattering amplitude (see formfactor).
        Only needed for formfactor 'sphere' and 'gauss'.
    ncpu : int, default 0
        Number of cpus used in the pool for multiprocessing.
         - not given or 0 : all cpus are used
         - int>0          : min(ncpu, mp.cpu_count)
         - int<0          : ncpu not to use
         - 1              : single core usage for testing or comparing speed to Debye

    Returns
    -------
    dataArray
        Columns [qx, qz, qw, Sq]
         - The forward scattering is Pq(q=0)= sumblength**2
         - .sumblength : Sum of blength with sumblength**2
         - .formfactoramplitude : formfactoramplitude of cloudpoints according to type for all q values.
         - .formfactoramplitude_q :corresponding q values.

    Examples
    --------
    How to use orientedCloudScattering for fitting see last Example in cloudScattering.

    Two points along y result in pattern independent of x but cos**2 for z
    with larger coneangle Ix becomes qx dependent. ::

     import jscatter as js
     import numpy as np
     rod0=np.zeros([2,3])
     rod0[:,1]=np.r_[0,np.pi]
     qxzw=np.mgrid[-6:6:50j, -6:6:50j].reshape(2,-1).T
     ffe=js.ff.orientedCloudScattering(qxzw,rod0,coneangle=5,nCone=10,rms=0)
     fig=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig.axes[0].set_title(r'cos**2 for Z and slow decay for X due to 5 degree cone')
     fig.show()
     # noise in positions
     ffe=js.ff.orientedCloudScattering(qxzw,rod0,coneangle=5,nCone=100,rms=0.1)
     fig=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig.axes[0].set_title('cos**2 for Y and slow decay for X with position noise')
     fig.show()


    Two points along z result in symmetric pattern around zero
    symmetry reflects fibonacci lattice -> increase nCone ::

     rod0=np.zeros([2,3])
     rod0[:,2]=np.r_[0,np.pi]
     ffe=js.ff.orientedCloudScattering(qxzw,rod0,coneangle=45,nCone=10,rms=0.005)
     fig2=js.mpl.surface(ffe.X,ffe.Z,ffe.Y)
     fig2.axes[0].set_title('symmetric because of orientation along z; \n nCone needs to be larger for large cones')
     fig2.show()


    5 spheres in line with small position distortion ::

     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     qxzw = np.mgrid[-6:6:50j, -6:6:50j].reshape(2, -1).T
     ffe = js.ff.orientedCloudScattering(qxzw,rod0,formfactor='sphere',V=4/3.*np.pi*2**3,coneangle=20,nCone=30,rms=0.02)
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 spheres with R=2 along Z with noise (rms=0.02)')
     fig4.show()


    Solution of oriented particle-composite of 3 touching core shell particles with small position distortion.
    Here we add a isotropic Percus-Yevick structure factor as effective composite interaction
    between particle composites. ::

     N=3    # number of particles
     d=16.0  # distance of particles
     Rc=2   # core radius
     Rs=8   # outer shell radius
     volumefraction=0.10  # single particles
     rms=1.5
     # position composite particles along X axis
     rod0 = np.zeros([N, 3])
     rod0[:, 0] = np.r_[0:N] * d  # positions
     # q grid
     qxzw = np.mgrid[-2:2:150j, -2:2:150j].reshape(2, -1).T
     # core shell formfactor for particles and use interpolation
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=Rc, Rs=Rs, bc=-0.1, bs=1, solventSLD=0)
     # oriented composite scattering
     ffe = js.ff.orientedCloudScattering(qxzw, rod0, formfactor=cs, coneangle=5, nCone=100, rms=rms)
     fig4a = js.mpl.contourImage(ffe.X, ffe.Z, ffe.Y, colorMap='gnuplot',scale='log')
     fig4a.axes[0].set_title('3 core shell particles with R=2 along Z with noise')

     # add structure factor according to radial q component
     sf=js.sf.PercusYevick(q, Rs*N/2, eta=volumefraction*N)  # approximate higher radius
     qradial=np.linalg.norm(ffe[:3],axis=0)
     ffe.Y=ffe.Y*sf.interp(qradial)
     fig4b = js.mpl.contourImage(ffe.X, ffe.Z, ffe.Y, colorMap='gnuplot',scale='log')
     fig4b.axes[0].set_title('3 core shell particles with noise and interparticle interaction ')
     #fig4b.savefig(js.examples.imagepath+'/orientedCloudScattering.jpg')

    .. image:: ../../examples/images/orientedCloudScattering.jpg
     :width: 70 %
     :align: center
     :alt: orientedCloudScattering



    Make a slice for an angular region but with higher resolution to see the additional peaks due to alignment
    ::

     # rod0 will be position of 5 points in a row
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3

     qxzw = np.mgrid[-4:4:150j, -4:4:150j].reshape(2, -1).T    # xz plane grid
     # only as demo : extract q from qxzw
     qxzw = np.c_[qxzw, np.zeros_like(qxzw[:, 0])]              # add y=0 component
     qrpt = js.formel.xyz2rphitheta(qxzw)                     # spherical coordinates
     q = np.unique(sorted(qrpt[:, 0]))

     # or use interpolation; cs will be our formfactor
     q = js.loglist(0.01, 7, 100)
     cs = js.ff.sphereCoreShell(q=q, Rc=1, Rs=2, bc=0.1, bs=1, solventSLD=0)

     # calc scattering in plane qxzw
     ffe = js.ff.orientedCloudScattering(qxzw, rod0, formfactor=cs, coneangle=20, nCone=100, rms=0.05)

     # show it in surface plot
     fig4 = js.mpl.surface(ffe.X, ffe.Z, np.log10(ffe.Y), colorMap='gnuplot')
     fig4.axes[0].set_title('5 core shell particles with R=2 along Z with noise (rms=0.05)')
     fig4.show()

     # We do an explicit radial average
     # transform X,Z to spherical coordinates
     qphi=js.formel.xyz2rphitheta([ffe.X,ffe.Z,np.zeros_like(ffe.X)],transpose=True )[:,:2]
     # add qphi or use later rp[1] for selection
     ffb=ffe.addColumn(2,qphi.T)
     # select a portion of the phi angles
     phi=np.pi/2
     dphi=0.2
     ffn=ffb[:,(ffb[-1]<phi+dphi)&(ffb[-1]>phi-dphi)]
     ffn.isort(-2)    # sort along radial q
     p=js.grace()
     p.plot(ffn[-2],ffn.Y,le='oriented spheres form factor')
     # compare to coreshell formfactor scaled
     p.plot(cs.X,cs.Y/cs.Y[0]*25,li=1,le='coreshell form factor')
     p.yaxis(label='F(Q,phi=90°+-11°)', scale='log')
     p.title('5 aligned core shell particle with additional interferences',size=1.)
     p.subtitle(' due to sphere alignment dependent on observation angle')

     # 2: direct way with 2D q in xz plane
     rod0 = np.zeros([5, 3])
     rod0[:, 1] = np.r_[0, 1, 2, 3, 4] * 3
     x=np.r_[0.0:6:0.05]
     qxzw = np.c_[x, x*0,x*0]
     for alpha in np.r_[0:91:30]:
         R=js.formel.rotationMatrix(np.r_[0,0,1],np.deg2rad(alpha)) # rotate around Z axis
         qa=np.dot(R,qxzw.T).T[:,:2]
         ffe = js.ff.orientedCloudScattering(qa, rod0, formfactor=cs, coneangle=20, nCone=100, rms=0.05)
         p.plot(x,ffe.Y,li=[1,2,-1],sy=0,le='alpha=%g' %alpha)
     p.xaxis(label=r'Q / nm\S-1')
     p.legend()

    References
    ----------
    .. [1] M. Kotlarchyk and S.-H. Chen, J. Chem. Phys. 79, 2461 (1983).1
    .. [2] An improved method for calculating the contribution of solvent to
           the X-ray diffraction pattern of biological molecules
           Fraser R MacRae T Suzuki E IUCr Journal of Applied Crystallography 1978 vol: 11 (6) pp: 693-694
    .. [3] X-ray diffuse scattering by proteins in solution. Consideration of solvent influence
           B. A. Fedorov, O. B. Ptitsyn and L. A. Voronin J. Appl. Cryst. (1974). 7, 181-186
           doi: 10.1107/S0021889874009137

    """
    nCone = max(10, nCone)
    if qxzw.shape[1] == 2:
        # make 3D q with qz=0
        qxzw = np.c_[qxzw, np.zeros_like(qxzw[:, 0])]

    if cloud.shape[1] == 5:
        # last columns are scattering length and iff
        blength = cloud[:, 3]
        iff = cloud[:, 4].astype(int)  # index in formfactor
        cloud = cloud[:, :3]
    elif cloud.shape[1] == 4:
        # last column is scattering length
        blength = cloud[:, 3]
        cloud = cloud[:, :3]
        iff =np.ones(cloud.shape[0], dtype=int)
    else:
        blength = np.ones(cloud.shape[0])
        iff =np.ones(cloud.shape[0], dtype=int)
    sumblength = blength.sum()

    # cone to average  which is around Z direction = [0,0,1]xyz = [1,0,0]rpt
    qfib = formel.fibonacciLatticePointsOnSphere(nCone, 1)
    qfib = qfib[qfib[:, 2] < np.pi / 2, :]  # select half sphere
    qfib[:, 2] *= (coneangle / 90.)  # shrink to cone

    # generate reduced q list for formfactors
    # transform to spherical coordinates and make selective qlist
    qrpt = formel.xyz2rphitheta(qxzw)
    qround = np.round(qrpt[:, 0], 3)
    qred = np.unique(qround)  # reduced q list list to 10**-3 precision
    qlist = [(qi, np.where(qround == qi)[0]) for qi in qred]  # list of q with original Q indices

    # define formfactor for qround
    if isinstance(formfactor, str):
        if formfactor.startswith('g'):
            # gaussian shape
            formfactoramp = np.c_[qred, np.exp(-qred ** 2 * V ** (2 / 3.) / 4. / np.pi)].T
            formfactor = 'gaussian'
            iff = np.ones(cloud.shape[0], dtype=int)
        elif formfactor.startswith('s'):
            # sphere
            R = (3. * V / 4. / np.pi) ** (1 / 3.)
            formfactoramp = np.c_[qred, _fa_sphere(qred * R)].T
            formfactor = 'sphere'
            iff = np.ones(cloud.shape[0], dtype=int)
    elif isinstance(formfactor, np.ndarray):
        formfactoramp=formfactor.copy()
        formfactoramp[1:] = formfactor[1:] ** 0.5 / formfactor[1:, :1] ** 0.5
        formfactor = 'explicit'
    else:
        # const form factor as default
        formfactoramp = np.c_[qred, np.ones_like(qred)].T
        formfactor = 'constant'
        iff = np.ones(cloud.shape[0], dtype=int)

    # do in parallel for all q rings
    res = parallel.doForList(_coneAverage, qlist,
                             qxzw=qxzw, qrpt=qrpt, qfib=qfib, r=cloud, blength=blength,iff=iff,
                             formfactoramp=formfactoramp,rms=rms,
                             ncpu=ncpu, loopover='qlist', output=False)

    # distribute Sxy according to saved indices from qlist
    Sq = np.zeros_like(qxzw[:, 0])
    for res1 in res:
        for ii, Sxy in res1.items():
            Sq[ii] = Sxy
    result = dA(np.c_[qxzw, Sq].T, dtype=np.float)
    result.sumblength = sumblength
    result.formfactoramplitude_q = formfactoramp[0]
    result.formfactoramplitude = formfactoramp[1]
    result.formfactortype = formfactor
    if isinstance(V,numbers.Number):
        result.Volume = V
    result.setColumnIndex(ix=0, iy=3, iz=1, iw=2, iey=None)
    result.columnname = 'qx; qz; qw; Sq'

    result.modelname = inspect.currentframe().f_code.co_name
    return result
