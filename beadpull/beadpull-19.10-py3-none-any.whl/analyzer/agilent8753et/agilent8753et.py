import logging
import numpy as np
from typing import Optional, Dict, List, TypeVar, Generic
import visa

Instrument = TypeVar("Instrument")


class Agilent8753et(Generic[Instrument]):
    """Class for Agilent8753ET"""

    def __init__(self) -> None:
        self._aglog = logging.getLogger("agilent8753et")
        self.__rm = visa.ResourceManager()
        self.__buffer = ""
        self.__instrument: Optional[Instrument] = None
        self.unit = "HZ"  # HZ|KHZ|MHZ|GHZ
        self.__freq_log = False
        self.__data_format = "???"
        self.__number_of_points = 51

    def listPorts(self) -> List[str]:
        """List available ports"""
        return [x for x in self.__rm.list_resources() if "GPIB" in x]

    def connect(self, port: str) -> bool:
        """Connect to instrument.
        port: name of instrument
        Output value: true for success, false for failure"""
        if self.__instrument is None:
            try:
                self.__instrument = self.__rm.get_instrument(port)
                self.__instrument.write_termination = ";\n"
                self.__instrument.read_termination = "\n"
                self._aglog.info(f"Connected to {port}")
                return True
            except visa.VisaIOError:
                self.__instrument = None
                self._aglog.error(f"Cannot connect to {port}")
                return False
        else:
            self._aglog.warning("Already connected to instrument")
            return False

    def timeout(self, timeout: Optional[int]) -> None:
        """Configure serial communication timeout.
        timeout: communication timeout in ms. None for no timeout"""
        if self.__instrument is not None:
            self.__instrument.timeout = timeout

    def disconnect(self) -> None:
        """Disconnect from port"""
        if self.__instrument is not None:
            self.__instrument.close()
            self.__instrument = None
            self._aglog.info("Connection closed")

    def _bufferCommand(self, command: str) -> None:
        """add command to buffer to send later"""
        self.__buffer = self.__buffer + ";" + command

    def identity(self) -> Optional[Dict[str, str]]:
        """get device identity"""
        if self.__instrument is None:
            return None
        try:
            rv = self.__instrument.query("IDN?")
            words = rv.strip().split(",")
            output = {
                "vendor": words[0],
                "model": words[1],
                "serial number": words[2],
                "firmware revision": words[3],
            }
            self._aglog.debug(f"Device information: {output}")
            return output
        except (visa.VisaIOError, IndexError) as e:
            self._aglog.error(f"No response from device: {e}")
            return None

    def release(self) -> None:
        """release device"""
        self._aglog.debug("Releasing analyzer")
        self._bufferCommand("KEY42")

    def reset(self) -> bool:
        """Reset device"""
        try:
            self.__instrument.write("*RST")
            self._aglog.debug(f"Device reset")
            return True
        except visa.VisaIOError:
            self._aglog.error("No response from device")
            return False

    def sendBuffer(self) -> bool:
        self._aglog.debug(f"Send buffered data")
        if self.__buffer == "":
            return True
        try:
            self.__instrument.write(f"{self.__buffer}")
            self.__buffer = ""
            return True
        except visa.VisaIOError:
            return False

    def adapterCoax(self) -> None:
        """push adapterCoax command to buffer"""
        self._aglog.debug(f"Select coax adapter")
        self._bufferCommand("ADPTCOAX")

    def adapterWaveguide(self) -> None:
        """push adapterWaveguide command to buffer"""
        self._aglog.debug(f"Select waveguide adapter")
        self._bufferCommand("ADPTWAVE")

    def autoScale(self) -> None:
        """push autoscale command to buffer"""
        self._aglog.debug(f"Autoscale")
        self._bufferCommand("AUTO")

    def blankDisplay(self, val: bool) -> None:
        """push blankDisplay command to buffer"""
        self._aglog.debug(f"Disable display")
        self._bufferCommand(f"BLAD{'ON' if val else 'OFF'}")

    def averaging(self, n: int) -> None:
        """set averaging factor"""
        self._aglog.debug(f"Set averaging")
        self._bufferCommand(f"AVERFACT{n}")

    def averagingOn(self, val: bool) -> None:
        """enable averaging"""
        self._aglog.debug(f"Enable averaging")
        self._bufferCommand(f"AVER{'ON' if val else 'OFF'}")

    def averagingReset(self) -> None:
        """reset averaging"""
        self._bufferCommand("AVERREST")

    def setFreqUnit(self, val: str) -> None:
        """set frequency unit"""
        self._aglog.debug(f"Frequency unit set to {val}")
        self.unit = val

    def freqCenter(self, val: int) -> None:
        """set center frequency"""
        self._aglog.debug(f"Set center frequency {val}{self.unit}")
        self._bufferCommand(f"CENT{val}{self.unit}")

    def freqSpan(self, val: int) -> None:
        """frequency span"""
        self._aglog.debug(
            f"Set frequency span {val} \
{self.unit if not self.__freq_log else 'DB'}"
        )
        self._bufferCommand(
            f"SPAN{val}{self.unit if not self.__freq_log else 'DB'}"
        )

    def freqGetCenter(self) -> Optional[float]:
        """set center frequency
        flushes buffer"""
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values(f"CENT?")[0]
            return rv
        except (visa.VisaIOError, IndexError):
            return None

    def freqGetSpan(self) -> Optional[float]:
        """set frequency span
        flushes buffer"""
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values(f"SPAN?")[0]
            return rv
        except (visa.VisaIOError, IndexError):
            return None

    def freqStart(self, val: int) -> None:
        """set start frequency"""
        self._bufferCommand(
            f"STAR{val}{self.unit if not self.__freq_log else 'DB'}"
        )

    def freqStop(self, val: int) -> None:
        """set stop frequency"""
        self._bufferCommand(
            f"STOP{val}{self.unit if not self.__freq_log else 'DB'}"
        )

    def freqCW(self, val: int) -> None:
        """CW frequency"""
        self._bufferCommand(f"CWFREQ{val}{self.unit}")

    def freqGetRange(self) -> Optional[np.ndarray]:
        """get frequency range
        flushes buffer"""
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values(
                "OUTPLIML",
                separator=lambda x: x.splitlines(),
                converter=lambda x: [float(y.strip()) for y in x.split(",")],
                container=np.array,
            )
            return rv[:, 0]
        except (visa.VisaIOError, IndexError):
            return None

    def channel(self, val: int) -> None:
        """change channel"""
        self._bufferCommand(f"CHAN{val}")

    def continuous(self) -> None:
        """select continuous mode"""
        self._aglog.debug("Select continuous data read")
        self._bufferCommand(f"CONT")

    def hold(self) -> None:
        """select hold mode"""
        self._aglog.debug("Select data hold mode")
        self._bufferCommand(f"HOLD")

    def single(self) -> None:
        """do single measure"""
        self._aglog.debug("Single measure")
        self._bufferCommand(f"SING")

    def waitClean(self) -> None:
        """wait for clean sweep"""
        self._aglog.debug("Wait for clean measure")
        self._bufferCommand(f"WAIT")

    def restartMeasure(self) -> None:
        """restart measure"""
        self._bufferCommand(f"REST")

    def reflection(self) -> None:
        """measure reflection"""
        self._aglog.debug("Select reflection mode")
        self._bufferCommand(f"RFLP")

    def transmission(self) -> None:
        """measure transmission"""
        self._aglog.debug("Select transmission mode")
        self._bufferCommand(f"TRAP")

    def conversion(self, val: str) -> None:
        """convert data (1DS|OFF|YREF|YTRA|ZREF|ZTRA)"""
        self._bufferCommand(f"CONV{val}")

    def coupling(
        self, channel: Optional[bool] = None, power: Optional[bool] = None
    ) -> None:
        """control coupling"""
        if channel is not None:
            self._bufferCommand(f"COUC{'ON' if channel else 'OFF'}")
        if power is not None:
            self._bufferCommand(f"COUP{'ON' if power else 'OFF'}")

    def markerDeltaRef(self, n: int = 0) -> None:
        """select marker for delta measurements"""
        if n == 0:
            self._bufferCommand(f"DELO")
        else:
            self._bufferCommand(f"DELR{n}")

    def markerMeasureShow(self, val: bool) -> None:
        """show marker measures"""
        self._bufferCommand(f"DISM{'ON' if val else 'OFF'}")

    def markerSelect(self, n: int) -> None:
        """select marker (1-5)"""
        self._aglog.debug(f"Select marker {n}")
        self._bufferCommand(f"MARK{n}")

    def markerInterp(self, val: bool) -> None:
        """marker interpolation"""
        self._bufferCommand(f"MARK{'CONT' if val else 'DISC'}")

    def markerReadPos(self, n: int) -> Optional[float]:
        """read marker position
        This command flushes buffer"""
        self.markerSelect(n)
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values(f"MARK{n}?")[0]
            self._aglog.debug(f"Marker {n} position: {rv}")
            return rv
        except (visa.VisaIOError, IndexError):
            return None

    def markerRead(
        self, n: Optional[int] = None
    ) -> Optional[Dict[str, float]]:
        """read marker position
        This command flushes buffer"""
        if n is not None:
            self.markerSelect(n)
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values("OUTPMARK")
            output = {"val1": rv[0], "val2": rv[1], "f": rv[2]}
            return output
        except (visa.VisaIOError, IndexError):
            return None

    def markerCenter(self, n: Optional[int] = None) -> None:
        """set center frequency from marker value"""
        if n is not None:
            self.markerSelect(n)
        self._aglog.debug("Set center frequency to marker")
        self._bufferCommand(f"MARKCENT")

    def markerStart(self, n: Optional[int] = None) -> None:
        """set left frequency from marker value"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"MARKSTAR")

    def markerStop(self, n: Optional[int] = None) -> None:
        """set right frequency from marker value"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"MARKSTOP")

    def markerMax(self, n: Optional[int] = None) -> None:
        """set marker to maximum value"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"SEAMAX")  # MARKMAXI

    def markerMin(self, n: Optional[int] = None) -> None:
        """set marker to minimum value"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"SEAMIN")  # MARKMAXI

    def markerTarget(self, val: float, n: Optional[int] = None) -> None:
        """set marker to value"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"SEATARG{val}")

    def markerTargetLeft(self) -> None:
        """set marker to next occurrence of value to the left"""
        self._bufferCommand(f"SEAL")

    def markerTargetRight(self) -> None:
        """set marker to next occurrence of value to the right"""
        self._bufferCommand(f"SEAR")

    def markerTrack(self, val: bool) -> None:
        """marker tracking"""
        self._bufferCommand(f"TRACK{'ON' if val else 'OFF'}")

    def markerClear(self) -> None:
        """clear markers"""
        self._bufferCommand(f"MARKOFF")

    def markerSearchOff(self) -> None:
        """marker search off"""
        self._bufferCommand(f"SEAOFF")

    def markerSpan(self, n: Optional[int] = None) -> None:
        """set span to marker delta"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"MARKSPAN")

    def markerZero(self, n: Optional[int] = None) -> None:
        """set span to marker delta"""
        if n is not None:
            self.markerSelect(n)
        self._bufferCommand(f"MARKZERO")

    def markerPolType(self, val: str) -> None:
        """set marker type (POLMLIN|POLMLOG|POLMRI)"""
        self._bufferCommand(f"{val}")

    def markerSmithType(self, val: str) -> None:
        """set marker type (SMIMGB|SMILIN|SMILOG|SMIMRI|SMIMRX)"""
        self._bufferCommand(f"{val}")

    def searchWidth(self, val: bool = True) -> None:
        """search for bandwidth"""
        self._bufferCommand(f"WIDT{'ON' if val else 'OFF'}")

    def searchWidthVal(self, val: float) -> None:
        """search for bandwidth"""
        self._bufferCommand(f"WIDV{round(val, 3)}")

    def readWidth(self) -> Optional[Dict[str, float]]:
        """read bandwidth data
        This command flushes buffer"""
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values("OUTPMWIL")
            output = {
                "bandwidth": rv[0],
                "center": rv[1],
                "Q": rv[2],
                "loss": rv[3],
            }
            self._aglog.debug(f"Bandwidth data: {output}")
            return output
        except (visa.VisaIOError, IndexError):
            return None

    def smoothingOn(self, val: bool) -> None:
        """enable smoothing"""
        self._bufferCommand(f"SMOO{'ON' if val else 'OFF'}")

    def smoothing(self, val: float) -> None:
        """smoothing factor (0.05-20)"""
        self._bufferCommand(f"SMOOAPER{round(val, 2)}")

    def power(self, val: int) -> None:
        """set power (-20:5)"""
        self._bufferCommand(f"POWE{val}")

    def powerOn(self, val: bool) -> None:
        """enable power"""
        self._bufferCommand(f"POWT{'ON' if val else 'OFF'}")

    def revert(self) -> None:
        """revert to factory preset"""
        self._bufferCommand(f"PRES")

    def beep(self) -> None:
        """do a beep"""
        self._bufferCommand(f"EMIB")

    def dataForm(self, val: int = 3) -> None:
        """select data representation form"""
        if val == 2:
            self.__data_format = ">f4"
        elif val == 3:
            self.__data_format = ">f8"
        elif val == 4:
            self.__data_format = "ascii"
        else:
            self.__data_format = "???"
        self._bufferCommand(f"FORM{val}")

    def integBandw(self, val: int = 1000) -> None:
        """integration bandwidth (10|30|100|300|1000|3000|3700|6000)"""
        self._bufferCommand(f"IFBW{val}")

    def numPoints(self, val: int = 1601) -> None:
        """number of points (3|11|21|26|51|101|201|401|801|1601)"""
        self.__number_of_points = val
        self._aglog.debug(f"Set number of points to {val}")
        self._bufferCommand(f"POIN{val}")

    def numPointsUpdate(self) -> bool:
        """update internal number of points counter
        flushes buffer"""
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values("POIN?")[0]
            self.__number_of_points = rv
            self._aglog.debug(f"Number of points is {rv}")
            return True
        except (visa.VisaIOError, IndexError):
            return False

    def plotFormat(self, type: str) -> None:
        """plot type (REAL|IMAG|LINM|LOGM|PHAS|POLA|SMIC|SWR|DELA)"""
        self._bufferCommand(f"{type}")

    def phaseOffset(self, phase: int = 0) -> None:
        """set phase offset"""
        self._bufferCommand(f"PHAO{phase}")

    def keyPress(self, key: int) -> None:
        """emulate key press (1-69)"""
        self._bufferCommand(f"KEY{key}")

    def logSweep(self, val: bool) -> None:
        """log/linear sweep"""
        if val:
            self.__freq_log = True
            self._bufferCommand(f"LOGFREQ")
        else:
            self.__freq_log = False
            self._bufferCommand(f"LINFREQ")

    def measStat(self, val: bool) -> None:
        """show measure statistics"""
        self._bufferCommand(f"MEASTAT{'ON' if val else 'OFF'}")

    def readStat(self) -> Optional[Dict[str, float]]:
        """measure statistics
        This function flushes buffer"""
        self.sendBuffer()
        try:
            rv = self.__instrument.query_ascii_values("OUTPMSTA")
            output = {
                "mean": rv[0],
                "standard deviation": rv[1],
                "peak to peak": rv[2],
            }
            self._aglog.debug(f"Marker stats: {output}")
            return output
        except (visa.VisaIOError, IndexError):
            return None

    def readData(self, where: str = "FORM") -> Optional[np.ndarray]:
        """read data
        where: from where to read data (PRE|RAW<1-4>|DATA|FORM)
        This function flushes buffer"""
        self.sendBuffer()
        if self.__data_format == "ascii" or self.__data_format == "???":
            self._aglog.warn("Will only read binary data of FORM2 or FORM3")
            return None
        try:
            self.__instrument.write(f"OUTP{where}")
            if self.__instrument.read_bytes(2) != b"#A":
                return None
            nob = np.frombuffer(self.__instrument.read_bytes(2), dtype=">u2")
            rv = np.frombuffer(
                self.__instrument.read_bytes(int(nob)),
                dtype=self.__data_format,
            )
            data = rv.reshape((len(rv) // 2, 2))
            return data
        except visa.VisaIOError:
            return None
