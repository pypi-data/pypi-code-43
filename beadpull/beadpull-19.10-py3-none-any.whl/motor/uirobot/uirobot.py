import logging
import sys
from typing import Optional, Dict, Callable, Tuple, List, TypeVar, Generic
import visa
from . import convertbinary as cb


def _decodeACK(buf: bytes) -> Dict[str, str]:
    """Decode acknowledge byte"""
    return {
        "auto current reduction": str((buf[2] & (1 << 6)) != 0),
        "enabled": str((buf[2] & (1 << 5)) != 0),
        "direction": str(buf[2] & (1 << 4) != 0),
        "microsteps": str((buf[2] & 0b1111) + 1),
        "phase current": str(buf[3] & 0b111111),
        "desired velocity": str(cb.toi16(buf[4:7])),
        "desired position": str(cb.toi16(buf[7:12])),
    }


def ack_hdrchk(x: bytes) -> bool:
    return x[0:2] == b"\xaa\x00" and x[12] == 0xFF


Instrument = TypeVar("Instrument")


class UIRobot(Generic[Instrument]):
    """UIRobot motor driver class"""

    def __init__(self) -> None:
        self._uilog = logging.getLogger("uirobot")
        self.__rm = visa.ResourceManager()
        self.__buffer = ""
        self.__instrument: Optional[Instrument] = None

    def listPorts(self) -> List[str]:
        """List available serial ports"""
        return [x for x in self.__rm.list_resources() if "ASRL" in x][::-1]

    def connect(self, port: str, baudrate: int = 9600) -> bool:
        """Connect to instrument.
        port: name of instrument
        baudrate: communication baudrate. Defaults to 9600
        Output value: true for success, false for failure"""
        if self.__instrument is None:
            try:
                self.__instrument = self.__rm.get_instrument(port)
                self.__instrument.baud_rate = baudrate
                self.__instrument.read_termination = "\xff"
                self.__instrument.write_termination = ";"
                self._uilog.info(
                    f"""Connected to \
{port} with baudrate {baudrate}"""
                )
                return True
            except visa.VisaIOError:
                self._uilog.error(f"Cannot connect to {port}")
                return False
        else:
            self._uilog.warning("Already connected to instrument")
            return False

    def timeout(self, timeout: int) -> None:
        """Configure serial communication timeout.
        timeout: communication timeout."""
        if self.__instrument is not None:
            self.__instrument.timeout = timeout

    def disconnect(self) -> None:
        """Disconnect from port"""
        if self.__instrument is not None:
            self.__instrument.close()
            self.__instrument = None
            self._uilog.info("Connection closed")

    def _flushReadBuffer(self):
        """flush read buffer"""
        if (
            self.__instrument is not None
            and self.__instrument.bytes_in_buffer > 0
        ):  # flush buffer
            try:
                self.__instrument.read_raw(
                    size=self.__instrument.bytes_in_buffer
                )
            except visa.VisaIOError:
                pass

    def _sendCommand(
        self, command: str, chkhdr: Callable[[bytes], bool]
    ) -> Optional[bytes]:
        """send command, receive acknowledge"""
        self._flushReadBuffer()
        if self.__instrument is None:
            return None
        try:
            rv = self.__instrument.query_binary_values(
                command, header_fmt="empty", delay=0.1, datatype="s"
            )[0]
        except visa.VisaIOError:
            return None
        try:
            if not chkhdr(rv):
                self._uilog.warning("Wrong return message header")
                return None
            else:
                return rv
        except:
            e = sys.exc_info()[0]
            self._uilog.error(f"Header check function error: {e}")
            return None

    def _bufferCommand(self, command: str) -> None:
        """add command to buffer to send later"""
        self._uilog.debug(f"Adding {command} to buffer")
        self.__buffer = self.__buffer + command + ";"

    def _bufferSend(self, chkhdr: Callable[[bytes], bool]) -> Optional[bytes]:
        """send buffer"""
        if self.__buffer == "":
            return None
        rv = self._sendCommand("{" + f"{self.__buffer}" + "}", chkhdr)
        self.__buffer = ""
        return rv

    def sendBuffer(self) -> Optional[Dict[str, str]]:
        """send buffer, check acknowledge"""
        rv = self._bufferSend(ack_hdrchk)
        if rv is None:
            return None
        else:
            status = _decodeACK(rv)
            self._uilog.debug(f"Motor status: {status}")
            return status

    def model(self) -> Optional[Dict[str, str]]:
        """Get motor controller model"""
        rv = self._sendCommand(
            "MDL", lambda x: x[0:3] == b"\xcc\x00\xde" and x[10] == 0xFF
        )
        if rv is None:
            return None
        else:
            status = {
                "maximum current": str(rv[5]),
                "quadrature encoder": str((rv[6] & (1 << 6)) != 0),
                "closed loop": str((rv[6] & (1 << 5)) != 0),
                "advanced motion": str((rv[6] & (1 << 4)) != 0),
                "number of sensors": str(rv[6] & 0b1111),
                "firmware version": str(cb.toi16(rv[7:10])),
            }
            self._uilog.debug(f"Motor model data: {status}")
            return status

    def statusDesired(self) -> Optional[Dict[str, str]]:
        """Read desired motor status"""
        self._flushReadBuffer()
        rv = self._sendCommand("", ack_hdrchk)
        if rv is None:
            return None
        else:
            status = _decodeACK(rv)
            self._uilog.debug(f"Desired motor status: {status}")
            return status

    def statusCurrent(self) -> Optional[Dict[str, str]]:
        """Read desired motor status"""
        self._flushReadBuffer()
        rv = self._sendCommand(
            "FBK", lambda x: x[0:2] == b"\xcc\x00" and x[12] == 0xFF
        )
        if rv is None:
            return None
        else:
            status = {
                "auto current reduction": str((rv[2] & (1 << 6)) != 0),
                "enabled": str((rv[2] & (1 << 5)) != 0),
                "direction": str(rv[2] & (1 << 4) != 0),
                "microsteps": str((rv[2] & 0b1111) + 1),
                "phase current": str(rv[3] & 0b111111),
                "current velocity": str(cb.toi16(rv[4:7])),
                "current position": str(cb.toi16(rv[7:12])),
            }
            self._uilog.debug(f"Desired motor status: {status}")
            return status

    def enable(self) -> None:
        """Enable motor H-bridge"""
        self._bufferCommand("ENA")

    def disable(self) -> None:
        """disable motor H-bridge"""
        self._bufferCommand("OFF")

    def current(self, cur: float) -> None:
        """set supply current in amperes"""
        cur_int = int(round(cur * 10, 0))
        self._bufferCommand(f"CUR={cur_int}")

    def autoCurrentReduction(self, val: bool):
        """control automatic current reduction feature"""
        self._bufferCommand(f"ACR={int(val)}")

    def direction(self, val: bool):
        """set movement direction"""
        self._bufferCommand(f"DIR={int(val)}")

    def setBaudRate(self, baudrate: int = 57600) -> bool:
        """set rs232 baudrate (max 57600)"""
        self._flushReadBuffer()
        rv = self._sendCommand(
            f"BDR={int(baudrate)}",
            lambda x: x[0] == b"\xaa" and x[2:4] == b"\xbf\xff",
        )
        if rv is None:
            return False
        else:
            return True

    def configureMCR(
        self,
        adv_mode: bool = True,
        acc_per: bool = True,
        dec_per: bool = True,
        done_notify: bool = True,
        orig_notify: bool = False,
    ) -> Optional[Dict[str, str]]:
        """Configure Master control register"""
        msg = (
            (int(adv_mode) << 10)
            | (int(acc_per) << 9)
            | (int(dec_per) << 8)
            | (int(orig_notify) << 5)
            | (int(done_notify) << 4)
        )
        self._flushReadBuffer()
        rv = self._sendCommand(
            f"MCF={msg}", lambda x: x[0:3] == b"\xaa\x00\xb0" and x[6] == 0xFF
        )
        if rv is None:
            return None
        else:
            sv = cb.toi16(rv[3:6])
            status = {
                "enable analog input": str(sv & (1 << 15) != 0),
                "analog input channel": str(int(sv & (1 << 14) != 0)),
                "enable quad encoder": str(sv & (1 << 13) != 0),
                "enable quad encoder closed loop": str(sv & (1 << 11) != 0),
                "advanced motion control": str(sv & (1 << 10) != 0),
                "acceleration mode": str(int(sv & (1 << 9) != 0)),
                "deceleration mode": str(int(sv & (1 << 8) != 0)),
                "origin notify": str(sv & (1 << 5) != 0),
                "done notify": str(sv & (1 << 4) != 0),
                "S2 notify": str(sv & (1 << 1) != 0),
                "S1 notify": str(sv & (1 << 0) != 0),
            }
            self._uilog.debug(f"MCR value: {status}")
            return status

    def configureMicroStep(self, resolution: int):
        """set microstep size (0-4)"""
        self._bufferCommand(f"MCS={2**resolution}")

    def backlash(self, val: Optional[int] = None) -> Optional[int]:
        """get/set backlash compensation value (0-65535)"""
        msg = f"BLC={val}" if val is not None else "BLC"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg, lambda x: x[0:3] == b"\xaa\x00\xde" and x[6] == 0xFF
        )
        if rv is None:
            return None
        else:
            status = cb.toi16(rv[3:6])
            self._uilog.debug(f"Backlash value: {status}")
            return status

    def acceleration(
        self, val: Optional[int] = None
    ) -> Optional[Tuple[bool, int]]:
        """get/set acceleration value"""
        msg = f"MAC={val}" if val is not None else "MAC"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg, lambda x: x[0:3] == b"\xaa\x00\xb1" and x[9] == 0xFF
        )
        if rv is None:
            return None
        else:
            acc_type = rv[3] != 0
            acc_val = cb.toi32(rv[4:9])
            self._uilog.debug(
                f"""Acceleration type: {acc_type} \
value: {acc_val}"""
            )
            return acc_type, acc_val

    def deceleration(
        self, val: Optional[int] = None
    ) -> Optional[Tuple[bool, int]]:
        """get/set deceleration value"""
        msg = f"MDE={val}" if val is not None else "MDE"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg, lambda x: x[0:3] == b"\xaa\x00\xb2" and x[9] == 0xFF
        )
        if rv is None:
            return None
        else:
            acc_type = rv[3] != 0
            acc_val = cb.toi32(rv[4:9])
            self._uilog.debug(
                f"Deceleration type: {acc_type} value: {acc_val}"
            )
            return acc_type, acc_val

    def speedCes(self, val: Optional[int] = None) -> Optional[int]:
        """get/set cessation speed"""
        msg = f"MMD={val}" if val is not None else "MMD"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg, lambda x: x[0:3] == b"\xaa\x00\xb4" and x[6] == 0xFF
        )
        if rv is None:
            return None
        else:
            val = cb.toi16(rv[3:6])
            self._uilog.debug(f"Maximum cessation speed: {val}")
            return val

    def speedStart(self, val: Optional[int] = None) -> Optional[int]:
        """get/set start speed"""
        msg = f"MMS={val}" if val is not None else "MMS"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg, lambda x: x[0:3] == b"\xaa\x00\xb3" and x[6] == 0xFF
        )
        if rv is None:
            return None
        else:
            val = cb.toi16(rv[3:6])
            self._uilog.debug(f"Maximum starting speed: {val}")
            return val

    def origin(self, val: int = 0) -> Optional[int]:
        """set origin"""
        self._flushReadBuffer()
        rv = self._sendCommand(
            f"ORG={val}",
            lambda x: (x[0] == 0xAA or x[0] == 0xCC)
            and x[1] == 0
            and (x[2] == 0xB7 or x[2] == 0xB0)
            and x[8] == 0xFF,
        )
        if rv is None:
            return None
        else:
            val = cb.toi32(rv[3:8])
            self._uilog.debug(f"Origin position: {val}")
            return val

    def position(self, val: Optional[int] = None) -> Optional[int]:
        """get/set position"""
        msg = f"POS={val}" if val is not None else "POS"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg,
            lambda x: (x[0] == 0xAA or x[0] == 0xCC)
            and x[1] == 0
            and (x[2] == 0xB7 or x[2] == 0xB0)
            and x[8] == 0xFF,
        )
        if rv is None:
            return None
        else:
            val = cb.toi32(rv[3:8])
            self._uilog.debug(f"Position: {val}")
            return val

    def speed(self, val: Optional[int] = None) -> Optional[int]:
        """get/set desired speed"""
        msg = f"SPD={val}" if val is not None else "SPD"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg,
            lambda x: (x[0] == 0xAA or x[0] == 0xCC)
            and x[1] == 0
            and (x[2] == 0xB5 or x[2] == 0xB2)
            and x[6] == 0xFF,
        )
        if rv is None:
            return None
        else:
            val = cb.toi16(rv[3:6])
            self._uilog.debug(f"Speed: {val}")
            return val

    def step(self, val: Optional[int] = None) -> Optional[int]:
        """get/set incremental displacement"""
        msg = f"STP={val}" if val is not None else "STP"
        self._flushReadBuffer()
        rv = self._sendCommand(
            msg,
            lambda x: (x[0] == 0xAA or x[0] == 0xCC)
            and x[1] == 0
            and (x[2] == 0xB3 or x[2] == 0xB6)
            and x[8] == 0xFF,
        )
        if rv is None:
            return None
        else:
            val = cb.toi16(rv[3:8])
            self._uilog.debug(f"Displacement: {val}")
            return val

    def gotoPosition(self, pos: int, spd: int) -> None:
        """goto position with speed"""
        self._flushReadBuffer()
        self._sendCommand("{" + f"POS={pos};SPD={spd};" + "}", ack_hdrchk)

    def goForward(self, len: int, spd: int) -> None:
        """go forward with speed"""
        self._flushReadBuffer()
        self._sendCommand("{" + f"STP={len};SPD={spd};" + "}", ack_hdrchk)

    def wait_done(self, timeout: float = 1) -> bool:
        """wait for movement completion"""
        if self.__instrument is None:
            return False
        old_timeout = self.__instrument.timeout
        self.__instrument.timeout = timeout
        try:
            rv = self.__instrument.read_binary_values(
                header_fmt="empty", datatype="s"
            )[0]
        except visa.VisaIOError:
            return False
        self.__instrument.timeout = old_timeout
        if rv == b"\xcc\x00\xa8\xff":
            return True
        else:
            return False
