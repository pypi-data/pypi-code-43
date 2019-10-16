# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'variableselection.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(636, 473)
        Form.setProperty("update_from_can_file", False)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.logging_led = Led(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logging_led.sizePolicy().hasHeightForWidth())
        self.logging_led.setSizePolicy(sizePolicy)
        self.logging_led.setProperty("label_from_enumeration", True)
        self.logging_led.setObjectName("logging_led")
        self.gridLayout.addWidget(self.logging_led, 0, 4, 1, 1)
        self.update_parameters_button = QtWidgets.QPushButton(Form)
        self.update_parameters_button.setObjectName("update_parameters_button")
        self.gridLayout.addWidget(self.update_parameters_button, 1, 2, 1, 1)
        self.save_selection_button = QtWidgets.QPushButton(Form)
        self.save_selection_button.setObjectName("save_selection_button")
        self.gridLayout.addWidget(self.save_selection_button, 1, 1, 1, 1)
        self.load_binary_button = QtWidgets.QPushButton(Form)
        self.load_binary_button.setObjectName("load_binary_button")
        self.gridLayout.addWidget(self.load_binary_button, 0, 0, 1, 1)
        self.reset_button = Button(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reset_button.sizePolicy().hasHeightForWidth())
        self.reset_button.setSizePolicy(sizePolicy)
        self.reset_button.setProperty("label_visible", False)
        self.reset_button.setProperty("tx", True)
        self.reset_button.setObjectName("reset_button")
        self.gridLayout.addWidget(self.reset_button, 0, 2, 1, 1)
        self.load_selection_button = QtWidgets.QPushButton(Form)
        self.load_selection_button.setObjectName("load_selection_button")
        self.gridLayout.addWidget(self.load_selection_button, 0, 1, 1, 1)
        self.view = VariableSelectionView(Form)
        self.view.setObjectName("view")
        self.gridLayout.addWidget(self.view, 2, 0, 1, 5)
        self.configuration_is_valid_led = Led(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.configuration_is_valid_led.sizePolicy().hasHeightForWidth())
        self.configuration_is_valid_led.setSizePolicy(sizePolicy)
        self.configuration_is_valid_led.setProperty("label_from_enumeration", True)
        self.configuration_is_valid_led.setObjectName("configuration_is_valid_led")
        self.gridLayout.addWidget(self.configuration_is_valid_led, 1, 0, 1, 1)
        self.process_raw_log_button = QtWidgets.QPushButton(Form)
        self.process_raw_log_button.setObjectName("process_raw_log_button")
        self.gridLayout.addWidget(self.process_raw_log_button, 0, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.logging_led.setProperty("label_override", _translate("Form", "Logging"))
        self.update_parameters_button.setText(_translate("Form", "Update Parameters"))
        self.save_selection_button.setText(_translate("Form", "Save Selection"))
        self.load_binary_button.setText(_translate("Form", "Load Binary"))
        self.reset_button.setProperty("label_override", _translate("Form", "Reset Log"))
        self.load_selection_button.setText(_translate("Form", "Load Selection"))
        self.configuration_is_valid_led.setProperty("label_override", _translate("Form", "Configuration Is Valid"))
        self.process_raw_log_button.setText(_translate("Form", "Process Raw Log"))
from epyqlib.variableselectionview import VariableSelectionView
from epyqlib.widgets.button import Button
from epyqlib.widgets.led import Led
