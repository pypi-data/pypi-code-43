# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'parameteredit.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(558, 504)
        Form.setProperty("style_small", True)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 2, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 1)
        self.description = QtWidgets.QLabel(Form)
        self.description.setWordWrap(True)
        self.description.setObjectName("description")
        self.gridLayout.addWidget(self.description, 4, 0, 1, 1)
        self.to_device = Epc(Form)
        self.to_device.setProperty("label_visible", False)
        self.to_device.setProperty("tx", True)
        self.to_device.setProperty("show_enumeration_value", False)
        self.to_device.setObjectName("to_device")
        self.gridLayout.addWidget(self.to_device, 5, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.esc_button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.esc_button.sizePolicy().hasHeightForWidth())
        self.esc_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("FontAwesome")
        self.esc_button.setFont(font)
        self.esc_button.setObjectName("esc_button")
        self.horizontalLayout.addWidget(self.esc_button)
        self.save_to_nv_button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.save_to_nv_button.sizePolicy().hasHeightForWidth())
        self.save_to_nv_button.setSizePolicy(sizePolicy)
        self.save_to_nv_button.setObjectName("save_to_nv_button")
        self.horizontalLayout.addWidget(self.save_to_nv_button)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.description.setText(_translate("Form", "TextLabel"))
        self.esc_button.setText(_translate("Form", ""))
        self.save_to_nv_button.setText(_translate("Form", "Save All Parameters To NV"))
from epyqlib.widgets.epc import Epc
