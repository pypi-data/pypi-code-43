#!/usr/bin/env python3
import os
import re
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import libHREELS as hh
hhPath = hh.__path__[0]+"\\"    # path to the package directory. Needed to find graphical user interface files (*.ui)
# hhPath = "libHREELS\\"    # path to the package directory. Needed to find graphical user interface files (*.ui)
from libHREELS import HREELS, Auger
# from HREELS import HREELS
# from Auger.Auger import Auger

class Auger_Window(QtWidgets.QMainWindow):
    """ fill in some initial data """

    def __init__(self,datapath= None, remoteDir=None):
        super(Auger_Window, self).__init__()
        self.ui = self.ui = uic.loadUi(hhPath+"viewauger.ui", self)
        self.xmin = 10.
        self.factor = 1.
        self.offset = 0.5
        self.useOffset = False
        self.normalized = False
        if datapath and os.path.exists(datapath):
            self.datapath = datapath
        else:
            self.datapath = "\\\\141.48.167.189\\BackUp02\\0_experiments\\EELS-PC4\\AES\\2019"
        if remoteDir and os.path.exists(remoteDir):
            self.remoteDir = remoteDir
        else:
            self.remoteDir = '\\\\141.48.167.189\\BackUp02\\0_experiments\\EELS-PC4\\Auger'
        self.wideScan = True
        self.marker = []
        # self.markerSet = False

        # initialize the widget "drawWidget" and attach it into the ui
        self.drawing_figure = plt.figure(frameon=False,figsize=(5, 4), dpi=150, tight_layout = True)
        self.drawing_pane = FigureCanvas(self.drawing_figure)
        self.drawing_figure.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.drawing_figure.canvas.setFocus()        
        # self.drawing_figure.canvas.mpl_connect('button_press_event', self.onMouse)
        self.drawing_pane.axes = self.drawing_pane.figure.add_subplot(111)
        self.ui.drawWidget.layout().addWidget(self.drawing_pane)
        # Add toolbar
        self.xToolbar = NavigationToolbar(self.drawing_pane, self)
        self.ui.drawWidget.layout().addWidget(self.xToolbar)
        self.xToolbar.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed))
        
        self.ui.lineEdit_directory.setText(self.datapath)
        self.ui.lineEdit_factor.setText('%4.1f'%(self.factor))
        self.ui.lineEdit_offset.setText('%4.1f'%(self.offset))

        # Action on user events
        self.ui.checkBoxOffset.toggled.connect(self.onUseOffset)
        self.ui.checkBoxMarker.toggled.connect(self.onMarkerSet)
        self.ui.pushButton_details.pressed.connect(self.onPushButton_details3)
        self.ui.lineEdit_factor.editingFinished.connect(self.onFactor)
        self.ui.lineEdit_offset.editingFinished.connect(self.onOffset)
        self.ui.lineEdit_directory.editingFinished.connect(self.onNewDirectory)

        # Create list of all datafiles in the directory
        self.createFileList()
        self.ui.listWidget.itemSelectionChanged.connect(self.onFileSelection)
        self.dataDir = QtWidgets.QFileDialog(self)
        self.dataDir.setDirectory("D:\\Data\\Python\\")

        # Action on user menu events: 
        self.action_directory.triggered.connect(self.onActionDir)
        self.action_test.triggered.connect(self.onActionTest)
        self.action_help.triggered.connect(self.onActionHelp)

        #Add a cursor:
        self.cursor = Cursor(self.drawing_pane, self.drawing_pane.axes)
        # self.cursorId = self.drawing_figure.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)



    def onFactor(self):
        try:
            val = float(self.ui.lineEdit_factor.text())
            self.factor = val
        except ValueError:
            self.ui.lineEdit_factor.setText('%4.1f'%(self.factor))
        self.onFileSelection()

    def onUseOffset(self):
        self.useOffset = self.ui.checkBoxOffset.isChecked()
        self.onOffset()

    def onOffset(self):
        try:
            val = float(self.ui.lineEdit_offset.text())
            self.offset = val
        except ValueError:
            self.ui.lineEdit_offset.setText('%4.1f'%(self.offset))
        self.onFileSelection()

    def onNormalized(self):
        self.normalized = self.ui.checkBoxNormalized.isChecked()
        self.onFileSelection()

    def onActionDir(self):
        self.dataDir.setDirectory("D:\\Data\\Python\\expHREELS\\data")
        directory = self.openDirectoryDialog()
        if directory:
            self.ui.lineEdit_directory.setText(directory)
            self.directory = directory
            self.ui.listWidget.clear()
            self.datapath = directory
            self.createFileList()

    def onNewDirectory(self):
            dirText = self.ui.lineEdit_directory.text()
            if os.path.exists(dirText):
                self.directory = self.ui.lineEdit_directory.text()
                self.ui.listWidget.clear()
                self.datapath = self.directory
                self.createFileList()
            else:
                self.ui.lineEdit_directory.setText('')


    def onActionTest(self):
        self.dataDir.setDirectory(self.remoteDir)
        directory = self.openDirectoryDialog()
        if directory:
            self.ui.lineEdit_directory.setText(directory)
            self.directory = directory
            self.ui.listWidget.clear()
            self.datapath = directory
            self.createFileList()

    def onActionHelp(self):
        pass
        msg = QtWidgets.QMessageBox()
        msg.setText('''
        This is version 0.4.0 of the MLU-Auger data browser
        designed for fast data screening and plotting.
        ''')
        msg.setWindowTitle("Auger data browser help")
        # msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        layout = msg.layout()
        widget = QtWidgets.QWidget()
        widget.setFixedSize(650, 1)
        layout.addWidget(widget, 3, 0, 1, 3)
        msg.buttonClicked.connect(self.onOK)            
        msg.exec_()

    def onPushButton_details(self):
        try:
            details = self.d.infoText()
        except:
            return
        msg = QtWidgets.QMessageBox()
        msg.setText(details)
        msg.setWindowTitle("Dataset details")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        layout = msg.layout()
        widget = QtWidgets.QWidget()
        widget.setFixedSize(650, 1)
        layout.addWidget(widget, 3, 0, 1, 3)
        msg.buttonClicked.connect(self.onOK)            
        msg.exec_()

    def onPushButton_details3(self):
        """Shows a dialog containing data details"""
        # try:
        #     self.d.infoText()
        #     print(self.d.infoText())
        # except:
        #     print('no info available.')
        #     return
        self.dialog = QtWidgets.QDialog(self)
        self.dialog.ui = uic.loadUi(hhPath+"viewhreels_dialog.ui", self.dialog)
        self.dialog.ui.setWindowTitle('Dataset details')
        self.dialog.ui.textArea.setPlainText(self.d.infoText())
        self.dialog.show()

    def onMarkerSet(self):
        b = self.ui.checkBoxMarker.isChecked()
        self.markerSet = b
        if not b:
            # Disconnect all mouse events from canvas:
            self.drawing_figure.canvas.mpl_disconnect(self.cursorId)
            self.drawing_figure.canvas.mpl_disconnect(self.canvasId)
        else:
            # Connect all mouse events from canvas to routines:
            self.cursorId = self.drawing_figure.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
            self.canvasId = self.drawing_figure.canvas.mpl_connect('button_press_event', self.onMouse)
            print('mouse enabled')

    def onOK(self, button):
        print("Button pressed is:",button.text())


    def onFileSelection(self):
        iMax = len(self.ui.listWidget.selectedItems())
        if iMax == 0:
            return
        firstItem = self.ui.listWidget.selectedItems()[0]
        self.d = Auger(firstItem.text(),self.datapath)
        if iMax > 1:        # Remember the last plot size if there are already plots
            # Read xmin, xmax for current window and set these values for added spectra:
            self.xdmin, self.xdmax = self.drawing_pane.axes.get_xlim() 
        plotColor = plt.cm.gnuplot(0)     # Define the color map (coolwarm; plasma; inferno; gnuplot)         
        self.updatePlot(xmin=self.xmin, factor=self.factor, normalized=self.normalized, color=plotColor)
        self.ydmin, _ = self.drawing_pane.axes.get_ylim() 

        try:
            self.dialog.ui.textArea.setPlainText(self.d.infoText())
        except:
            pass

        if iMax > 1:
            i = 1.
            for item in self.ui.listWidget.selectedItems()[1:]:
                plotColor = plt.cm.gnuplot(i/iMax)     # Define the color map (coolwarm; plasma; inferno; gnuplot)
                self.d = Auger(item.text(),self.datapath)
                self.secondPlot(xmin=self.xmin, factor=self.factor, normalized=self.normalized, offset=i*self.offset*self.useOffset, color=plotColor)
                # print(i, item.text())
                i += 1
        # Reversing the sequence of labels in the legend:
        handles, labels = self.drawing_pane.axes.get_legend_handles_labels()
        self.drawing_pane.axes.legend(handles[::-1], labels[::-1])
        # self.drawing_pane.axes.set_ylim(bottom=0.)
        self.drawing_figure.tight_layout()
        self.cursor = Cursor(self.drawing_pane, self.drawing_pane.axes)
        self.drawing_figure.canvas.mpl_connect('motion_notify_event', self.cursor.mouse_move)
        self.drawing_pane.draw()

    def onMouse(self, event):
        if not self.markerSet:
            return
        if (event.xdata):
            if event.button==1:
                x,y = event.xdata, event.ydata
                print(x,y)
                self.marker.append((x,y))
                self.setMarker(x,y,self.ydmin)
            elif event.button==3:
                pass
            self.drawing_pane.draw()

    def setMarker(self, x, y, ymin=0, size=None):
        ''' Set vertical marker with text label. Note that self.figure() needs to be 
        called before use.'''
        # trans = offset(self.ax, 0, 30)
        self.drawing_pane.axes.plot([x,x],[ymin,y], lw=1, c='black', ls='dashed')
        x = round(x)
        # plt.text(x,y,'%4i' % x, rotation=90, verticalalignment='bottom', horizontalalignment='center', transform=trans)
        self.drawing_pane.axes.text(x,y,'%4i' % x, rotation=90, verticalalignment='bottom', horizontalalignment='center')
        return
    

    def updatePlot(self,xmin=10, factor=1, normalized=False, color="red"):
        self.drawing_pane.axes.cla()
        # self.plotWidget(normalized=normalized)
        self.plotWidget(factor=factor, color=color, normalized=normalized)

    def secondPlot(self,xmin=70, factor=1, normalized=False, offset = 0., color="b-"):
        self.secondPlotWidget(xmin=xmin, xdmin=self.xdmin, xdmax=self.xdmax, factor=factor, color=color, label=self.d.fname, normalized=normalized, offset = offset)

    def plotWidget(self, xmin=None, xmax=None, factor=1, label='x', normalized=False, color="black",marker=True, offset = 0.):
        ''' plot(self, xmin=None, xmax=None, factor=1, label='x', normalized=False, color="b-",marker=True)'''
        self.d.pFactor = factor
        if xmin:
            nstart = self.d.findIndex(xmin)
        else:
            nstart = 0
        if xmax:
            nend = self.d.findIndex(xmax)
        else:
            nend = len(self.d.xdata)
        if label == "x":
            label = self.d.fname        
        self.drawing_pane.axes.plot(self.d.xdata[nstart:nend], factor*self.d.ydata[nstart:nend] + offset, color=color, label=label)
        self.d.factor = factor
        self.drawing_pane.axes.set_xlabel('Kinetic Energy (eV)')
        self.drawing_pane.axes.set_ylabel('Intensity (arb. units)')
        if marker:
            for (x,y) in self.d.marker:
                self.d.setMarker(x,y*factor)
        return

    def secondPlotWidget(self, xmin=None, xmax=None, xdmin=None, xdmax=None, factor=1, label='x', normalized=False, color="black",marker=True, offset = 0.):
        ''' plot(self, xmin=None, xmax=None, factor=1, label='x', normalized=False, color="b-",marker=True)'''
        self.d.pFactor = factor
        if xmin:
            nstart = self.d.findIndex(xmin)
        else:
            nstart = 0
        if xmax:
            nend = self.d.findIndex(xmax)
        else:
            nend = len(self.d.xdata)
        if label == "x":
            label = self.d.fname        
        self.drawing_pane.axes.plot(self.d.xdata[nstart:nend], factor*self.d.ydata[nstart:nend] + offset, color=color, label=label)
        self.drawing_pane.axes.set_xlim(xdmin, xdmax) 
        self.d.factor = factor
        return

    def getFileList(self, directory):
        '''Get the list of all Auger data files. The list is 
        sorted by the file creation date.'''
        list = os.listdir(directory)
        files = []
        for file in list:
            location = os.path.join(directory, file)
            size = os.path.getsize(location)
            time = os.path.getmtime(location)
            files.append((file, time, size))
        files.sort(key=lambda s: -s[1])  # sort by time
        fileNames = [item[0] for item in files]
        # SElect the specific Auger data files: E.g. 181207_A_01
        # AESFiles = [fn for fn in fileNames if (fn[6:9]=='_A_')]
        AESFiles = []
        for fn in fileNames:
            if (fn[6:9]=='_A_'):
                AESFiles.append(fn)
            elif re.search('^1[0-9][0-1][0-9][0-3][0-9]_', fn):
                AESFiles.append(fn)
        return AESFiles, len(AESFiles)

    def createFileList(self):
        for item in self.getFileList(self.datapath)[0]:
            fname = re.split('\.',item)[0]
            self.ui.listWidget.addItem(fname)
          
    def openDirectoryDialog(self):
        self.dataDir = QtWidgets.QFileDialog(self)
        options = self.dataDir.Options()
        # options = self.dataDir.ShowDirsOnly
        options |= self.dataDir.DontUseNativeDialog
        dir =self.dataDir.getExistingDirectory(self, 'Select data directory', options=options)
        if dir:
            return dir

class Cursor(object):
    def __init__(self, fig, ax):
        self.figure = fig
        self.ax = ax
        self.ly = ax.axvline(color='r')  # the vert line

    def mouse_move(self, event):
        if not event.inaxes:
            return
        self.ly.set_data([event.xdata, event.xdata], [0, 1])
        self.figure.draw()

def runViewer(datapath= None, remoteDir=None):
    """ Main function for graphical application start """
    app = QtWidgets.QApplication(sys.argv)
    form = Auger_Window(datapath= datapath, remoteDir=remoteDir)
    form.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    runViewer()