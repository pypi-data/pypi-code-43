# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'variableselectionview.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.searchbox = SearchBox(Form)
        self.searchbox.setObjectName("searchbox")
        self.gridLayout.addWidget(self.searchbox, 0, 0, 1, 1)
        self.tree_view = QtWidgets.QTreeView(Form)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setObjectName("tree_view")
        self.gridLayout.addWidget(self.tree_view, 1, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
from epyqlib.searchbox import SearchBox
