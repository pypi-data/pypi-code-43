# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scriptingview.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(743, 550)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.stop_button = QtWidgets.QPushButton(Form)
        self.stop_button.setObjectName("stop_button")
        self.gridLayout.addWidget(self.stop_button, 0, 9, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 7, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 3, 1, 1)
        self.run_button = QtWidgets.QPushButton(Form)
        self.run_button.setObjectName("run_button")
        self.gridLayout.addWidget(self.run_button, 0, 4, 1, 1)
        self.load_button = QtWidgets.QPushButton(Form)
        self.load_button.setObjectName("load_button")
        self.gridLayout.addWidget(self.load_button, 0, 1, 1, 1)
        self.pause_button = QtWidgets.QPushButton(Form)
        self.pause_button.setObjectName("pause_button")
        self.gridLayout.addWidget(self.pause_button, 0, 8, 1, 1)
        self.loop_button = QtWidgets.QPushButton(Form)
        self.loop_button.setObjectName("loop_button")
        self.gridLayout.addWidget(self.loop_button, 0, 5, 1, 1)
        self.continue_button = QtWidgets.QPushButton(Form)
        self.continue_button.setObjectName("continue_button")
        self.gridLayout.addWidget(self.continue_button, 0, 6, 1, 1)
        self.save_button = QtWidgets.QPushButton(Form)
        self.save_button.setObjectName("save_button")
        self.gridLayout.addWidget(self.save_button, 0, 2, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 10, 1, 1)
        self.csv_edit = QtWidgets.QPlainTextEdit(Form)
        self.csv_edit.setObjectName("csv_edit")
        self.gridLayout.addWidget(self.csv_edit, 1, 0, 1, 11)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.stop_button.setText(_translate("Form", "Stop"))
        self.run_button.setText(_translate("Form", "Run"))
        self.load_button.setText(_translate("Form", "Load..."))
        self.pause_button.setText(_translate("Form", "Pause"))
        self.loop_button.setText(_translate("Form", "Loop"))
        self.continue_button.setText(_translate("Form", "Continue"))
        self.save_button.setText(_translate("Form", "Save..."))
