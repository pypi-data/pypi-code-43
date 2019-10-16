# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'compoundtoggle.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(152, 169)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.box = QtWidgets.QGroupBox(Form)
        self.box.setObjectName("box")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.box)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.command = Toggle(self.box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.command.sizePolicy().hasHeightForWidth())
        self.command.setSizePolicy(sizePolicy)
        self.command.setProperty("label_visible", False)
        self.command.setProperty("tx", True)
        self.command.setProperty("value_labels_visible", False)
        self.command.setObjectName("command")
        self.horizontalLayout.addWidget(self.command)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.status_on = Led(self.box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_on.sizePolicy().hasHeightForWidth())
        self.status_on.setSizePolicy(sizePolicy)
        self.status_on.setProperty("label_override", "")
        self.status_on.setProperty("label_visible", True)
        self.status_on.setProperty("label_from_enumeration", True)
        self.status_on.setObjectName("status_on")
        self.verticalLayout_12.addWidget(self.status_on)
        self.status_off = Led(self.box)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status_off.sizePolicy().hasHeightForWidth())
        self.status_off.setSizePolicy(sizePolicy)
        self.status_off.setProperty("label_override", "")
        self.status_off.setProperty("label_visible", True)
        self.status_off.setProperty("label_from_enumeration", True)
        self.status_off.setProperty("on_value", 0)
        self.status_off.setObjectName("status_off")
        self.verticalLayout_12.addWidget(self.status_off)
        self.horizontalLayout.addLayout(self.verticalLayout_12)
        self.horizontalLayout_2.addWidget(self.box)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.box.setTitle(_translate("Form", "GroupBox"))
from epyqlib.widgets.led import Led
from epyqlib.widgets.toggle import Toggle
