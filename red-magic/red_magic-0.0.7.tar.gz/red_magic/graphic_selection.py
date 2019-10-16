#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: misiak
"""

import numpy as np

from matplotlib.widgets import (
        LassoSelector, RectangleSelector,
        Button, RadioButtons
)
from matplotlib.path import Path

class Data_Selector(object):

    def __init__(self, ax, line, proceed_func=None, alpha_other=0.3):
        self.canvas = ax.figure.canvas
        self.line = line
        self.fig = line.get_figure()
     
        rightl = 0.7
        self.fig.subplots_adjust(right=rightl)
        
        
        if proceed_func is None:
            proceed_func = lambda x: print(x)
        self.proceed_func = proceed_func
        
        self.alpha_other = alpha_other

        self.xys = line.get_xydata()
        self.Npts = len(self.xys)

        rax = self.fig.add_axes([rightl+0.1, 0.5, 0.15, 0.15])
        
        self.radio_label = ('rect', 'lasso')
        self.radio = RadioButtons(rax, self.radio_label, active=0)

        self.radio.on_clicked(self._radio_func)

        self.lasso = LassoSelector(ax, onselect=self.onselect_lasso)
        self.rect = RectangleSelector(ax, onselect=self.onselect_rect)
        
        proceed_ax = self.fig.add_axes([rightl+0.1, 0.4, 0.1, 0.045])
        self.proceed_button = Button(proceed_ax, 'Proceed', hovercolor='0.975')
        self.proceed_button.on_clicked(self._proceed)     

        
        self._radio_func('rect')
        
        self.ind = []

        self.pts = ax.scatter([], [], marker='.')

        self.ax = ax

    def _radio_func(self, label):
        for lab in self.radio_label:
            selector = getattr(self, lab)
            selector.set_active(False)
        
        selector = getattr(self, label)
        selector.set_active(True)

    def _proceed(self, event):
        output = self.proceed_func(self.ind)
        return output

    def onselect_lasso(self, verts):
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.line.set_alpha(self.alpha_other)
        x_select, y_select = self.xys[self.ind].T
        self.pts.set_offsets(self.xys[self.ind])
        self.canvas.draw_idle()

    def onselect_rect(self, eclick, erelease):
        'eclick and erelease are the press and release events'
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        verts = [(x1,y1), (x1, y2), (x2, y2), (x2, y1)]
        self.onselect_lasso(verts)

    def disconnect(self):
        self.lasso.disconnect_events()
        self.canvas.draw_idle()
