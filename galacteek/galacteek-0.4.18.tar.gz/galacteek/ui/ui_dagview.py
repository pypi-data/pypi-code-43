# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'galacteek/ui/dagview.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DagViewForm(object):
    def setupUi(self, DagViewForm):
        DagViewForm.setObjectName("DagViewForm")
        DagViewForm.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DagViewForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dagPath = QtWidgets.QLabel(DagViewForm)
        self.dagPath.setText("")
        self.dagPath.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.dagPath.setObjectName("dagPath")
        self.horizontalLayout.addWidget(self.dagPath)
        self.dagControlButton = QtWidgets.QToolButton(DagViewForm)
        self.dagControlButton.setMinimumSize(QtCore.QSize(32, 32))
        self.dagControlButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/share/icons/ipld.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.dagControlButton.setIcon(icon)
        self.dagControlButton.setIconSize(QtCore.QSize(24, 24))
        self.dagControlButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.dagControlButton.setObjectName("dagControlButton")
        self.horizontalLayout.addWidget(self.dagControlButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dagTree = QtWidgets.QTreeWidget(DagViewForm)
        self.dagTree.setColumnCount(2)
        self.dagTree.setObjectName("dagTree")
        self.dagTree.headerItem().setText(0, "1")
        self.dagTree.headerItem().setText(1, "2")
        self.dagTree.header().setVisible(False)
        self.dagTree.header().setDefaultSectionSize(200)
        self.dagTree.header().setMinimumSectionSize(180)
        self.dagTree.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.dagTree)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(DagViewForm)

    def retranslateUi(self, DagViewForm):
        _translate = QtCore.QCoreApplication.translate
        DagViewForm.setWindowTitle(_translate("DagViewForm", "Form"))

from . import galacteek_rc
