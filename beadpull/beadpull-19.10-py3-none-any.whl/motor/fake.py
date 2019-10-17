"""Fake motor class."""
from typing import Dict, List
from time import sleep

from .generic import GenericMotor


class FakeMotor(GenericMotor):
    """fake motor method interfaces for BeadPull"""

    def __init__(self):
        self.connected = False

    def bpConnect(self, port: str, baudrate: int) -> bool:
        """connect to motor

        Arguments:
        port[str] -- motor serial port
        baudrate[int] -- serial baudrate

        Return value[bool] -- success/failure
        """
        self.connected = True
        return True

    def bpDisconnect(self) -> bool:
        """disconnect motor

        Return value[bool] -- success/failure
        """
        self.connected = False
        return True

    def bpIsConnected(self) -> bool:
        """check if motor is connected

        Return value[bool] -- connected/not connected
        """
        return self.connected

    def bpStatus(self) -> Dict[str, str]:
        """motor status

        Return value[Dict[str, str]] -- key-value pairs of motor status info"""
        return {"driver": "fake"}

    def bpListPorts(self) -> List[str]:
        """list possible motor ports"""
        return ["motor port"]

    def bpWait(self, timeout: int) -> bool:
        """wait for acknowledge signal from motor

        If motor has no acknowledge capability - just wait for
        specified amount of time

        Arguments:
        timeout[float] -- wait timeout in ms
        Return value[bool] -- success/timed out
        """
        sleep(timeout * 1000)
        return False
