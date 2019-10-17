from os import path
from PyQt5 import QtWidgets, uic, QtCore, QtWebEngineWidgets
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure


def prettyDict(dict):
    "prepare dict for pretty printing"
    s = str(dict)
    for i in ["'", "{", "}"]:
        s = s.replace(i, "")
    s = s.replace(", ", "\n")
    return s


class AlertWindow(QtWidgets.QDialog):
    def __init__(self, basedir, message):
        super(AlertWindow, self).__init__()
        uic.loadUi(path.join(basedir, "ui", "alert.ui"), self)
        self.textBrowser.setText(message)


class CalibrateWindow(QtWidgets.QDialog):
    settingsChaned = QtCore.pyqtSignal("PyQt_PyObject", "PyQt_PyObject")

    def __init__(self, basedir, motor, motor_defaults):
        super(CalibrateWindow, self).__init__()
        self.motor = motor
        self.basedir = basedir
        uic.loadUi(path.join(basedir, "ui", "calibrate.ui"), self)
        self.motorMoveVal.setValue(motor_defaults["calibration"]["step"])
        self.motorMeasureVal.setValue(motor_defaults["calibration"]["length"])
        self.motor.bpCalibrateVal(self.motorMoveVal.value())
        self.actionMotorStep.clicked.connect(self.step)
        self.actionGotoOrigin.clicked.connect(self.origin)
        self.actionStop.clicked.connect(self.stop)
        self.actionOk.accepted.connect(
            lambda: (
                self.motor.bpCalibrateSet(self.motorMeasureVal.value()),
                self.settingsChaned.emit(
                    self.motorMoveVal.value(), self.motorMeasureVal.value()
                ),
            )
        )

    def origin(self):
        if not self.motor.bpCalibrateOrigin():
            dialog = AlertWindow(self.basedir, "Cannot return to origin")
            dialog.exec_()

    def step(self):
        if self.motor.bpPreMoveHook():
            if (
                not self.motor.bpCalibrateVal(self.motorMoveVal.value())
                or not self.motor.bpCalibrateStep()
            ):
                dialog = AlertWindow(
                    self.basedir, "Error during calibration step"
                )
                dialog.exec_()
            self.motor.bpPostMoveHook()

    def stop(self):
        if not self.motor.bpStop():
            dialog = AlertWindow(self.basedir, "Cannot stop motor")
            dialog.exec_()


class MplCanvas(FigureCanvas):
    def __init__(
        self, parent=None, width=5, height=4, dpi=100, projection=None
    ):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection=projection)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self,
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        FigureCanvas.updateGeometry(self)


class CloneThread(QtCore.QThread):
    measureStep = QtCore.pyqtSignal(
        "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject"
    )
    measureF0 = QtCore.pyqtSignal("PyQt_PyObject")
    measureActual = QtCore.pyqtSignal(
        "PyQt_PyObject", "PyQt_PyObject", "PyQt_PyObject"
    )
    measureEnd = QtCore.pyqtSignal("PyQt_PyObject")
    measureAbort = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, motor, analyzer, steps, logger, metadata):
        QtCore.QThread.__init__(self)
        self.motor = motor
        self.va = analyzer
        self.steps = steps
        self._uilog = logger
        self._uilog.debug("Thread spawned")
        self.mtype = metadata["measure type"]
        self.mpart = metadata["field part"]
        self.mstrategy = metadata["strategy"]
        self.stop = False

    def run(self):
        if self.mtype == "reflection" and self.mstrategy == "direct":
            if self.mpart == "electric" or self.mpart == "magnetic":
                preHook = self.va.bpPreFieldReflectionDFMeasureHook
                postHook = self.va.bpPostFieldReflectionDFMeasureHook
                measure = self.va.bpMeasureFieldReflectionDF
            else:
                self.measureAbort.emit(
                    """Reflection direct measure supports only electric or \
magnetic field parts"""
                )
                return
        elif self.mtype == "reflection" and self.mstrategy != "direct":
            if self.mpart == "electric":
                preHook = self.va.bpPreFieldReflectionDSEMeasureHook
                postHook = self.va.bpPostFieldReflectionDSEMeasureHook
                measure = self.va.bpMeasureFieldReflectionDSE
            elif self.mpart == "electric phase":
                preHook = self.va.bpPreFieldReflectionDSPhiMeasureHook
                postHook = self.va.bpPostFieldReflectionDSPhiMeasureHook
                measure = self.va.bpMeasureFieldReflectionDSPhi
            else:
                self.measureAbort.emit(
                    """Reflection indirect measure supports only electric \
or electric phase field parts"""
                )
                return
        elif self.mtype == "transmission" and self.mstrategy == "direct":
            if self.mpart == "electric" or self.mpart == "magnetic":
                preHook = self.va.bpPreFieldTransmissionDFMeasureHook
                postHook = self.va.bpPostFieldTransmissionDFMeasureHook
                measure = self.va.bpMeasureFieldTransmissionDF
            else:
                self.measureAbort.emit(
                    """Transmission direct measure supports only electric \
or magnetic field parts"""
                )
                return
        elif self.mtype == "transmission" and self.mstrategy != "direct":
            if self.mpart == "electric" or self.mpart == "magnetic":
                preHook = self.va.bpPreFieldTransmissionDPhiMeasureHook
                postHook = self.va.bpPostFieldTransmissionDPhiMeasureHook
                measure = self.va.bpMeasureFieldTransmissionDPhi
            else:
                self.measureAbort.emit(
                    """Transmission indirect measure supports only electric \
or magnetic field parts"""
                )
                return
        if not self.motor.bpReturn():
            self.measureAbort.emit("""Cannot return motor""")
            return
        while self.motor.bpIsMoving():
            self.motor.bpWait(100)
            if self.stop:
                self._uilog.debug("Stopping measure")
                break
        if self.motor.bpPreMoveHook() and self.va.bpPreMeasureHook():
            if not preHook():
                self.measureAbort.emit("""Measure hook failed""")
                return
            f0 = self.va.bpGetFrequencyCenter()
            if f0 is None:
                self.measureAbort.emit("Cannot get data from analyzer")
                return
            else:
                self.measureF0.emit(f0)
            self._uilog.debug("Field measure start")
            step_counter = 0
            for x in self.steps:
                self._uilog.debug(
                    f"""Field measure \
step {step_counter} at position {x}"""
                )
                if self.stop:
                    self._uilog.debug("Stopping measure")
                    break
                if not self.motor.bpGotoPosition(x):
                    self.measureAbort.emit("Cannot move motor")
                    return
                while self.motor.bpIsMoving():
                    self.motor.bpWait(100)
                    if self.stop:
                        self._uilog.debug("Stopping measure")
                        break
                data = measure()
                if data is None:
                    self.measureAbort.emit("Cannot get data from analyzer")
                    return
                self.measureStep.emit(data, x, step_counter)
                step_counter += 1
            postHook()
            self.va.bpPostMeasureHook()
            self.motor.bpPostMoveHook()
        else:
            self.measureAbort.emit("Premeasure hook failed")
            return
        self._uilog.debug("Field measure end")
        self.measureEnd.emit(self.stop)


class WebViewWidget(QtWidgets.QWidget):
    """A QWebEngineView is required to display a QWebEnginePage."""

    def __init__(self, parent=None, html_file=None):
        super().__init__(parent)
        self.view = QtWebEngineWidgets.QWebEngineView()
        self.page = QtWebEngineWidgets.QWebEnginePage()

        self.url = QtCore.QUrl.fromLocalFile(html_file)
        self.page.load(self.url)

        self.view.setPage(self.page)

        # set layout
        self.vl = QtWidgets.QVBoxLayout()
        self.vl.addWidget(self.view)
        self.setLayout(self.vl)
