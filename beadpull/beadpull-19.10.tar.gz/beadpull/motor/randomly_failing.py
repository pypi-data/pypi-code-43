"""Randomly failing motor class. It is intended for testing."""
from typing import Dict, List
from random import randint

from .fake import FakeMotor


def random(per: int = 30) -> bool:
    return randint(0, 100) > per


class RandomlyFailingMotor(FakeMotor):
    """randomly failing motor for BeadPull"""

    def __init__(self):
        super(RandomlyFailingMotor, self).__init__()

    def bpConnect(self, port: str, baudrate: int) -> bool:
        """connect to motor

        Arguments:
        port[str] -- motor serial port
        baudrate[int] -- serial baudrate

        Return value[bool] -- success/failure
        """
        if random():
            self.connected = True
            return True
        else:
            return False

    def bpDisconnect(self) -> bool:
        """disconnect motor

        Return value[bool] -- success/failure
        """
        if random():
            self.connected = False
            return True
        else:
            return False

    def bpListPorts(self) -> List[str]:
        """list possible motor ports"""
        return ["ports"] if random() else []

    def bpInit(self) -> bool:
        """initialize motor

        Return value[bool] -- success/failure
        """
        return random(5)

    def bpDeinit(self) -> bool:
        """deinitialize motor

        Return value[bool] -- success/failure
        """
        return random(5)

    def bpStatus(self) -> Dict[str, str]:
        """motor status

        Return value[Dict[str, str]] -- key-value pairs of motor status info
        """
        return {"driver": "randomly failing"}

    def bpIsMoving(self) -> bool:
        """check if motor is moving

        Return value[bool] -- moving/not moving
        """
        return random()

    def bpHold(self) -> bool:
        """set motor to hold

        Return value[bool] -- success/failure
        """
        return random()

    def bpRelease(self) -> bool:
        """release motor

        Return value[bool] -- success/failure
        """
        return random()

    def bpStop(self) -> bool:
        """stop motion and clear motion commands

        Return value[bool] -- success/failure
        """
        return random()

    def bpMoveSpeed(self, spd: float) -> bool:
        """set motor move speed

        Arguments:
        spd[float] -- motor speed in mm/s
        Return value[bool] -- success/failure
        """
        return random(5)

    def bpReturnSpeed(self, spd: float) -> bool:
        """set motor return to origin speed

        Arguments:
        spd[float] -- motor speed in mm/s
        Return value[bool] -- success/failure
        """
        return random(5)

    def bpPreMoveHook(self) -> bool:
        """function to call before movement

        Return value[bool] -- success/failure. If False is returned,
        motor will not move
        """
        return random()

    def bpPreReturnHook(self) -> bool:
        """function to call before return to origin

        Return value[bool] -- success/failure. If False is returned,
        motor will not move
        """
        return random()

    def bpDirection(self, val: bool) -> bool:
        """change movement direction

        Arguments:
        val[bool] -- direction
        Return value[bool] -- success/failure
        """
        return random()

    def bpOrigin(self) -> bool:
        """set origin to current position

        Return value[bool] -- success/failure
        """
        return random()

    def bpStep(self, leng: float) -> bool:
        """make a step

        This function needs to be asynchronous in order for
        bpStop to work

        Arguments:
        leng[float] -- step length in mm
        Return value[bool] -- success/failure
        """
        return random()

    def bpGotoPosition(self, pos: float) -> bool:
        """go to position

        This function needs to be asynchronous in order for
        bpStop to work

        Arguments:
        pos[float] -- desired position in mm
        Return value[bool] -- success/failure
        """
        return random()

    def bpReturn(self) -> bool:
        """return to origin

        This function needs to be asynchronous in order for
        bpStop to work

        Return value[bool] -- success/failure
        """
        return random()

    def bpAcceleration(self, acc: float) -> bool:
        """set motor acceleration period

        Arguments:
        acc[float] -- desired acceleration period
        Return value[bool] -- success/failure
        """
        return random(5)

    def bpDeceleration(self, dec: float) -> bool:
        """set motor deceleration period

        Arguments:
        acc[float] -- desired deceleration period
        Return value[bool] -- success/failure
        """
        return random(5)

    def bpWait(self, timeout: int) -> bool:
        """wait for acknowledge signal from motor

        If motor has no acknowledge capability - just wait for
        specified amount of time

        Arguments:
        timeout[float] -- wait timeout in ms
        Return value[bool] -- success/timed out
        """
        return random()

    def bpCalibratePreset(self, val: float) -> bool:
        """calibrate motor - set saved calibration ratio

        Arguments:
        val[float] -- unit/mm ratio
        Return value[bool] -- success/failure
        """
        return random()

    def bpCalibrateVal(self, leng: int) -> bool:
        """calibrate motor - set step length

        Step one of three-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).

        Arguments:
        leng[int] -- number of steps in motor units
        Return value[bool] -- success/failure
        """
        return random()

    def bpCalibrateStep(self) -> bool:
        """calibrate motor - make a step

        Step two of two-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).
        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure
        """
        return random()

    def bpCalibrateOrigin(self) -> bool:
        """return to origin in calibrate mode

        At this point motor is uncalibrated. Return with some preset speed.
        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure"""
        return random()
