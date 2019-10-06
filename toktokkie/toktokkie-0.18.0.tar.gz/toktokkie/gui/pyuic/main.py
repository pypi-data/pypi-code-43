# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toktokkie/gui/qt_designer/main.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(972, 525)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.media_tree = QtWidgets.QTreeWidget(self.splitter)
        self.media_tree.setMinimumSize(QtCore.QSize(200, 0))
        self.media_tree.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.media_tree.setObjectName("media_tree")
        self.widget_stack = QtWidgets.QStackedWidget(self.splitter)
        self.widget_stack.setMinimumSize(QtCore.QSize(750, 0))
        self.widget_stack.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.widget_stack.setFrameShadow(QtWidgets.QFrame.Raised)
        self.widget_stack.setObjectName("widget_stack")
        self.stackedWidgetPage1 = QtWidgets.QWidget()
        self.stackedWidgetPage1.setObjectName("stackedWidgetPage1")
        self.widget_stack.addWidget(self.stackedWidgetPage1)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 972, 24))
        self.menuBar.setObjectName("menuBar")
        self.menuAdd_Directories = QtWidgets.QMenu(self.menuBar)
        self.menuAdd_Directories.setObjectName("menuAdd_Directories")
        MainWindow.setMenuBar(self.menuBar)
        self.add_directories_option = QtWidgets.QAction(MainWindow)
        self.add_directories_option.setObjectName("add_directories_option")
        self.remove_directories_option = QtWidgets.QAction(MainWindow)
        self.remove_directories_option.setObjectName("remove_directories_option")
        self.menuAdd_Directories.addAction(self.add_directories_option)
        self.menuAdd_Directories.addAction(self.remove_directories_option)
        self.menuBar.addAction(self.menuAdd_Directories.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "toktokkie"))
        self.media_tree.headerItem().setText(0, _translate("MainWindow", "Media"))
        self.menuAdd_Directories.setTitle(_translate("MainWindow", "File"))
        self.add_directories_option.setText(_translate("MainWindow", "Add directories"))
        self.remove_directories_option.setText(_translate("MainWindow", "Remove directories"))
