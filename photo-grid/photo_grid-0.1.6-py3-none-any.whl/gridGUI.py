# basic imports 
import os
import sys
from enum import Enum

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from .grid import *
from .gui import * 
from .lib import *

class GRID_GUI(QMainWindow):
    """
    """
        
    def __init__(self, gridInput=None, idxPn=None):
        """
        ----------
        Parameters
        ----------
        """
        super().__init__()
        self.setStyleSheet("""
        QWidget {
            font: 20pt Trebuchet MS
        }
        QGroupBox::title{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;ㄊ
        }
        QGroupBox {
            border: 1px solid gray;
            border-radius: 9px;
            margin-top: 0.5em;
        }
        """)

        # CLI 
        self.grid = GRID()

        # GUI
        self.nPanel = -1
        self.pnContent = QWidget()
        self.pnMain = QStackedWidget()

        self.pnNavi = QWidget()
        self.btNext = QPushButton()
        self.btPrev = QPushButton()
        self.layout = None

        # Shortcut
        self.gridInput = gridInput
        self.idxPn = idxPn

        # UI
        self.initUI()    

    def startover(self):
        while self.pnMain.count()!=0:
            widget = self.pnMain.widget(self.pnMain.count()-1)
            self.pnMain.removeWidget(widget)

        self.nPanel = -1
        self.gridInput = None
        self.idxPn = None
        del self.grid
        self.grid = GRID()
        self.initUI()

    def initUI(self):
        """
        ----------
        Parameters
        ----------
        """
        
        # window setup
        self.setWindowTitle("GRID")
        self.setMinimumSize(QSize(1440, 900))
        self.centerWindow()
       
        # initialize with first panel
        if self.gridInput is None:
            self.showInputer()
        else:
        # or use shortcut
            self.grid = self.gridInput
            if self.idxPn==0:
                self.showInputer()
            elif self.idxPn==1:
                self.showCropper()
            elif self.idxPn==2:
                self.showKMeaner()
            elif self.idxPn==3:
                self.showAnchor()
            elif self.idxPn==4:
                self.showOutputer()
        
        # show
        self.show()

    def showInputer(self, isNew=True):
        bugmsg("show input")
        self.assembleNavigation(nameNext="Load Files ->", oneSide=True)
        self.btNext.clicked.connect(
            lambda: self.showCropper())
        self.updateMainPn(panel=Panels.INPUTER, isNew=isNew)

    def showCropper(self, isNew=True):
        bugmsg("crop")
        self.assembleNavigation()
        self.btPrev.clicked.connect(
            lambda: self.showInputer(isNew=False))
        self.btNext.clicked.connect(
            lambda: self.showKMeaner())
        self.updateMainPn(panel=Panels.CROPPER, isNew=isNew)     

    def showKMeaner(self, isNew=True):
        bugmsg("kmean")
        self.assembleNavigation()
        self.btPrev.clicked.connect(
            lambda: self.showCropper(isNew=False))
        self.btNext.clicked.connect(
            lambda: self.showAnchor())
        self.updateMainPn(panel=Panels.KMEANER, isNew=isNew)

    def showAnchor(self, isNew=True):
        bugmsg("anchor")
        self.assembleNavigation()
        self.btPrev.clicked.connect(
            lambda: self.showKMeaner(isNew=False))
        self.btNext.clicked.connect(
            lambda: self.showOutputer())
        self.updateMainPn(panel=Panels.ANCHOR, isNew=isNew)

    def showOutputer(self, isNew=True):
        bugmsg("show output")
        self.assembleNavigation(nameNext="Finish")
        self.btPrev.clicked.connect(
            lambda: self.showAnchor(isNew=False))
        self.btNext.clicked.connect(lambda: self.finalize())
        self.updateMainPn(panel=Panels.OUTPUTER, isNew=isNew)

    def updateMainPn(self, panel, isNew=True):
        # traverse forward
        if isNew:
            try:
                # run computation from the previous panel
                bugmsg("run")
                self.pnMain.currentWidget().run()
            except Exception as e:
                bugmsg(e)
                # except the initial one
                None

            self.pnMain.addWidget(panel.value[1](self.grid))
            self.nPanel += 1
        # traverse backward
        else:
            widget = self.pnMain.widget(panel.value[0]+1)
            self.pnMain.removeWidget(widget)
            self.nPanel -= 1
            
        # set current widget
        self.pnMain.setCurrentIndex(self.nPanel)

        # show
        self.assembleAndShow()

    def finalize(self):
        """
        ----------
        Parameters
        ----------
        """

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Finished!")
        msgBox.setInformativeText("Save and start another job?")
        msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Save:
            path = self.pnMain.currentWidget().fd_output.text()
            prefix = self.pnMain.currentWidget().fd_project.text()
            self.grid.save(path=path, prefix=prefix)
            self.startover()
        elif returnValue == QMessageBox.Discard:
            self.startover()
            
    def centerWindow(self):
        """
        ----------
        Parameters
        ----------
        """

        center = QApplication.desktop().availableGeometry().center()
        rect = self.geometry()
        rect.moveCenter(center)
        self.setGeometry(rect)

    def assembleNavigation(self, nameNext="Next ->", namePrev="<- Prev", oneSide=False):
        """
        ----------
        Parameters
        ----------
        """

        self.pnNavi = QWidget()
        self.btNext = QPushButton(nameNext)
        self.btPrev = QPushButton(namePrev)
        loNavi = QHBoxLayout()
        if oneSide:
            loNavi.addStretch(1)
        else:
            loNavi.addWidget(self.btPrev)
        loNavi.addWidget(self.btNext)
        self.pnNavi.setLayout(loNavi)

    def assembleAndShow(self):
        """
        ----------
        Parameters
        ----------
        """

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pnMain, Qt.AlignCenter)
        self.layout.addWidget(self.pnNavi)
        self.pnContent = QWidget()
        self.pnContent.setLayout(self.layout)
        self.setCentralWidget(self.pnContent)
        self.show()

class Panels(Enum):
    INPUTER = 0, PnInputer
    CROPPER = 1, PnCropper
    KMEANER = 2, PnKmeaner
    ANCHOR = 3, PnAnchor
    OUTPUTER = 4, PnOutputer



# ARCHIVE:
# def test(self):
#     import json
#     with open('anchors', 'w') as fout:
#         json.dump(self.params['anchors'], fout)
#     np.save("img_crop", self.params['crop'])
#     np.save("img_bin", self.params['bin'])
#     np.save("map", self.params['map'])
#     np.save("img_k", self.params['k'])
#     np.save("ls_bin", self.params['ls_bin'])
#     bugmsg("nc:%d" % (self.params['nc']))
#     bugmsg("nr:%d" % (self.params['nr']))


# def updateMainPn(self, panel, isNew=True):
#     # traverse forward
#     if isNew:
#         try:
#             # run computation from the previous panel
#             bugmsg("run")
#             self.pnMain.currentWidget().run()
#         except:
#             # except the initial one
#             None
#         self.pnMain.addWidget(panel.value[1](self.grid))
#     # traverse backward
#     else:
#         self.pnMain.removeWidget(self.pnMain.widget(panel.value[0]+1))

#     # set current widget
#     self.pnMain.setCurrentIndex(panel.value[0])

#     # show
#     self.assembleAndShow()
# 
# def updateMainPn(self, panel, isNew=True):
#     """
#     ----------
#     Parameters
#     ----------
#     """
#     # define events
#     if panel == Panels.INPUTER:
#         bugmsg("panel Input")
#         self.assembleNavigation(nameNext="Load Files ->", oneSide=True)
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.CROPPER))
#     elif panel == Panels.CROPPER:
#         bugmsg("panel cropper")
#         self.assembleNavigation()
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.INPUTER, isNew=False))
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.KMEANER))
#     elif panel == Panels.KMEANER:
#         bugmsg("panel kmeaner")
#         self.assembleNavigation()
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.CROPPER, isNew=False))
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.ANCHOR))
#     elif panel == Panels.ANCHOR:
#         self.assembleNavigation()
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.KMEANER, isNew=False))
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.OUTPUTER))
#     elif panel == Panels.OUTPUTER:
#         self.assembleNavigation(nameNext="Finish")
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.ANCHOR, isNew=False))
#         self.btNext.clicked.connect(lambda: self.finalize())

#     # traverse forward
#     if isNew:
#         try:
#             # run computation from the previous panel
#             bugmsg("run")
#             self.pnMain.currentWidget().run()
#         except:
#             # except the initial one
#             None
#         self.pnMain.addWidget(panel.value[1](self.grid))
#     # traverse backward
#     else:
#         self.pnMain.removeWidget(self.pnMain.widget(panel.value[0]+1))

#     # set current widget
#     self.pnMain.setCurrentIndex(panel.value[0])

#     # show
#     self.assembleAndShow()
# 