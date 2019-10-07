from scipy.special import *
from itertools import chain, combinations_with_replacement
from sklearn import linear_model
from pyearth import Earth
from sklearn.decomposition import KernelPCA

def generate_kronecker(X, y, p=4):
    r"""

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree
    :return: data after applying new basis
    """
    def k(a, max_degree=p):
        (N,) = a.shape  # Unpacking fails if a is not 1-dimensional
        index_combs = chain.from_iterable((combinations_with_replacement(range(N), r) for r in range(1, max_degree)))
        return [np.prod(a[list(indices)]) for indices in index_combs]
    return np.apply_along_axis(k, 1, X)

def generate_hadamard(X, y, p=4):
    r"""

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree
    :return: data after applying new basis
    """
    x_hadamard = []
    N, _ = X.shape
    for i in range(N):
        x_hadamard_i = []
        # counting from p to 1
        for t in reversed(range(p)):
            if (t != 0):
                # hadamard product of each X^i_p
                x_hadamard_i = np.concatenate((x_hadamard_i, np.power(X[i], t)), axis=None)
        x_hadamard.append(x_hadamard_i)
    X_p = np.array(x_hadamard)
    return X_p


def generate_hermit(X, y, p=3):
    r"""
    The hermite polynomial is defined by

    .. math::

        H_n(x) = (-1)^ne^{x^2}\frac{d^n}{dx^n}e^{-x^2};

    :math:`H_n` is a polynomial of degree :math:`n`.

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree
    :return: data after applying new basis
    """
    N, n = X.shape
    X_p = np.zeros((N, p * n))
    for i in range(N):
        X_i = []
        for j in reversed(range(p)):
            h = hermite(j + 1)
            for m in reversed(range(n)):
                X_i.append(h(X[i, m]))
        X_p[i] = np.array(X_i)
    return X_p


def generate_legendre(X, y, p=3):
    r"""The legendre polynomial is defined

    .. math::

        \frac{d}{dx}\left[(1 - x^2)\frac{d}{dx}P_n(x)\right] + n(n + 1)P_n(x) = 0;

    :math:`P_n(x)` is a polynomial of degree :math:`n`.

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree
    :return: data after applying new basis
    """
    N, n = X.shape
    X_p = np.zeros((N, p * n))
    for i in range(N):
        X_i = []
        for j in reversed(range(p)):
            h = legendre(j + 1)
            for m in reversed(range(n)):
                X_i.append(h(X[i, m]))
        X_p[i] = np.array(X_i)
    return X_p


def generate_laguerre(X, y, p=3):
    r"""The laguerre polynomial is defined

    .. math::

        \frac{d}{dx}\left[(1 - x^2)\frac{d}{dx}P_n(x)\right] + n(n + 1)P_n(x) = 0;

    :math:`P_n(x)` is a polynomial of degree :math:`n`.

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree
    :return: data after applying new basis
    """
    N, n = X.shape
    X_p = np.zeros((N, p * n))
    for i in range(N):
        X_i = []
        for j in reversed(range(p)):
            h = laguerre(j + 1)
            for m in reversed(range(n)):
                X_i.append(h(X[i, m]))
        X_p[i] = np.array(X_i)
    return X_p


def generate_chebychev(X, y, p=5):
    r"""Chebyshev polynomial of the second kind on :math:`[-2, 2]`.
    Defined as :math:`S_n(x) = U_n(x/2)` where :math:`U_n` is the
    nth Chebychev polynomial of the second kind.

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree
    :return: data after applying new basis
    """
    N, n = X.shape
    X_p = np.zeros((N, p * n))
    for i in range(N):
        X_i = []
        for j in reversed(range(p)):
            # c = np.ones(j+2)
            # print(eval_chebys(j+2, X[i]).shape)
            X_i = np.concatenate((X_i, eval_chebys(j + 2, X[i])), axis=None)
        X_p[i] = np.array(X_i)
    return X_p


def generate_fourier(X, y, p=4):
    r"""For :math:`i`-th sample :math:`X[i]`, the constructed form is defined

    .. math::

        X_p[i]=X[i]\cdot C - X[i]\cdot S,

    :math:`C,S` are :math:`n\times n` matrices with

    .. math::
        C[k]=[\cos(k\cdot\frac{2\pi 0}{n}),...,\cos(k\cdot\frac{2\pi n}{n})],\\
        S[k]=[\sin(k\cdot\frac{2\pi 0}{n}),...,\sin(k\cdot\frac{2\pi n}{n})]

    for each :math:`k` in :math:`[0,...,n-1]`.

    :param X: original data
    :param y: low dimensional representation
    :param p: int, degree of polynomial basis, which is redundant for this fourier basis implementation
    :return: data after applying new basis
    """
    N, n = X.shape
    X_p = np.zeros((N, n))

    C = np.zeros((n, n))
    S = np.zeros((n, n))
    ns = np.arange(n)
    one_cycle = 2 * np.pi * ns / n
    for k in range(n):
        t_k = k * one_cycle
        C[k, :] = np.cos(t_k)
        S[k, :] = np.sin(t_k)
    for i in range(N):
        # ignore the imaginary i?
        X_p[i] = np.dot(X[i], C) - np.dot(X[i], S)

    # X_p = fft(X)
    return generate_kronecker(X_p, y)

def generate_spline(X, y):
    '''
    based on the implementation of MARS
    :param X:
    :return:
    '''
    model = Earth()
    model.fit(X, y)
    B = model.transform(X)
    return B

def generate_kpca(X, y):
    """

    :param X:
    :param y:
    :return:
    """
    model = KernelPCA(n_components=2, kernel="rbf")
    return model.fit_transform(X)