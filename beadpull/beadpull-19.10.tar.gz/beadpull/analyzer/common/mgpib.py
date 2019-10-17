import gpib
import logging
from time import sleep
from typing import Optional, Dict

gpib_time = {
    1000: gpib.T1000s,
    300: gpib.T300s,
    100: gpib.T100s,
    30: gpib.T30s,
    10: gpib.T10s,
    3: gpib.T3s,
    1: gpib.T1s,
    0.3: gpib.T300ms,
    0.1: gpib.T100ms,
    0.03: gpib.T30ms,
    0.01: gpib.T10ms,
    0.003: gpib.T3ms,
    0.001: gpib.T1ms,
    0.0003: gpib.T300us,
    0.0001: gpib.T100us,
    0.00003: gpib.T30us,
    0.00001: gpib.T10us,
    0: gpib.TNONE,
}

gpib_settingsA = {
    "7BitEOS": gpib.Iba7BitEOS,
    "AUTOPOLL": gpib.IbaAUTOPOLL,
    "BNA": gpib.IbaBNA,
    "CICPROT": gpib.IbaCICPROT,
    "EOSchar": gpib.IbaEOSchar,
    "EOScmp": gpib.IbaEOScmp,
    "EOSrd": gpib.IbaEOSrd,
    "EOSwrt": gpib.IbaEOSwrt,
    "EOT": gpib.IbaEOT,
    "EndBitIsNormal": gpib.IbaEndBitIsNormal,
    "EventQueue": gpib.IbaEventQueue,
    "HSCableLength": gpib.IbaHSCableLength,
    "Ist": gpib.IbaIst,
    "PAD": gpib.IbaPAD,
    "PP2": gpib.IbaPP2,
    "PPC": gpib.IbaPPC,
    "PPollTime": gpib.IbaPPollTime,
    "READDR": gpib.IbaREADDR,
    "ReadAdjust": gpib.IbaReadAdjust,
    "Rsv": gpib.IbaRsv,
    "SAD": gpib.IbaSAD,
    "SC": gpib.IbaSC,
    "SPollBit": gpib.IbaSPollBit,
    "SPollTime": gpib.IbaSPollTime,
    "SRE": gpib.IbaSRE,
    "SendLLO": gpib.IbaSendLLO,
    "TIMING": gpib.IbaTIMING,
    "TMO": gpib.IbaTMO,
    "UnAddr": gpib.IbaUnAddr,
    "WriteAdjust": gpib.IbaWriteAdjust,
}

gpib_settingsC = {
    "AUTOPOLL": gpib.IbcAUTOPOLL,
    "BNA": gpib.IbcBNA,
    "CICPROT": gpib.IbcCICPROT,
    "EOSchar": gpib.IbcEOSchar,
    "EOScmp": gpib.IbcEOScmp,
    "EOSrd": gpib.IbcEOSrd,
    "EOSwrt": gpib.IbcEOSwrt,
    "EOT": gpib.IbcEOT,
    "EndBitIsNormal": gpib.IbcEndBitIsNormal,
    "EventQueue": gpib.IbcEventQueue,
    "HSCableLength": gpib.IbcHSCableLength,
    "Ist": gpib.IbcIst,
    "PAD": gpib.IbcPAD,
    "PP2": gpib.IbcPP2,
    "PPC": gpib.IbcPPC,
    "PPollTime": gpib.IbcPPollTime,
    "READDR": gpib.IbcREADDR,
    "ReadAdjust": gpib.IbcReadAdjust,
    "Rsv": gpib.IbcRsv,
    "SAD": gpib.IbcSAD,
    "SC": gpib.IbcSC,
    "SPollBit": gpib.IbcSPollBit,
    "SPollTime": gpib.IbcSPollTime,
    "SRE": gpib.IbcSRE,
    "SendLLO": gpib.IbcSendLLO,
    "TIMING": gpib.IbcTIMING,
    "TMO": gpib.IbcTMO,
    "UnAddr": gpib.IbcUnAddr,
    "WriteAdjust": gpib.IbcWriteAdjust,
}


class MGpib:
    """Wrapper for gpib library"""

    Time_READ = 0.1  # time to wait for data in seconds

    def __init__(self) -> None:
        self.__mglog = logging.getLogger("gpib")
        self.__device = None
        self.__devname = ""
        self.__buffer = ""  # send message buffer

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    def configure(self, name: str) -> None:
        """Select GPIB device
        name: name of device"""
        self.__devname = name
        self.__mglog.info(f"Device name set to {name}")

    def timeout(self, time: float) -> bool:
        """Configure gpib device timeout.
        timeout: communication timeout."""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                gpib.timeout(self.__device, gpib_time[time])
                self.__mglog.warn(
                    f"Device {self.__devname} timeout set to {time}"
                )
                return True
            except (gpib.GpibError, KeyError) as e:
                self.__mglog.warn(
                    f"Cannot set device {self.__devname} timeout: {e}"
                )
                return False

    def clear(self) -> bool:
        """clear device."""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                gpib.clear(self.__device)
                self.__mglog.warn(f"Device {self.__devname} cleared")
                return True
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot clear device {self.__devname}")
                return False

    def connect(self) -> bool:
        """Connect to device.
        Output value: true for success, false for failure"""
        if self.__device is not None:
            self.__mglog.warn(f"Already connected to {self.__devname}")
            return False
        else:
            try:
                self.__device = gpib.find(self.__devname)
                self.__mglog.info(f"Connected to {self.__devname}")
                return True
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot connect to {self.__devname}")
                return False

    def connected(self) -> bool:
        """check if connected"""
        return self.__device is not None

    def disconnect(self) -> bool:
        """Disconnect from port"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                gpib.close(self.__device)
                self.__device = None
                return True
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot disconnect from {self.__devname}")
                return False

    def send_string(self, msg: str) -> bool:
        """Write string to device
        str: data string"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                msg = "OPC?;" + msg
                gpib.write(self.__device, msg.encode())
                self.__mglog.debug(
                    f"Sent string {msg} to device {self.__devname}"
                )
                return True
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot write to device {self.__devname}")
                return False

    def buffer_string(self, msg: str) -> None:
        """Write string to buffer to send later
        str: data string"""
        self.__buffer = self.__buffer + msg

    def send_buffer(self) -> bool:
        """Send buffer to device"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        if self.__buffer == "":
            self.__mglog.info("Buffer is empty")
            return True
        try:
            self.__buffer = "OPC?;" + self.__buffer
            gpib.write(self.__device, self.__buffer.encode())
            self.__mglog.debug(
                f"Sent string {self.__buffer} to device {self.__devname}"
            )
            self.__buffer = ""
            return True
        except gpib.GpibError:
            self.__mglog.warn(f"Cannot write to device {self.__devname}")
            return False

    def trigger(self) -> bool:
        """trigger device"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                gpib.trigger(self.__device)
                self.__mglog.debug(f"Triggered device {self.__devname}")
                return True
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot trigger device {self.__devname}")
                return False

    def get_settings(self) -> Optional[Dict[str, str]]:
        """get device settings"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return None
        else:
            output = {}
            for i, j in gpib_settingsA.items():
                try:
                    output[i] = gpib.ask(self.__device, j)
                except gpib.GpibError:
                    self.__mglog.warn(
                        f"Cannot get device {self.__devname} property {i}"
                    )
            self.__mglog.debug(f"Device {self.__devname} settings: {output}")
            return output

    def set_setting(self, name: str, val: int) -> bool:
        """set device settings
        name: name of settings
        val: value of setting"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                gpib.config(self.__device, gpib_settingsC[name], val)
                self.__mglog.debug(
                    f"Set device {self.__devname} setting {name} to {val}"
                )
                return True
            except (gpib.GpibError, KeyError) as e:
                self.__mglog.warn(
                    f"Cannot set device {self.__devname} property: {e}"
                )
                return False

    def byte_count(self) -> int:
        """get number of transferred bytes"""
        n = gpib.ibcnt()
        self.__mglog.debug(f"Transferred {n} bytes")
        return n

    def status(self) -> int:
        """get status"""
        n = gpib.ibsta()
        self.__mglog.debug(f"Status: {n}")
        return n

    def release(self) -> bool:
        """push device to local mode"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return False
        else:
            try:
                gpib.ibloc(self.__device)
                self.__mglog.debug(
                    f"Device {self.__devname} sent to local mode"
                )
                return True
            except gpib.GpibError:
                self.__mglog.warn(
                    f"Cannot send device {self.__devname} to local mode"
                )
                return False

    def recieve_bytes(
        self, n: int = 8448, validate: bool = False
    ) -> Optional[bytes]:
        """Get n bytes from port
        n: number of bytes to read
        validate: validate status byte or not
        Output value: string of read bytes"""
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return None
        else:
            try:
                if validate:
                    rv = gpib.serial_poll(self.__device)
                    if rv & (1 << 4) == 0:
                        self.__mglog.debug(
                            f"Nothing to read from device {self.__devname}"
                        )
                        return None
                output = gpib.read(self.__device, n)
                self.__mglog.debug(
                    f"""Read {n} bytes from device {self.__devname}: \
{output if len(output) < 15 else output[0:16] + b'...'}"""
                )
                return output
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot read from device {self.__devname}")
                return None

    def wait_recieve(
        self, n: int = 8448, time: float = 0, frac: int = 10
    ) -> Optional[bytes]:
        """Try to read all bytes from port for period of time (every time/frac)
        n: number of bytes
        time: time to wait for the data
        Output value: string of read bytes"""
        time_inc = time / frac if time != 0 else self.Time_READ / frac
        if self.__device is None:
            self.__mglog.warn("Not connected to device")
            return None
        else:
            try:
                while True:
                    rv = gpib.serial_poll(self.__device)
                    if rv & (1 << 4) != 0:
                        return self.recieve_bytes(n)
                    else:
                        if time <= 0:
                            self.__mglog.debug("Serial read none available")
                            return None
                        else:
                            time = time - time_inc
                            sleep(time_inc)
            except gpib.GpibError:
                self.__mglog.warn(f"Cannot read from device {self.__devname}")
                return None
