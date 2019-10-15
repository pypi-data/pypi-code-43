# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Projects\python\pyModSlave\ui\settings.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(240, 72)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Settings.sizePolicy().hasHeightForWidth())
        Settings.setSizePolicy(sizePolicy)
        Settings.setMinimumSize(QtCore.QSize(240, 72))
        Settings.setMaximumSize(QtCore.QSize(240, 96))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/options-16.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Settings.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Settings)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.sbMaxNoOfBusMonitorLines = QtWidgets.QSpinBox(Settings)
        self.sbMaxNoOfBusMonitorLines.setMaximum(100)
        self.sbMaxNoOfBusMonitorLines.setProperty("value", 50)
        self.sbMaxNoOfBusMonitorLines.setObjectName("sbMaxNoOfBusMonitorLines")
        self.gridLayout.addWidget(self.sbMaxNoOfBusMonitorLines, 0, 2, 1, 1)
        self.lblMaxNoOfBusMonitorLines = QtWidgets.QLabel(Settings)
        self.lblMaxNoOfBusMonitorLines.setObjectName("lblMaxNoOfBusMonitorLines")
        self.gridLayout.addWidget(self.lblMaxNoOfBusMonitorLines, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Settings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Settings)
        self.buttonBox.accepted.connect(Settings.accept)
        self.buttonBox.rejected.connect(Settings.reject)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Settings"))
        self.lblMaxNoOfBusMonitorLines.setText(_translate("Settings", "Max No of Bus Monitor Lines"))

import pyModSlaveQt_rc
