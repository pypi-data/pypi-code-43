# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './snitch/ui/modifier_picker.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ModifierCheckboxes(object):
    def setupUi(self, ModifierCheckboxes):
        ModifierCheckboxes.setObjectName("ModifierCheckboxes")
        ModifierCheckboxes.resize(190, 20)
        ModifierCheckboxes.setAutoFillBackground(True)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ModifierCheckboxes)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ctrlCheckBox = QtWidgets.QCheckBox(ModifierCheckboxes)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.ctrlCheckBox.setFont(font)
        self.ctrlCheckBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ctrlCheckBox.setIconSize(QtCore.QSize(16, 16))
        self.ctrlCheckBox.setObjectName("ctrlCheckBox")
        self.horizontalLayout.addWidget(self.ctrlCheckBox)
        self.shiftCheckBox = QtWidgets.QCheckBox(ModifierCheckboxes)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.shiftCheckBox.setFont(font)
        self.shiftCheckBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.shiftCheckBox.setIconSize(QtCore.QSize(16, 16))
        self.shiftCheckBox.setObjectName("shiftCheckBox")
        self.horizontalLayout.addWidget(self.shiftCheckBox)
        self.altCheckBox = QtWidgets.QCheckBox(ModifierCheckboxes)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.altCheckBox.setFont(font)
        self.altCheckBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.altCheckBox.setIconSize(QtCore.QSize(16, 16))
        self.altCheckBox.setObjectName("altCheckBox")
        self.horizontalLayout.addWidget(self.altCheckBox)
        self.alt_grCheckBox = QtWidgets.QCheckBox(ModifierCheckboxes)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.alt_grCheckBox.setFont(font)
        self.alt_grCheckBox.setFocusPolicy(QtCore.Qt.NoFocus)
        self.alt_grCheckBox.setIconSize(QtCore.QSize(16, 16))
        self.alt_grCheckBox.setObjectName("alt_grCheckBox")
        self.horizontalLayout.addWidget(self.alt_grCheckBox)

        self.retranslateUi(ModifierCheckboxes)
        QtCore.QMetaObject.connectSlotsByName(ModifierCheckboxes)

    def retranslateUi(self, ModifierCheckboxes):
        _translate = QtCore.QCoreApplication.translate
        ModifierCheckboxes.setWindowTitle(_translate("ModifierCheckboxes", "Form"))
        self.ctrlCheckBox.setText(_translate("ModifierCheckboxes", "ctrl"))
        self.shiftCheckBox.setText(_translate("ModifierCheckboxes", "shift"))
        self.altCheckBox.setText(_translate("ModifierCheckboxes", "alt"))
        self.alt_grCheckBox.setText(_translate("ModifierCheckboxes", "alt gr"))
