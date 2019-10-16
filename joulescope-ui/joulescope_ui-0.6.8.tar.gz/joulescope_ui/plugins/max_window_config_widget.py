# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\plugins\max_window_config_widget.ui',
# licensing of 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\plugins\max_window_config_widget.ui' applies.
#
# Created: Tue Oct 15 17:20:22 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(368, 123)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.signal = QtWidgets.QComboBox(Dialog)
        self.signal.setObjectName("signal")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.signal)
        self.time_len = QtWidgets.QDoubleSpinBox(Dialog)
        self.time_len.setDecimals(5)
        self.time_len.setMinimum(1e-05)
        self.time_len.setMaximum(1000.0)
        self.time_len.setSingleStep(0.1)
        self.time_len.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.time_len.setObjectName("time_len")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.time_len)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Max Window configuration", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Width of window (in seconds)", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Signal", None, -1))

