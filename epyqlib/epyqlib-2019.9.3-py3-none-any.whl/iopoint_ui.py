# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iopoint.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(795, 224)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.status = Led(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy)
        self.status.setProperty("label_visible", True)
        self.status.setObjectName("status")
        self.horizontalLayout.addWidget(self.status)
        self.set_label = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.set_label.sizePolicy().hasHeightForWidth())
        self.set_label.setSizePolicy(sizePolicy)
        self.set_label.setObjectName("set_label")
        self.horizontalLayout.addWidget(self.set_label)
        self.set = Check(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.set.sizePolicy().hasHeightForWidth())
        self.set.setSizePolicy(sizePolicy)
        self.set.setProperty("label_visible", False)
        self.set.setObjectName("set")
        self.horizontalLayout.addWidget(self.set)
        self.override = Check(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.override.sizePolicy().hasHeightForWidth())
        self.override.setSizePolicy(sizePolicy)
        self.override.setProperty("label_visible", False)
        self.override.setObjectName("override")
        self.horizontalLayout.addWidget(self.override)
        self.override_label = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.override_label.sizePolicy().hasHeightForWidth())
        self.override_label.setSizePolicy(sizePolicy)
        self.override_label.setObjectName("override_label")
        self.horizontalLayout.addWidget(self.override_label)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.set_label.setText(_translate("Form", "Set"))
        self.override_label.setText(_translate("Form", "Override"))
from epyqlib.widgets.check import Check
from epyqlib.widgets.led import Led
