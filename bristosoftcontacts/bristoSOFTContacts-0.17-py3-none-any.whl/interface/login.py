# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_loginDialog(object):
    def setupUi(self, loginDialog):
        loginDialog.setObjectName("loginDialog")
        loginDialog.resize(485, 344)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/edit-user.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        loginDialog.setWindowIcon(icon)
        self.loginButtonBox = QtWidgets.QDialogButtonBox(loginDialog)
        self.loginButtonBox.setGeometry(QtCore.QRect(260, 290, 191, 32))
        self.loginButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.loginButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.loginButtonBox.setObjectName("loginButtonBox")
        self.label = QtWidgets.QLabel(loginDialog)
        self.label.setGeometry(QtCore.QRect(220, 20, 221, 31))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/icons/icons/bristo_logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.tabWidget = QtWidgets.QTabWidget(loginDialog)
        self.tabWidget.setGeometry(QtCore.QRect(50, 70, 401, 191))
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        self.tabWidget.setMovable(False)
        self.tabWidget.setObjectName("tabWidget")
        self.userTab = QtWidgets.QWidget()
        self.userTab.setAutoFillBackground(False)
        self.userTab.setObjectName("userTab")
        self.layoutWidget = QtWidgets.QWidget(self.userTab)
        self.layoutWidget.setGeometry(QtCore.QRect(18, 49, 361, 51))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.userNameLabel = QtWidgets.QLabel(self.layoutWidget)
        self.userNameLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.userNameLabel.setObjectName("userNameLabel")
        self.horizontalLayout.addWidget(self.userNameLabel)
        self.userNameLineEdit = QtWidgets.QLineEdit(self.layoutWidget)
        self.userNameLineEdit.setStyleSheet("background-color: rgb(255, 252, 213);")
        self.userNameLineEdit.setObjectName("userNameLineEdit")
        self.horizontalLayout.addWidget(self.userNameLineEdit)
        self.tabWidget.addTab(self.userTab, icon, "")
        self.passwordTab = QtWidgets.QWidget()
        self.passwordTab.setObjectName("passwordTab")
        self.layoutWidget1 = QtWidgets.QWidget(self.passwordTab)
        self.layoutWidget1.setGeometry(QtCore.QRect(21, 61, 351, 41))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.layoutWidget1)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.passwordLabel = QtWidgets.QLabel(self.layoutWidget1)
        self.passwordLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.passwordLabel.setObjectName("passwordLabel")
        self.gridLayout_2.addWidget(self.passwordLabel, 0, 0, 1, 1)
        self.passwordLineEdit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.passwordLineEdit.setStyleSheet("background-color: rgb(126, 154, 255);")
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.gridLayout_2.addWidget(self.passwordLineEdit, 0, 1, 1, 1)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/lock.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.tabWidget.addTab(self.passwordTab, icon1, "")
        self.label_2 = QtWidgets.QLabel(loginDialog)
        self.label_2.setGeometry(QtCore.QRect(60, 30, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.passwordLabel.setBuddy(self.passwordLineEdit)

        self.retranslateUi(loginDialog)
        self.tabWidget.setCurrentIndex(0)
        self.loginButtonBox.accepted.connect(loginDialog.accept)
        self.loginButtonBox.rejected.connect(loginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(loginDialog)

    def retranslateUi(self, loginDialog):
        _translate = QtCore.QCoreApplication.translate
        loginDialog.setWindowTitle(_translate("loginDialog", "bristoSOFT Contacts - Login"))
        self.userNameLabel.setText(_translate("loginDialog", "Username:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.userTab), _translate("loginDialog", "User"))
        self.passwordLabel.setText(_translate("loginDialog", "Password:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.passwordTab), _translate("loginDialog", "Password"))
        self.label_2.setText(_translate("loginDialog", "Login:"))

from . import resources_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    loginDialog = QtWidgets.QDialog()
    ui = Ui_loginDialog()
    ui.setupUi(loginDialog)
    loginDialog.show()
    sys.exit(app.exec_())

