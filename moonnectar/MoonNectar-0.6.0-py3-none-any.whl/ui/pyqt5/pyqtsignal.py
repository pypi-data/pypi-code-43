from PyQt5           import QtCore

class QSignalControl(QtCore.QObject):
    """Convert python signals to pyqt5 UI synchronous signals"""

    # PyQt only signals
    selected    = QtCore.pyqtSignal(list) # Current selection in the main library window (ARGS: List of MRLs)


    def __init__(self, app=None, *arg, **kw):
        super().__init__(*arg, **kw)
        self.app = app

