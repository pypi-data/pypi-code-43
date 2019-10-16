# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\plugins\histogram_config_widget.ui',
# licensing of 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\plugins\histogram_config_widget.ui' applies.
#
# Created: Tue Oct 15 17:20:22 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(368, 173)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.num_bins = QtWidgets.QSpinBox(Dialog)
        self.num_bins.setMaximum(1000)
        self.num_bins.setObjectName("num_bins")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.num_bins)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.signal = QtWidgets.QComboBox(Dialog)
        self.signal.setObjectName("signal")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.signal)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.normalization = QtWidgets.QComboBox(Dialog)
        self.normalization.setObjectName("normalization")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.normalization)
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
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Histogram configuration", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Number of bins (0 for auto)", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Signal", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("Dialog", "Histogram Type", None, -1))

