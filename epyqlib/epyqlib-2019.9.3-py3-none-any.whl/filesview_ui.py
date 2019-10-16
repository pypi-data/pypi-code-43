# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filesview.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.gridLayout_2 = QtWidgets.QGridLayout(Form)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.listView = QtWidgets.QListView(Form)
        self.listView.setObjectName("listView")
        self.gridLayout.addWidget(self.listView, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.something = QtWidgets.QPushButton(Form)
        self.something.setObjectName("something")
        self.horizontalLayout.addWidget(self.something)
        self.more = QtWidgets.QPushButton(Form)
        self.more.setObjectName("more")
        self.horizontalLayout.addWidget(self.more)
        self.other = QtWidgets.QPushButton(Form)
        self.other.setObjectName("other")
        self.horizontalLayout.addWidget(self.other)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.something.setText(_translate("Form", "Something"))
        self.more.setText(_translate("Form", "More"))
        self.other.setText(_translate("Form", "Other..."))
