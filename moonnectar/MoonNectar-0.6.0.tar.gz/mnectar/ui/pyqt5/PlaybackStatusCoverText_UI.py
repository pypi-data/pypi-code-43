# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mnectar/ui/pyqt5/PlaybackStatusCoverText.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlaybackStatusCoverText(object):
    def setupUi(self, PlaybackStatusCoverText):
        PlaybackStatusCoverText.setObjectName("PlaybackStatusCoverText")
        PlaybackStatusCoverText.resize(457, 124)
        self.gridLayout = QtWidgets.QGridLayout(PlaybackStatusCoverText)
        self.gridLayout.setObjectName("gridLayout")
        self.cover = QtWidgets.QLabel(PlaybackStatusCoverText)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cover.sizePolicy().hasHeightForWidth())
        self.cover.setSizePolicy(sizePolicy)
        self.cover.setMinimumSize(QtCore.QSize(100, 100))
        self.cover.setMaximumSize(QtCore.QSize(100, 100))
        self.cover.setText("")
        self.cover.setObjectName("cover")
        self.gridLayout.addWidget(self.cover, 0, 0, 2, 1)
        self.track_info = QtWidgets.QLabel(PlaybackStatusCoverText)
        self.track_info.setMinimumSize(QtCore.QSize(50, 0))
        self.track_info.setText("")
        self.track_info.setTextFormat(QtCore.Qt.RichText)
        self.track_info.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.track_info.setObjectName("track_info")
        self.gridLayout.addWidget(self.track_info, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.widget = QtWidgets.QWidget(PlaybackStatusCoverText)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.elapsed = QtWidgets.QLabel(self.widget)
        self.elapsed.setMinimumSize(QtCore.QSize(40, 0))
        self.elapsed.setText("")
        self.elapsed.setObjectName("elapsed")
        self.horizontalLayout.addWidget(self.elapsed)
        self.position = QtWidgets.QSlider(self.widget)
        self.position.setMaximum(10000)
        self.position.setPageStep(100)
        self.position.setOrientation(QtCore.Qt.Horizontal)
        self.position.setObjectName("position")
        self.horizontalLayout.addWidget(self.position)
        self.remaining = QtWidgets.QLabel(self.widget)
        self.remaining.setMinimumSize(QtCore.QSize(40, 0))
        self.remaining.setText("")
        self.remaining.setObjectName("remaining")
        self.horizontalLayout.addWidget(self.remaining)
        self.gridLayout.addWidget(self.widget, 1, 1, 1, 2)

        self.retranslateUi(PlaybackStatusCoverText)
        QtCore.QMetaObject.connectSlotsByName(PlaybackStatusCoverText)

    def retranslateUi(self, PlaybackStatusCoverText):
        _translate = QtCore.QCoreApplication.translate
        PlaybackStatusCoverText.setWindowTitle(_translate("PlaybackStatusCoverText", "Form"))
