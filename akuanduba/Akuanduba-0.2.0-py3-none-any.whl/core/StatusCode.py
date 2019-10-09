__all__ = [ 'StatusCode', 'StatusTool', 'StatusThread', 'StatusTrigger']

from Akuanduba.core import EnumStringification, NotSet

# Status code object used for error code
class StatusObj(object):

  _status = 1

  def __init__(self, sc):
    self._status = sc

  def isFailure(self):
    if self._status < 1:
      return True
    else:
      return False

  def __eq__(self, a):
    if self.status == a.status:
      return True
    else:
      return False

  def __ne__(self, a):
    if self.status != a.status:
      return True
    else:
      return False

  @property
  def status(self):
    return self._status

# status code enumeration
class StatusCode(object):
  """
    The status code of something
  """
  SUCCESS = StatusObj(1)
  FAILURE = StatusObj(0)
  FATAL   = StatusObj(-1)

class StatusTool(EnumStringification):
  """
    The status of the tool
  """
  IS_FINALIZED   = 3
  IS_INITIALIZED = 2 
  ENABLE  = 1
  DISABLE = -1
  NOT_INITIALIZED = -2
  NOT_FINALIZED = -3
 
class StatusThread(EnumStringification):
  """
    Use this to check the thread status
  """
  RUNNING = 1
  STOP    = 0

class StatusTrigger (EnumStringification):
  """
    Use this to check the trigger status
  """
  TRIGGERED = True
  NOT_TRIGGERED = False