# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'compoundscaleleft.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(335, 428)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.command = Epc(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.command.sizePolicy().hasHeightForWidth())
        self.command.setSizePolicy(sizePolicy)
        self.command.setProperty("label_visible", True)
        self.command.setProperty("tx", True)
        self.command.setObjectName("command")
        self.verticalLayout.addWidget(self.command)
        self.echo = Epc(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.echo.sizePolicy().hasHeightForWidth())
        self.echo.setSizePolicy(sizePolicy)
        self.echo.setProperty("label_visible", True)
        self.echo.setProperty("tx", False)
        self.echo.setObjectName("echo")
        self.verticalLayout.addWidget(self.echo)
        self.numeric_status = Epc(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.numeric_status.sizePolicy().hasHeightForWidth())
        self.numeric_status.setSizePolicy(sizePolicy)
        self.numeric_status.setProperty("label_visible", True)
        self.numeric_status.setProperty("tx", False)
        self.numeric_status.setObjectName("numeric_status")
        self.verticalLayout.addWidget(self.numeric_status)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.status = Scale(Form)
        self.status.setObjectName("status")
        self.horizontalLayout.addWidget(self.status)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.command.setProperty("label_override", _translate("Form", "Command"))
        self.echo.setProperty("label_override", _translate("Form", "Response"))
        self.numeric_status.setProperty("label_override", _translate("Form", "Measured"))
from epyqlib.widgets.epc import Epc
from epyqlib.widgets.scale import Scale
