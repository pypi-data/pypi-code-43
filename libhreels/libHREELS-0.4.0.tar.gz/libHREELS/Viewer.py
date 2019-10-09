#!/usr/bin/env python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import libHREELS as h

app = QtWidgets.QApplication(sys.argv)
form = h.HREELS_Window()
form.show()
sys.exit(app.exec_())