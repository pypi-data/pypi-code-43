# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Dialog_Residue.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(622, 276)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMinimumSize(QtCore.QSize(170, 220))
        Dialog.setMaximumSize(QtCore.QSize(700, 450))
        Dialog.setStyleSheet("background-color: rgb(165, 181, 209);")
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.Matplotlib_container_Dialog = QtWidgets.QWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Matplotlib_container_Dialog.sizePolicy().hasHeightForWidth())
        self.Matplotlib_container_Dialog.setSizePolicy(sizePolicy)
        self.Matplotlib_container_Dialog.setMinimumSize(QtCore.QSize(150, 150))
        self.Matplotlib_container_Dialog.setMaximumSize(QtCore.QSize(700, 400))
        self.Matplotlib_container_Dialog.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.Matplotlib_container_Dialog.setObjectName("Matplotlib_container_Dialog")
        self.gridLayout.addWidget(self.Matplotlib_container_Dialog, 0, 0, 1, 4)
        self.Av_Autokorrelation = QtWidgets.QPushButton(Dialog)
        self.Av_Autokorrelation.setMinimumSize(QtCore.QSize(0, 20))
        self.Av_Autokorrelation.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Av_Autokorrelation.setFont(font)
        self.Av_Autokorrelation.setObjectName("Av_Autokorrelation")
        self.gridLayout.addWidget(self.Av_Autokorrelation, 1, 0, 1, 1)
        self.Autokorrelation = QtWidgets.QPushButton(Dialog)
        self.Autokorrelation.setMinimumSize(QtCore.QSize(0, 20))
        self.Autokorrelation.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Autokorrelation.setFont(font)
        self.Autokorrelation.setObjectName("Autokorrelation")
        self.gridLayout.addWidget(self.Autokorrelation, 1, 1, 1, 1)
        self.Residues_Button = QtWidgets.QPushButton(Dialog)
        self.Residues_Button.setMinimumSize(QtCore.QSize(0, 20))
        self.Residues_Button.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Residues_Button.setFont(font)
        self.Residues_Button.setObjectName("Residues_Button")
        self.gridLayout.addWidget(self.Residues_Button, 1, 2, 1, 1)
        self.OK_Dialog_Button = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.OK_Dialog_Button.sizePolicy().hasHeightForWidth())
        self.OK_Dialog_Button.setSizePolicy(sizePolicy)
        self.OK_Dialog_Button.setMinimumSize(QtCore.QSize(0, 20))
        self.OK_Dialog_Button.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.OK_Dialog_Button.setFont(font)
        self.OK_Dialog_Button.setObjectName("OK_Dialog_Button")
        self.gridLayout.addWidget(self.OK_Dialog_Button, 1, 3, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Residual Inspection"))
        self.Av_Autokorrelation.setText(_translate("Dialog", "Av. Autocorrelation"))
        self.Autokorrelation.setText(_translate("Dialog", "Autocorrelation"))
        self.Residues_Button.setText(_translate("Dialog", "Residues"))
        self.OK_Dialog_Button.setText(_translate("Dialog", "Exit"))

