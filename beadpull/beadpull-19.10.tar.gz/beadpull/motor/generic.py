"""Generic motor class. This class contains method interfaces needed
for BeadPull.
In order to add support for another motor, create a subclass of GenericMotor
class and implement methods. It's OK leave some of them unimplemented.
Watch out for method data types."""
from typing import Dict, List


class GenericMotor:
    """motor method interfaces for BeadPull"""

    def bpConnect(self, port: str, baudrate: int) -> bool:
        """connect to motor

        Arguments:
        port[str] -- motor serial port
        baudrate[int] -- serial baudrate

        Return value[bool] -- success/failure
        """
        return True

    def bpDisconnect(self) -> bool:
        """disconnect motor

        Return value[bool] -- success/failure
        """
        return True

    def bpListPorts(self) -> List[str]:
        """list possible motor ports"""
        return []

    def bpInit(self) -> bool:
        """initialize motor

        Return value[bool] -- success/failure
        """
        return True

    def bpDeinit(self) -> bool:
        """deinitialize motor

        Return value[bool] -- success/failure
        """
        return True

    def bpStatus(self) -> Dict[str, str]:
        """motor status

        Return value[Dict[str, str]] -- key-value pairs of motor status info
        """
        return {"": ""}

    def bpIsMoving(self) -> bool:
        """check if motor is moving

        Return value[bool] -- moving/not moving
        """
        return False

    def bpHold(self) -> bool:
        """set motor to hold

        Return value[bool] -- success/failure
        """
        return True

    def bpRelease(self) -> bool:
        """release motor

        Return value[bool] -- success/failure
        """
        return True

    def bpStop(self) -> bool:
        """stop motion and clear motion commands

        Return value[bool] -- success/failure
        """
        return True

    def bpMoveSpeed(self, spd: float) -> bool:
        """set motor move speed

        Arguments:
        spd[float] -- motor speed in mm/s
        Return value[bool] -- success/failure
        """
        return True

    def bpReturnSpeed(self, spd: float) -> bool:
        """set motor return to origin speed

        Arguments:
        spd[float] -- motor speed in mm/s
        Return value[bool] -- success/failure
        """
        return True

    def bpPreMoveHook(self) -> bool:
        """function to call before movement

        Return value[bool] -- success/failure. If False is returned,
        motor will not move
        """
        return True

    def bpPostMoveHook(self) -> None:
        """function to call after movement"""
        pass

    def bpPreReturnHook(self) -> bool:
        """function to call before return to origin

        Return value[bool] -- success/failure. If False is returned,
        motor will not move
        """
        return True

    def bpPostReturnHook(self) -> None:
        """function to call after return to origin"""
        pass

    def bpDirection(self, val: bool) -> bool:
        """change movement direction

        Arguments:
        val[bool] -- direction
        Return value[bool] -- success/failure
        """
        return True

    def bpOrigin(self) -> bool:
        """set origin to current position

        Return value[bool] -- success/failure
        """
        return True

    def bpIsConnected(self) -> bool:
        """check if motor is connected

        Return value[bool] -- connected/not connected
        """
        return True

    def bpStep(self, leng: float) -> bool:
        """make a step

        This function needs to be asynchronous in order for
        bpStop to work

        Arguments:
        leng[float] -- step length in mm
        Return value[bool] -- success/failure
        """
        return True

    def bpGotoPosition(self, pos: float) -> bool:
        """go to position

        This function needs to be asynchronous in order for
        bpStop to work

        Arguments:
        pos[float] -- desired position in mm
        Return value[bool] -- success/failure
        """
        return True

    def bpReturn(self) -> bool:
        """return to origin

        This function needs to be asynchronous in order for
        bpStop to work

        Return value[bool] -- success/failure
        """
        return True

    def bpAcceleration(self, acc: float) -> bool:
        """set motor acceleration period

        Arguments:
        acc[float] -- desired acceleration period
        Return value[bool] -- success/failure
        """
        return True

    def bpDeceleration(self, dec: float) -> bool:
        """set motor deceleration period

        Arguments:
        acc[float] -- desired deceleration period
        Return value[bool] -- success/failure
        """
        return True

    def bpWait(self, timeout: int) -> bool:
        """wait for acknowledge signal from motor

        If motor has no acknowledge capability - just wait for
        specified amount of time

        Arguments:
        timeout[float] -- wait timeout in ms
        Return value[bool] -- success/timed out
        """
        return True

    def bpCalibratePreset(self, val: float) -> bool:
        """calibrate motor - set saved calibration ratio

        Arguments:
        val[float] -- unit/mm ratio
        Return value[bool] -- success/failure
        """
        return True

    def bpCalibrateVal(self, leng: int) -> bool:
        """calibrate motor - set step length

        Step one of three-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).

        Arguments:
        leng[int] -- number of steps in motor units
        Return value[bool] -- success/failure
        """
        return True

    def bpCalibrateStep(self) -> bool:
        """calibrate motor - make a step

        Step two of two-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).
        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure
        """
        return True

    def bpCalibrateSet(self, leng: float) -> float:
        """calibrate motor - Set measured length of leng in step one.
        Calculate unit/mm relation

        Step three of two-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).

        Arguments:
        leng[float] -- measured step length in mm
        Return value[float] -- calculated unit/mm ratio
        """
        return 0

    def bpCalibrateOrigin(self) -> bool:
        """return to origin in calibrate mode

        At this point motor is uncalibrated. Return with some preset speed.
        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure"""
        return True
