# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './snitch/ui/list_manager.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_EventMgmtButtons(object):
    def setupUi(self, EventMgmtButtons):
        EventMgmtButtons.setObjectName("EventMgmtButtons")
        EventMgmtButtons.resize(206, 71)
        self.horizontalLayout = QtWidgets.QHBoxLayout(EventMgmtButtons)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonAdd = QtWidgets.QToolButton(EventMgmtButtons)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/controls/ui/icons/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonAdd.setIcon(icon)
        self.buttonAdd.setIconSize(QtCore.QSize(24, 24))
        self.buttonAdd.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.buttonAdd.setObjectName("buttonAdd")
        self.horizontalLayout.addWidget(self.buttonAdd)
        self.buttonDel = QtWidgets.QPushButton(EventMgmtButtons)
        self.buttonDel.setEnabled(False)
        self.buttonDel.setMinimumSize(QtCore.QSize(32, 32))
        self.buttonDel.setMaximumSize(QtCore.QSize(32, 32))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/controls/ui/icons/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonDel.setIcon(icon1)
        self.buttonDel.setIconSize(QtCore.QSize(24, 24))
        self.buttonDel.setObjectName("buttonDel")
        self.horizontalLayout.addWidget(self.buttonDel)
        spacerItem = QtWidgets.QSpacerItem(51, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonDown = QtWidgets.QPushButton(EventMgmtButtons)
        self.buttonDown.setEnabled(False)
        self.buttonDown.setMinimumSize(QtCore.QSize(32, 32))
        self.buttonDown.setMaximumSize(QtCore.QSize(32, 32))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/controls/ui/icons/down.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonDown.setIcon(icon2)
        self.buttonDown.setIconSize(QtCore.QSize(24, 24))
        self.buttonDown.setObjectName("buttonDown")
        self.horizontalLayout.addWidget(self.buttonDown)
        self.buttonUp = QtWidgets.QPushButton(EventMgmtButtons)
        self.buttonUp.setEnabled(False)
        self.buttonUp.setMinimumSize(QtCore.QSize(32, 32))
        self.buttonUp.setMaximumSize(QtCore.QSize(32, 32))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/controls/ui/icons/up.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonUp.setIcon(icon3)
        self.buttonUp.setIconSize(QtCore.QSize(24, 24))
        self.buttonUp.setObjectName("buttonUp")
        self.horizontalLayout.addWidget(self.buttonUp)

        self.retranslateUi(EventMgmtButtons)
        QtCore.QMetaObject.connectSlotsByName(EventMgmtButtons)

    def retranslateUi(self, EventMgmtButtons):
        _translate = QtCore.QCoreApplication.translate
        EventMgmtButtons.setWindowTitle(_translate("EventMgmtButtons", "Form"))
        self.buttonDel.setToolTip(_translate("EventMgmtButtons", "Remove selected event"))
        self.buttonDown.setToolTip(_translate("EventMgmtButtons", "Move event down"))
        self.buttonUp.setToolTip(_translate("EventMgmtButtons", "Move event up"))
from snitch import assets_rc
