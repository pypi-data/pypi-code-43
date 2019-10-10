# All list
__all__ = ["TimerCondition"]

from Akuanduba.core import StatusCode, NotSet, StatusTrigger
from Akuanduba.core.messenger.macros import *
from Akuanduba.core import TriggerCondition
import time
from threading import Timer

class TimerCondition (TriggerCondition):

  def __init__(self, name, maxseconds, handler=None):
    
    TriggerCondition.__init__(self, name)
    self._name = name
    self._maxseconds = maxseconds
    self._then = NotSet
    self._handler = handler if handler is not None else self.__defaultHandler
    self._timer = Timer(self._maxseconds, self._handler)
    self._status = StatusTrigger.NOT_TRIGGERED
    self._initialized = False
    self._context = NotSet

  def __defaultHandler (self):
    MSG_INFO (self, "{} condition triggered".format(self._name))
    self._status = StatusTrigger.TRIGGERED
    self._timer = Timer(self._maxseconds, self._handler)
    self._timer.start()

  def isInitialized (self):
    return self._initialized

  def setMaxSeconds (self, maxseconds):
    self._maxseconds = maxseconds
    MSG_INFO (self, "TimerCondition w/ name {} timeout has been set to {}".format(self._name, self._maxseconds))

  def setContext (self, context):
    self._context = context

  def getContext (self):
    return self._context

  def resetTimer (self):
    self._timer.cancel()
    self._timer = Timer(self._maxseconds, self._handler)
    self._timer.start()

  def initialize(self):
  
    self._timer.start()
    self.getContext().setDecor("TriggerTimer", self._maxseconds)
    self._initialized = True
    return StatusCode.SUCCESS

  def execute (self):

    if self._status == StatusTrigger.TRIGGERED:
      self._status = StatusTrigger.NOT_TRIGGERED
      return StatusTrigger.TRIGGERED
    else:
      return self._status

  def finalize(self):

    return StatusCode.SUCCESS