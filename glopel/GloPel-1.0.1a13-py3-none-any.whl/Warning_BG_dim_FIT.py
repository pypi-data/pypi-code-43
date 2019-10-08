# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Warning_BG_dim_FIT.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Warning_BGDIMFIT(object):
    def setupUi(self, Warning_BGDIMFIT):
        Warning_BGDIMFIT.setObjectName("Warning_BGDIMFIT")
        Warning_BGDIMFIT.resize(361, 151)
        Warning_BGDIMFIT.setStyleSheet("background-color: rgb(165, 181, 209);")
        self.gridLayout = QtWidgets.QGridLayout(Warning_BGDIMFIT)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(Warning_BGDIMFIT)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(Warning_BGDIMFIT)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 2)
        self.Cancel_BGDIM_Button_reject = QtWidgets.QPushButton(Warning_BGDIMFIT)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Cancel_BGDIM_Button_reject.setFont(font)
        self.Cancel_BGDIM_Button_reject.setObjectName("Cancel_BGDIM_Button_reject")
        self.gridLayout.addWidget(self.Cancel_BGDIM_Button_reject, 4, 1, 1, 1)
        self.Continue_BGDIM_Button = QtWidgets.QPushButton(Warning_BGDIMFIT)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Continue_BGDIM_Button.setFont(font)
        self.Continue_BGDIM_Button.setObjectName("Continue_BGDIM_Button")
        self.gridLayout.addWidget(self.Continue_BGDIM_Button, 4, 0, 1, 1)
        self.label = QtWidgets.QLabel(Warning_BGDIMFIT)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(Warning_BGDIMFIT)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)

        self.retranslateUi(Warning_BGDIMFIT)
        QtCore.QMetaObject.connectSlotsByName(Warning_BGDIMFIT)

    def retranslateUi(self, Warning_BGDIMFIT):
        _translate = QtCore.QCoreApplication.translate
        Warning_BGDIMFIT.setWindowTitle(_translate("Warning_BGDIMFIT", "Warning"))
        self.label_3.setText(_translate("Warning_BGDIMFIT", "not yet fully decayed!"))
        self.label_4.setText(_translate("Warning_BGDIMFIT", "Are you sure that you want to fit the dimension?"))
        self.Cancel_BGDIM_Button_reject.setText(_translate("Warning_BGDIMFIT", "Cancel"))
        self.Continue_BGDIM_Button.setText(_translate("Warning_BGDIMFIT", "Continue"))
        self.label.setText(_translate("Warning_BGDIMFIT", "Fitting the background dimension might"))
        self.label_2.setText(_translate("Warning_BGDIMFIT", "lead to wrong results if the modulation has"))

