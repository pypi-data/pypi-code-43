# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mnectar/ui/pyqt5/PlaybackStatusText.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlaybackStatusText(object):
    def setupUi(self, PlaybackStatusText):
        PlaybackStatusText.setObjectName("PlaybackStatusText")
        PlaybackStatusText.resize(550, 65)
        self.horizontalLayout = QtWidgets.QHBoxLayout(PlaybackStatusText)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.track_info = QtWidgets.QLabel(PlaybackStatusText)
        self.track_info.setMinimumSize(QtCore.QSize(100, 0))
        self.track_info.setText("")
        self.track_info.setTextFormat(QtCore.Qt.RichText)
        self.track_info.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.track_info.setObjectName("track_info")
        self.horizontalLayout.addWidget(self.track_info)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.retranslateUi(PlaybackStatusText)
        QtCore.QMetaObject.connectSlotsByName(PlaybackStatusText)

    def retranslateUi(self, PlaybackStatusText):
        _translate = QtCore.QCoreApplication.translate
        PlaybackStatusText.setWindowTitle(_translate("PlaybackStatusText", "Form"))
