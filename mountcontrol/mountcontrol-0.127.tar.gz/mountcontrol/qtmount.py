############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.7.4

#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import socket
import sys
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
# local imports
import mountcontrol.mount


__all__ = ['Mount',
           ]


class WorkerSignals(PyQt5.QtCore.QObject):
    """
    The WorkerSignals class offers a list of signals to be used and instantiated by the
    Worker class to get signals for error, finished and result to be transferred to the
    caller back
    """

    __all__ = ['WorkerSignals']
    version = '1.0'

    finished = PyQt5.QtCore.pyqtSignal()
    error = PyQt5.QtCore.pyqtSignal(object)
    result = PyQt5.QtCore.pyqtSignal(object)


class Worker(PyQt5.QtCore.QRunnable):
    """
    The Worker class offers a generic interface to allow any function to be executed as a
    thread in an threadpool
    """

    __all__ = ['Worker',
               'run']
    version = '1.0.1'
    logger = logging.getLogger(__name__)

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        # the worker signal must not be a class variable, but instance otherwise
        # we get trouble when having multiple threads running
        self.signals = WorkerSignals()

    def run(self):
        """
        runs an arbitrary methods with it's parameters and catches the result

        :return: nothing, but sends results and status as signals
        """

        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            # as we want to send a clear message to the log file
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = exc_traceback

            # moving toward the end of the trace
            while tb.tb_next is not None:
                tb = tb.tb_next

            # getting data out for processing
            file = tb.tb_frame.f_code.co_filename
            line = tb.tb_frame.f_lineno

            errorString = f'{file}, line {line} {exc_value}'
            self.logger.error(errorString)
            self.signals.error.emit(errorString)
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class MountSignals(PyQt5.QtCore.QObject):
    """
    The MountSignals class offers a list of signals to be used and instantiated by
    the Mount class to get signals for triggers for finished tasks to
    enable a gui to update their values transferred to the caller back.

    This has to be done in a separate class as the signals have to be subclassed from
    QObject and the Mount class itself is subclassed from object
    """

    __all__ = ['MountSignals']
    version = '1.0'

    pointDone = PyQt5.QtCore.pyqtSignal(object)
    settingDone = PyQt5.QtCore.pyqtSignal(object)
    alignDone = PyQt5.QtCore.pyqtSignal(object)
    namesDone = PyQt5.QtCore.pyqtSignal(object)
    firmwareDone = PyQt5.QtCore.pyqtSignal(object)
    locationDone = PyQt5.QtCore.pyqtSignal(object)
    calcTLEdone = PyQt5.QtCore.pyqtSignal(object)
    statTLEdone = PyQt5.QtCore.pyqtSignal(object)
    getTLEdone = PyQt5.QtCore.pyqtSignal(object)
    mountUp = PyQt5.QtCore.pyqtSignal(object)
    slewFinished = PyQt5.QtCore.pyqtSignal()
    alert = PyQt5.QtCore.pyqtSignal()


class Mount(mountcontrol.mount.Mount):
    """
    The Mount class is the main interface for interacting with the mount computer.
    The user could:
        setup / change the interface to the mount
        start / stop cyclic tasks to poll data from mount
        send and get data from mount
        has signals for interfacing to external GUI's for data updates

        >>> settings = Mount(
        >>>                     host=host,
        >>>                     MAC=MAC,
        >>>                     threadPool=threadPool,
        >>>                     pathToData=pathToData,
        >>>                     expire=expire,
        >>>                     verbose=verbose,
        >>>                 )

    """

    CYCLE_POINTING = 500
    CYCLE_MOUNT_UP = 2000
    CYCLE_SETTING = 3000

    # set timeout
    SOCKET_TIMEOUT = 0.5

    def __init__(self,
                 host=None,
                 MAC=None,
                 threadPool=None,
                 pathToData=None,
                 expire=None,
                 verbose=None,
                 ):

        super().__init__(host=host,
                         MAC=MAC,
                         pathToData=pathToData,
                         expire=expire,
                         verbose=verbose,
                         )

        if threadPool is None:
            self.threadPool = PyQt5.QtCore.QThreadPool()
        else:
            self.threadPool = threadPool
        self._settlingTime = 0

        self.statusAlert = False
        self.statusSlew = True

        # signal handling
        self.signals = MountSignals()
        # timers
        self.timerPointing = PyQt5.QtCore.QTimer()
        self.timerPointing.setSingleShot(False)
        self.timerPointing.timeout.connect(self.cyclePointing)
        self.timerSetting = PyQt5.QtCore.QTimer()
        self.timerSetting.setSingleShot(False)
        self.timerSetting.timeout.connect(self.cycleSetting)
        self.timerMountUp = PyQt5.QtCore.QTimer()
        self.timerMountUp.setSingleShot(False)
        self.timerMountUp.timeout.connect(self.cycleCheckMountUp)
        self.settlingWait = PyQt5.QtCore.QTimer()
        self.settlingWait.setSingleShot(True)
        self.settlingWait.timeout.connect(self.waitSettlingAndEmit)

    @property
    def settlingTime(self):
        return self._settlingTime / 1000

    @settlingTime.setter
    def settlingTime(self, value):
        # settling time is in seconds
        self._settlingTime = value * 1000

    def waitSettlingAndEmit(self):
        """
        waitSettlingAndEmit emit the signal for slew finished

        :return: true for test purpose
        """
        self.signals.slewFinished.emit()
        return True

    def startTimers(self):
        """
        startTimers enables the cyclic timers for polling necessary mount data.

        :return: true for test purpose
        """
        self.timerSetting.start(self.CYCLE_SETTING)
        self.timerPointing.start(self.CYCLE_POINTING)
        self.timerMountUp.start(self.CYCLE_MOUNT_UP)
        return True

    def stopTimers(self):
        """
        stopTimers disables the cyclic timers for polling necessary mount data.
        in addition wait for threadPool to finish

        :return: true for test purpose
        """
        self.timerPointing.stop()
        self.timerSetting.stop()
        self.timerMountUp.stop()
        self.threadPool.waitForDone()
        return True

    def resetData(self):
        """
        resetData deletes all data already stored in classes just by redefining the
        classes. it send as well a signal, when the data is cleared.

        :return: true for test purpose
        """
        super().resetData()
        self.signals.pointDone.emit(self.obsSite)
        self.signals.settingDone.emit(self.setting)
        self.signals.alignDone.emit(self.model)
        self.signals.namesDone.emit(self.model)
        self.signals.firmwareDone.emit(self.firmware)
        self.signals.locationDone.emit(self.obsSite.location)
        return True

    def checkMountUp(self):
        """
        checkMountUp polls the host/port of the mount computer and set the state and
        signals for the status accordingly.

        :return: true for test purpose
        """

        client = socket.socket()
        client.settimeout(self.SOCKET_TIMEOUT)
        try:
            client.connect(self.host)
        except Exception:
            if self.mountUp:
                self.mountUp = False
            client.close()
        else:
            if not self.mountUp:
                self.mountUp = True
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        finally:
            return True

    def errorCycleCheckMountUp(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearCycleCheckMountUp(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.mountUp.emit(self.mountUp)
        return True

    def cycleCheckMountUp(self):
        """
        cycleCheckMountUp prepares the worker thread and the signals for getting the settings
        data.
        status None means that no chance to connect due to missing host entry

        :return: success
        """

        # if not host entry, don't poll for mount, because it does not make sense
        if not self.host:
            self.signals.mountUp.emit(None)
            return False

        worker = Worker(self.checkMountUp)
        worker.signals.finished.connect(self.clearCycleCheckMountUp)
        worker.signals.error.connect(self.errorCycleCheckMountUp)
        self.threadPool.start(worker)
        return True

    def errorCyclePointing(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearCyclePointing(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        # if  has emergency stop, emit warning
        if self.obsSite.status in [1, 98, 99]:
            if not self.statusAlert:
                self.signals.alert.emit()
            self.statusAlert = True
        else:
            self.statusAlert = False

        # if stop slewing, emit warning
        if self.obsSite.status not in [2, 6, 6]:
            if not self.statusSlew:
                # start timer for settling time and emit signal afterwards
                self.settlingWait.start(self._settlingTime)
            self.statusSlew = True
        else:
            self.statusSlew = False

        self.signals.pointDone.emit(self.obsSite)
        return True

    def cyclePointing(self):
        """
        cyclePointing prepares the worker thread and the signals for getting the pointing
        data.

        :return: success
        """

        if not self.mountUp:
            self.signals.pointDone.emit(self.obsSite)
            return False
        worker = Worker(self.obsSite.pollPointing)
        worker.signals.finished.connect(self.clearCyclePointing)
        worker.signals.error.connect(self.errorCyclePointing)
        self.threadPool.start(worker)
        return True

    def errorCycleSetting(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearCycleSetting(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.settingDone.emit(self.setting)
        return True

    def cycleSetting(self):
        """
        cycleSet prepares the worker thread and the signals for getting the settings
        data.

        :return: success
        """
        if not self.mountUp:
            self.signals.settingDone.emit(self.setting)
            return False
        worker = Worker(self.setting.pollSetting)
        worker.signals.finished.connect(self.clearCycleSetting)
        worker.signals.error.connect(self.errorCycleSetting)
        self.threadPool.start(worker)
        return True

    def errorGetAlign(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearGetAlign(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.alignDone.emit(self.model)
        return True

    def getAlign(self):
        """
        getAlign prepares the worker thread and the signals for getting the alignment model
        data.

        :return: success
        """
        if not self.mountUp:
            self.signals.alignDone.emit(self.model)
            return False
        worker = Worker(self.model.pollStars)
        worker.signals.finished.connect(self.clearGetAlign)
        worker.signals.error.connect(self.errorGetAlign)
        self.threadPool.start(worker)
        return True

    def errorGetNames(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearGetNames(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.namesDone.emit(self.model)
        return True

    def getNames(self):
        """
        getNames prepares the worker thread and the signals for getting the alignment model
        names.

        :return: success
        """
        if not self.mountUp:
            self.signals.namesDone.emit(self.model)
            return False
        worker = Worker(self.model.pollNames)
        worker.signals.finished.connect(self.clearGetNames)
        worker.signals.error.connect(self.errorGetNames)
        self.threadPool.start(worker)
        return True

    def errorGetFW(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearGetFW(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.geometry.initializeGeometry(self.firmware.product)
        self.signals.firmwareDone.emit(self.firmware)
        return True

    def getFW(self):
        """
        getFW prepares the worker thread and the signals for getting the build data of
        the mount computer.

        :return: success
        """
        if not self.mountUp:
            self.signals.firmwareDone.emit(self.firmware)
            return False
        worker = Worker(self.firmware.poll)
        worker.signals.finished.connect(self.clearGetFW)
        worker.signals.error.connect(self.errorGetFW)
        self.threadPool.start(worker)
        return True

    def errorGetLocation(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearGetLocation(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.locationDone.emit(self.obsSite)
        return True

    def getLocation(self):
        """
        getLocation prepares the worker thread and the signals for getting the mount
        location data.

        :return: success
        """
        if not self.mountUp:
            self.signals.locationDone.emit(self.obsSite)
            return False
        worker = Worker(self.obsSite.getLocation)
        worker.signals.finished.connect(self.clearGetLocation)
        worker.signals.error.connect(self.errorGetLocation)
        self.threadPool.start(worker)
        return True

    def errorCalcTLE(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearCalcTLE(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.calcTLEdone.emit(self.satellite.tleParams)
        return True

    def calcTLE(self):
        """
        getCalcTLE prepares the worker thread and the signals for getting the mount
        location data.

        :return: success
        """
        if not self.mountUp:
            self.signals.calcTLEdone.emit(self.satellite.tleParams)
            return False
        worker = Worker(self.satellite.calcTLE, self.obsSite.timeJD.tt)
        worker.signals.finished.connect(self.clearCalcTLE)
        worker.signals.error.connect(self.errorCalcTLE)
        self.threadPool.start(worker)
        return True

    def errorStatTLE(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearStatTLE(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.statTLEdone.emit(self.satellite.tleParams)
        return True

    def statTLE(self):
        """
        statTLE prepares the worker thread and the signals for getting the mount
        location data.

        :return: success
        """
        if not self.mountUp:
            self.signals.statTLEdone.emit(self.satellite.tleParams)
            return False
        worker = Worker(self.satellite.statTLE)
        worker.signals.finished.connect(self.clearStatTLE)
        worker.signals.error.connect(self.errorStatTLE)
        self.threadPool.start(worker)
        return True

    def errorGetTLE(self, e):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.logger.error(f'Cycle error: {e}')
        return True

    def clearGetTLE(self):
        """
        the cyclic or long lasting tasks for getting date from the mount should not run
        twice for the same data at the same time.

        :return: true for test purpose
        """
        self.signals.getTLEdone.emit(self.satellite.tleParams)
        return True

    def getTLE(self):
        """
        getTLE prepares the worker thread and the signals for getting the mount
        location data.

        :return: success
        """
        if not self.mountUp:
            self.signals.getTLEdone.emit(self.satellite.tleParams)
            return False
        worker = Worker(self.satellite.getTLE)
        worker.signals.finished.connect(self.clearGetTLE)
        worker.signals.error.connect(self.errorGetTLE)
        self.threadPool.start(worker)
        return True
