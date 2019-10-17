import serial
from serial.tools.list_ports import comports
import logging
from time import sleep
from typing import List, Optional


class MSerial:
    """Wrapper for serial library"""

    TIME_READ = 0.1  # time to wait for data in seconds

    def __init__(self) -> None:
        self.__mserlog = logging.getLogger("serial")
        self.__serial = serial.Serial()
        self.__serial.timeout = 100

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()

    def list_ports(self) -> List[str]:
        """list ports"""
        return [x.device for x in comports()]

    def configure(
        self, port: Optional[str] = None, baudrate: int = None
    ) -> None:
        """Configure serial port
        port: name of port. Defaults to None
        baudrate: communication baudrate. Defaults to 9600"""
        if port is not None:
            self.__serial.port = port
        if baudrate is not None:
            self.__serial.baudrate = baudrate

    def timeout(self, time: Optional[int]) -> None:
        """Configure serial communication timeout.
        timeout: communication timeout.
See pyserial documentation for details"""
        self.__serial.timeout = time

    def connect(self) -> bool:
        """Connect to configured port.
        Output value: true for success, false for failure"""
        if not self.__serial.is_open:
            try:
                self.__serial.open()
                self.__mserlog.info(
                    f"""Serial open: opened port \
{self.__serial.port} with baudrate {self.__serial.baudrate}"""
                )
                sleep(0.1)
                return True
            except serial.SerialException as e:
                self.__mserlog.error(f"Serial open: {e}")
                return False
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is already opened"
            )
            return False

    def disconnect(self) -> None:
        """Disconnect from port"""
        if self.__serial.is_open:
            self.__serial.close()
            self.__mserlog.info(f"Serial port {self.__serial.port} closed")
        # else:
        #     self.__mserlog.warning(
        #         f"Serial port {self.__serial.port} is not opened"
        #     )

    def send_string(self, msg: str) -> None:
        """Write string to port
        str: data string"""
        if self.__serial.is_open:
            self.__serial.write(msg.encode())
            self.__mserlog.debug(f"Serial write: {msg}")
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )

    def send_newline(self) -> None:
        """Send string newline to port"""
        if self.__serial.is_open:
            self.__serial.write(b"\n\r")
            self.__serial.flush()
            self.__mserlog.debug("Serial write: \\n\\r")
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )

    def send_bytes(self, msg: bytes) -> None:
        """Send bytes to port
        msg: array of data to sent"""
        if self.__serial.is_open:
            self.__serial.write(bytes(msg))
            self.__serial.flush()
            self.__mserlog.debug(f"Serial write {len(msg)} bytes")
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )

    def send_confirm(
        self, msg: bytes, rv: List[bytes]
    ) -> Optional[List[bool]]:
        """Send bytes to port and compare recieved value with expected
        msg: array of data to sent
        rv: array of expected return values
        Output value: array of bools, indicating match or miss"""
        if self.__serial.is_open:
            compared = []
            for i in range(0, len(msg)):
                self.__serial.write(bytes([msg[i]]))
                self.__serial.flush()
                ans = self.wait_recieve(self.TIME_READ)
                if ans is not None:
                    ansb: bool = ans == rv[i]
                    compared.append(ansb)
                else:
                    compared.append(False)
            return compared
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )
            return None

    def recieve_bytes(self, n: int) -> Optional[bytes]:
        """Get n bytes from port
        n: number of bytes to read
        Output value: string of read bytes"""
        if self.__serial.is_open:
            self.__mserlog.debug(f"Serial read <= {n} bytes")
            return self.__serial.read(n)
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )
            return None

    def recieve_all(self) -> Optional[bytes]:
        """Get all avaliable bytes from port
        Output value: string of read bytes"""
        if self.__serial.is_open:
            n = self.__serial.in_waiting
            if n > 0:
                self.__mserlog.debug(f"Serial read {n} bytes")
                return self.__serial.read(self.__serial.in_waiting)
            else:
                self.__mserlog.debug("Serial read none avaliable")
                return None
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )
            return None

    def wait_recieve(self, time: float = 0, frac: int = 10) -> Optional[bytes]:
        """Try to read all bytes from port for period of time (every time/frac)
        time: time to wait for the data
        Output value: string of read bytes"""
        time_inc = time / frac if time != 0 else self.TIME_READ / frac
        if self.__serial.is_open:
            while True:
                n = self.__serial.in_waiting
                if n > 0:
                    return self.recieve_all()
                else:
                    if time <= 0:
                        self.__mserlog.debug("Serial read none available")
                        return None
                    else:
                        time = time - time_inc
                        sleep(time_inc)
        else:
            self.__mserlog.warning(
                f"Serial port {self.__serial.port} is not opened"
            )
            return None
