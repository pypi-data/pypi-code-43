# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dualscale.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_container(object):
    def setupUi(self, container):
        container.setObjectName("container")
        container.resize(638, 627)
        self.gridLayout = QtWidgets.QGridLayout(container)
        self.gridLayout.setObjectName("gridLayout")
        self.glayout = QtWidgets.QGridLayout()
        self.glayout.setObjectName("glayout")
        self.gridLayout.addLayout(self.glayout, 0, 0, 1, 1)

        self.retranslateUi(container)
        QtCore.QMetaObject.connectSlotsByName(container)

    def retranslateUi(self, container):
        _translate = QtCore.QCoreApplication.translate
        container.setWindowTitle(_translate("container", "Form"))
