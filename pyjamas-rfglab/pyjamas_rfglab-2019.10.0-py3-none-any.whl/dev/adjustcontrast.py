# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'adjustcontrast.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(221, 245)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(-150, 200, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox_3 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 120, 181, 71))
        self.groupBox_3.setObjectName("groupBox_3")
        self.sbdilation = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbdilation.setGeometry(QtCore.QRect(5, 40, 48, 24))
        self.sbdilation.setObjectName("sbdilation")
        self.sbdilation_2 = QtWidgets.QSpinBox(self.groupBox_3)
        self.sbdilation_2.setGeometry(QtCore.QRect(130, 40, 48, 24))
        self.sbdilation_2.setObjectName("sbdilation_2")
        self.pushButton = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButton.setGeometry(QtCore.QRect(55, 37, 71, 32))
        self.pushButton.setObjectName("pushButton")
        self.horizontalSlider = QtWidgets.QSlider(self.groupBox_3)
        self.horizontalSlider.setGeometry(QtCore.QRect(4, 20, 171, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.preview_window = QtWidgets.QWidget(Dialog)
        self.preview_window.setGeometry(QtCore.QRect(210, 10, 361, 331))
        self.preview_window.setObjectName("preview_window")

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Adjust contrast"))
        self.groupBox_3.setTitle(_translate("Dialog", "Min and max"))
        self.pushButton.setText(_translate("Dialog", "Auto"))


