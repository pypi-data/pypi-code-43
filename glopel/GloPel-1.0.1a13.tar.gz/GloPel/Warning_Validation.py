# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Warning_Validation.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Warning_validation_Number(object):
    def setupUi(self, Warning_validation_Number):
        Warning_validation_Number.setObjectName("Warning_validation_Number")
        Warning_validation_Number.resize(292, 83)
        Warning_validation_Number.setStyleSheet("background-color: rgb(165, 181, 209);")
        self.gridLayout = QtWidgets.QGridLayout(Warning_validation_Number)
        self.gridLayout.setObjectName("gridLayout")
        self.Lable_with_Number_of_eval = QtWidgets.QLabel(Warning_validation_Number)
        self.Lable_with_Number_of_eval.setMinimumSize(QtCore.QSize(30, 0))
        self.Lable_with_Number_of_eval.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Lable_with_Number_of_eval.setFont(font)
        self.Lable_with_Number_of_eval.setText("")
        self.Lable_with_Number_of_eval.setObjectName("Lable_with_Number_of_eval")
        self.gridLayout.addWidget(self.Lable_with_Number_of_eval, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(Warning_validation_Number)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 2)
        self.Lable_with_Number_of_eval_2 = QtWidgets.QLabel(Warning_validation_Number)
        self.Lable_with_Number_of_eval_2.setMinimumSize(QtCore.QSize(30, 0))
        self.Lable_with_Number_of_eval_2.setMaximumSize(QtCore.QSize(50, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.Lable_with_Number_of_eval_2.setFont(font)
        self.Lable_with_Number_of_eval_2.setText("")
        self.Lable_with_Number_of_eval_2.setObjectName("Lable_with_Number_of_eval_2")
        self.gridLayout.addWidget(self.Lable_with_Number_of_eval_2, 1, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(Warning_validation_Number)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 2)
        self.Continue_Evaluation_Button = QtWidgets.QPushButton(Warning_validation_Number)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Continue_Evaluation_Button.setFont(font)
        self.Continue_Evaluation_Button.setObjectName("Continue_Evaluation_Button")
        self.gridLayout.addWidget(self.Continue_Evaluation_Button, 2, 1, 1, 1)
        self.Cancel_Evaluation_Button_reject = QtWidgets.QPushButton(Warning_validation_Number)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.Cancel_Evaluation_Button_reject.setFont(font)
        self.Cancel_Evaluation_Button_reject.setObjectName("Cancel_Evaluation_Button_reject")
        self.gridLayout.addWidget(self.Cancel_Evaluation_Button_reject, 2, 2, 1, 1)

        self.retranslateUi(Warning_validation_Number)
        QtCore.QMetaObject.connectSlotsByName(Warning_validation_Number)

    def retranslateUi(self, Warning_validation_Number):
        _translate = QtCore.QCoreApplication.translate
        Warning_validation_Number.setWindowTitle(_translate("Warning_validation_Number", "Large number of validations"))
        self.label.setText(_translate("Warning_validation_Number", "total evaluations might take pretty long!"))
        self.label_2.setText(_translate("Warning_validation_Number", "Are you sure that you want to continue?"))
        self.Continue_Evaluation_Button.setText(_translate("Warning_validation_Number", "Continue"))
        self.Cancel_Evaluation_Button_reject.setText(_translate("Warning_validation_Number", "Cancel"))

