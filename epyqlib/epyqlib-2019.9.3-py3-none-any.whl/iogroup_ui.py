# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iogroup.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(909, 590)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.box = QtWidgets.QGroupBox(Form)
        self.box.setObjectName("box")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.box)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setObjectName("layout")
        self.verticalLayout_3.addLayout(self.layout)
        self.verticalLayout.addWidget(self.box)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.box.setTitle(_translate("Form", "GroupBox"))
