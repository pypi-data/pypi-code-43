# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'listselect.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(801, 462)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.menu_view = ListMenuView(Form)
        self.menu_view.setObjectName("menu_view")
        self.gridLayout.addWidget(self.menu_view, 0, 0, 3, 1)
        self.accept_button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.accept_button.sizePolicy().hasHeightForWidth())
        self.accept_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("FontAwesome")
        self.accept_button.setFont(font)
        self.accept_button.setObjectName("accept_button")
        self.gridLayout.addWidget(self.accept_button, 0, 2, 1, 1)
        self.cancel_button = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancel_button.sizePolicy().hasHeightForWidth())
        self.cancel_button.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("FontAwesome")
        self.cancel_button.setFont(font)
        self.cancel_button.setObjectName("cancel_button")
        self.gridLayout.addWidget(self.cancel_button, 2, 2, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.accept_button.setText(_translate("Form", ""))
        self.cancel_button.setText(_translate("Form", ""))
from epyqlib.listmenuview import ListMenuView
