# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Waveform widgets."""

import time
from warnings import warn

import pyqtgraph as pg


class TimeStampAxisItem(pg.AxisItem):
    """Axis with times or dates as ticks."""
    def __init__(self, what_show='time', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enableAutoSIPrefix(enable=False)
        if what_show not in ['time', 'date']:
            raise ValueError("show must be 'time' or 'date'")
        self.what_show = what_show

    def tickStrings(self, values, scale, spacing):
        if self.what_show == 'time':
            return [time.strftime("%H:%M:%S", time.gmtime(secs))
                    for secs in values]
        if self.what_show == 'date':
            return [time.strftime("%y-%m-%d", time.gmtime(secs))
                    for secs in values]
        raise RuntimeError("scale must be time or date")


def get_time_stamp_axis_item(top=True):
    """Return custom axis item with time stamps."""
    res = {
        'bottom': TimeStampAxisItem(
            what_show='time',
            orientation='bottom'
        )
    }
    if top:
        res['top'] = TimeStampAxisItem(
            what_show='date',
            orientation='top'
        )
    return res


class Waveform(pg.PlotWidget):
    """Customized PyQtGraph.PlotWidget."""
    def __init__(self, parent=None, xlabel=None, time_axis=True):
        if time_axis:
            axisItems = get_time_stamp_axis_item()
        else:
            axisItems = None
        super().__init__(parent, axisItems=axisItems)

        self.showAxis('top')
        self.showAxis('right')

        self.state = {
            'online': False,
            'plot_color': (255, 255, 255),
        }
        self.showGrid(x=True, y=True)
        self.setMouseEnabled(x=True, y=False)

        if xlabel is not None:
            self.setLabel('bottom', xlabel)

        self.setDownsampling(mode='peak')
        self.setClipToView(True)
        self.enableAutoRange(True)
        self.curve = self.plot()

    def reset(self):
        """Clear plot."""
        self.clear()
        self.curve = self.plot()
        self.set_plot_color(self.state['plot_color'])
        self.setMouseEnabled(x=True, y=False)
        self.enableAutoRange(True)

    def set_online(self, value):
        """Set online or offline mode for waveform."""
        self.state['online'] = value
        if value:
            self.setClipToView(True)
            self.setMouseEnabled(x=False)
        else:
            self.setClipToView(False)
            self.setMouseEnabled(x=True)

    def set_plot_color(self, color):
        """Change plot color."""
        self.curve.setPen(color)
        self.state['plot_color'] = color

    def update_data(self, t, x):
        """Update plot."""
        if self.state['online'] and not self.isVisible():
            return
        if len(t) == 0:
            return
        self.curve.setData(t, x)
        self.setLimits(xMin=t[0], xMax=t[-1])
        self.setRange(
            xRange=(t[0], t[-1]),
            yRange=(min(x), max(x)),
            disableAutoRange=False
        )


class MultiWaveform(pg.GraphicsLayoutWidget):
    """Customized PyQtGraph.GraphicsLayoutWidget."""
    def __init__(self, parent=None):
        """Initialization."""
        super().__init__(parent)
        self.state = {
            'online': False,
            'plot_color': (255, 255, 255),
        }
        self.plots = {}
        self.curves = {}
        self._main = None
        self.__main_plot_limits = None

    def set_main_plot(self, key):
        """Set the plot used for synchronization (main plot)."""
        self._main = key

    def get_main_plot(self):
        """Set the plot used for synchronization (main plot)."""
        return self._main

    main_plot = property(
        get_main_plot,
        set_main_plot,
        doc="Plot used for synchronization"
    )

    def _init_plot(self, key):
        # TODO: move this code to add_plot
        """Bring plot to initial state."""
        if key not in self.plots.keys():
            return
        plot = self.plots[key]
        plot.setDownsampling(mode='peak')
        plot.showGrid(x=True, y=True)
        plot.setMouseEnabled(x=True, y=False)
        plot.showAxis('right')
        for axis in ['left', 'right']:
            plot.getAxis(axis).setStyle(
                tickTextWidth=40,
                autoExpandTextSpace=False
            )
        plot.enableAutoRange(True)

    def add_plot(self, key, title=None, main=False, time_axes=False):
        """Add plot."""
        if time_axes:
            axes = get_time_stamp_axis_item()
        else:
            axes = None

        self.plots[key] = self.addPlot(len(self.plots), 0, axisItems=axes)
        self._init_plot(key)

        if title is not None:
            self.plots[key].setTitle(title, justify='left')

        self.curves[key] = self.plots[key].plot()
        self.curves[key].setPen(self.state['plot_color'])

        # TODO: deprecate main argument
        if main:
            self._main = key

    def remove_plots(self):
        """Remove all plots."""
        for key in self.plots:
            self.removeItem(self.plots[key])
        self.plots = {}
        self.curves = {}
        self._main = None

    def update_data(self, key, t, x):
        """Update data on the plot."""
        if len(t) == 0:
            return
        if self.state['online'] and not self.isVisible():
            return

        xlims = (t[0], t[-1])

        if key == self._main:
            self.__main_plot_limits = xlims
        elif self._main is not None:
            xlims = self.__main_plot_limits

        self.curves[key].setData(t, x)

        self.plots[key].setLimits(xMin=xlims[0], xMax=xlims[1])
        self.plots[key].setRange(
            xRange=(xlims[0], xlims[1]),
            yRange=(min(x), max(x)),
            disableAutoRange=False
        )

    def set_online(self, value):
        """Turn on or turn off the online mode."""
        self.state['online'] = value
        if value:
            for plot in self.plots.values():
                plot.setClipToView(True)
                plot.setMouseEnabled(x=False)
        else:
            for plot in self.plots.values():
                plot.setClipToView(False)
                plot.setMouseEnabled(x=True)

    def set_plot_color(self, color):
        """Set color for all plots."""
        message = "MultiWaveform.set_plot_color() is deprecated. "
        message += "Use MultiWaveform.set_plots_color()."
        warn(message)
        self.set_plots_color(color)

    def set_plots_color(self, color):
        """Set color for all plots."""
        for curve in self.curves.values():
            curve.setPen(color)
        self.state['plot_color'] = color

    def set_link_to_main(self, value=True):
        """Link plots to main or unlink."""
        for key in self.plots:
            if key == self._main:
                continue
            self.plots[key].setXLink(self.plots[self._main] if value else None)
