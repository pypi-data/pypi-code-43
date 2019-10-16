# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tirons/src/akvo/akvo/gui/Loop.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoopAdd(object):
    def setupUi(self, LoopAdd):
        LoopAdd.setObjectName("LoopAdd")
        LoopAdd.resize(400, 300)
        self.formLayout = QtWidgets.QFormLayout(LoopAdd)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(LoopAdd)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label = QtWidgets.QLabel(LoopAdd)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.comboBox = QtWidgets.QComboBox(LoopAdd)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.comboBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(LoopAdd)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)
        self.lineEdit = QtWidgets.QLineEdit(LoopAdd)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)

        self.retranslateUi(LoopAdd)
        self.buttonBox.accepted.connect(LoopAdd.accept)
        self.buttonBox.rejected.connect(LoopAdd.reject)
        QtCore.QMetaObject.connectSlotsByName(LoopAdd)

    def retranslateUi(self, LoopAdd):
        _translate = QtCore.QCoreApplication.translate
        LoopAdd.setWindowTitle(_translate("LoopAdd", "Dialog"))
        self.label_2.setText(_translate("LoopAdd", "Label"))
        self.label.setText(_translate("LoopAdd", "Type"))
        self.comboBox.setItemText(0, _translate("LoopAdd", "Circular"))
        self.comboBox.setItemText(1, _translate("LoopAdd", "figure-8"))
        self.comboBox.setItemText(2, _translate("LoopAdd", "square-8"))
        self.comboBox.setItemText(3, _translate("LoopAdd", "New Item"))
        self.comboBox.setItemText(4, _translate("LoopAdd", "polygon"))
