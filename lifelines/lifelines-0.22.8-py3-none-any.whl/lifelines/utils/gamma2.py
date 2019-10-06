# -*- coding: utf-8 -*-
from scipy.special import gammainc as _scipy_gammainc, gammaincc as _scipy_gammaincc
from autograd import numpy as np
from autograd.scipy.special import gamma
from autograd.extend import primitive, defvjp
from autograd.numpy.numpy_vjps import unbroadcast_f

"""
more ideas:

I should not be recreate gammainc and gammaincc. Better to use those routines
_and_ the gradient w.r.t x (z) that are already available. I should just replace
the gradient w.r.t s! This will use autograd's primitives, etc.


It's easy to test the accuracy of this gradient's approximation too.




autograd-gamma library?


"""


def approx_regularized_lower_inc_gamma(a, x):
    """
    Unstable when a << x because of floating point problems in _lower_gamma.
    In this case, a and x should be high floating point
    accurate numbers (float64 or float128)
    """
    v = x ** a * np.exp(-x) / _lower_gamma(a, x) / gamma(a)
    return v


def _lower_gamma(a, x, frac=40):
    CONTD_FRAC_ITERATIONS = frac
    assert CONTD_FRAC_ITERATIONS % 2 == 0, "must be even"
    n = CONTD_FRAC_ITERATIONS
    v = 1.0

    while n > 0:
        v = (a + n) - ((a + n / 2) * x) / v  # even n
        n -= 1
        v = (a + n) + ((n + 1) / 2) * x / v  # odd n
        n -= 1
    v = a - a * x / v

    return np.clip(v, 1e-15, np.inf)


delta = 1e-10
gammainc = primitive(_scipy_gammainc)

defvjp(
    gammainc,
    lambda ans, a, x: unbroadcast_f(
        # a, lambda g: (gammainc(a + delta, x) - gammainc(a, x)) / delta
        a,
        lambda g: g * grad(approx_regularized_lower_inc_gamma)(a, x),
    ),
    lambda ans, a, x: unbroadcast_f(x, lambda g: g * np.exp(-x) * np.power(x, a - 1) / gamma(a)),
)
