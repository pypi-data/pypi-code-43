# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LibrarySettings.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LibrarySettings(object):
    def setupUi(self, LibrarySettings):
        LibrarySettings.setObjectName("LibrarySettings")
        LibrarySettings.resize(600, 500)
        self.gridLayout_2 = QtWidgets.QGridLayout(LibrarySettings)
        self.gridLayout_2.setVerticalSpacing(25)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(LibrarySettings)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setMinimumSize(QtCore.QSize(100, 0))
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.groupBox)
        self.pushButton_2.setMinimumSize(QtCore.QSize(100, 0))
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 2, 1, 1)
        self.listView = QtWidgets.QListView(self.groupBox)
        self.listView.setObjectName("listView")
        self.gridLayout.addWidget(self.listView, 0, 0, 1, 3)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 3, 0, 1, 3)
        self.label = QtWidgets.QLabel(LibrarySettings)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(LibrarySettings)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_2.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(LibrarySettings)
        self.checkBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout_2.addWidget(self.checkBox, 1, 0, 1, 3)
        self.pushButton_3 = QtWidgets.QPushButton(LibrarySettings)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout_2.addWidget(self.pushButton_3, 0, 2, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 0, 1, 1)

        self.retranslateUi(LibrarySettings)
        QtCore.QMetaObject.connectSlotsByName(LibrarySettings)

    def retranslateUi(self, LibrarySettings):
        _translate = QtCore.QCoreApplication.translate
        LibrarySettings.setWindowTitle(_translate("LibrarySettings", "Form"))
        self.groupBox.setTitle(_translate("LibrarySettings", "Library Directories"))
        self.pushButton.setText(_translate("LibrarySettings", "Remove"))
        self.pushButton_2.setText(_translate("LibrarySettings", "Add"))
        self.label.setText(_translate("LibrarySettings", "Library Databas File"))
        self.checkBox.setText(_translate("LibrarySettings", "Scan Library Directories on Startup"))
        self.pushButton_3.setText(_translate("LibrarySettings", "PushButton"))


