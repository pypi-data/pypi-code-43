# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Validation_Progress_Bar.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Validation_Progress_Dialog(object):
    def setupUi(self, Validation_Progress_Dialog):
        Validation_Progress_Dialog.setObjectName("Validation_Progress_Dialog")
        Validation_Progress_Dialog.resize(327, 121)
        font = QtGui.QFont()
        font.setPointSize(9)
        Validation_Progress_Dialog.setFont(font)
        Validation_Progress_Dialog.setStyleSheet("background-color: rgb(165, 181, 209);")
        self.gridLayout = QtWidgets.QGridLayout(Validation_Progress_Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Validation_Progress_Dialog)
        self.label.setMinimumSize(QtCore.QSize(0, 20))
        self.label.setMaximumSize(QtCore.QSize(16777215, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.progressBar_Validation = QtWidgets.QProgressBar(Validation_Progress_Dialog)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.progressBar_Validation.setFont(font)
        self.progressBar_Validation.setProperty("value", 0)
        self.progressBar_Validation.setObjectName("progressBar_Validation")
        self.gridLayout.addWidget(self.progressBar_Validation, 1, 0, 1, 2)
        self.Validation_Progress_OK = QtWidgets.QPushButton(Validation_Progress_Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Validation_Progress_OK.setFont(font)
        self.Validation_Progress_OK.setObjectName("Validation_Progress_OK")
        self.gridLayout.addWidget(self.Validation_Progress_OK, 2, 0, 1, 1)
        self.Validation_Progress_Exit = QtWidgets.QPushButton(Validation_Progress_Dialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Validation_Progress_Exit.setFont(font)
        self.Validation_Progress_Exit.setObjectName("Validation_Progress_Exit")
        self.gridLayout.addWidget(self.Validation_Progress_Exit, 2, 1, 1, 1)

        self.retranslateUi(Validation_Progress_Dialog)
        QtCore.QMetaObject.connectSlotsByName(Validation_Progress_Dialog)

    def retranslateUi(self, Validation_Progress_Dialog):
        _translate = QtCore.QCoreApplication.translate
        Validation_Progress_Dialog.setWindowTitle(_translate("Validation_Progress_Dialog", "Validation in progress"))
        self.label.setText(_translate("Validation_Progress_Dialog", "This may take from a few seconds up to several minutes"))
        self.Validation_Progress_OK.setText(_translate("Validation_Progress_Dialog", "OK"))
        self.Validation_Progress_Exit.setText(_translate("Validation_Progress_Dialog", "Exit"))

