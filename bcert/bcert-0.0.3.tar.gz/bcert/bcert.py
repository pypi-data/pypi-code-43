# coding: utf-8

import os
import numpy as np

from abc import ABCMeta, abstractmethod
from multiprocessing import Pool
from itertools import product

class FunLipschitz(object):
    """ Abstract class representing function witch bound on the gradient.

    """
    def __init__(self, dim, fix_param=None):
        self.dim = dim
        self.fix_param = fix_param
        self.b_grad = self.bound_grad()

    @abstractmethod
    def f(self,x):
        """ The function itself. Please implement it.

        Parameters
        ----------
        x : list
            List of input of the function. Should be the same size as `dim`.

        Returns
        -------
        y : float
            Scalar corresponding to `f(x)`.
        """
        raise NotImplemented("Please implement the function")

    @abstractmethod
    def bound_grad(self):
        """ Bound on the gradient of f(x).

        Returns
        -------
            : float
            Scalar corresponding to an upper bound on the gradient of `f`.
        """
        raise NotImplemented("Please implement the function: return a scalar bound of the norm of the gradient")


class CompactSpace(object):
    """ Compact space class.

    """
    def __init__(self, bound):
        self.__bound = self.__check_dim_bound(bound)
        self.__dim = len(bound)

    def __check_dim_bound(self,bound):
        """ Safety check on the format of provided bound.

        Parameters
        ---------
        bound : numpy.ndarray
            2 dimension list

        Returns
        -------
        bound : numpy.ndarray
            Return the input `bound` if the format is correct. Raise an exception otherwise.
        """
        if len(bound.shape) != 2:
            raise ValueError("bound should be of two dimensions, found dimension {}".format(len(bound.shape)))
        elif len(bound[0]) !=2:
            raise ValueError("bound should contain exactly two elements per dimension")
        else:
            return bound

    def discretized(self, step):
        """ Discretized the domain (cf. `bound`) into subdomain -- hypercubes centered on points from a grid.

        Parameters
        ----------
        step : int or list
            Seperation between grid points.

        Returns
        -------
        grid : numpy.ndarray
            Discretized space i.e. grid.
        """
        if type(step) in [int,float]:
            return self.discretized_symmetric(step)
        elif type(step) is np.ndarray:
            return self.discretized_asymmetric(step)

    def discretized_symmetric(self, step):
        """ Discretized the domain. Grid with same distance between first nieghboring points.

        Parameters
        ----------
        step : int
            Seperation between grid points.

        Returns
        -------
        grid : numpy.ndarray
            Discretized space i.e. grid with distance `step` between first nieghbors.
        """
        X = np.meshgrid(*[np.arange(b[0],b[1]+step,step) for b in self.__bound])
        grid = np.array([x.ravel() for x in X]).T
        return grid

    def discretized_asymmetric(self, step):
        """ Discretized the domain. Grid with same distance between first nieghboring points.

        Parameters
        ----------
        step : list
            Seperation between grid points. `n`th element is the distance between point in the `n` direction.

        Returns
        -------
        grid : numpy.ndarray
            Discretized space i.e. grid.
        """
        raise NotImplemented("Function not implemente -- not compatible with discr_elem currently.")

    def discr_element(self, elem, step):
        """ Create new grid from a single point.

        Parameters
        ----------
        elem : list or numpy.array
            One dimensional list repsenting a point in the domain of definition.
        step : int
            Step, the distance between first neighbors grid point.

        Returns
        -------
        grid : numpy.ndarray
            A new grid, each element are the center `elem` shifted in all diagonal of the space.
        """
        if len(elem) != self.__dim:
            raise ValueError("provide element is not in the same space as the original compact space")
        grid = []
        new_center = step*np.array([c for c in product(range(-1,2,2), repeat=self.__dim)])
        for c in new_center:
            if (np.all([c[i]+e > self.__bound[i][0] for i,e in enumerate(elem)]) and
                np.all([c[i]+e < self.__bound[i][1] for i,e in enumerate(elem)])):
                    grid.append(c+elem)
        return np.array(grid)


def boundCert(fun, space, lmbd, step, exclude_element=None, **kwargs):
    """ Certification of an upper bound of a function with a bounded gradient.

    Parameters
    ----------
    fun : bcert.FunLipschitz
        Function to certify the bound on.
    space : bcert.CompactSpace
        A compact space from the BCert class.
    step : int
        Distance between first neighbors grid element.
    exclude_elem : None or numpy.ndarray
        2D-array, each element are point to exclude from the grid. Default `None`.

    Returns
    -------
    f_max : int
        Maximum of the function evolution found.
    g_max : list
        Point for which `f_max` was obtain.
    """
    depth = kwargs.get("depth", 0)
    verbose = kwargs.get("verbose",0)
    max_depth = kwargs.get("max_depth",-1)
    f_max = kwargs.get("f_max", -np.inf)
    g_max = kwargs.get("g_max", None)
    elem = kwargs.get("elem", None)
    grid = space.discretized(step) if depth == 0 else space.discr_element(elem, step/2)
    if verbose != 0:
        if depth % verbose:
            print("Depth {}, step is {}, max_function {}".format(depth, delta,max_f))
    for e,g in enumerate(grid):
        if type(exclude_element) is np.ndarray:
            if np.array([(g==_).all() for _ in exclude_element]).any():
                continue
        eval_f = fun.f(g)
        if eval_f >= lmbd:
            raise Exception("Exceed or found {}: reach {} at grid element {}, certification failed.".format(lmbd, eval_f, g))
        evol_f = eval_f+(step*fun.b_grad*np.sqrt(fun.dim)/2)
        exceed_lmbd = evol_f > lmbd
        if exceed_lmbd:
            f_max_tmp, g_max_tmp = boundCert(fun, space, lmbd, step/2,
                    exclude_element=exclude_element, f_max=f_max, 
                    g_max=g_max, depth=depth+1, elem=g)
            if f_max_tmp > f_max:
                f_max = f_max_tmp
                g_max = g_max_tmp
        else:
            if evol_f >= f_max:
                f_max = evol_f
                g_max = g
    if depth == 0:
        print("Maximum value found {} for x={}".format(f_max,g_max))
        print("Certification sucessfull.")
    return f_max, g_max

def boundCertPar(fun, bound, lmbd, step, exclude_element=None, threads=None):
    """ Parallelization of the `boundCert` function. This will subvide in `threads` the domain,
    this in the direction with the greatest distance between boundaries.

    Parameters
    ----------
    fun : bcert.FunLipschitz
        Function to certify the bound on.
    bound : numpy.ndarray
        Bound, 2D-array, to create a compact space from the BCert class.
    step : int
        Distance between first neighbors grid element.
    exclude_elem : None or numpy.ndarray
        2D-array, each element are point to exclude from the grid. Default `None`.
    threads : int
        Number of threads to use. Default is the number of core found on
        the device, or `1` if the preceding is inapplicable.

    Returns
    -------
    res : list
        List of output of `boundCert` for every subdomain.

    """
    if threads is None:
        try:
            threads = os.cpu_count()
        except:
            threads = 1
            print("Couldn't use automatic number of thread detection.",
            "This might occure when using virtualization.")
    bound_max = np.argmax([b[1]-b[0] for b in bound])
    bound_subdiv = bound[bound_max][1]/threads
    bound_div = [bound[:bound_max].tolist() + [[bound_subdiv*_, bound_subdiv*(_+1)]] 
            + bound[bound_max+1:].tolist() for _ in range(threads)]
    if step > bound_subdiv:
        step = bound_subdiv/2
        print("Step larger than bound_subdiv, changing it's value to {}".format(step))
    spaces = [CompactSpace(np.array(b)) for b in bound_div]
    with Pool(processes=threads) as pool:
        res = pool.starmap(boundCert, [(fun, s, lmbd, step,
            exclude_element) for s in spaces])
        print("Found max:\n",res)
        print("Certified.\n")
        return res

def boundCertUserPar(fun, bounds, lmbd, step, exclude_element=None):
    """ Parallelization of the `boundCert` function. One thread per provided bound.

    Parameters
    ----------
    fun : bcert.FunLipschitz
        Function to certify the bound on.
    bounds : numpy.ndarray or list
        List of bounds -- 3D-array -- to create compact spaces from each
        of the bound from the BCert class.
    step : int
        Distance between first neighbors grid element.
    exclude_elem : None or numpy.ndarray
        2D-array, each element are point to exclude from the grid. Default `None`.

    Returns
    -------
    res : list
        List of output of `boundCert` for every subdomain.
    """
    threads = len(bounds)
    spaces = [CompactSpace(b) for b in bounds]
    with Pool(processes=threads) as pool:
        res = pool.starmap(boundCert, [(fun, space, lmbd, step,
            exclude_element) for space in spaces])
        print("Found max:\n",res)
        print("Certified.\n")
        return res
