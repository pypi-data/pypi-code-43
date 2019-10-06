# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mnectar/ui/pyqt5/PlaylistDetail.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlaylistDetail(object):
    def setupUi(self, PlaylistDetail):
        PlaylistDetail.setObjectName("PlaylistDetail")
        PlaylistDetail.resize(726, 474)
        self.verticalLayout = QtWidgets.QVBoxLayout(PlaylistDetail)
        self.verticalLayout.setObjectName("verticalLayout")
        self.search = QtWidgets.QLineEdit(PlaylistDetail)
        self.search.setDragEnabled(False)
        self.search.setClearButtonEnabled(True)
        self.search.setObjectName("search")
        self.verticalLayout.addWidget(self.search)
        self.playlist_view = QPlaylistView(PlaylistDetail)
        self.playlist_view.setSortingEnabled(True)
        self.playlist_view.setWordWrap(False)
        self.playlist_view.setObjectName("playlist_view")
        self.playlist_view.verticalHeader().setSortIndicatorShown(True)
        self.verticalLayout.addWidget(self.playlist_view)

        self.retranslateUi(PlaylistDetail)
        QtCore.QMetaObject.connectSlotsByName(PlaylistDetail)

    def retranslateUi(self, PlaylistDetail):
        _translate = QtCore.QCoreApplication.translate
        PlaylistDetail.setWindowTitle(_translate("PlaylistDetail", "Form"))
from .QPlaylistView import QPlaylistView
