import PyQt5.QtCore

PyQt5.QtCore.QCoreApplication.setAttribute(PyQt5.QtCore.Qt.AA_ShareOpenGLContexts)

from .gui import *
from .displayOptimization import *
from .fastPlot import *
