# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/tirons/src/akvo/akvo/gui/addPolygonalLoop.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_polygonalLoopAdd(object):
    def setupUi(self, polygonalLoopAdd):
        polygonalLoopAdd.setObjectName("polygonalLoopAdd")
        polygonalLoopAdd.resize(515, 446)
        self.gridLayout = QtWidgets.QGridLayout(polygonalLoopAdd)
        self.gridLayout.setObjectName("gridLayout")
        self.loopTableWidget = QtWidgets.QTableWidget(polygonalLoopAdd)
        self.loopTableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.loopTableWidget.setObjectName("loopTableWidget")
        self.loopTableWidget.setColumnCount(0)
        self.loopTableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.loopTableWidget, 3, 0, 1, 2)
        self.label = QtWidgets.QLabel(polygonalLoopAdd)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 5, 0, 1, 1)
        self.loopTurns = QtWidgets.QSpinBox(polygonalLoopAdd)
        self.loopTurns.setMinimum(1)
        self.loopTurns.setObjectName("loopTurns")
        self.gridLayout.addWidget(self.loopTurns, 5, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(polygonalLoopAdd)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 7, 1, 1, 1)

        self.retranslateUi(polygonalLoopAdd)
        self.buttonBox.accepted.connect(polygonalLoopAdd.accept)
        self.buttonBox.rejected.connect(polygonalLoopAdd.reject)
        QtCore.QMetaObject.connectSlotsByName(polygonalLoopAdd)

    def retranslateUi(self, polygonalLoopAdd):
        _translate = QtCore.QCoreApplication.translate
        polygonalLoopAdd.setWindowTitle(_translate("polygonalLoopAdd", "Dialog"))
        self.loopTableWidget.setToolTip(_translate("polygonalLoopAdd", "<html><head/><body><p>This table is used to enter coil geometries the format is as follows: each row specifies a single point on a coil. The first column is the coil index (using the GMR channel is useful), the next three colums specify the point in Northing, Easting, and Elevation. These can either be local coordinates or global ones. The final column specifies the loop radius if it is a circle or figure 8, for non circular or figure 8 loops leave this column blank. For figure-8 loops the coils do not need to be touching (see Irons and Kass, 2017). If a given index has 1 row it will be a circular loop, two rows will be a figure 8, and more than that will be a polygonal representation of the points, linearlly interpolated between them. </p></body></html>"))
        self.label.setText(_translate("polygonalLoopAdd", "Number of Turns"))
