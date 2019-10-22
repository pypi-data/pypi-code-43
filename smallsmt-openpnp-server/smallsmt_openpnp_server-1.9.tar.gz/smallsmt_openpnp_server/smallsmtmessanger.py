from PyQt5.QtCore import pyqtSlot,pyqtSignal
from PyQt5.QtCore import QObject,QTimer,Qt

import copy


class SmallSmtMessanger(QObject):

    PING_TIMEOUT = 200

    SmallSmtMessangerLog = pyqtSignal([str])
    messageDone = pyqtSignal([bool])
    messagePing = pyqtSignal()

    timer = QTimer()
    timerPing = QTimer()

    requests = []
    requests_id = 0
    timeout = 0
    active = 0

    def __init__(self,  serial):
        QObject.__init__(self)

        self.serial = serial
        self.timer.setSingleShot(True)
        self.timerPing.setSingleShot(False)

        self.timer.timeout.connect(self.executeRequestTimeout,Qt.QueuedConnection)
        self.timerPing.timeout.connect(self.executePing,Qt.QueuedConnection)
        self.serial.getFromSmallSmt.connect(self.sendLoop, Qt.QueuedConnection)

    def logInfo(self, logText):
        self.SmallSmtMessangerLog.emit(logText)

    def prepare(self):
        self.requests.clear()
        self.requests_id = 0

    def add(self,item):
        self.requests.append(item)

    def send(self):
        # Triggers sending
        result = self.sendNextPacket()
        if result==0:
            self.timerPing.start(self.PING_TIMEOUT)
            self.active = 1
        return result

    def notEmpty(self):
        if len(self.requests) > 0:
            return True
        else:
            return False

    def getRetVal(self,idx):
        if idx < len(self.requests):
            try:
                result = self.requests[idx]["result_bytes"]
            except:
                result = bytearray()

            return result
        else:
            return 0

    def sendNextPacket(self):
        packet = self.requests[self.requests_id]["packet"]
        self.timeout = self.requests[self.requests_id]["tout"]

        if self.serial.sendToSmallSmt(packet.bytes) != 0:
            self.logInfo(str.format("Command sending error"))
            self.messageDone.emit(False)
            return -1
        else:
            if self.timeout != 0:
                # Command with timeout - we assume response is expected
                self.timer.start(self.timeout)
            else:
                # Some commands do no provide response
                # We use small delay anyway
                self.timer.start(10)
            return 0

    def sendFinalyze(self,result):
        self.timerPing.stop()
        self.messageDone.emit(result)
        self.active = 0

    @pyqtSlot(bytearray)
    def sendLoop(self,in_bytes):
        self.timer.stop()
        # Preserve incoming packet and continue sending packets
        # Note - Messages ent from playground also end up here
        #        that is why we check if our request is active
        if (self.active > 0) and (len(self.requests)> self.requests_id):
            self.requests[self.requests_id]["result_bytes"] = in_bytes
            self.requests_id = self.requests_id + 1
            if self.requests_id < len(self.requests):
                self.sendNextPacket()
            else:
                # All packages sent
                self.sendFinalyze(True)

    @pyqtSlot()
    def executePing(self):
        self.messagePing.emit()


    @pyqtSlot()
    def executeRequestTimeout(self):
        if self.timeout == 0:
            # This was packet without response - timeout as expected
            # Execute next request
            self.sendLoop(bytearray())
        else:
            # Unexpected timeout
            self.logInfo(str.format("Command timeout - no machine response"))
            self.sendFinalyze(False)
