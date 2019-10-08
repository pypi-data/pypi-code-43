from scipy.interpolate import CubicSpline
import numpy as np


def height(x, y):
    """
    Returns the height of the lane as a function of horizontal distance

    Parameters:

    x: array
        List with x-coordinates of the knots

    y: array
        List with the y-coordinates of the knots

    >>> from eksternlab import height
    >>> x = [0.0, 0.2, 0.4, 0.6, 0.8]
    >>> y = [1.0, 0.7, 0.4, 0.5, 0.6]
    >>> h = height(x, y)

    To get the height at an arbitrary position x
    
    >>> x1 = 0.23
    >>> y1 = h(x1)
    """
    return CubicSpline(x, y, bc_type='natural', extrapolate=True)


def slope(cs, x):
    """
    Return the slope of the curve

    Parameters:

    cs: CubicSpline
        Instance of a cubic spline class
    x: float or array of floats
        Points at which to evaluate the slope angle

    >>> from eksternlab import slope
    >>> x = [0.23, 0.26, 0.39]
    >>> alpha = slope(h, x)
    """
    values = cs(x, 1)
    return -np.arctan(values)


def curvature(cs, x):
    """
    Return the curvature (inverse radius of curvature) of the lane.

    Parameters:

    cs: CubicSpline
        Instance of the CubicSpline calss

    x: float or array of floats
        Points at which to evaluate the curvature

    >>> from eksternlab import curvature
    >>> x = [0.23, 0.26, 0.39]
    >>> kappa = curvature(h, x)
    """
    second_deriv = cs(x, 2)
    deriv = cs(x, 1)
    return second_deriv/(1.0 + deriv**2)**1.5
