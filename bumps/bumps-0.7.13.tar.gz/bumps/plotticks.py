from __future__ import print_function, division

from math import ceil, floor, log10
from collections import namedtuple

from matplotlib import ticker as mticker
from matplotlib import axis as maxis
from matplotlib import font_manager as mfont
from matplotlib import rcParams

_RenderKey = namedtuple('RenderKey', 'length limits scale')

class NiceLocator(mticker.Locator):
    def __init__(self, ticker, ttype):
        self.ticker = ticker
        self.ttype = ttype

    def __call__(self):
        if self.ttype == 'major':
            return self.ticker.get_major_ticks(self.axis)
        else:
            return self.ticker.get_minor_ticks(self.axis)

class NiceFormatter(mticker.Formatter):
    def __init__(self, ticker):
        self.ticker = ticker

    def __call__(self, value, pos=None):
        return self.ticker.get_label_value(self.axis, value)

class NiceTicks:
    def __init__(self, spacing):
        """
        *spacing* is in points
        """
        self.spacing = spacing / 72.  # 72 points per inch
        self._last_ticks = None
        self.major_locator = NiceLocator(self, 'major')
        self.minor_locator = NiceLocator(self, 'minor')
        self.major_formatter = NiceFormatter(self)
        self.minor_formatter = mticker.NullFormatter()

    def get_major_ticks(self, axis):
        self._calc_ticks(axis)
        return self.major_values

    def get_minor_ticks(self, axis):
        self._calc_ticks(axis)
        return self.minor_values

    def get_label_value(self, axis, value):
        # Assume the plot layout didn't change between get ticks and get label
        # Otherwise, we will be continually querying the backend for the size
        # of the axis on the canvas.
        #self._calc_ticks(axis)
        return self.major_labels.get(value, '')

    def _calc_ticks(self, axis):
        # Determine if the plot state has changed since ticks were calculated
        horizontal = isinstance(axis, maxis.XAxis)
        fig = axis.get_figure()
        bbox = axis.get_window_extent(fig.canvas.renderer)
        if bbox.width == 0.:
            bbox = axis.axes.get_window_extent(fig.canvas.renderer)
            if bbox.width == 0.:
                bbox = fig.get_window_extent(fig.canvas.renderer)
        bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
        length = bbox.width if horizontal else bbox.height
        key = _RenderKey(
            length,   # axis extent in inches
            tuple(axis.get_view_interval()),  # axis limits
            axis.get_scale(),  # linear/log scale
        )
        if self._last_ticks == key:
            return

        steps = max(int(key.length/self.spacing + 0.5), 2)
        if key.scale == 'log':
            major, minor = log_ticks(key.limits[0], key.limits[1], steps)
        else:
            major, minor = linear_ticks(key.limits[0], key.limits[1], steps)

        self.major_labels = dict(major)
        self.major_values = [value for value, label in major]
        self.minor_values = minor
        #print(key, major, minor)


def nice_ticks(axes=None, xlabel_spacing=7, ylabel_spacing=3):
    """
    label spacing in em units
    """
    if axes is None:
        # Delay loading pyplot as late as possible since it sets the backend.
        from matplotlib import pyplot
        axes = pyplot.gca()
    xlabelsize = rcParams['xtick.labelsize']
    xpoints = mfont.FontProperties(size=xlabelsize).get_size_in_points()
    xaxis = axes.get_xaxis()
    xticker = NiceTicks(spacing=xlabel_spacing*xpoints)
    xaxis.set_major_locator(xticker.major_locator)
    xaxis.set_minor_locator(xticker.minor_locator)
    xaxis.set_major_formatter(xticker.major_formatter)
    xaxis.set_minor_formatter(xticker.minor_formatter)
    ylabelsize = rcParams['ytick.labelsize']
    ypoints = mfont.FontProperties(size=ylabelsize).get_size_in_points()
    yaxis = axes.get_yaxis()
    yticker = NiceTicks(spacing=ylabel_spacing*ypoints)
    yaxis.set_major_locator(yticker.major_locator)
    yaxis.set_minor_locator(yticker.minor_locator)
    yaxis.set_major_formatter(yticker.major_formatter)
    yaxis.set_minor_formatter(yticker.minor_formatter)


def preset_ticks(axis_min, axis_max, major, minor):
    axis_width = axis_max - axis_min
    score = lambda v: (v - axis_min)/axis_width
    major = [(score(value), label) for value, label in ticks]
    minor = [score(value) for value in mticks]
    return major, minor


def linear_ticks(axis_min, axis_max, steps):
    # locate tick marks
    major_values, minor_values = linear_tick_values(axis_min, axis_max, steps)

    if len(major_values) > 1:
        step = major_values[1] - major_values[0]
        precision = int(floor(log10(step)))
        if precision < 0:
            precision = -precision + 1
    else:
        precision = 0

    # normalize maks to [0, 1] and format major tick labels
    axis_width = axis_max - axis_min
    #score = lambda v: (v - axis_min)/axis_width
    score = lambda v: v
    num_format = "%."+str(precision)+"g" if precision > 0 else "%g"
    major = [(score(v), num_format%v) for v in major_values]
    minor = [score(v) for v in minor_values]
    return major, minor


def linear_tick_values(axis_min, axis_max, steps):
    # Determine major and minor increment and number of subincrements
    width = axis_max - axis_min
    d = 10**ceil(log10(width/steps))
    if 5.*width/d <= steps:
        # major = d/5.
        minor = d/20.
        sub = 4
    elif 2.*width/d <= steps:
        # major = d/2.
        minor = d/10.
        sub = 5
    else:
        # major = d
        minor = d/5.
        sub = 5

    # Compute tics
    n = int(ceil(axis_min/minor))
    ticks, mticks = [], []
    d = n*minor
    while d <= axis_max:
        if n%sub == 0:
            # major tic --- normalized position followed by text
            # FIXME: for a small range away from 0 we are losing too many digits
            ticks.append(d)
        else:
            # minor tic --- just add normalized position
            mticks.append(d)
        n += 1
        d = n*minor

    return ticks, mticks


def log_ticks(axis_min, axis_max, steps):
    # Correct bad ranges
    # FIXME: this needs to be based on the actual values plotted
    if axis_max <= 0.:
        axis_max = 1.0
    if axis_min <= 0.:
        axis_min = axis_max/1000.
    major_values, minor_values = log_tick_values(axis_min, axis_max, steps)

    # normalize maks to [0, 1] and format major tick labels
    log_axis_min = log10(axis_min)
    log_axis_width = log10(axis_max) - log_axis_min
    #score = lambda v: (v - log_axis_min)/log_axis_width
    score = lambda v: v
    major = [(score(v), "%g"%v) for v in major_values]
    minor = [score(v) for v in minor_values]
    return major, minor


def log_tick_values(axis_min, axis_max, steps):
    width = log10(axis_max/axis_min)
    # find last decade marker below
    val = 10**floor(log10(axis_min))
    if width < 0.5:
        return linear_tick_values(axis_min, axis_max, steps)
    elif width > steps:
        # Multiple decades per tick, minor tics at remainder
        # FIXME: may want multiple decades per minor tick, too
        subticks = int(ceil(width/steps))
        # If data is not on a decade boundary, then start at next decade
        if val < axis_min*0.99:
            val = val*10.
        i = 0
        ticks, mticks = [], []
        while val <= axis_max:
            if i % subticks == 0:
                ticks.append(val)
            else:
                mticks.append(val)
            val *= 10.
            i += 1
    elif width*3 > steps:
        # Major tics at decades, minor tics at 2 and 5
        ticks, mticks = [], []
        while val <= axis_max:
            if val >= axis_min and val <= axis_max:
                ticks.append(val)
            elif 2.*val >= axis_min and 2.*val <= axis_max:
                mticks.append(2.*val)
            elif 5.*val >= axis_min and 5.*val <= axis_max:
                mticks.append(5.*val)
            val *= 10.
    elif width*10 > steps:
        # Major ticks at 1 2 5, minor ticks at 3 4 6 7 8 9
        ticks, mticks = [], []
        while val <= axis_max:
            for i in range(1, 10):
                if i*val >= axis_min and i*val <= axis_max:
                    if i in [1, 2, 5]:
                        ticks.append(i * val)
                    else:
                        mticks.append(i * val)
            val *= 10.
    else:
        # Major ticks a 1 2 3 4 5 6 7 8 9, no minor ticks
        # FIXME: consider minor tics at 1.2, 1.5, 2.5, 3.5, 4.5
        major = [1, 1.5, 2, 3, 4, 5, 7]
        minor = [1.2, 2.5, 3.5, 6, 8, 9]
        ticks, mticks = [], []
        while val < axis_max:
            for v in major:
                if v*val >= axis_min and v*val <= axis_max:
                    ticks.append(v*val)
            for v in minor:
                if v*val >= axis_min and v*val <= axis_max:
                    mticks.append(v*val)
            val *= 10.

    return ticks, mticks


def demo():
    import numpy as np
    import matplotlib.pyplot as plt
    t = np.linspace(-5, 5)
    v = np.exp(t)
    plt.subplot(211)
    h = plt.semilogy(t, v, '-')
    nice_ticks()
    plt.grid(True)
    plt.subplot(212)
    h = plt.semilogy(t, v, '-')
    nice_ticks()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    demo()