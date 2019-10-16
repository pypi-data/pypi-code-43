# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'compoundscale.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(330, 211)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.status = Scale(Form)
        self.status.setObjectName("status")
        self.verticalLayout.addWidget(self.status)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.command = Epc(Form)
        self.command.setProperty("label_visible", True)
        self.command.setProperty("tx", True)
        self.command.setObjectName("command")
        self.horizontalLayout.addWidget(self.command)
        self.echo = Epc(Form)
        self.echo.setProperty("label_visible", True)
        self.echo.setProperty("tx", False)
        self.echo.setObjectName("echo")
        self.horizontalLayout.addWidget(self.echo)
        self.numeric_status = Epc(Form)
        self.numeric_status.setProperty("label_visible", True)
        self.numeric_status.setProperty("tx", False)
        self.numeric_status.setObjectName("numeric_status")
        self.horizontalLayout.addWidget(self.numeric_status)
        self.verticalLayout.addLayout(self.horizontalLayout)

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
