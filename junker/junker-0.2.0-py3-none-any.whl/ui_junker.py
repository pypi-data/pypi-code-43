# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_junker.ui'
#
# Created: Thu Dec 15 17:42:12 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Junker(object):
    def setupUi(self, Junker):
        Junker.setObjectName("Junker")
        Junker.resize(1009, 856)
        self.centralwidget = QtGui.QWidget(Junker)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelPNG = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelPNG.sizePolicy().hasHeightForWidth())
        self.labelPNG.setSizePolicy(sizePolicy)
        self.labelPNG.setAlignment(QtCore.Qt.AlignCenter)
        self.labelPNG.setObjectName("labelPNG")
        self.verticalLayout.addWidget(self.labelPNG)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonUndo = QtGui.QPushButton(self.centralwidget)
        self.buttonUndo.setObjectName("buttonUndo")
        self.horizontalLayout.addWidget(self.buttonUndo)
        self.buttonSalvage = QtGui.QPushButton(self.centralwidget)
        self.buttonSalvage.setObjectName("buttonSalvage")
        self.horizontalLayout.addWidget(self.buttonSalvage)
        self.buttonJunk = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonJunk.sizePolicy().hasHeightForWidth())
        self.buttonJunk.setSizePolicy(sizePolicy)
        self.buttonJunk.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.buttonJunk.setObjectName("buttonJunk")
        self.horizontalLayout.addWidget(self.buttonJunk)
        self.verticalLayout.addLayout(self.horizontalLayout)
        Junker.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(Junker)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1009, 19))
        self.menubar.setObjectName("menubar")
        Junker.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(Junker)
        self.statusbar.setObjectName("statusbar")
        Junker.setStatusBar(self.statusbar)

        self.retranslateUi(Junker)
        QtCore.QMetaObject.connectSlotsByName(Junker)

    def retranslateUi(self, Junker):
        Junker.setWindowTitle(QtGui.QApplication.translate("Junker", "Image Junker", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPNG.setText(QtGui.QApplication.translate("Junker", "PNG goes here", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonUndo.setText(QtGui.QApplication.translate("Junker", "Undo", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonSalvage.setText(QtGui.QApplication.translate("Junker", "Salvage It", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonJunk.setText(QtGui.QApplication.translate("Junker", "Junk it", None, QtGui.QApplication.UnicodeUTF8))

