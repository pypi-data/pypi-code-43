from scipy.stats import linregress
import numpy as np


def extend_dataset(x, y, xmin, xmax, num_points=10):
    """
    Extends the dataset by fitting a linear curve to the end of
    the dataset.

    Parameters:

    x: array
        Original x array
    y: array
        Original y array
    xmin: float
        New minimum value for x
    xmax: float
        New maximum value for x
    num_points: int
        Number of points used in fit on each side

    Returns:

    x: array
        New extended x-array
    y: array
        New extended y-array
    """

    if xmin > np.min(x):
        raise ValueError("The new minimum value has to be smaller that the "
                         "current minimum value.")
    if xmax < np.max(x):
        raise ValueError("The new maximum value has to be larger than the "
                         "current maximum value.")

    if num_points > len(x):
        raise ValueError("num_points has to be smaller than the length of the "
                         "array")

    x1 = x[:num_points]
    y1 = y[:num_points]

    slope1, interscept1, pvalue, rvalue, stderr = linregress(x1, y1)

    new_y1 = slope1*xmin + interscept1
    x2 = x[-num_points:]
    y2 = y[-num_points:]
    slope2, interscept2, pvalue, rvalue, stderr = linregress(x1, y1)

    new_y2 = slope2*xmax + interscept2

    x_new = np.zeros(len(x)+2)
    y_new = np.zeros_like(x_new)
    x_new[1:-1] = x
    y_new[1:-1] = y
    x_new[0] = xmin
    x_new[-1] = xmax
    y_new[0] = new_y1
    y_new[-1] = new_y2
    return x_new, y_new

