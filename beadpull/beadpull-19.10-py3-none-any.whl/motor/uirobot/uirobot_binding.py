import yaml
from os.path import dirname, join
from typing import Dict, List
from .uirobot import UIRobot
from ..generic import GenericMotor


class UIRobot_binding(UIRobot, GenericMotor):
    """UIRobot bindings for BeadPull"""

    def __init__(self) -> None:
        """init class"""
        super(UIRobot_binding, self).__init__()
        self.bp_status = {"driver": "UIRobot"}
        self.motor_settings = yaml.load(
            open(join(dirname(__file__), "settings.yaml"), "r"),
            Loader=yaml.FullLoader,
        )
        self.bp_move_speed = self.motor_settings["initial"]["moveSpeed"]
        self.bp_return_speed = self.motor_settings["initial"]["returnSpeed"]
        self.bp_unit_over_mm = self.motor_settings["initial"]["unit_over_mm"]
        self.bp_calibration_steps = 1
        self.bp_direction = (
            -1 if self.motor_settings["initial"]["reverceDirection"] else 1
        )
        self.bp_speed_limit = self.motor_settings["speedLimit"]
        self.bp_calib_speed = self.motor_settings["calibration"]["speed"]

    def bpConnect(self, port: str, baudrate: int) -> bool:
        """connect to motor

        Arguments:
        port[str] -- motor serial port
        baudrate[int] -- serial baudrate

        Return value[bool] -- success/failure
        """
        rv = self.connect(port=port, baudrate=baudrate)
        if rv:
            self._uilog.info("Motor connected")
        self.timeout(100)
        return rv

    def bpDisconnect(self) -> bool:
        """disconnect motor"""
        self.disconnect()
        self._uilog.info("Motor disconnected")
        return True

    def bpListPorts(self) -> List[str]:
        """list possible motor ports"""
        return self.listPorts()

    def bpInit(self) -> bool:
        """initialize motor

        Return value[bool] -- success/failure
        """
        data = self.model()
        if data is not None:
            self.bp_status.update(data)
        self.autoCurrentReduction(
            self.motor_settings["current"]["autoReduction"]
        ) is None
        self.current(self.motor_settings["current"]["limit"])
        data = self.configureMCR(
            adv_mode=self.motor_settings["MCR"]["advancedMotion"],
            acc_per=self.motor_settings["MCR"]["accelerationPeriod"],
            dec_per=self.motor_settings["MCR"]["decelerationPeriod"],
            done_notify=self.motor_settings["MCR"]["doneNotify"],
            orig_notify=self.motor_settings["MCR"]["originNotify"],
        )
        if data is not None:
            self.bp_status.update(data)
        self.configureMicroStep(self.motor_settings["microsteps"])
        self.speedStart(self.motor_settings["advancedMotion"]["startSpeed"])
        self.speedCes(self.motor_settings["advancedMotion"]["cessateSpeed"])
        self.direction(self.bp_direction == 1)
        rv = self.sendBuffer()
        self._uilog.info("Motor initialized")
        return rv is not None

    def bpStatus(self) -> Dict[str, str]:
        """motor status

        Return value[Dict[str, str]] -- key-value pairs of motor status info
        """
        rv = self.statusDesired()
        if rv is not None:
            self.bp_status.update(rv)
        rv = self.statusCurrent()
        if rv is not None:
            self.bp_status.update(rv)
        return self.bp_status

    def bpIsMoving(self) -> bool:
        """check if motor is moving

        Return value[bool] -- moving/not moving
        """
        return self.speed() != 0

    def bpHold(self) -> bool:
        """set motor to hold

        Return value[bool] -- success/failure
        """
        self.enable()
        return self.sendBuffer() is not None

    def bpRelease(self) -> bool:
        """release motor

        Return value[bool] -- success/failure
        """
        self.disable()
        return self.sendBuffer() is not None

    def bpStop(self) -> bool:
        """stop motion and clear motion commands

        Return value[bool] -- success/failure
        """
        self.speed(0)
        return True

    def bpMoveSpeed(self, spd: float) -> bool:
        """set motor move speed

        Arguments:
        spd[float] -- motor speed in mm/s
        Return value[bool] -- success/failure
        """
        self.bp_move_speed = spd
        return True

    def bpReturnSpeed(self, spd: float) -> bool:
        """set motor return to origin speed

        Arguments:
        spd[float] -- motor speed in mm/s
        Return value[bool] -- success/failure
        """
        self.bp_return_speed = spd
        return True

    def bpDirection(self, val: bool) -> bool:
        """change movement direction

        Arguments:
        val[bool] -- direction
        Return value[bool] -- success/failure
        """
        self.direction(val)
        if val:
            self.bp_direction = 1
        else:
            self.bp_direction = -1
        return self.sendBuffer() is not None

    def bpOrigin(self) -> bool:
        """set origin to current position

        Return value[bool] -- success/failure
        """
        return True if self.origin() is not None else False

    def bpIsConnected(self) -> bool:
        """check if motor is connected

        Return value[bool] -- connected/not connected
        """
        return True if self.statusCurrent() is not None else False

    def bpStep(self, leng: float) -> bool:
        """make a step

        This function needs to be asynchronous in order for
        bpStop to work.

        Arguments:
        leng[float] -- step length in mm
        Return value[bool] -- success/failure
        """
        pos = int(round(self.bp_direction * leng * self.bp_unit_over_mm, 0))
        spd = int(round(self.bp_move_speed * self.bp_unit_over_mm, 0))
        self.goForward(
            pos, spd if spd <= self.bp_speed_limit else self.bp_speed_limit
        )
        return True

    def bpGotoPosition(self, pos: float) -> bool:
        """go to position

        This function needs to be asynchronous in order for
        bpStop to work.

        Arguments:
        pos[float] -- desired position in mm
        Return value[bool] -- success/failure
        """
        coord = int(round(self.bp_direction * pos * self.bp_unit_over_mm, 0))
        spd = int(round(self.bp_move_speed * self.bp_unit_over_mm, 0))
        self.gotoPosition(
            coord, spd if spd <= self.bp_speed_limit else self.bp_speed_limit
        )
        return True

    def bpReturn(self) -> bool:
        """return to origin

        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure
        """
        self.gotoPosition(
            0, int(round(self.bp_return_speed * self.bp_unit_over_mm, 0))
        )
        return True

    def bpAcceleration(self, acc: float) -> bool:
        """set motor acceleration period

        Arguments:
        acc[float] -- desired acceleration period
        Return value[bool] -- success/failure
        """
        return self.acceleration(int(round(acc * 1e3, 0))) is not None

    def bpDeceleration(self, dec: float) -> bool:
        """set motor deceleration period

        Arguments:
        acc[float] -- desired deceleration period
        Return value[bool] -- success/failure
        """
        return self.deceleration(int(round(dec * 1e3, 0))) is not None

    def bpWait(self, timeout: int) -> bool:
        """wait for acknowledge signal from motor

        If motor has no acknowledge capability - just wait for
        specified amount of time

        Arguments:
        timeout[float] -- wait timeout in ms
        Return value[bool] -- success/timed out
        """
        rv = self.wait_done(timeout)
        return rv

    def bpCalibratePreset(self, val: float) -> bool:
        """calibrate motor - set saved calibration ratio

        Arguments:
        val[float] -- unit/mm ratio
        Return value[bool] -- success/failure
        """
        self.bp_unit_over_mm = val
        return True

    def bpCalibrateVal(self, leng: int) -> bool:
        """calibrate motor - set step length

        Step one of three-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).

        Arguments:
        leng[int] -- number of steps in motor units
        Return value[bool] -- success/failure
        """
        self.bp_calibration_steps = leng
        return True

    def bpCalibrateStep(self) -> bool:
        """calibrate motor - make a step

        Step two of two-step calibration procedure
        (bpCalibrateVal, bpCalibrateStep, bpCalibrateSet).
        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure
        """
        self.goForward(
            self.bp_calibration_steps * self.bp_direction, self.bp_calib_speed
        )
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
        self.bp_unit_over_mm = self.bp_calibration_steps / leng
        return self.bp_unit_over_mm

    def bpCalibrateOrigin(self) -> bool:
        """return to origin in calibrate mode

        At this point motor is uncalibrated. Return with some preset speed.
        This function needs to be asynchronous in order for
        bpStop to work.

        Return value[bool] -- success/failure"""
        self.gotoPosition(0, self.bp_calib_speed)
        return True
