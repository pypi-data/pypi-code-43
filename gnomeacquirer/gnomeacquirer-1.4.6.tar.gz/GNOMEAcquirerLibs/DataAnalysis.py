#!/usr/bin/env python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import matplotlib
matplotlib.use('Qt5Agg')
os.environ['QT_API'] = 'pyqt'

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import datetime
import copy

class DataAnalysisWidget(QWidget):
    MaxSizeToPlot = 10000
    def __init__(self, parent=None):
        super(DataAnalysisWidget, self).__init__(parent)

        self.mainLayout = QGridLayout()
        self.setLayout(self.mainLayout)

        self.initPlots(1)

    def appendData(self, dataToSave, startTime, samplingRate):
        timeArray = []
        timestep = datetime.timedelta(microseconds=float(10 ** 6) / float(samplingRate))
        t0 = copy.deepcopy(startTime)

        # get a random element to get array size
        for self.tmpDSName in dataToSave:
            pass

        # create time array
        for i in range(len(dataToSave[self.tmpDSName])):
            timeArray.append(mdates.date2num(t0))
            t0 += timestep

        if len(dataToSave) == len(self.dataToPlot):
            self.dataToPlot_timeAxis = self.dataToPlot_timeAxis + timeArray
            for self.tmpDataset in dataToSave:
                self.dataToPlot[self.tmpDataset] = self.dataToPlot[self.tmpDataset] + dataToSave[
                    self.tmpDataset].tolist()
            if len(self.dataToPlot[self.tmpDataset]) > self.MaxSizeToPlot:
                self.dataToPlot_timeAxis = self.dataToPlot_timeAxis[-self.MaxSizeToPlot:]
                for el in self.dataToPlot:
                    self.dataToPlot[el] = self.dataToPlot[el][-self.MaxSizeToPlot:]
        else:
            self.dataToPlot = dataToSave
            for self.tmpDataset in dataToSave:
                self.dataToPlot[self.tmpDataset] = dataToSave[self.tmpDataset].tolist()
            self.dataToPlot_timeAxis = timeArray

    def appendData(self, dataToSave, startTime, samplingRate):
        timeArray = []
        timestep = datetime.timedelta(microseconds=float(10 ** 6) / float(samplingRate))
        t0 = copy.deepcopy(startTime)

        # get a random element to get array size
        for self.tmpDSName in dataToSave:
            pass

        # create time array
        for i in range(len(dataToSave[self.tmpDSName])):
            timeArray.append(mdates.date2num(t0))
            t0 += timestep

        if len(dataToSave) == len(self.dataToPlot):
            self.dataToPlot_timeAxis = self.dataToPlot_timeAxis + timeArray
            for self.tmpDataset in dataToSave:
                self.dataToPlot[self.tmpDataset] = self.dataToPlot[self.tmpDataset] + dataToSave[
                    self.tmpDataset].tolist()
            if len(self.dataToPlot[self.tmpDataset]) > self.MaxSizeToPlot:
                self.dataToPlot_timeAxis = self.dataToPlot_timeAxis[-self.MaxSizeToPlot:]
                for el in self.dataToPlot:
                    self.dataToPlot[el] = self.dataToPlot[el][-self.MaxSizeToPlot:]
        else:
            self.dataToPlot = dataToSave
            for self.tmpDataset in dataToSave:
                self.dataToPlot[self.tmpDataset] = dataToSave[self.tmpDataset].tolist()
            self.dataToPlot_timeAxis = timeArray

    def setData(self, dataToSave, startTime, samplingRate):
        timeArray = []
        timestep = datetime.timedelta(microseconds=float(10 ** 6) / float(samplingRate))
        t0 = copy.deepcopy(startTime)

        # get a random element to get array size
        for self.tmpDSName in dataToSave:
            pass

        # create time array
        for i in range(len(dataToSave[self.tmpDSName])):
            timeArray.append(mdates.date2num(t0))
            t0 += timestep

        self.dataToPlot = dataToSave
        for self.tmpDataset in dataToSave:
            #the following line was changed by removing tolist(), which didn't work when the plotting scheme was changed
            # from passing DataBatch class to passing DataToPlot class
            # self.dataToPlot[self.tmpDataset] = dataToSave[self.tmpDataset].tolist()
            self.dataToPlot[self.tmpDataset] = dataToSave[self.tmpDataset]
        self.dataToPlot_timeAxis = timeArray

    def initPlots(self,numOfPlots):

        self.dataToPlot = []
        self.dataToPlot_timeAxis = []

        # generate the plot
        # prepare figure objects of Matplotlib
        self.gs = gridspec.GridSpec(numOfPlots,1)
        self.fig = Figure(figsize=(600,600), dpi=72, facecolor=(1,1,1), edgecolor=(0,0,0))
        self.ax = []
        try:
            for i in range(numOfPlots):
                self.ax.append(self.fig.add_subplot(self.gs[i]))
                self.ax[-1].plot([])
        except: pass

        # generate the canvas to display the plot
        self.canvas = FigureCanvas(self.fig)

        self.mainLayout.removeWidget(self.canvas)

        # add the plot canvas to a window
        self.mainLayout.addWidget(self.canvas,0,0,1,1)


    def doPlotData(self):

        #generate the plot
        #prepare figure objects of Matplotlib

        self.plotNumCounter = 0
        try:
            for array in sorted(self.dataToPlot):
                QCoreApplication.processEvents()
                self.ax[self.plotNumCounter].cla()
                self.ax[self.plotNumCounter].plot(self.dataToPlot_timeAxis,self.dataToPlot[array])
                self.ax[self.plotNumCounter].set_ylabel(array,size=12)
                self.ax[self.plotNumCounter].ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useOffset=True)
                if (self.plotNumCounter == len(self.dataToPlot)-1):
                    self.ax[self.plotNumCounter].tick_params(labelsize=12)
                    max_xticks = 6
                    xloc = plt.MaxNLocator(max_xticks)
                    self.ax[self.plotNumCounter].xaxis.set_major_locator(xloc)
                    xfmt = mdates.DateFormatter('%H:%M:%S\n%Y-%m-%d')
                    self.ax[self.plotNumCounter].xaxis.set_major_formatter(xfmt)
                    # print(self.dataToPlot[array])
                else:
                    self.ax[self.plotNumCounter].set_xticklabels([])
                    self.ax[self.plotNumCounter].tick_params(
                        axis='x',  # changes apply to the x-axis
                        labelbottom=False)  # labels along the bottom edge are off

                self.plotNumCounter += 1
                QCoreApplication.processEvents()
        except:
            sys.stderr.write("Error while trying to doPlot.\n")

        # generate the canvas to display the plot
        self.canvas.draw()
