#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
plotting functions
author: Valentyn Stadnytskyi
data: 2017 - Nov 17 2018

"""
__vesrion__ = '1.0.0'
from time import  time, sleep
import sys
if sys.version_info[0] == 2:
    from time import clock as perf_counter
else:
    from time import perf_counter
import platform

#def generate_plot(x,y):#
    #from matplotlib.figure import Figure
    #from matplotlib import pyplot
    #from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
    #figure = Figure(figsize=(8,3),dpi=80)
    #axis = figure.add_subplot(1,1,1)
    #axis.plot(x,y)
    #return axis

def generate_plot(x,y):
    from matplotlib.figure import Figure
    from matplotlib import pyplot as plt
    #from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
    figure = plt.figure()
    axis = figure.add_subplot(1,1,1)
    axis.plot(x,y)
    return figure

from ubcs_auxiliary import save_object, load_object


if __name__ == '__main__':
    from numpy import arange, random
    x = arange(0,100,1)
    y = random.random((100,))
    #save_object('plot.pltpkl',generate_plot(x,y))
    figure_loaded = load_object('plot.pltpkl')

    #figure_loaded.show()
