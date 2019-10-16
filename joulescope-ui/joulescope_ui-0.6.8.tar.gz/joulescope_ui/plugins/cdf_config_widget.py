# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\plugins\cdf_config_widget.ui',
# licensing of 'D:\repos\Jetperch\pyjoulescope_ui\joulescope_ui\plugins\cdf_config_widget.ui' applies.
#
# Created: Tue Oct 15 17:20:22 2019
#      by: pyside2-uic  running on PySide2 5.13.0
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(259, 140)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.signal = QtWidgets.QComboBox(Dialog)
        self.signal.setObjectName("signal")
        self.signal.addItem("")
        self.signal.addItem("")
        self.signal.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.signal)
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
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "CDF configuration", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Signal                              ", None, -1))
        self.signal.setItemText(0, QtWidgets.QApplication.translate("Dialog", "current", None, -1))
        self.signal.setItemText(1, QtWidgets.QApplication.translate("Dialog", "voltage", None, -1))
        self.signal.setItemText(2, QtWidgets.QApplication.translate("Dialog", "power", None, -1))

