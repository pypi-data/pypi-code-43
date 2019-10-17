from os import path, environ
import logging
import numpy as np
from datetime import datetime
import platform

from PyQt5 import QtWidgets, uic, QtGui
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar,
)

from smithplot import SmithAxes
from beadpull.motor.motor import select_motor
from beadpull.analyzer.analyzer import select_analyzer
from .support import (
    prettyDict,
    AlertWindow,
    CalibrateWindow,
    MplCanvas,
    CloneThread,
    WebViewWidget,
)
from beadpull.equation.equation import (
    fieldRemoveDrift,
    processFieldData,
    convertFreq,
)
from .loadsettings import (
    load_defaults_motor,
    save_defaults_motor,
    load_defaults_analyzer,
    save_defaults_analyzer,
    load_defaults_ui,
    save_defaults_ui,
    load_defaults_equation,
    save_defaults_equation,
)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, basedir):
        super(MainWindow, self).__init__()
        # load ui
        uic.loadUi(path.join(basedir, "ui", "window.ui"), self)
        self.setWindowIcon(QtGui.QIcon(path.join(basedir, "icon", "icon.ico")))
        # load default values
        self.motor_defaults = load_defaults_motor(basedir)
        self.va_defaults = load_defaults_analyzer(basedir)
        self.proj_defaults = load_defaults_ui(basedir)
        self.eq_defaults = load_defaults_equation(basedir)
        # setup logger
        self._uilog = logging.getLogger("QtPy")
        self.basedir = basedir  # package directory
        self.lastdir = (
            environ.get("HOMEPATH")
            if platform.system() == "Windows"
            else environ.get("HOME")
        )  # last accessed directory
        mpl.rcParams[
            "savefig.directory"
        ] = self.lastdir  # default plot directory
        # setup motor and analyzer drivers
        self.motor = select_motor(self.motor_defaults["driver"]["selected"])()
        self.va = select_analyzer(self.va_defaults["driver"]["selected"])()
        # data arrays
        self.scatter_data = np.empty((0, 0))
        self.scatter_data_raw = np.empty((0, 0))
        self.field_coord = np.empty(0)
        self.field_data = np.empty(0, dtype="complex")
        self.scatter_metadata = None
        self.field_metadata = None
        self.thread = None
        self.actionQuit.triggered.connect(self.close)

        self.setRibbon()
        self.setMotorPage()
        self.setAnalyzerPage()
        self.setScatteringPage()
        self.setPostprocessingPage()
        self.setFieldPage()

        self._uilog.info("UI initialized")
        self.show()

    def closeEvent(self, *args):
        """common close event"""
        self._uilog.info("Saving changes")
        self.readMotorPage()
        self.readAnalyzerPage()
        self.readScatteringPage()
        self.readPostprocessingPage()
        self.readFieldPage()
        save_defaults_motor(self.motor_defaults)
        save_defaults_analyzer(self.va_defaults)
        save_defaults_ui(self.proj_defaults)
        save_defaults_equation(self.eq_defaults)

        self._uilog.info("Closing program")
        self.motorDisconnect()
        self.vaDisconnect()

    def uiDisableTabsWrap(function):
        """disable tabs for duration of a function"""

        def wrapper(self, *args, **kwargs):
            self.Tabs.setEnabled(False)
            self.Tabs.repaint()
            function(self, *args, **kwargs)
            self.Tabs.setEnabled(True)
            self.Tabs.repaint()

        return wrapper

    def motorCheckConnectedWrap(function):
        """check if motor is connected"""

        def wrapper(self, *args, **kwargs):
            if self.motor.bpIsConnected():
                function(self, *args, **kwargs)
            else:
                dialog = AlertWindow(self.basedir, "Not connected to motor")
                dialog.exec_()

        return wrapper

    def motorMoveHooks(function):
        """apply move hooks"""

        def wrapper(self, *args, **kwargs):
            if self.motor.bpPreMoveHook():
                function(self, *args, **kwargs)
                self.motor.bpPostMoveHook()

        return wrapper

    def motorReturnHooks(function):
        """apply return hooks"""

        def wrapper(self, *args, **kwargs):
            if self.motor.bpPreReturnHook():
                function(self, *args, **kwargs)
                self.motor.bpPostReturnHook()
            else:
                dialog = AlertWindow(self.basedir, "Motor hook failed")
                dialog.exec_()

        return wrapper

    @uiDisableTabsWrap
    def motorDriverChanged(self, driver):
        """select new driver and restart"""
        self.motor_defaults["driver"]["selected"] = driver
        dialog = AlertWindow(
            self.basedir,
            "In order to apply changes, application must be restarted",
        )
        dialog.exec_()

    @uiDisableTabsWrap
    def analyzerDriverChanged(self, driver):
        """select new driver and restart"""
        self.va_defaults["driver"]["selected"] = driver
        dialog = AlertWindow(
            self.basedir,
            "In order to apply changes, application must be restarted",
        )
        dialog.exec_()

    @uiDisableTabsWrap
    @motorCheckConnectedWrap
    def motorSet(self, *args):
        if (
            not self.motor.bpMoveSpeed(self.motorMoveSpeed.value())
            or not self.motor.bpReturnSpeed(self.motorReturnSpeed.value())
            or not self.motor.bpAcceleration(self.motorAcceleration.value())
            or not self.motor.bpDeceleration(self.motorDeceleration.value())
            or not self.motor.bpCalibratePreset(
                self.motorConversionRatio.value()
            )
        ):
            dialog = AlertWindow(
                self.basedir, "Could not apply motor settings"
            )
            dialog.exec_()

    @uiDisableTabsWrap
    @motorCheckConnectedWrap
    def openCalibrationWindow(self, *args):
        calibrate = CalibrateWindow(
            self.basedir, self.motor, self.motor_defaults
        )
        calibrate.settingsChaned.connect(self.readCalibrateWindowSettings)
        calibrate.exec_()
        if calibrate.result():
            self.motorConversionRatio.setValue(
                calibrate.motorMoveVal.value()
                / calibrate.motorMeasureVal.value()
            )
            self.motorSet()

    @uiDisableTabsWrap
    @motorCheckConnectedWrap
    def motorShowStatus(self, *args):
        """show motor status"""
        dialog = AlertWindow(self.basedir, prettyDict(self.motor.bpStatus()))
        dialog.exec_()

    @motorCheckConnectedWrap
    @motorReturnHooks
    def motorReturn(self, *args):
        """return motor"""
        if not self.motor.bpReturn():
            dialog = AlertWindow(self.basedir, "Motor refuses to return")
            dialog.exec_()

    @uiDisableTabsWrap
    def motorConnect(self, *args):
        """motor connect"""
        if not self.motor.bpIsConnected():
            if self.motor.bpConnect(
                self.motorPort.currentText(), int(self.motorBaud.currentText())
            ):
                if self.motor.bpInit():
                    self.motorSet()
                else:
                    dialog = AlertWindow(
                        self.basedir, "Error during initialization"
                    )
                    dialog.exec_()
            else:
                dialog = AlertWindow(self.basedir, "Cannot connect to motor")
                dialog.exec_()
        else:
            dialog = AlertWindow(self.basedir, "Motor already connected")
            dialog.exec_()

    @uiDisableTabsWrap
    def motorDisconnect(self, *args):
        """motor disconnect"""
        if self.motor.bpIsConnected():
            if (
                not self.motor.bpStop()
                or not self.motor.bpRelease()
                or not self.motor.bpDeinit()
            ):
                dialog = AlertWindow(self.basedir, "Error during disconnect")
                dialog.exec_()
        self.motor.bpDisconnect()  # this must always execute

    @uiDisableTabsWrap
    @motorCheckConnectedWrap
    def motorHold(self, *args):
        """motor hold"""
        if not self.motor.bpStop() or not self.motor.bpHold():
            dialog = AlertWindow(self.basedir, "Cannot enable motor")
            dialog.exec_()

    @uiDisableTabsWrap
    @motorCheckConnectedWrap
    def motorRelease(self, *args):
        """motor release"""
        if not self.motor.bpRelease():
            dialog = AlertWindow(self.basedir, "Cannot release motor")
            dialog.exec_()

    @motorCheckConnectedWrap
    def motorStop(self, *args):
        """motor stop"""
        if not self.motor.bpStop():
            dialog = AlertWindow(self.basedir, "Cannot stop motor")
            dialog.exec_()

    @uiDisableTabsWrap
    @motorCheckConnectedWrap
    def motorSetOrigin(self, *args):
        """motor set origin"""
        if not self.motor.bpOrigin():
            dialog = AlertWindow(self.basedir, "Cannot set motor origin")
            dialog.exec_()

    @motorCheckConnectedWrap
    def motorChangeDirection(self, direction, *args):
        """motor set direction"""
        if not self.motor.bpDirection(bool(direction)):
            dialog = AlertWindow(self.basedir, "Cannot change motor direction")
            dialog.exec_()
            self.motorDirection.setChecked(not self.motorDirection.isChecked())

    @motorCheckConnectedWrap
    @motorMoveHooks
    def motorStep(self, *args):
        """motor step"""
        if not self.motor.bpStep(self.motorStepVal.value()):
            dialog = AlertWindow(self.basedir, "Cannot make step")
            dialog.exec_()

    @motorCheckConnectedWrap
    @motorMoveHooks
    def motorGoto(self, *args):
        """motor return"""
        if not self.motor.bpGotoPosition(self.motorGotoPositionVal.value()):
            dialog = AlertWindow(self.basedir, "Cannot go to position")
            dialog.exec_()

    def vaCheckConnectedWrap(function):
        """check if analyzer is connected"""

        def wrapper(self, *args, **kwargs):
            if self.va.bpIsConnected():
                function(self, *args, **kwargs)
            else:
                dialog = AlertWindow(self.basedir, "Not connected to analyzer")
                dialog.exec_()

        return wrapper

    @uiDisableTabsWrap
    def vaConnect(self, *args):
        """analyzer connect"""
        if not self.va.bpIsConnected():
            if self.va.bpConnect(self.vaName.currentText()):
                if not self.va.bpInit():
                    dialog = AlertWindow(
                        self.basedir, "Error during initialization"
                    )
                    dialog.exec_()
            else:
                dialog = AlertWindow(
                    self.basedir, "Cannot connect to analyzer"
                )
                dialog.exec_()
        else:
            dialog = AlertWindow(self.basedir, "Already connected to analyzer")
            dialog.exec_()

    @uiDisableTabsWrap
    def vaDisconnect(self, *args):
        """analyzer disconnect"""
        if self.va.bpIsConnected():
            if not self.va.bpDeinit():
                dialog = AlertWindow(self.basedir, "Error during deinitialize")
                dialog.exec_()
        self.va.bpDisconnect()  # this must always execute

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    def vaStatus(self, *args):
        """analyzer status"""
        dialog = AlertWindow(self.basedir, prettyDict(self.va.bpStatus()))
        dialog.exec_()

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    def vaRelease(self, *args):
        """analyzer release"""
        if not self.va.bpReleaseControl():
            dialog = AlertWindow(self.basedir, "Cannot release control")
            dialog.exec_()

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    def vaReset(self, *args):
        """analyzer reset"""
        if not self.va.bpReset():
            dialog = AlertWindow(self.basedir, "Cannot reset")
            dialog.exec_()

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    def vaRestart(self, *args):
        """analyzer restart"""
        if not self.va.bpRestart():
            dialog = AlertWindow(self.basedir, "Cannot restart")
            dialog.exec_()

    def vaMeasureHooksWrap(function):
        """apply analyzer measure hooks"""

        def wrapper(self, *args, **kwargs):
            if self.va.bpPreMeasureHook():
                function(self, *args, **kwargs)
                self.va.bpPostMeasureHook()
            else:
                dialog = AlertWindow(self.basedir, "Analyzer hook failed")
                dialog.exec_()

        return wrapper

    def vaApplySettingsWrap(function):
        """set general settings"""

        def wrapper(self, *args, **kwargs):
            if not self.va.bpApplyGeneralSettings(
                power=self.vaPower.isChecked(),
                power_val=self.vaPowerVal.value(),
                averaging=self.vaAveraging.isChecked(),
                averaging_val=self.vaAveragingVal.value(),
                smoothing=self.vaSmoothing.isChecked(),
                smoothing_val=self.vaSmoothingVal.value(),
                integ_band=int(self.vaIntBand.currentText()),
                sweep=self.vaSweepType.currentText(),
                nop=int(self.vaNOP.currentText()),
                unit=self.vaFreqUnit.currentText(),
                phase_offset=self.vaPhaseOffset.value(),
                display=self.vaDisplayEnable.isChecked(),
            ):
                dialog = AlertWindow(
                    self.basedir, "Cannot apply analyzer settings"
                )
                dialog.exec_()
            function(self, *args, **kwargs)

        return wrapper

    def scatApplySettingsWrap(function):
        """apply analyzer settings from scattering measure menu"""

        def wrapper(self, *args, **kwargs):
            if not self.va.bpApplyScatterMeasureSettings(
                measure_type=self.scatMeasureType.currentText(),
                measure_part=self.scatMeasurePart.currentText(),
                freq_center=int(self.scatFreqCenter.value()),
                freq_span=int(self.scatFreqSpan.value()),
            ):
                dialog = AlertWindow(
                    self.basedir, "Cannot apply scattering settings"
                )
                dialog.exec_()
            function(self, *args, **kwargs)

        return wrapper

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    @vaApplySettingsWrap
    def vaSettingsApply(self, *args):
        """apply analyzer settings from settings menu"""
        pass

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    def vaSetFreq(self, *args):
        """read frequency from analyzer and set in UI"""
        center = self.va.bpGetFrequencyCenter()
        span = self.va.bpGetFrequencySpan()
        if center is None or span is None:
            dialog = AlertWindow(self.basedir, "Cannot get frequency")
            dialog.exec_()
            return
        self.scatFreqCenter.setValue(
            int(round(convertFreq(center, self.vaFreqUnit.currentText()), 0))
        )
        self.scatFreqSpan.setValue(
            int(round(convertFreq(span, self.vaFreqUnit.currentText()), 0))
        )

    def vaFreqChanged(self, unit):
        """frequency unit changed"""
        center = self.scatFreqCenter.value()
        span = self.scatFreqSpan.value()
        old_unit = self.scatFreqCenter.suffix().upper().strip()
        if old_unit == "[KHZ]":
            center = center * 1e3
            span = span * 1e3
        elif old_unit == "[MHZ]":
            center = center * 1e6
            span = span * 1e6
        elif old_unit == "[GHZ]":
            center = center * 1e9
            span = span * 1e9
        self.scatFreqCenter.setSuffix(f" [{unit}]")
        self.scatFreqSpan.setSuffix(f" [{unit}]")
        self.scatFreqCenter.setValue(
            int(round(convertFreq(center, self.vaFreqUnit.currentText()), 0))
        )
        self.scatFreqSpan.setValue(
            int(round(convertFreq(span, self.vaFreqUnit.currentText()), 0))
        )

    @uiDisableTabsWrap
    @vaCheckConnectedWrap
    @vaApplySettingsWrap
    @scatApplySettingsWrap
    @vaMeasureHooksWrap
    def vaScatMeasure(self, *args):
        """measure scattering"""
        self._uilog.debug("Measuring scattering")
        freq = self.va.bpGetFrequencyPoints()
        data = self.va.bpMeasureScattering()
        data_raw = self.va.bpMeasureScatteringRaw()
        if freq is None or data is None or data_raw is None:
            self.va.bpNotifyUser()
            dialog = AlertWindow(self.basedir, "Cannot get data from analyzer")
            dialog.exec_()
            return
        self._uilog.debug("Obtained data from analyzer")
        self.scatCanvasDec.axes.clear()
        self.scatCanvasPol.axes.clear()
        self.scatCanvasSmt.axes.clear()
        self._uilog.debug("Cleared plots")
        self._uilog.debug("Processing markers")
        fmin = None
        fmax = None
        fQcent = None
        fQband = None
        if self.scatMarkerMin.isChecked():
            rv = self.va.bpMarkerMin()
            if rv is not None:
                fmin = convertFreq(rv["f"], self.vaFreqUnit.currentText())
                self.labelScatMarkerMin.setText(
                    f"""Minimum:\t{fmin}\
{self.vaFreqUnit.currentText()};\t{rv['val1']};\t{rv['val2']}"""
                )
                self._uilog.debug("Read marker minimum")
        if self.scatMarkerMax.isChecked():
            rv = self.va.bpMarkerMax()
            if rv is not None:
                fmax = convertFreq(rv["f"], self.vaFreqUnit.currentText())
                self.labelScatMarkerMax.setText(
                    f"""Maximum:\t{fmax}\
{self.vaFreqUnit.currentText()};\t{rv['val1']};\t{rv['val2']}"""
                )
                self._uilog.debug("Read marker maximum")
        if self.scatMarkerQ.isChecked():
            rv = self.va.bpMarkerQ(
                self.scatMarkerQVal.value(), self.scatMeasureType.currentText()
            )
            if rv is not None:
                fQcent = convertFreq(
                    rv["center"], self.vaFreqUnit.currentText()
                )
                fQband = convertFreq(
                    rv["bandwidth"], self.vaFreqUnit.currentText()
                )
                lQ = rv["level"]
                self.labelScatMarkerQ.setText(
                    f"""Q: {rv['Q']};\tLoss: {rv['loss']} dB;\tCenter: {fQcent}\
{self.vaFreqUnit.currentText()};\tBandwidth: {fQband}\
{self.vaFreqUnit.currentText()}\tLevel 1: {lQ};\tLevel 2:\
{lQ + self.scatMarkerQVal.value()}"""
                )
                self._uilog.debug("Read marker Q")

        self._uilog.debug("Plotting scattering")
        self.scatter_data = np.concatenate(
            (freq.reshape(data.shape[0], 1), data, data_raw), axis=1
        )
        freq = convertFreq(freq, self.vaFreqUnit.currentText())
        unit1, unit2 = self.va_defaults["measurePart"]["options"][
            self.scatMeasurePart.currentText()
        ]
        self.scatter_metadata = {
            "project info": self.projInfo.text(),
            "timestamp": str(datetime.now()),
            "data format": """frequency; data 1; data 2; \
raw data 1; raw data 2""",
            "unit column 1": "Hz",
            "unit column 2": unit1 if unit1 is not None else "NA",
            "unit column 3": unit2 if unit2 is not None else "NA",
            "unit column 4": "real",
            "unit column 5": "imag",
        }
        self.scatter_metadata.update(self.vaReadSettings())
        self._uilog.debug("Prepared scatter metadata")
        if unit2 is None:
            data = data[:, 0]
            canvas = self.scatCanvasDec
            self.scatterPlotFrameDec.setVisible(True)
            self.scatterPlotFramePol.setVisible(False)
            self.scatterPlotFrameSmt.setVisible(False)
            canvas.axes.set_ylabel(unit1)
            if self.vaSweepType == "Logarithmic":
                canvas.axes.plot.set_xscale("log")
            canvas.axes.plot(freq, data, color=self.proj_defaults["dataColor"])
            if fmin is not None:
                canvas.axes.axvline(
                    fmin, color=self.proj_defaults["minMarkerColor"]
                )
            if fmax is not None:
                canvas.axes.axvline(
                    fmax, color=self.proj_defaults["maxMarkerColor"]
                )
            if (
                fQcent is not None
                and fQcent != 0
                and fQband is not None
                and fQband != 0
            ):
                canvas.axes.axvline(
                    fQcent, color=self.proj_defaults["QMarkerColor"]
                )
                canvas.axes.axvline(
                    fQcent - fQband / 2,
                    color=self.proj_defaults["QMarkerColor"],
                )
                canvas.axes.axvline(
                    fQcent + fQband / 2,
                    color=self.proj_defaults["QMarkerColor"],
                )
                canvas.axes.axhline(
                    lQ, color=self.proj_defaults["QMarkerColor"]
                )
                canvas.axes.axhline(
                    lQ + self.scatMarkerQVal.value(),
                    color=self.proj_defaults["QMarkerColor"],
                )
        else:
            self.scatterPlotFrameDec.setVisible(False)
            if self.scatMeasurePart.currentText() == "Smith":
                canvas = self.scatCanvasSmt
                self.scatterPlotFramePol.setVisible(False)
                self.scatterPlotFrameSmt.setVisible(True)
                canvas.axes.plot(
                    data[:, 0],
                    data[:, 1],
                    color=self.proj_defaults["dataColor"],
                )
            else:
                canvas = self.scatCanvasPol
                self.scatterPlotFramePol.setVisible(True)
                self.scatterPlotFrameSmt.setVisible(False)
                canvas.axes.plot(
                    np.arctan2(data[:, 1], data[:, 0]),
                    np.sqrt(data[:, 0] ** 2 + data[:, 1] ** 2),
                    color=self.proj_defaults["dataColor"],
                )
        self._uilog.debug("Plot data set")
        canvas.axes.set_title(self.scatMeasureType.currentText())
        canvas.axes.set_xlabel(f"Frequency, {self.vaFreqUnit.currentText()}")
        canvas.axes.grid()
        canvas.fig.tight_layout()
        canvas.draw()
        self._uilog.debug("Plot redrawn")
        self._uilog.debug("Scatter measure done")
        self.va.bpNotifyUser()

    @motorCheckConnectedWrap
    @vaCheckConnectedWrap
    @vaApplySettingsWrap
    @scatApplySettingsWrap
    def fieldMeasure(self, *args):
        """measure field"""
        if not self.motor.bpHold():
            dialog = AlertWindow(self.basedir, "Cannot enable motor")
            dialog.exec_()
        if self.thread is None:
            step = self.projStep.value()
            nos = int(self.projTotalLength.value() // step + 1)
            steps = np.linspace(0, self.projTotalLength.value(), nos)
            self.field_metadata = {
                "project info": self.projInfo.text(),
                "timestamp": str(datetime.now()),
                "data format": """frequency; data; raw data""",
                "unit column 1": "mm",
                "unit column 2": "NA",
                "total length": self.projTotalLength.value(),
                "field part": self.eqFieldPart.currentText().lower(),
                "strategy": self.fieldStrategy.currentText().lower(),
                "bead material": self.eqBeadMaterial.currentText().lower(),
                "electric formfactor": self.eqKEMantissa.value()
                * 10 ** self.eqKEExponent.value(),
                "magnetic formfactor": self.eqKHMantissa.value()
                * 10 ** self.eqKHExponent.value(),
                "formfactor for inderect reflection \
measurements": self.eqKSMantissa.value()
                * 10 ** self.eqKSExponent.value(),
                "Qload": self.eqQLoad.value(),
            }
            self.field_metadata.update(self.vaReadSettings())
            self.fieldProgressBar.setMaximum(len(steps))
            self.field_data = np.empty(0, dtype="complex")
            self.field_coord = np.empty(0)
            self.thread = CloneThread(
                self.motor, self.va, steps, self._uilog, self.field_metadata
            )
            self.thread.measureStep.connect(self.fieldNewPoint)
            self.thread.measureF0.connect(
                lambda x: self.field_metadata.update({"central frequency": x})
            )
            self.thread.measureEnd.connect(self.fieldMeasureEnd)
            self.thread.measureAbort.connect(self.fieldMeasureAbort)
            self.thread.start()
        else:
            dialog = AlertWindow(self.basedir, "Measure already in progress")
            dialog.exec_()

    @uiDisableTabsWrap
    def fieldStop(self, *args):
        """interrupt measure"""
        if self.thread is not None:
            self._uilog.debug("Field measure interrupt")
            self.thread.stop = True
            self._uilog.debug("Wait for thread")
            self.thread.wait()
            self._uilog.debug("Thread finished")
            self.motor.bpStop()
        self.fieldRedraw()

    @uiDisableTabsWrap
    def fieldMeasureAbort(self, message):
        """interrupt measure"""
        if self.thread is not None:
            self._uilog.debug("Abort measure")
            dialog = AlertWindow(self.basedir, message)
            dialog.exec_()
            self.thread.wait()
            self.thread = None
            self.motor.bpStop()

    def fieldReturn(self, *args):
        """return to origin"""
        self.fieldStop()
        self.motorReturn()

    def fieldNewPoint(self, data, x, i):
        """add new measured point"""
        self.fieldProgressBar.setValue(i + 1)
        self.field_data = np.append(self.field_data, data)
        self.field_coord = np.append(self.field_coord, x)
        self.plotField()

    def fieldRedraw(self, *args):
        """redraw filed plot"""
        if self.field_metadata is not None:
            self.plotField()

    def plotField(self):
        self.fieldCanvas.axes.clear()
        if self.fieldPlotType.currentText() == "Raw data":
            y = np.real(self.field_data)
            x = self.field_coord
        else:
            x, y = processFieldData(
                *fieldRemoveDrift(
                    self.field_coord,
                    self.field_data,
                    self.fieldDriftFirst.value(),
                    self.fieldDriftLast.value(),
                ),
                self.field_metadata,
            )
        self.fieldCanvas.axes.plot(x, y, color=self.proj_defaults["dataColor"])
        self.fieldCanvas.axes.grid()
        self.fieldCanvas.fig.tight_layout()
        self.fieldCanvas.draw()

    def fieldMeasureEnd(self, interrupted=True):
        """measure ended"""
        self.thread = None
        self.fieldRedraw()
        self._uilog.debug("Field measure end hook")
        self.va.bpNotifyUser()

    # download data section

    def scatDownload(self, *args):
        if self.scatter_metadata is None:  # there's no data yet
            return
        fle, tpe = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save File",
            path.join(
                self.lastdir, self.scatter_metadata["measure type"] + ".csv"
            ),
            "CSV Files (*.csv);;All Files (*)",
        )
        if fle != "":
            fle = path.splitext(fle)[0] + ".csv"
            self.lastdir = path.dirname(fle)
            mpl.rcParams["savefig.directory"] = self.lastdir
            self.scatter_metadata["project info"] = self.projInfo.text()
            if self.scatMarkerMax.isChecked():
                self.scatter_metadata[
                    "marker max"
                ] = self.labelScatMarkerMax.text().replace("\t", " ")
            if self.scatMarkerMin.isChecked():
                self.scatter_metadata[
                    "marker min"
                ] = self.labelScatMarkerMin.text().replace("\t", " ")
            if self.scatMarkerQ.isChecked():
                self.scatter_metadata[
                    "marker Q"
                ] = self.labelScatMarkerQ.text().replace("\t", " ")
            try:
                with open(fle, "w") as f:
                    f.write(
                        "# "
                        + prettyDict(self.scatter_metadata).replace(
                            "\n", "\n# "
                        )
                        + "\n"
                    )
                    f.write("""freq,data_1,data_2,raw_data_1,raw_data_2\n""")
                    np.savetxt(f, self.scatter_data, delimiter=",")
            except PermissionError:
                dialog = AlertWindow(self.basedir, "Cannot open file")
                dialog.exec_()

    def fieldDownload(self, *args):
        if self.field_metadata is None:  # there's no data yet
            return
        fle, tpe = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save File",
            path.join(self.lastdir, "field.csv"),
            "CSV Files (*.csv);;All Files (*)",
        )
        if fle != "":
            fle = path.splitext(fle)[0] + ".csv"
            self.lastdir = path.dirname(fle)
            mpl.rcParams["savefig.directory"] = self.lastdir
            self.field_metadata["project info"] = self.projInfo.text()
            try:
                with open(fle, "w") as f:
                    f.write(
                        "# "
                        + prettyDict(self.field_metadata).replace("\n", "\n# ")
                        + "\n"
                    )
                    f.write("# raw_data\nx,val_1,val_2\n")
                    nop = len(self.field_coord)
                    data = np.concatenate(
                        (
                            self.field_coord.reshape(nop, 1),
                            self.field_data.reshape(nop, 1),
                        ),
                        axis=1,
                    )
                    np.savetxt(f, data, delimiter=",")
                    f.write("# data\nx,val_1\n")
                    x, y = processFieldData(
                        *fieldRemoveDrift(
                            self.field_coord,
                            self.field_data,
                            self.fieldDriftFirst.value(),
                            self.fieldDriftLast.value(),
                        ),
                        self.field_metadata,
                    )
                    nop = len(x)
                    data = np.concatenate(
                        (x.reshape(nop, 1), y.reshape(nop, 1)), axis=1
                    )
                    np.savetxt(f, data, delimiter=",")
            except PermissionError:
                dialog = AlertWindow(self.basedir, "Cannot open file")
                dialog.exec_()

    # set/read UI section

    def vaReadSettings(self, *args):
        """read analyzer settings"""
        return {
            "measure type": self.scatMeasureType.currentText().lower(),
            "measure part": self.scatMeasurePart.currentText().lower(),
            "power": str(self.vaPower.isChecked()),
            "power level": str(self.vaPowerVal.value()),
            "averaging": str(self.vaAveraging.isChecked()),
            "averaging value": str(self.vaAveragingVal.value()),
            "smoothing": str(self.vaAveraging.isChecked()),
            "smoothing value": str(self.vaSmoothingVal.value()),
            "integration bandwidth": self.vaIntBand.currentText().lower(),
            "central frequency": self.scatFreqCenter.value(),
            "frequency span": self.scatFreqSpan.value(),
            "frequency unit": self.vaFreqUnit.currentText(),
            "phase offset": self.vaPhaseOffset.value(),
        }

    def setRibbon(self, *args):
        """set ribbon"""
        for x in self.motor_defaults["driver"]["options"]:
            action = self.menuMotor.addAction(x)
            action.triggered.connect(
                lambda y: self.motorDriverChanged(self.sender().text())
            )
        for x in self.va_defaults["driver"]["options"]:
            action = self.menuAnalyzer.addAction(x)
            action.triggered.connect(
                lambda y: self.analyzerDriverChanged(self.sender().text())
            )

    def setMotorPage(self, *args):
        """set motor page UI"""
        self.motorShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+1"), self
        )
        self.motorShortcut.activated.connect(
            lambda: self.Tabs.setCurrentIndex(0)
        )

        ports = self.motor.bpListPorts()
        self.motorPort.addItems(ports)
        if self.motor_defaults["connection"]["name"] in ports:
            self.motorPort.setCurrentIndex(
                ports.index(self.motor_defaults["connection"]["name"])
            )
        self.motorBaud.addItems(
            [str(x) for x in self.motor_defaults["connection"]["baudrates"]]
        )
        self.motorBaud.setCurrentIndex(
            self.motor_defaults["connection"]["baudrates"].index(
                self.motor_defaults["connection"]["baudrate"]
            )
        )
        self.motorMoveSpeed.setValue(
            self.motor_defaults["movement"]["moveSpeed"]
        )
        self.motorReturnSpeed.setValue(
            self.motor_defaults["movement"]["returnSpeed"]
        )
        self.motorAcceleration.setValue(
            self.motor_defaults["movement"]["acceleration"]
        )
        self.motorDeceleration.setValue(
            self.motor_defaults["movement"]["deceleration"]
        )
        self.projTotalLength.setValue(self.eq_defaults["stand"]["length"])
        self.projStep.setValue(self.eq_defaults["stand"]["step"])
        self.motorDirection.setChecked(
            self.motor_defaults["motion"]["reverseDirection"]
        )
        self.motorGotoPositionVal.setValue(
            self.motor_defaults["motion"]["position"]
        )
        self.motorStepVal.setValue(self.motor_defaults["motion"]["step"])
        self.motorConversionRatio.setValue(
            self.motor_defaults["calibration"]["ratio"]
        )

        self.actionMotorConnect.clicked.connect(self.motorConnect)
        self.actionMotorDisconnect.clicked.connect(self.motorDisconnect)
        self.actionMotorHold.clicked.connect(self.motorHold)
        self.actionMotorRelease.clicked.connect(self.motorRelease)
        self.actionMotorSetOrigin.clicked.connect(self.motorSetOrigin)
        self.actionMotorReturn.clicked.connect(self.motorReturn)
        self.actionMotorSet.clicked.connect(self.motorSet)
        self.motorDirection.stateChanged.connect(self.motorChangeDirection)
        self.actionMotorGotoPosition.clicked.connect(self.motorGoto)
        self.actionMotorStep.clicked.connect(self.motorStep)
        self.actionMotorCalibrate.clicked.connect(self.openCalibrationWindow)
        self.actionMotorStatus.clicked.connect(self.motorShowStatus)
        self.actionMotorStop.clicked.connect(self.motorStop)

    def readMotorPage(self, *args):
        """read motor page UI"""
        self.motor_defaults["connection"][
            "name"
        ] = self.motorPort.currentText()
        self.motor_defaults["connection"]["baudrate"] = int(
            self.motorBaud.currentText()
        )
        self.motor_defaults["movement"][
            "moveSpeed"
        ] = self.motorMoveSpeed.value()
        self.motor_defaults["movement"][
            "returnSpeed"
        ] = self.motorReturnSpeed.value()
        self.motor_defaults["movement"][
            "acceleration"
        ] = self.motorAcceleration.value()
        self.motor_defaults["movement"][
            "deceleration"
        ] = self.motorDeceleration.value()
        self.eq_defaults["stand"]["length"] = self.projTotalLength.value()
        self.eq_defaults["stand"]["step"] = self.projStep.value()
        self.motor_defaults["motion"][
            "reverseDirection"
        ] = self.motorDirection.isChecked()
        self.motor_defaults["motion"][
            "position"
        ] = self.motorGotoPositionVal.value()
        self.motor_defaults["motion"]["step"] = self.motorStepVal.value()
        self.motor_defaults["calibration"][
            "ratio"
        ] = self.motorConversionRatio.value()

    def setAnalyzerPage(self, *args):
        """set analyzer page UI"""
        self.analyzerShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+2"), self
        )
        self.analyzerShortcut.activated.connect(
            lambda: self.Tabs.setCurrentIndex(1)
        )

        ports = self.va.bpListPorts()
        self.vaName.addItems(ports)
        if self.va_defaults["connection"]["name"] in ports:
            self.vaName.setCurrentIndex(
                ports.index(self.va_defaults["connection"]["name"])
            )
        self.vaPower.setChecked(self.va_defaults["power"]["enable"])
        self.vaPowerVal.setValue(self.va_defaults["power"]["value"])
        self.vaAveraging.setChecked(self.va_defaults["averaging"]["enable"])
        self.vaAveragingVal.setValue(self.va_defaults["averaging"]["value"])
        self.vaSmoothing.setChecked(self.va_defaults["smoothing"]["enable"])
        self.vaSmoothingVal.setValue(self.va_defaults["smoothing"]["value"])
        self.vaIntBand.addItems(
            map(str, self.va_defaults["intBand"]["options"])
        )
        self.vaIntBand.setCurrentIndex(
            self.va_defaults["intBand"]["options"].index(
                self.va_defaults["intBand"]["selected"]
            )
        )
        self.vaNOP.addItems(
            map(str, self.va_defaults["numberOfPoints"]["options"])
        )
        self.vaNOP.setCurrentIndex(
            self.va_defaults["numberOfPoints"]["options"].index(
                self.va_defaults["numberOfPoints"]["selected"]
            )
        )
        self.vaSweepType.addItems(self.va_defaults["sweepTypes"]["options"])
        self.vaSweepType.setCurrentIndex(
            self.va_defaults["sweepTypes"]["options"].index(
                self.va_defaults["sweepTypes"]["selected"]
            )
        )
        self.vaFreqUnit.addItems(self.va_defaults["frequencyUnits"]["options"])
        self.vaFreqUnit.setCurrentIndex(
            self.va_defaults["frequencyUnits"]["options"].index(
                self.va_defaults["frequencyUnits"]["selected"]
            )
        )
        self.vaDisplayEnable.setChecked(self.va_defaults["display"]["enable"])
        self.projInfo.setText(self.proj_defaults["projectInfo"])
        self.vaPhaseOffset.setValue(self.va_defaults["phaseOffset"])

        self.actionVaConnect.clicked.connect(self.vaConnect)
        self.actionVaDisconnect.clicked.connect(self.vaDisconnect)
        self.actionVaStatus.clicked.connect(self.vaStatus)
        self.actionVaRelease.clicked.connect(self.vaRelease)
        self.actionVaReset.clicked.connect(self.vaReset)
        self.actionVaRestart.clicked.connect(self.vaRestart)
        self.actionVaSettingsApply.clicked.connect(self.vaSettingsApply)

    def readAnalyzerPage(self, *args):
        """read analyzer page UI"""
        self.va_defaults["connection"]["name"] = self.vaName.currentText()
        self.va_defaults["power"]["enable"] = self.vaPower.isChecked()
        self.va_defaults["power"]["value"] = self.vaPowerVal.value()
        self.va_defaults["averaging"]["enable"] = self.vaAveraging.isChecked()
        self.va_defaults["averaging"]["value"] = self.vaAveragingVal.value()
        self.va_defaults["smoothing"]["enable"] = self.vaSmoothing.isChecked()
        self.va_defaults["smoothing"]["value"] = self.vaSmoothingVal.value()
        self.va_defaults["intBand"]["selected"] = int(
            self.vaIntBand.currentText()
        )
        self.va_defaults["numberOfPoints"]["selected"] = int(
            self.vaNOP.currentText()
        )
        self.va_defaults["sweepTypes"][
            "selected"
        ] = self.vaSweepType.currentText()
        self.va_defaults["frequencyUnits"][
            "selected"
        ] = self.vaFreqUnit.currentText()
        self.va_defaults["display"][
            "enable"
        ] = self.vaDisplayEnable.isChecked()
        self.proj_defaults["projectInfo"] = self.projInfo.text()
        self.va_defaults["phaseOffset"] = self.vaPhaseOffset.value()

    def setScatteringPage(self, *args):
        """set scattering page UI"""
        self.scatteringShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+3"), self
        )
        self.scatteringShortcut.activated.connect(
            lambda: self.Tabs.setCurrentIndex(2)
        )

        self.scatMeasureType.addItems(
            self.va_defaults["measureType"]["options"]
        )
        self.scatMeasureType.setCurrentIndex(
            self.va_defaults["measureType"]["options"].index(
                self.va_defaults["measureType"]["selected"]
            )
        )
        self.scatMeasurePart.addItems(
            self.va_defaults["measurePart"]["options"].keys()
        )
        self.scatMeasurePart.setCurrentIndex(
            list(self.va_defaults["measurePart"]["options"].keys()).index(
                self.va_defaults["measurePart"]["selected"]
            )
        )
        self.scatMarkerMax.setChecked(self.va_defaults["markers"]["max"])
        self.scatMarkerMin.setChecked(self.va_defaults["markers"]["min"])
        self.scatMarkerQ.setChecked(self.va_defaults["markers"]["Q"])
        self.scatMarkerQVal.setValue(self.va_defaults["markers"]["QLevel"])
        self.scatFreqCenter.setValue(self.va_defaults["frequency"]["center"])
        self.scatFreqCenter.setSuffix(
            f' [{self.va_defaults["frequencyUnits"]["selected"]}]'
        )
        self.scatFreqSpan.setValue(self.va_defaults["frequency"]["span"])
        self.scatFreqSpan.setSuffix(
            f' [{self.va_defaults["frequencyUnits"]["selected"]}]'
        )
        self.scatCanvasDec = MplCanvas(self)
        self.scatToolbarDec = NavigationToolbar(self.scatCanvasDec, self)
        self.scatterPlotFrameDec.layout().addWidget(self.scatCanvasDec)
        self.scatterPlotFrameDec.layout().addWidget(self.scatToolbarDec)
        self.scatCanvasPol = MplCanvas(self, projection="polar")
        self.scatToolbarPol = NavigationToolbar(self.scatCanvasPol, self)
        self.scatterPlotFramePol.layout().addWidget(self.scatCanvasPol)
        self.scatterPlotFramePol.layout().addWidget(self.scatToolbarPol)
        self.scatterPlotFramePol.setVisible(False)
        self.scatCanvasSmt = MplCanvas(self, projection="smith")
        self.scatToolbarSmt = NavigationToolbar(self.scatCanvasSmt, self)
        self.scatterPlotFrameSmt.layout().addWidget(self.scatCanvasSmt)
        self.scatterPlotFrameSmt.layout().addWidget(self.scatToolbarSmt)
        self.scatterPlotFrameSmt.setVisible(False)
        self.labelScatMarkerMin.setVisible(self.va_defaults["markers"]["min"])
        self.labelScatMarkerMax.setVisible(self.va_defaults["markers"]["max"])
        self.labelScatMarkerQ.setVisible(self.va_defaults["markers"]["Q"])
        self.labelScatMarkerMin.setStyleSheet(
            f"color: {self.proj_defaults['minMarkerColor']};"
        )
        self.labelScatMarkerMax.setStyleSheet(
            f"color: {self.proj_defaults['maxMarkerColor']};"
        )
        self.labelScatMarkerQ.setStyleSheet(
            f"color: {self.proj_defaults['QMarkerColor']};"
        )
        self.scatCanvasDec.get_default_filename = (
            lambda: self.scatMeasureType.currentText().lower() + ".png"
        )
        self.scatCanvasPol.get_default_filename = (
            lambda: self.scatMeasureType.currentText().lower() + ".png"
        )
        self.scatCanvasSmt.get_default_filename = (
            lambda: self.scatMeasureType.currentText().lower() + ".png"
        )

        self.vaFreqUnit.currentTextChanged.connect(self.vaFreqChanged)
        self.actionScatMeasure.clicked.connect(self.vaScatMeasure)
        self.scatMarkerMin.toggled.connect(
            lambda x: self.labelScatMarkerMin.setVisible(bool(x))
        )
        self.scatMarkerMax.toggled.connect(
            lambda x: self.labelScatMarkerMax.setVisible(bool(x))
        )
        self.scatMarkerQ.toggled.connect(
            lambda x: self.labelScatMarkerQ.setVisible(bool(x))
        )
        self.actionScatDownload.clicked.connect(self.scatDownload)
        self.actionScatContinious.clicked.connect(
            lambda x: self.va.bpDisplayContinuous()
        )
        self.actionScatRelease.clicked.connect(self.vaRelease)
        self.actionScatFreqGet.clicked.connect(self.vaSetFreq)

    def readScatteringPage(self, *args):
        """set scattering page UI"""
        self.va_defaults["measureType"][
            "selected"
        ] = self.scatMeasureType.currentText()
        self.va_defaults["measurePart"][
            "selected"
        ] = self.scatMeasurePart.currentText()
        self.va_defaults["markers"]["max"] = self.scatMarkerMax.isChecked()
        self.va_defaults["markers"]["min"] = self.scatMarkerMin.isChecked()
        self.va_defaults["markers"]["Q"] = self.scatMarkerQ.isChecked()
        self.va_defaults["markers"]["QLevel"] = self.scatMarkerQVal.value()
        self.va_defaults["frequency"]["center"] = self.scatFreqCenter.value()
        self.va_defaults["frequency"]["span"] = self.scatFreqSpan.value()

    def setPostprocessingPage(self, *args):
        """set scattering page UI"""
        self.postprocessingShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+4"), self
        )
        self.postprocessingShortcut.activated.connect(
            lambda: self.Tabs.setCurrentIndex(3)
        )

        self.eqBeadMaterial.addItems(
            self.eq_defaults["beadMaterial"]["options"]
        )
        self.eqBeadMaterial.setCurrentIndex(
            self.eq_defaults["beadMaterial"]["options"].index(
                self.eq_defaults["beadMaterial"]["selected"]
            )
        )
        self.eqFieldPart.addItems(self.eq_defaults["fieldPart"]["options"])
        self.eqFieldPart.setCurrentIndex(
            self.eq_defaults["fieldPart"]["options"].index(
                self.eq_defaults["fieldPart"]["selected"]
            )
        )
        self.eqKEMantissa.setValue(self.eq_defaults["kE"]["mantissa"])
        self.eqKEExponent.setValue(self.eq_defaults["kE"]["exponent"])
        self.eqKHMantissa.setValue(self.eq_defaults["kH"]["mantissa"])
        self.eqKHExponent.setValue(self.eq_defaults["kH"]["exponent"])
        self.eqKSMantissa.setValue(self.eq_defaults["kS"]["mantissa"])
        self.eqKSExponent.setValue(self.eq_defaults["kS"]["exponent"])
        self.eqQLoad.setValue(self.eq_defaults["Qload"])
        self.webPage = WebViewWidget(
            html_file=path.join(
                self.basedir, path.normpath(self.eq_defaults["docs"])
            )
        )
        self.webPageWidget.layout().addWidget(self.webPage)
        self.webPage.show()

    def readPostprocessingPage(self, *args):
        """set scattering page UI"""
        self.eq_defaults["beadMaterial"][
            "selected"
        ] = self.eqBeadMaterial.currentText()
        self.eq_defaults["fieldPart"][
            "selected"
        ] = self.eqFieldPart.currentText()
        self.eq_defaults["kE"]["mantissa"] = self.eqKEMantissa.value()
        self.eq_defaults["kE"]["exponent"] = self.eqKEExponent.value()
        self.eq_defaults["kH"]["mantissa"] = self.eqKHMantissa.value()
        self.eq_defaults["kH"]["exponent"] = self.eqKHExponent.value()
        self.eq_defaults["kS"]["mantissa"] = self.eqKSMantissa.value()
        self.eq_defaults["kS"]["exponent"] = self.eqKSExponent.value()
        self.eq_defaults["Qload"] = self.eqQLoad.value()

    def setFieldPage(self, *args):
        """set field page UI"""
        self.fieldShortcut = QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+5"), self
        )
        self.fieldShortcut.activated.connect(
            lambda: self.Tabs.setCurrentIndex(4)
        )

        self.fieldPlotType.addItems(
            self.va_defaults["fieldPlotType"]["options"]
        )
        self.fieldPlotType.setCurrentIndex(
            self.va_defaults["fieldPlotType"]["options"].index(
                self.va_defaults["fieldPlotType"]["selected"]
            )
        )
        self.fieldStrategy.addItems(
            self.va_defaults["fieldStrategy"]["options"]
        )
        self.fieldStrategy.setCurrentIndex(
            self.va_defaults["fieldStrategy"]["options"].index(
                self.va_defaults["fieldStrategy"]["selected"]
            )
        )
        self.fieldDriftFirst.setValue(self.eq_defaults["fieldDrift"]["first"])
        self.fieldDriftLast.setValue(self.eq_defaults["fieldDrift"]["last"])
        self.fieldCanvas = MplCanvas(self)
        self.fieldToolbar = NavigationToolbar(self.fieldCanvas, self)
        self.fieldPlotFrame.layout().addWidget(self.fieldCanvas)
        self.fieldPlotFrame.layout().addWidget(self.fieldToolbar)
        self.fieldCanvas.get_default_filename = lambda: "field.png"

        self.actionFieldMeasure.clicked.connect(self.fieldMeasure)
        self.actionFieldStop.clicked.connect(self.fieldStop)
        self.actionFieldReturn.clicked.connect(self.fieldReturn)
        self.actionFieldDownload.clicked.connect(self.fieldDownload)
        self.fieldPlotType.currentTextChanged.connect(self.fieldRedraw)

    def readFieldPage(self, *args):
        """set field page UI"""
        self.va_defaults["fieldPlotType"][
            "selected"
        ] = self.fieldPlotType.currentText()
        self.va_defaults["fieldStrategy"][
            "selected"
        ] = self.fieldStrategy.currentText()
        self.eq_defaults["fieldDrift"]["first"] = self.fieldDriftFirst.value()
        self.eq_defaults["fieldDrift"]["last"] = self.fieldDriftLast.value()

    def readCalibrateWindowSettings(self, step, measure):
        """read settings from calibration window"""
        self.motor_defaults["calibration"]["step"] = step
        self.motor_defaults["calibration"]["length"] = measure
