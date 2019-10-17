"""Generic vector analyzer class. This class contains method interfaces
needed for BeadPull.
In order to add support for another motor, create a subclass of GenericMotor
class and implement methods. It's OK leave some of them unimplemented.
Watch out for method data types."""
from typing import Dict, Optional, List
import numpy as np


class GenericAnalyzer:
    """analyzer method interfaces for BeadPull"""

    def bpConnect(self, name: str) -> bool:
        """connect to analyzer

        Arguments:
        name[str] -- analyzer GPIB name

        Return value[bool] -- success/failure
        """
        return True

    def bpDisconnect(self) -> bool:
        """disconnect analyzer

        Return value[bool] -- success/failure
        """
        return True

    def bpListPorts(self) -> List[str]:
        """list possible analyzer ports"""
        return []

    def bpIsConnected(self) -> bool:
        """check if connected to analyzer

        Return value[bool] -- connected/not connected
        """
        return True

    def bpReset(self) -> bool:
        """reset vector analyzer to factory settings

        Return value[bool] -- success/failure
        """
        return True

    def bpRestart(self) -> bool:
        """restart vector analyzer

        Return value[bool] -- success/failure
        """
        return True

    def bpReleaseControl(self) -> bool:
        """release control of vector analyzer (push to local mode)

        Return value[bool] -- success/failure
        """
        return True

    def bpInit(self) -> bool:
        """initialize vector analyzer

        Return value[bool] -- success/failure
        """
        return True

    def bpDeinit(self) -> bool:
        """deinitialize vector analyzer

        Return value[bool] -- success/failure
        """
        return True

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
        return True

    def bpApplyScatterMeasureSettings(
        self,
        measure_type: str = "Reflection",
        measure_part: str = "Logarithmic magnitude",
        freq_center: int = 2856,
        freq_span: int = 10,
    ) -> bool:
        """apply scattering measure settings

        Arguments:
        measure_type[str] -- measure type ("Reflection" or "Transmission")
        measure_part[str] -- measure part ("Real" or "Imaginary" or
"Linear magnitude" or "Logarithmic magnitude" or "Phase" or "Delay" or
"Polar" or "Smith" or "Standing wave ratio")
        freq_center[int] -- center frequency in selected units
        freq_span[int] -- frequency span in selected units

        Return value[bool] -- success/failure
        """
        return True

    def bpStatus(self) -> Dict[str, str]:
        """analyzer status

        Return value[Dict[str, str]] -- key-value pairs of analyzer status info
        """
        return {"": ""}

    def bpDisplayContinuous(self) -> bool:
        """set analyzer to continuous measure display

        Return value[bool] -- success/failure
        """
        return True

    def bpNotifyUser(self) -> bool:
        """visual and/or sound notification

        Return value[bool] -- success/failure
        """
        return True

    def bpMarkerMin(self) -> Optional[Dict[str, float]]:
        """find trace minimum

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"val1": float, "val2": float, "f": float}. val1 and val2 are
        data values f is frequency in Hz. None in case of errors
        """
        return None

    def bpMarkerMax(self) -> Optional[Dict[str, float]]:
        """find trace maximum

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"val1": float, "val2": float, "f": float}. val1 and val2 are
        data values f is frequency in Hz. None in case of errors
        """
        return None

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
        return None

    def bpMeasureScattering(self) -> Optional[np.ndarray]:
        """measure scattering parameters

        Return value[Optional[np.ndarray] -- measured array of scattering data
        in shape (n, 2), where n is a number of points
        None in case of errors
        """
        return None

    def bpMeasureScatteringRaw(self) -> Optional[np.ndarray]:
        """measure scattering parameters without post processing

        Return value[Optional[np.ndarray] -- measured array of scattering data
        in shape (n, 2), where n is a number of points with real/imaginary data
        columns. None in case of errors
        """
        return None

    def bpGetFrequencyPoints(self) -> Optional[np.ndarray]:
        """get measure frequency points

        Return value[Optional[np.ndarray] -- measured array of frequency points
        in Hz. None in case of errors
        """
        return None

    def bpGetFrequencyCenter(self) -> Optional[float]:
        """get center frequency

        Return value[Optional[float] -- analyzer center frequency in Hz.
        None in case of errors
        """
        return None

    def bpGetFrequencySpan(self) -> Optional[float]:
        """get frequency span

        Return value[Optional[float] -- analyzer frequency span in Hz.
        None in case of errors
        """
        return None

    def bpPreMeasureHook(self) -> bool:
        """function to call before any measure

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        return True

    def bpPostMeasureHook(self) -> None:
        """function to call after any measure"""
        pass

    def bpMeasureFieldReflectionDF(self) -> Optional[float]:
        """measure field from reflection data using frequency deviation

        Return value[Optional[float] -- measured frequency deviation.
        None in case of error
        """
        return None

    def bpPreFieldReflectionDFMeasureHook(self) -> bool:
        """prepare field measure using reflection data using frequency
        deviation

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        return True

    def bpPostFieldReflectionDFMeasureHook(self) -> None:
        """cleanup after field measure using reflection data frequency
        deviation
        """
        pass

    def bpMeasureFieldReflectionDSE(self) -> Optional[complex]:
        """measure field from complex reflection data

        Return value[Optional[complex] -- measured complex S11 parameter.
        None in case of error
        """
        return None

    def bpPreFieldReflectionDSEMeasureHook(self) -> bool:
        """prepare field measure using complex reflection data

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        return True

    def bpPostFieldReflectionDSEMeasureHook(self) -> None:
        """cleanup after field measure using complex reflection data"""
        pass

    def bpMeasureFieldReflectionDSPhi(self) -> Optional[float]:
        """measure field phase from reflection phase data

        Return value[Optional[complex] -- measured S11 parameter phase.
        None in case of error
        """
        return None

    def bpPreFieldReflectionDSPhiMeasureHook(self) -> bool:
        """prepare field phase measure using reflection phase data

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        return True

    def bpPostFieldReflectionDSPhiMeasureHook(self) -> None:
        """cleanup after field phase measure using reflection phase data"""
        pass

    def bpMeasureFieldTransmissionDF(self) -> Optional[float]:
        """measure field from transmission data using frequency deviation

        Return value[Optional[float] -- measured resonant frequency.
        Number imaginary part is only needed for data compatibility.
        None in case of error
        """
        return None

    def bpPreFieldTransmissionDFMeasureHook(self) -> bool:
        """prepare field measure using transmission data using frequency
        deviation

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        return True

    def bpPostFieldTransmissionDFMeasureHook(self) -> None:
        """cleanup after field measure using transmission data using
        frequency deviation
        """
        pass

    def bpMeasureFieldTransmissionDPhi(self) -> Optional[float]:
        """measure field from transmission data using phase deviation

        Return value[Optional[float] -- measured phase.
        None in case of error
        """
        return None

    def bpPreFieldTransmissionDPhiMeasureHook(self) -> bool:
        """prepare field measure using transmission data using phase
        deviation

        Return value[bool] -- success/failure. Measure will not be done if
        returned False
        """
        return True

    def bpPostFieldTransmissionDPhiMeasureHook(self) -> None:
        """cleanup after field measure using transmission data using
        phase deviation
        """
        pass
