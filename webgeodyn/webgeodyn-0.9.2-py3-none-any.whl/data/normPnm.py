import numpy as np


def semiNormalisedSchmidt(lmax):
    """ Given the maximal degree lmax, builds an array of
    Schmidt semi-normalisation constants for the Legendre functions.

    :param lmax: maximum degree
    :type lmax: int
    :return: normalisation of the Legendre functions for all l and m.
    :rtype: np.array
    """
    PnmNorm = np.zeros((lmax+1, lmax+1))
    for n in range(lmax+1):
        for m in range(lmax+1):
            if m > n:
                continue
            if m == 0:
                PnmNorm[m, n] = 1
                continue
            faclminusm = np.math.factorial(n-m)
            faclplusm = np.math.factorial(n+m)
            PnmNorm[m, n] = np.sqrt(2*faclminusm/faclplusm)*(-1)**m
    return PnmNorm


def noNorm(lmax):
    """ Returns an array of ones ('1') of appropriate dimensions to have
     non-normalised Legendre functions.

    :param lmax: maximum degree
    :type lmax: int
    :return: array of ones ('1') (dim: lmax x lmax+1)
    :rtype: np.array
    """
    return np.ones((lmax+1, lmax+1))
