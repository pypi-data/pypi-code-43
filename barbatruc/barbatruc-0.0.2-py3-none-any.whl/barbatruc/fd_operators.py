"""Module to handle Finite diff operators"""

import numpy as np

__all__ = ["grad_1", "grad_2", "scnd_der_2"]

#pylint: disable=unsupported-assignment-operation,invalid-sequence-index

def grad_1st_order(array_, d_x, perio=True):
    """Compute gradient of array (2nd order centered)"""
    grad_ = np.ones_like(array_)
    grad_[:, 1:-1] = (array_[:, 1:-1] - array_[:, 0:-2])/d_x
    if perio:
        grad_[:, -1] = (array_[:, -1] - array_[:, -2])/d_x
        grad_[:, 0] = (array_[:, 0] - array_[:, -2])/d_x
    else:
        grad_[:, -1] = (array_[:, -1] - array_[:, -2])/d_x
        grad_[:, 0] = (array_[:, 1] - array_[:, 0])/d_x
    return grad_


def grad_2nd_order(array_, d_x, perio=True):
    """Compute gradient of array (2nd order centered)"""
    grad_ = np.zeros_like(array_)
    grad_[:, 1:-1] = (array_[:, 2:] - array_[:, 0:-2])/(2*d_x)
    if perio:
        grad_[:, -1] = (array_[:, 1] - array_[:, -2])/(2*d_x)
        grad_[:, 0] = (array_[:, 1] - array_[:, -2])/(2*d_x)
    else:
        grad_[:, -1] = (array_[:, -1] - array_[:, -2])/d_x
        grad_[:, 0] = (array_[:, 1] - array_[:, 0])/d_x
    return grad_


def gradgrad_2nd_order(array_, d_x, perio=True, no_center=False):
    """Compute gradient of array (2nd order centered)"""
    ggrad = np.zeros_like(array_)
    if no_center:
        coef_center = 0
    else:
        coef_center = 2
    ggrad[:, 1:-1] = (
        array_[:, 2:]
        - coef_center*array_[:, 1:-1]
        + array_[:, 0:-2])/d_x**2

    if perio:
        ggrad[:, -1] = (array_[:, 1]
                        - coef_center*array_[:, -1]
                        + array_[:, -2])/d_x**2
        ggrad[:, 0] = (array_[:, 1]
                       - coef_center*array_[:, 0]
                       + array_[:, -2])/d_x**2
    else:
        ggrad[:, -1] = 2*ggrad[:, -2] - ggrad[:, -3]
        ggrad[:, 0] = 2*ggrad[:, 1] - ggrad[:, 2]
    return ggrad


def grad_1(array_, d_x, periox=False, perioy=False):
    """Compute the two gradients of an array."""
    g_x = grad_1st_order(array_, d_x, perio=periox)
    g_y = grad_1st_order(
        np.swapaxes(array_, 0, 1),
        d_x,
        perio=perioy)
    g_y = np.swapaxes(g_y, 0, 1)
    return g_x, g_y


def grad_2(array_, d_x, periox=False, perioy=False):
    """Compute the two gradients of an array."""
    g_x = grad_2nd_order(array_, d_x, perio=periox)
    g_y = grad_2nd_order(
        np.swapaxes(array_, 0, 1),
        d_x,
        perio=perioy)
    g_y = np.swapaxes(g_y, 0, 1)
    return g_x, g_y


def scnd_der_2(array_, d_x, periox=False, perioy=False, no_center=False):
    """Compute the two scnd derivatives of an array."""
    gg_x = gradgrad_2nd_order(
        array_,
        d_x,
        perio=periox,
        no_center=no_center)
    gg_y = gradgrad_2nd_order(
        np.swapaxes(array_, 0, 1),
        d_x,
        perio=perioy,
        no_center=no_center)
    gg_y = np.swapaxes(gg_y, 0, 1)
    return gg_x, gg_y
