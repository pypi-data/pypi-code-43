# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/qschemecreatemapping.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QSchemeMappingDialog(object):
    def setupUi(self, QSchemeMappingDialog):
        QSchemeMappingDialog.setObjectName("QSchemeMappingDialog")
        QSchemeMappingDialog.resize(592, 297)
        self.gridLayout_3 = QtWidgets.QGridLayout(QSchemeMappingDialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtWidgets.QLabel(QSchemeMappingDialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.mappingName = QtWidgets.QLineEdit(QSchemeMappingDialog)
        self.mappingName.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.mappingName.setMaxLength(32)
        self.mappingName.setObjectName("mappingName")
        self.gridLayout_2.addWidget(self.mappingName, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(QSchemeMappingDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.ipnsResolveFrequency = QtWidgets.QSpinBox(QSchemeMappingDialog)
        self.ipnsResolveFrequency.setMaximumSize(QtCore.QSize(16777215, 32))
        self.ipnsResolveFrequency.setMinimum(60)
        self.ipnsResolveFrequency.setMaximum(86400)
        self.ipnsResolveFrequency.setProperty("value", 3600)
        self.ipnsResolveFrequency.setObjectName("ipnsResolveFrequency")
        self.gridLayout_2.addWidget(self.ipnsResolveFrequency, 1, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(QSchemeMappingDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 1, 0, 1, 1)
        self.mappedPath = QtWidgets.QLabel(QSchemeMappingDialog)
        self.mappedPath.setMaximumSize(QtCore.QSize(16777215, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.mappedPath.setFont(font)
        self.mappedPath.setText("")
        self.mappedPath.setObjectName("mappedPath")
        self.gridLayout_3.addWidget(self.mappedPath, 0, 0, 1, 1)

        self.retranslateUi(QSchemeMappingDialog)

    def retranslateUi(self, QSchemeMappingDialog):
        _translate = QtCore.QCoreApplication.translate
        QSchemeMappingDialog.setWindowTitle(_translate("QSchemeMappingDialog", "q:// scheme mapping"))
        self.label.setText(_translate("QSchemeMappingDialog", "Mapping name"))
        self.label_2.setText(_translate("QSchemeMappingDialog", "IPNS resolve frequency (seconds)"))

