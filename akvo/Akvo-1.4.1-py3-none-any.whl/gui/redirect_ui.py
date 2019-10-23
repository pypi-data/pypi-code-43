# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tirons/src/akvo/akvo/gui/redirect.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_callScript(object):
    def setupUi(self, callScript):
        callScript.setObjectName("callScript")
        callScript.resize(691, 852)
        self.verticalLayout = QtWidgets.QVBoxLayout(callScript)
        self.verticalLayout.setObjectName("verticalLayout")
        self.statusbar = QtWidgets.QStatusBar(callScript)
        self.statusbar.setObjectName("statusbar")
        self.verticalLayout.addWidget(self.statusbar)
        self.textEdit = QtWidgets.QTextEdit(callScript)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.textEdit.setFont(font)
        self.textEdit.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.textEdit.setMouseTracking(False)
        self.textEdit.setReadOnly(True)
        self.textEdit.setOverwriteMode(True)
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)

        self.retranslateUi(callScript)
        QtCore.QMetaObject.connectSlotsByName(callScript)

    def retranslateUi(self, callScript):
        _translate = QtCore.QCoreApplication.translate
        callScript.setWindowTitle(_translate("callScript", "Dialog"))
        self.textEdit.setPlaceholderText(_translate("callScript", "This windows outputs STDOUT from a separate process."))
