"""
Example usage
-------------

"""
from __future__ import division
import math

import numpy

from .golub_welsch import _golub_welsch
from ..stieltjes import generate_stieltjes
from ..combine import combine


def quad_gauss_turan(n, dist=None):
    """
    Example:
        >>> abscissas, weights = quad_gauss_turan(6)
        >>> print(numpy.around(abscissas, 3))
        >>> print(numpy.around(weights, 3))
    """
    if dist is None:
        from chaospy.distributions.collection import Uniform
        dist = Uniform(lower=-1, upper=1)

    s = n+1
    hom = 1

    s0 = 1 if hom else s
    xw = numpy.zeros((n, 2*s+2))
    sn = (s+1)*n
    sn2 = (s+1)*n**2

    _, _, coeffs_a, coeffs_b = generate_stieltjes(dist, sn, retall=True)
    X, W = _golub_welsch(
        [len(coeffs_a[0])]*len(dist), coeffs_a, coeffs_b)
    ab0 = numpy.array([X[0], W]).T

    f = numpy.zeros((2*n-1, 1))
    fjac = numpy.zeros(2*n-1)
    A = numpy.zeros((n+1, sn2))
    B = numpy.zeros((n+1, sn2))
    D = numpy.zeros((n, sn2))
    P = numpy.zeros((n, sn2))
    Q = numpy.zeros((n, sn2))
    PI = numpy.zeros((n+1, sn))
    PI[0] = 1
    ab = ab0[:n]

    for sp in range(s0, s):
        rho = 
        rhop = numpy.zeros((2*n-1, 1))

    return xw
