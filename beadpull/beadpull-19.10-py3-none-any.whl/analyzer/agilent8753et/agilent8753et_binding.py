import yaml
import numpy as np
from os.path import join, dirname
from typing import Dict, Optional, List

from .agilent8753et import Agilent8753et
from ..generic import GenericAnalyzer

measure_parts = {
    "real": "REAL",
    "imaginary": "IMAG",
    "linear magnitude": "LINM",
    "logarithmic magnitude": "LOGM",
    "phase": "PHAS",
    "delay": "DELA",
    "polar": "POLA",
    "smith": "SMIC",
    "standing wave ratio": "SWR",
}


COMM_TIMEOUT = 3000
DATA_TIMEOUT = 600000


class Agilent8753et_binding(Agilent8753et, GenericAnalyzer):
    """Agilent8753et class bindings for BeadPull"""

    def __init__(self) -> None:
        super(Agilent8753et_binding, self).__init__()
        self.va_settings = yaml.load(
            open(join(dirname(__file__), "settings.yaml"), "r"),
            Loader=yaml.FullLoader,
        )

    def bpConnect(self, name: str) -> bool:
        """connect to analyzer

        Arguments:
        name[str] -- analyzer GPIB name

        Return value[bool] -- success/failure
        """
        rv = self.connect(name)
        if rv:
            self.timeout(COMM_TIMEOUT)
        return rv

    def bpDisconnect(self) -> bool:
        """disconnect analyzer

        Return value[bool] -- success/failure
        """
        self._aglog.info("Analyzer disconnected")
        self.disconnect()
        return True

    def bpListPorts(self) -> List[str]:
        """list possible analyzer ports"""
        return self.listPorts()

    def bpIsConnected(self) -> bool:
        """check if connected to analyzer

        Return value[bool] -- connected/not connected
        """
        if self.identity() is not None:
            self._aglog.info("Analyzer connected")
            return True
        else:
            return False

    def bpReset(self) -> bool:
        """reset vector analyzer to factory settings

        Return value[bool] -- success/failure
        """
        self.revert()
        self._aglog.info("Analyzer reset")
        return self.sendBuffer()

    def bpRestart(self) -> bool:
        """restart vector analyzer

        Return value[bool] -- success/failure
        """
        self.reset()
        self._aglog.info("Analyzer restart")
        return self.sendBuffer()

    def bpReleaseControl(self) -> bool:
        """release control of vector analyzer (push to local mode)

        Return value[bool] -- success/failure
        """
        self.release()
        self._aglog.info("Analyzer release")
        return self.sendBuffer()

    def bpInit(self) -> bool:
        """initialize vector analyzer

        Return value[bool] -- success/failure
        """
        self.dataForm()
        self.markerClear()
        self.markerTrack(True)
        self.markerInterp(True)
        self._aglog.info("Analyzer initialized")
        return self.sendBuffer()

    def bpApplyGeneralSettings(
        self,
        power: bool = True,
        power_val: int = 0,
        averaging: bool = False,
        averaging_val: int = 1,
        smoothing: bool = False,
        smoothing_val: float = 1,
        integ_band: int = 1000,
        sweep: str = "Linear",
        nop: int = 101,
        unit: str = "MHz",
        phase_offset: int = 0,
        display: bool = True,
    ) -> bool:
        """apply general settings

        Arguments:
        power[bool] -- enable source power
        power_val[int] -- desired power level in dBm
        averaging[bool] -- enable measure averaging
        averaging_val[int] -- number of averaging passes
        smoothing[bool] -- enable measure smoothing
        smoothing_val[int] -- smoothing aperture in %
        integ_band[int] -- desired integration bandwidth
        sweep[str] -- frequency sweep type ("Linear" or "Logarithmic")
        nop[int] -- number of measure points
        unit[str] -- frequency unit ("Hz" or "kHz" or "MHz" or "GHz")
        phase_offset[int] -- set analyzer phase offset
        display[bool] -- enable analyzer display

        Return value[bool] -- success/failure
        """
        self.powerOn(power)
        self.power(power_val)
        self.averaging(averaging_val)
        self.averagingOn(averaging)
        self.smoothingOn(smoothing)
        self.smoothing(smoothing_val)
        self.integBandw(integ_band)
        self.logSweep(sweep == "Logarithmic")
        self.numPoints(nop)
        self.phaseOffset(phase_offset)
        self.unit = unit.upper()
        self.blankDisplay(not display)
        self._aglog.info("Analyzer general settings applied")
        return self.sendBuffer()

    def bpApplyScatterMeasureSettings(
        self,
        measure_type: str = "Reflection",
        measure_part: str = "Logarithmic magnitude",
        freq_center: int = 2856,
        freq_span: int = 10,
    ) -> bool:
        """apply scattering measure settings

        Arguments:
        measure_type[str] -- measure type ("reflection" or "transmission")
        measure_part[str] -- measure part ("real" or "imaginary" or
"linear magnitude" or "logarithmic magnitude" or "phase" or "delay" or
"polar" or "smith" or "standing wave ratio")
        freq_center[int] -- center frequency in selected units
        freq_span[int] -- frequency span in selected units

        Return value[bool] -- success/failure
        """
        if measure_type.lower() == "transmission":
            self.transmission()
        else:
            self.reflection()
        self.plotFormat(
            measure_parts.get(
                measure_part.lower(), measure_parts["logarithmic magnitude"]
            )
        )
        self.freqCenter(freq_center)
        self.freqSpan(freq_span)
        self._aglog.info("Analyzer scatter measure settings applied")
        return self.sendBuffer()

    def bpStatus(self) -> Dict[str, str]:
        """analyzer status

        Return value[Dict[str, str]] -- key-value pairs of analyzer status info
        """
        output = {"driver": "agilent8753et"}
        rv = self.identity()
        if rv is not None:
            output.update(rv)
        return output

    def bpDisplayContinuous(self) -> bool:
        """set analyzer to continuous measure display

        Return value[bool] -- success/failure
        """
        self.continuous()
        return self.sendBuffer()

    def bpNotifyUser(self) -> bool:
        """visual and/or sound notification

        Return value[bool] -- success/failure
        """
        self.beep()
        return self.sendBuffer()

    def bpMarkerMin(self) -> Optional[Dict[str, float]]:
        """find trace minimum

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"val1": float, "val2": float, "f": float}. val1 and val2 are
        data values f is frequency in Hz. None in case of errors
        """
        self.markerSelect(4)
        self.markerMin()
        rv = self.markerRead()
        if rv is not None:
            self._aglog.info("Analyzer found minimum")
        return rv

    def bpMarkerMax(self) -> Optional[Dict[str, float]]:
        """find trace maximum

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"val1": float, "val2": float, "f": float}. val1 and val2 are
        data values f is frequency in Hz. None in case of errors
        """
        self.markerSelect(5)
        self.markerMax()
        rv = self.markerRead()
        if rv is not None:
            self._aglog.info("Analyzer found maximum")
        return rv

    def bpMarkerQ(
        self, marker_Q_val: float, measure_type: str = "reflection"
    ) -> Optional[Dict[str, float]]:
        """find trace Q

        Attributes:
        measure_type[str] -- measure type ("reflection" or "transmission")
        marker_Q_val[float] -- Q width target

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"Q": float, "loss": float, "center": float, "bandwidth": float,
        "level": float}.
        Q and loss are themselves. center and bandwidth are frequencies in Hz.
        level is a value of central frequency point.
        None in case of errors
        """
        self.markerClear()
        self.markerSelect(1)
        level: Optional[Dict[str, float]] = {}
        if measure_type.lower() == "transmission":
            self.markerMax()
        else:
            self.markerMin()
        level = self.markerRead()
        self.markerZero()
        self.searchWidthVal(marker_Q_val)
        self.searchWidth(True)
        rv = self.readWidth()
        if rv is not None:
            self._aglog.info("Analyzer Q measured")
            rv.update({"level": level["val1"]})
        return rv

    def bpMeasureScattering(self) -> Optional[np.ndarray]:
        """measure scattering parameters

        Return value[Optional[np.ndarray] -- measured array of scattering data
        in shape (n, 2), where n is a number of points
        None in case of errors
        """
        rv = self.readData()
        if rv is None:
            self._aglog.warn("Could not get data")
        else:
            self._aglog.info("Scattering data obtained")
        return rv

    def bpMeasureScatteringRaw(self) -> Optional[np.ndarray]:
        """measure scattering parameters without post processing

        Return value[Optional[np.ndarray] -- measured array of scattering data
        in shape (n, 2), where n is a number of points with real/imaginary data
        columns. None in case of errors
        """
        rv = self.readData("DATA")
        if rv is None:
            self._aglog.warn("Could not get raw data")
        else:
            self._aglog.info("Raw scattering data obtained")
        return rv

    def bpGetFrequencyPoints(self) -> Optional[np.ndarray]:
        """get measure frequency points

        Return value[Optional[np.ndarray] -- measured array of frequency points
        in Hz. None in case of errors
        """
        rv = self.freqGetRange()
        if rv is None:
            self._aglog.warn("Could not get frequency points")
        else:
            self._aglog.info("Frequency points obtained")
        return rv

    def bpGetFrequencyCenter(self) -> Optional[float]:
        """get center frequency

        Return value[Optional[float] -- analyzer center frequency in Hz.
        None in case of errors
        """
        rv = self.freqGetCenter()
        if rv is None:
            self._aglog.warn("Could not center frequency")
        else:
            self._aglog.info("Center frequency obtained")
        return rv

    def bpGetFrequencySpan(self) -> Optional[float]:
        """get frequency span

        Return value[Optional[float] -- analyzer frequency span in Hz.
        None in case of errors
        """
        rv = self.freqGetSpan()
        if rv is None:
            self._aglog.warn("Could not get frequency span")
        else:
            self._aglog.info("Frequency span obtained")
        return rv

    def bpPreMeasureHook(self) -> bool:
        """function to call before any measure

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        self.timeout(DATA_TIMEOUT)
        self.markerClear()
        self.hold()
        self.numPointsUpdate()
        self.single()
        self.waitClean()
        self._aglog.info("Analyzer premeasure hook run")
        return self.sendBuffer()

    def bpPostMeasureHook(self) -> None:
        """function to call after any measure"""
        self.autoScale()
        self.sendBuffer()
        self.timeout(COMM_TIMEOUT)
        self._aglog.info("Analyzer postmeasure hook run")

    def bpMeasureFieldReflectionDF(self) -> Optional[float]:
        """measure field from reflection data using frequency deviation

        Return value[Optional[float] -- measured frequency deviation.
        None in case of error
        """
        self._aglog.info(
            """Measuring field from reflection using frequency\
 deviation"""
        )
        self.single()
        self.waitClean()
        self.autoScale()
        self.sendBuffer()
        self.markerMin()
        self.markerCenter()
        self.sendBuffer()
        data = self.markerRead()
        if data is None:
            self._aglog.warn("Could not get data")
            return None
        else:
            return data["f"]

    def bpPreFieldReflectionDFMeasureHook(self) -> bool:
        """prepare field measure using reflection data using frequency
        deviation

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        self.reflection()
        self.plotFormat("LOGM")
        self.autoScale()
        self.markerMin()
        self.markerCenter()
        self._aglog.info(
            """Analyzer reflection frequency deviation \
field premeasure hook run"""
        )
        return self.sendBuffer()

    def bpMeasureFieldReflectionDSE(self) -> Optional[complex]:
        """measure field from complex reflection data

        Return value[Optional[complex] -- measured complex S11 parameter.
        None in case of error
        """
        self.single()
        self.waitClean()
        self.sendBuffer()
        data = self.readData("DATA")
        if data is None:
            self._aglog.warn("Could not get data")
            return None
        else:
            return complex(data[1, 0], data[1, 1])

    def bpPreFieldReflectionDSEMeasureHook(self) -> bool:
        """prepare field measure using complex reflection data

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        self.reflection()
        self.plotFormat("LOGM")
        self.markerMin()
        self.markerCenter()
        self.numPoints(3)
        self._aglog.info(
            "Analyzer complex reflection field premeasure hook run"
        )
        return self.sendBuffer()

    def bpMeasureFieldReflectionDSPhi(self) -> Optional[float]:
        """measure field phase from reflection phase data

        Return value[Optional[float] -- measured S11 phase parameter.
        None in case of error
        """
        self.single()
        self.waitClean()
        self.sendBuffer()
        data = self.readData()
        if data is None:
            self._aglog.warn("Could not get data")
            return None
        else:
            return data[1, 0]

    def bpPreFieldReflectionDSPhiMeasureHook(self) -> bool:
        """prepare field phase measure using reflection phase data

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        self.reflection()
        self.plotFormat("LOGM")
        self.markerMin()
        self.markerCenter()
        self.plotFormat("PHAS")
        self.autoScale()
        self.numPoints(3)
        self._aglog.info("Analyzer reflection phase field premeasure hook run")
        return self.sendBuffer()

    def bpMeasureFieldTransmissionDF(self) -> Optional[float]:
        """measure field from transmission data using frequency deviation

        Return value[Optional[float] -- measured resonant frequency.
        None in case of error
        """
        self.single()
        self.waitClean()
        self.sendBuffer()
        self.markerMax()
        self.markerCenter()
        self.sendBuffer()
        data = self.markerRead()
        if data is None:
            self._aglog.warn("Could not get data")
            return None
        else:
            return data["f"]

    def bpPreFieldTransmissionDFMeasureHook(self) -> bool:
        """prepare field measure using transmission data using frequency
        deviation

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        self.transmission()
        self.plotFormat("LOGM")
        self.autoScale()
        self.markerMax()
        self.markerCenter()
        self._aglog.info(
            """Analyzer transmission frequency deviation \
field premeasure hook run
        """
        )
        return self.sendBuffer()

    def bpMeasureFieldTransmissionDPhi(self) -> Optional[float]:
        """measure field from transmission data using phase deviation

        Return value[Optional[float] -- measured phase.
        None in case of error
        """
        self.single()
        self.waitClean()
        self.sendBuffer()
        data = self.readData()
        if data is None:
            self._aglog.warn("Could not get data")
            return None
        else:
            return data[1, 0]

    def bpPreFieldTransmissionDPhiMeasureHook(self) -> bool:
        """prepare field measure using transmission data using phase
        deviation

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        self.transmission()
        self.plotFormat("PHAS")
        self.autoScale()
        self.markerMax()
        self.markerCenter()
        self.numPoints(3)
        self._aglog.info(
            """Analyzer transmission phase deviation \
field premeasure hook run"""
        )
        return self.sendBuffer()
