# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './snitch/ui/about.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(320, 162)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text = QtWidgets.QLabel(AboutDialog)
        self.text.setTextFormat(QtCore.Qt.RichText)
        self.text.setObjectName("text")
        self.verticalLayout.addWidget(self.text)

        self.retranslateUi(AboutDialog)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About Snitch"))
        self.text.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:600;\">Snitch</span> v0.0.0</p><p align=\"center\">by <a href=\"mailto:gregory@millasseau.fr\"><span style=\" text-decoration: underline; color:#0000ff;\">Grégory Millasseau</span></a> (<a href=\"https://uk.codra.net/informatique/\"><span style=\" text-decoration: underline; color:#0000ff;\">Codra</span></a>) for <a href=\"http://www.irsn.fr\"><span style=\" text-decoration: underline; color:#0000ff;\">IRSN</span></a></p><p>Credits:</p><p>Icons by <a href=\"http://dryicons.com\"><span style=\" text-decoration: underline; color:#0000ff;\">DryIcons</span></a></p><p><br/></p></body></html>"))
