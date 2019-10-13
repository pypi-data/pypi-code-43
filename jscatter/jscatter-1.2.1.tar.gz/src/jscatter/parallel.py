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
Functions for parallel computations on a single multi core machine using the standard library multiprocessing.

Not the programming details, but the way how to speed up some things.

- If your computation is already fast (e.g. <1s) go on without parallelisation.
  In an optimal case you gain a speedup as the number of cpu cores.
- If you want to use a cluster with all cpus, this is not the way (you need MPI).

Parallelisation is no magic and this module is for convenience for non specialist of parallel computing.
The main thing is to pass additional parameters to the processes (a pool of workers)
and loop only over one parameter given as list.
Opening and closing of the pool is hidden in the function.
In this way we can use a multicore machine with all cpus.

During testing I found that shared memory does not really speed up,
if we just want to calculate a function e.g. for a list of different
Q values dependent on model parameters. Here the pickling of numpy arrays is
efficient enough compared to the computation we do.
The amount of data pickled should not be too large as each process
gets a copy and pickling needs time.

If speed is an issue and shared memory gets important i advice using Fortran with OpenMP
as used for ff.cloudScattering with parallel computation and shared memory.
For me this was easier than the different solutions around.

We use here only non modified input data and return a new dataset,
so we dont need to care about what happens if one process changes the data needed
in another process (race conditions,...), anyway its not shared.
Please keep this in mind and dont complain if you find a way to modify input data.

For easier debugging (to find the position of an error in the pdb debugger) use the option debug.
In this case the multiprocessing is not used and the debugger finds the error correctly.

See example in doForList.

"""
from __future__ import print_function
from __future__ import division

import scipy.constants as constants
import multiprocessing as mp
import numpy as np

try:
    from . import fscatter
    useFortran = True
except ImportError:
    useFortran = False

_Nrand = np.random.random_integers

from math import log, floor, ceil, fmod


def haltonSequence(size, dim, skip=0):
    """
    Pseudo random numbers from the  Halton sequence in interval [0,1].

    To use them as coordinate points transpose the array.

    Parameters
    ----------
    size : int
        Samples from the sequence
    dim : int
        Dimensions
    skip : int
        Number of points to skip in Halton sequence .

    Returns
    -------
    array

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     for i,color in enumerate(['b','g','r','y']):
        # create halton sequence and shift it to needed shape
        pxyz=js.parallel.haltonSequence(400,3).T*2-1
        ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color=color,s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)


    References
    ----------
    .. [1] https://mail.python.org/pipermail/scipy-user/2013-June/034741.html
            Author: Sebastien Paris,  Josef Perktold translation from c
    .. [2] https://en.wikipedia.org/wiki/Low-discrepancy_sequence

    """

    if useFortran:
        return fscatter.pseudorandom.halton_sequence(skip+1, skip + size, dim)
    else:
        size = size + skip
        h = np.empty(size * dim)
        h.fill(np.nan)
        p = np.empty(size)
        p.fill(np.nan)
        P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]
        logsize = log(size + 1)
        for i in range(dim):
            b = P[i]
            n = int(ceil(logsize / log(b)))
            for t in range(n):
                p[t] = pow(b, -(t + 1))

            for j in range(size):
                d = j + 1
                sum_ = fmod(d, b) * p[0]
                for t in range(1, n):
                    d = floor(d / b)
                    sum_ += fmod(d, b) * p[t]
                h[j * dim + i] = sum_

        return h.reshape(size, dim).T[:, skip:]


def randomPointsOnSphere(NN, r=1, skip=0):
    r"""
    N quasi random points on sphere of radius r based on low-discrepancy sequence.

    For numerical integration quasi random numbers are better than random samples as
    the error drops faster [1]_. Here we use the Halton sequence to generate the sequence.
    Skipping points makes the sequence additive and does not repeat points.

    Parameters
    ----------
    NN : int
        Number of points to generate.
    r : float
        Radius of sphere
    skip : int
        Number of points to skip in Halton sequence .


    Returns
    -------
    array of [r,phi,theta]  pairs in radians


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Low-discrepancy_sequence

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     for i,color in enumerate(['b','g','r','y']):
        points=js.parallel.randomPointsOnSphere(400,skip=400*i)
        points=points[points[:,1]>0,:]
        pxyz=js.formel.rphitheta2xyz(points)
        ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color=color,s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     fig.axes[0].set_title('random points on sphere (half shown)')
     plt.tight_layout()
     plt.show(block=False)
     #fig.savefig(js.examples.imagepath+'/randomPointsOnSphere.jpg')

    .. image:: ../../examples/images/randomPointsOnSphere.jpg
     :align: center
     :height: 300px
     :alt: convolve


    """

    NN = abs(NN)
    seq = haltonSequence(NN + skip, 2)
    return np.c_[(r * np.ones_like(seq[0]),
                  2 * np.pi * seq[0] - np.pi,
                  np.arccos(2 * seq[1] - 1))]


def randomPointsInCube(NN, skip=0, dim=3):
    r"""
    N quasi random points in cube of edge 1 based on low-discrepancy sequence.

    For numerical integration quasi random numbers are better than random samples as
    the error drops faster [1]_. Here we use the Halton sequence to generate the sequence.
    Skipping points makes the sequence additive and does not repeat points.

    Parameters
    ----------
    NN : int
        Number of points to generate.
    skip : int
        Number of points to skip in Halton sequence .
    dim : int, default 3
        Dimension of the cube.

    Returns
    -------
    array of [x,y,z]


    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Low-discrepancy_sequence

    Examples
    --------
    ::

     # random cubes of random points in cube
     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     N=30
     cubes=js.parallel.randomPointsInCube(20)*3
     for i,color in enumerate(['b','g','r','y','k']*3):
        points=js.parallel.randomPointsInCube(N,skip=N*i).T
        pxyz=points*0.3+cubes[i][:,None]
        ax.scatter(pxyz[0,:],pxyz[1,:],pxyz[2,:],color=color,s=20)
     ax.set_xlim([0,3])
     ax.set_ylim([0,3])
     ax.set_zlim([0,3])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)


    """
    return haltonSequence(abs(NN), dim, skip).T


def fibonacciLatticePointsOnSphere(NN, r=1):
    """
    Fibonacci lattice points on a sphere with radius r (default r=1)

    This can be used to integrate efficiently over a sphere with well distributed points.

    Parameters
    ----------
    NN : integer
        number of points = 2*N+1
    r : float, default 1
        radius of sphere

    Returns
    -------
    list of [r,phi,theta]  pairs in radians
        phi  azimuth -pi<phi<pi; theta polar angle  0<theta<pi

    References
    ----------
    .. [1] Measurement of Areas on a Sphere Using Fibonacci and Latitude–Longitude Lattices
          Á. González Mathematical Geosciences 42, 49-64 (2009)

    Examples
    --------
    ::

     import jscatter as js
     import numpy as np
     import matplotlib.pyplot as plt
     from mpl_toolkits.mplot3d import Axes3D
     points=js.formel.fibonacciLatticePointsOnSphere(1000)
     pp=list(filter(lambda a:(a[1]>0) & (a[1]<np.pi/2) & (a[2]>0) & (a[2]<np.pi/2),points))
     pxyz=js.formel.rphitheta2xyz(pp)
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     ax.set_aspect("equal")
     plt.tight_layout()
     plt.show(block=False)

     points=js.formel.fibonacciLatticePointsOnSphere(1000)
     pp=list(filter(lambda a:(a[2]>0.3) & (a[2]<1) ,points))
     v=js.formel.rphitheta2xyz(pp)
     R=js.formel.rotationMatrix([1,0,0],np.deg2rad(-30))
     pxyz=np.dot(R,v.T).T
     #points in polar coordinates
     prpt=js.formel.xyz2rphitheta(np.dot(R,pxyz.T).T)
     fig = plt.figure()
     ax = fig.add_subplot(111, projection='3d')
     ax.scatter(pxyz[:,0],pxyz[:,1],pxyz[:,2],color="k",s=20)
     ax.set_xlim([-1,1])
     ax.set_ylim([-1,1])
     ax.set_zlim([-1,1])
     ax.set_aspect("equal")
     ax.set_xlabel('x')
     ax.set_ylabel('y')
     ax.set_zlabel('z')
     plt.tight_layout()
     plt.show(block=False)

    """
    return np.c_[(r * np.ones(2 * NN + 1),
                  np.mod((2 * np.pi * np.r_[-NN:NN + 1] / constants.golden) + np.pi, 2 * np.pi) - np.pi,
                  np.arcsin(2 * np.r_[-NN:NN + 1] / (2 * NN + 1.)) + np.pi / 2)]


def rphitheta2xyz(RPT):
    """
    Transformation  spherical coordinates [r,phi,theta]  to cartesian coordinates [x,y,z]
    
    Parameters
    ----------
    RPT : array Nx3
        | dim Nx3 with [r,phi,theta] coordinates
        | r     : float       length
        | phi   : float   azimuth     -pi < phi < pi
        | theta : float   polar angle  0 < theta  < pi

    Returns
    -------
    Array with same dimension as RPT.

    """
    rpt = np.array(RPT, ndmin=2)
    xyz = np.zeros(rpt.shape)
    xyz[:, 0] = rpt[:, 0] * np.cos(rpt[:, 1]) * np.sin(rpt[:, 2])
    xyz[:, 1] = rpt[:, 0] * np.sin(rpt[:, 1]) * np.sin(rpt[:, 2])
    xyz[:, 2] = rpt[:, 0] * np.cos(rpt[:, 2])
    return np.array(xyz.squeeze(), ndmin=np.ndim(RPT))


# noinspection PyIncorrectDocstring
def psphereAverage(funktion, relError=300, *args, **kwargs):
    """
    Parallel evaluation of spherical average of function.
    
    A Fibonacci lattice or Monte Carlo integration with pseudo random grid is used.
    
    Parameters
    ----------
    funktion : function
        Function to evaluate.
        Function first argument gets cartesian coordinate [x,y,z] of point on unit sphere.
    relError : float, default 300
        Determines how points on sphere are selected
         - >1  Fibonacci Lattice with relError*2+1 points
         - 0<1 Pseudo random points on sphere (see randomPointsOnSphere).
               Stops if relative improvement in mean is less than relError (uses steps of 40 new points).
               Final error is (stddev of N points) /sqrt(N) as for Monte Carlo methods
               even if it is not a correct 1-sigma error in this case.
    arg,kwargs : 
        forwarded to function
    
    Returns
    -------
    array like with values from function and appended error

    Notes
    -----
     - Works also on single core machines.
     - For integration over a continuous function as a form factor in scattering the random
       points are not statistically independent. Think of neighbouring points on an isosurface
       which are correlated and therefore the standard deviation is biased. In this case the
       Fibonacci lattice is the better choice as the standard deviation in a random sample
       is not a measure of error but more a measure of the differences on the isosurface.

    Examples
    --------
    ::

     def f(x,r):
        return [js.formel.xyz2rphitheta(x)[1:].sum()*r]
     js.parallel.psphereAverage(f,relError=500,r=1)
     js.parallel.psphereAverage(f,relError=0.01,r=1)


    """
    if relError < 0:
        relError = abs(relError)
    if 'ncpu' in kwargs:
        ncpu = kwargs['ncpu']
        del kwargs['ncpu']
    else:
        ncpu = mp.cpu_count()
    pool = mp.Pool(ncpu)
    steps = ncpu * 20
    if relError == 0:
        print('Try again with relError > 0')
        return
    elif 0 < abs(relError) < 1:
        points = rphitheta2xyz(randomPointsOnSphere(NN=steps))
        npoints = steps
        jobs = [pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
        result = [np.asarray(job.get(0xFFFF)) for job in jobs]
        prevmean = np.r_[result].mean(axis=0).real
        # prevstd =result.std(axis=0).real
        while 1:
            points = rphitheta2xyz(randomPointsOnSphere(NN=steps, skip=npoints))
            npoints += steps
            jobs = [pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
            result += [np.asarray(job.get(0xFFFF)) for job in jobs]
            results = np.array(result)
            mean = results.mean(axis=0).real
            # std=results.std(axis=0).real
            if np.all(abs(1 - abs(prevmean / mean)) < relError):
                # abs(results[:,0].std()/results[:,0].mean()/np.sqrt(results.shape[0]-1))<relError
                # and results.shape[0]>42:
                break
            prevmean = mean
            # prevstd  = std
    elif relError > 1:
        qfib = fibonacciLatticePointsOnSphere(relError, 1)
        points = rphitheta2xyz(qfib)  # to cartesian
        jobs = [pool.apply_async(funktion, (point,) + args, kwargs) for point in points]
        results = np.r_[[np.asarray(job.get(0xFFFF)) for job in jobs]]
    # clean up
    pool.close()
    pool.join()
    return np.r_[results.mean(axis=0), results.std(axis=0) / np.sqrt(np.shape(results[:, 0])[0])]


# noinspection PyIncorrectDocstring
def doForList(funktion, looplist, *args, **kwargs):
    """
    Calculates function for values in looplist in a pool of workers in parallel using multiprocessing.
    
    Like multiprocessing map_async but distributes automatically all given arguments.
    
    Parameters
    ----------
    funktion : function
        Function to process with arguments (looplist[i],args,kwargs)
        Return value of function should contain parameters or at least the loopover value to allow a check, if desired.
    looplist : list
        List of values to loop over.
    loopover : string, int,default= Not given
        Name of argument to use for looping over with values in looplist.
        If not given the first argument is used, which should be not included as argument.
    ncpu : int, optional
        Number of cpus in the pool.
         - not given or 0   -> all cpus are used
         - int>0      min (ncpu, mp.cpu_count)
         - int<0      ncpu not to use
    cb : None, function
        Callback after each calculation.
    debug : int
        debug > 0 allows serial output for testing

    Returns
    -------
    list : list of function return values as  [result1,result2,.....]
           The order of return values is not explicitly synced to looplist.

    Notes
    -----
    The return array of function may be prepended with the value looplist[i] as reference.
    E.g.::

     def f(x,a,b,c,d):
         return [x,x+a+b+c+d]

    Examples
    --------
    ::

     def f(x,a,b,c,d):
        res=x+a+b+c+d
        return [x,res]
     # loop over first argument, here x
     res = js.parallel.doForList(f,looplist=np.arange(100),a=1,b=2,c=3,d=11)
     # loop over 'd' ignoring the given d=11 (which can be omitted here)
     res = js.parallel.doForList(f,looplist=np.arange(100),loopover='d',x=0,a=1,b=2,c=3,d=11)

    """
    output = kwargs.pop('output', True)
    ncpu = mp.cpu_count()
    if 'ncpu' in kwargs:
        if kwargs['ncpu'] < 0:
            ncpu = max(ncpu + kwargs['ncpu'], 1)
        elif kwargs['ncpu'] > 0:
            ncpu = min(ncpu, kwargs['ncpu'])
        del kwargs['ncpu']
    cb = kwargs.pop('cb', None)
    loopover = kwargs.pop('loopover', None)
    if ('debug' in kwargs and kwargs['debug'] > 0) or ncpu == 1:  # in sequence for testing purposes
        if 'debug' in kwargs.keys():
            del kwargs['debug']
        res = []
        if output: print('start NO pool; this is a test ')
        if isinstance(loopover, str):
            for Q in looplist:
                # noinspection PyCallingNonCallable
                res.append(funktion(*args, **dict(kwargs, **{loopover: Q})))
                if cb is not None:  cb(res[-1])
        else:
            for Q in looplist:
                # noinspection PyCallingNonCallable
                res.append(funktion(*((Q,) + args), **kwargs))
                if cb is not None:  cb(res[-1])
    else:  # in parallel for production run
        if 'debug' in kwargs: del kwargs['debug']
        if output: print('start pool of ', ncpu)
        pool = mp.Pool(ncpu)
        # we need to create a temporary dict that is given to a job and is not only a view to the updated kwargs
        # this is needed as the view changes to each new value in the loop even in the jobs
        if isinstance(loopover, str):
            jobs = [pool.apply_async(funktion, args, dict(kwargs, **{loopover: Q}), callback=cb) for Q in looplist]
        else:
            jobs = [pool.apply_async(funktion, (Q,) + args, kwargs, callback=cb) for Q in looplist]
        res = [job.get() for job in jobs]
        # clean up
        pool.close()
        pool.join()
        if output: print('closed pool again')
    return res


# noinspection PyIncorrectDocstring
def doForQlist(funktion, qList, *args, **kwargs):
    """
    Calculates for qlist the function in a pool of workers using multiprocessing.
    
    Calcs [function(Qi, *args, **kwargs) for Qi in qlist ] in parallel.
    The return value of function will contain the value Qi as reference.

    Parameters
    ----------
    funktion : function
        Function to process with arguments (looplist[i],args,kwargs)
    qList : list
        List of values for first argument in function.
        qList value prepends the arguments args.
    ncpu : int, optional
        | number of cpus in the pool
        | not given or 0   -> all cpus are used
        | int>0      min (ncpu, mp.cpu_count)
        | int<0      ncpu not to use
    cb :function, optional
        Callback after each calculation
    debug : int
        debug > 0 allows serial output for testing

    Returns
    -------
    list : ndim function_return.ndim+1
        The list elements will be prepended with the value qlist[i] as reference.

    Examples
    --------
    ::

     def f(x,a,b,c,d):
        return [x+a+b+c+d]
     # loop over first argument here x
     js.parallel.doForList(f,Qlist=np.arange(100),a=1,b=2,c=3,d=11)

    """
    output = kwargs.pop('output', True)
    ncpu = mp.cpu_count()
    if 'ncpu' in kwargs:
        if kwargs['ncpu'] < 0:
            ncpu = max(ncpu + kwargs['ncpu'], 1)
        elif kwargs['ncpu'] > 0:
            ncpu = min(ncpu, kwargs['ncpu'])
        del kwargs['ncpu']
    cb = kwargs.pop('cb', None)
    jobGetArg = kwargs.pop('jobGetArg', None)
    if ('debug' in kwargs and kwargs['debug'] > 0) or ncpu == 1:  # in sequence for testing purposes
        res = []
        if 'debug' in kwargs:
            del kwargs['debug']
        if output: print('start NO pool  this is a test ')
        for Q in qList:
            # noinspection PyCallingNonCallable
            res.append(funktion(*(Q,) + args, **kwargs))
            if cb is not None:
                cb(res[-1])
    else:  # in parallel for production run
        # print 'start pool of ',ncpu
        pool = mp.Pool(ncpu)
        jobs = [(Q, pool.apply_async(funktion, (Q,) + args, kwargs, callback=cb)) for Q in qList]
        res = [job[1].get(jobGetArg) for job in jobs]
        # clean up
        pool.close()
        pool.join()
        # print 'closed pool again'
    return res
