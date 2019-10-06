# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mnectar/ui/pyqt5/PlaybackControl.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlaybackControl(object):
    def setupUi(self, PlaybackControl):
        PlaybackControl.setObjectName("PlaybackControl")
        PlaybackControl.resize(183, 51)
        self.horizontalLayout = QtWidgets.QHBoxLayout(PlaybackControl)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Prev = QtWidgets.QPushButton(PlaybackControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Prev.sizePolicy().hasHeightForWidth())
        self.Prev.setSizePolicy(sizePolicy)
        self.Prev.setMinimumSize(QtCore.QSize(50, 50))
        self.Prev.setMaximumSize(QtCore.QSize(50, 50))
        self.Prev.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/PlaybackControl/icons/Media-skip-backward.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Prev.setIcon(icon)
        self.Prev.setIconSize(QtCore.QSize(30, 30))
        self.Prev.setObjectName("Prev")
        self.horizontalLayout.addWidget(self.Prev)
        self.PlayPause = QtWidgets.QPushButton(PlaybackControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PlayPause.sizePolicy().hasHeightForWidth())
        self.PlayPause.setSizePolicy(sizePolicy)
        self.PlayPause.setMinimumSize(QtCore.QSize(50, 50))
        self.PlayPause.setMaximumSize(QtCore.QSize(50, 50))
        self.PlayPause.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/PlaybackControl/icons/Media-playback-start.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/PlaybackControl/icons/Media-playback-pause.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.PlayPause.setIcon(icon1)
        self.PlayPause.setIconSize(QtCore.QSize(30, 30))
        self.PlayPause.setCheckable(True)
        self.PlayPause.setDefault(False)
        self.PlayPause.setObjectName("PlayPause")
        self.horizontalLayout.addWidget(self.PlayPause)
        self.Stop = QtWidgets.QPushButton(PlaybackControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Stop.sizePolicy().hasHeightForWidth())
        self.Stop.setSizePolicy(sizePolicy)
        self.Stop.setMinimumSize(QtCore.QSize(50, 50))
        self.Stop.setMaximumSize(QtCore.QSize(50, 50))
        self.Stop.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/PlaybackControl/icons/Media-playback-stop.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Stop.setIcon(icon2)
        self.Stop.setIconSize(QtCore.QSize(30, 30))
        self.Stop.setObjectName("Stop")
        self.horizontalLayout.addWidget(self.Stop)
        self.Next = QtWidgets.QPushButton(PlaybackControl)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Next.sizePolicy().hasHeightForWidth())
        self.Next.setSizePolicy(sizePolicy)
        self.Next.setMinimumSize(QtCore.QSize(50, 50))
        self.Next.setMaximumSize(QtCore.QSize(50, 50))
        self.Next.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/PlaybackControl/icons/Media-skip-forward.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Next.setIcon(icon3)
        self.Next.setIconSize(QtCore.QSize(30, 30))
        self.Next.setObjectName("Next")
        self.horizontalLayout.addWidget(self.Next)

        self.retranslateUi(PlaybackControl)
        QtCore.QMetaObject.connectSlotsByName(PlaybackControl)

    def retranslateUi(self, PlaybackControl):
        pass
from . import PlaybackControl_rc
