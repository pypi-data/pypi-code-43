import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d


class Lane(object):
    """
    Utility class for extracting useful properties of a lane. It is assumed
    that there is a one-to-one mapping between the x- and y-coordinates.

    Parameters:

    x: array
        Array with x coordinates

    y: array
        Array with height coordinates of the lane
    """
    def __init__(self, x, y):
        self.x = np.linspace(np.min(x), np.max(x), len(x))
        interpolator = interp1d(x, y)
        self.y = interpolator(self.x)

    @property
    def dx(self):
        return self.x[1] - self.x[0]

    def height(self, smooth=5):
        """
        Returns an interpolator for the height of the lane

        Parameters:

        smooth: int
            Window length in Savgol-Filter. Has to be odd.
        """
        if smooth < 5:
            raise ValueError("smooth parameter has to be larger than 5")

        if smooth % 2 == 0:
            raise ValueError('smooth parameter has to be an odd number')

        filtered_data = savgol_filter(self.y, smooth, 3)
        return interp1d(self.x, filtered_data, bounds_error=False,
                        fill_value='extrapolate', assume_sorted=True)

    def slope(self, smooth=5):
        """
        Returns an interpolator for the slope angle (in radians) of the lane

        Parameters:

        smooth: int
            Window length in Savgol filter. Has to be odd.
        """
        if smooth < 5:
            raise ValueError('smooth parameter has to be larger than 5')

        if smooth % 2 == 0:
            raise ValueError('smooth parameter has to be an odd number')

        dydx = savgol_filter(self.y, smooth, 3, deriv=1, delta=self.dx)
        angle = np.arctan(-dydx)
        return interp1d(self.x, angle, bounds_error=False,
                        fill_value='extrapolate', assume_sorted=True)

    def radius_of_curvature(self, smooth=5):
        """
        Returns the radius of curvature

        Parameters:

        smooth: int
            Window length in Savgol filter. Has to be odd.
        """
        if smooth < 5:
            raise ValueError('smooth parameter has to be larger than 5')

        if smooth % 2 == 0:
            raise ValueError('smooth parameter has to be an odd number')

        dy2dx2 = savgol_filter(self.y, smooth, 3, deriv=2, delta=self.dx)
        dydx = savgol_filter(self.y, smooth, 3, deriv=1, delta=self.dx)
        R = (1.0 + dydx**2)**1.5
        R /= dy2dx2
        return interp1d(self.x, R, bounds_error=False,
                        fill_value='extrapolate', assume_sorted=True)
