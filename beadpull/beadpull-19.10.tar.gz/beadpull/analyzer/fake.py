"""Fake vector analyzer class"""
from typing import Dict, Optional, List
import numpy as np
from random import uniform

from .generic import GenericAnalyzer


class FakeAnalyzer(GenericAnalyzer):
    """analyzer method interfaces for BeadPull"""

    def __init__(self):
        self.nop = 101
        self.f0 = 2856e6
        self.span = 10e6
        self.data_index = 0
        self.data_freq = 0.01
        self.connected = False

    def bpConnect(self, name: str) -> bool:
        """connect to analyzer

        Arguments:
        name[str] -- analyzer GPIB name

        Return value[bool] -- success/failure
        """
        self.connected = True
        return True

    def bpDisconnect(self) -> bool:
        """disconnect analyzer

        Return value[bool] -- success/failure
        """
        self.connected = False
        return True

    def bpIsConnected(self) -> bool:
        """check if connected to analyzer

        Return value[bool] -- connected/not connected
        """
        return self.connected

    def bpListPorts(self) -> List[str]:
        """list possible analyzer ports"""
        return ["analyzer port"]

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
        self.nop = nop
        self.data_freq = uniform(0.01, 0.5)
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
        self.f0 = freq_center
        self.span = freq_span
        return True

    def bpStatus(self) -> Dict[str, str]:
        """analyzer status

        Return value[Dict[str, str]] -- key-value pairs of analyzer status info
        """
        return {"driver": "fake"}

    def bpMarkerMin(self) -> Optional[Dict[str, float]]:
        """find trace minimum

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"val1": float, "val2": float, "f": float}. val1 and val2 are
        data values f is frequency in Hz. None in case of errors
        """
        return {"val1": uniform(0, 1), "val2": uniform(0, 1), "f": self.f0}

    def bpMarkerMax(self) -> Optional[Dict[str, float]]:
        """find trace maximum

        Return value[Optional[Dict[str, float]]] -- measured marker dict with
        syntax {"val1": float, "val2": float, "f": float}. val1 and val2 are
        data values f is frequency in Hz. None in case of errors
        """
        return {"val1": uniform(0, 1), "val2": uniform(0, 1), "f": self.f0}

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
        return {
            "Q": uniform(0, 1),
            "loss": uniform(0, 1),
            "center": self.f0,
            "bandwidth": self.span,
            "level": uniform(0, 1),
        }

    def bpMeasureScattering(self) -> Optional[np.ndarray]:
        """measure scattering parameters

        Return value[Optional[np.ndarray] -- measured array of scattering data
        in shape (n, 2), where n is a number of points
        None in case of errors
        """
        return np.concatenate(
            (
                np.sin(np.linspace(0, uniform(1, 15), self.nop)).reshape(
                    self.nop, 1
                ),
                np.cos(np.linspace(0, uniform(1, 15), self.nop)).reshape(
                    self.nop, 1
                ),
            ),
            axis=1,
        )

    def bpMeasureScatteringRaw(self) -> Optional[np.ndarray]:
        """measure scattering parameters without post processing

        Return value[Optional[np.ndarray] -- measured array of scattering data
        in shape (n, 2), where n is a number of points with real/imaginary data
        columns. None in case of errors
        """
        return np.concatenate(
            (
                np.sin(np.linspace(0, uniform(1, 15), self.nop)).reshape(
                    self.nop, 1
                ),
                np.cos(np.linspace(0, uniform(1, 15), self.nop)).reshape(
                    self.nop, 1
                ),
            ),
            axis=1,
        )

    def bpGetFrequencyPoints(self) -> Optional[np.ndarray]:
        """get measure frequency points

        Return value[Optional[np.ndarray] -- measured array of frequency points
        in Hz. None in case of errors
        """
        return np.linspace(
            self.f0 - self.span / 2, self.f0 + self.span / 2, self.nop
        )

    def bpGetFrequencyCenter(self) -> Optional[float]:
        """get center frequency

        Return value[Optional[float] -- analyzer center frequency in Hz.
        None in case of errors
        """
        return self.f0

    def bpGetFrequencySpan(self) -> Optional[float]:
        """get frequency span

        Return value[Optional[float] -- analyzer frequency span in Hz.
        None in case of errors
        """
        return self.span

    def bpMeasureFieldReflectionDF(self) -> Optional[float]:
        """measure field from reflection data using frequency deviation

        Return value[Optional[float] -- measured frequency deviation.
        None in case of error
        """
        self.data_index += 1
        return np.abs(np.sin(self.data_freq * self.data_index))

    def bpMeasureFieldReflectionDSE(self) -> Optional[complex]:
        """measure field from reflection data modulus

        Return value[Optional[complex] -- measured modulus of S11 parameter.
        None in case of error
        """
        self.data_index += 1
        return complex(
            np.abs(np.sin(self.data_freq * self.data_index)),
            np.abs(np.sin(self.data_freq * self.data_index)),
        )

    def bpMeasureFieldReflectionDSPhi(self) -> Optional[float]:
        """measure field phase from reflection phase data

        Return value[Optional[complex] -- measured S11 parameter phase.
        None in case of error
        """
        self.data_index += 1
        return np.abs(np.sin(self.data_freq * self.data_index))

    def bpMeasureFieldTransmissionDF(self) -> Optional[float]:
        """measure field from transmission data using frequency deviation

        Return value[Optional[float] -- measured resonant frequency.
        None in case of error
        """
        self.data_index += 1
        return np.abs(np.sin(self.data_freq * self.data_index))

    def bpMeasureFieldTransmissionDPhi(self) -> Optional[float]:
        """measure field from transmission data using phase deviation

        Return value[Optional[float] -- measured phase.
        None in case of error
        """
        self.data_index += 1
        return np.abs(np.sin(self.data_freq * self.data_index))
