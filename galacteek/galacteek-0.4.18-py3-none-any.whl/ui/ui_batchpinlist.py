# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/batchpinlist.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BatchPinList(object):
    def setupUi(self, BatchPinList):
        BatchPinList.setObjectName("BatchPinList")
        BatchPinList.resize(588, 397)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(BatchPinList)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelBasePath = QtWidgets.QLabel(BatchPinList)
        self.labelBasePath.setText("")
        self.labelBasePath.setObjectName("labelBasePath")
        self.horizontalLayout.addWidget(self.labelBasePath)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableWidget = QtWidgets.QTableWidget(BatchPinList)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout.addWidget(self.tableWidget)
        self.hLayoutCtrl = QtWidgets.QHBoxLayout()
        self.hLayoutCtrl.setObjectName("hLayoutCtrl")
        self.proceedButton = QtWidgets.QPushButton(BatchPinList)
        self.proceedButton.setMaximumSize(QtCore.QSize(300, 16777215))
        self.proceedButton.setObjectName("proceedButton")
        self.hLayoutCtrl.addWidget(self.proceedButton)
        self.cancelButton = QtWidgets.QPushButton(BatchPinList)
        self.cancelButton.setMaximumSize(QtCore.QSize(200, 16777215))
        self.cancelButton.setObjectName("cancelButton")
        self.hLayoutCtrl.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.hLayoutCtrl)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(BatchPinList)
        QtCore.QMetaObject.connectSlotsByName(BatchPinList)

    def retranslateUi(self, BatchPinList):
        _translate = QtCore.QCoreApplication.translate
        BatchPinList.setWindowTitle(_translate("BatchPinList", "Form"))
        self.proceedButton.setText(_translate("BatchPinList", "Pin selection"))
        self.cancelButton.setText(_translate("BatchPinList", "Cancel"))

