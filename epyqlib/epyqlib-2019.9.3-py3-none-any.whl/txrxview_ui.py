# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'txrxview.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(648, 598)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.searchbox = SearchBox(Form)
        self.searchbox.setObjectName("searchbox")
        self.verticalLayout.addWidget(self.searchbox)
        self.tree_view = QtWidgets.QTreeView(Form)
        self.tree_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setObjectName("tree_view")
        self.verticalLayout.addWidget(self.tree_view)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
from epyqlib.searchbox import SearchBox
