__all__ = ["EventStatus"]

from Akuanduba.core import Logger, NotSet
from Akuanduba.core import StatusCode, AkuandubaDataframe

class EventStatus(AkuandubaDataframe):

  def __init__(self, name):
    Logger.__init__(self)
    AkuandubaDataframe.__init__(self, name)
    self._stop = False
    self._terminate = False


  def execute(self):
    return StatusCode.SUCCESS

  def initialize(self):
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

  def acquire (self, timeout = -1):
    return StatusCode.SUCCESS

  def release (self):
    return StatusCode.SUCCESS

  def forceStop(self):
    self._stop = True

  def stop(self):
    return self._stop

  def resetStop(self):
    self._stop = False


  def forceTerminate(self):
    self._terminate = True

  def terminate(self):
    return self._terminate

  def resetTerminate(self):
    self._terminate = False

