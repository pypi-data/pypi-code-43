__all__ = ['AkuandubaTool', 'AkuandubaService', 'AkuandubaDataframe']

from Akuanduba.core import Logger, EnumStringification, NotSet, StatusCode, StatusThread, StatusTool
from Akuanduba.core.messenger.macros import *
from Akuanduba.core.constants import *
from queue import Queue
from threading import Thread, Lock
import time


# Base class used for all tools for this framework
class AkuandubaTool ( Logger ):

  def __init__(self, name):
    Logger.__init__(self)
    Thread.__init__(self)
    self._name          = name
    self._status        = StatusTool.ENABLE
    self._initialized   = StatusTool.NOT_INITIALIZED
    self._finalized     = StatusTool.NOT_FINALIZED
    self._context       = NotSet

  def name(self):
    return self._name

  def setContext( self, context ):
    self._context = context

  def getContext(self):
    return self._context

  def initialize(self):
    self.enable()
    return StatusCode.SUCCESS

  def execute(self, context):
    self.setContext(context)
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

  def status(self):
    return self._status

  def disable(self):
    MSG_INFO( self, 'Disable %s tool service.',self._name )
    self._status = StatusTool.DISABLE

  def enable(self):
    MSG_INFO( self, 'Enable %s tool service.',self._name)
    self._status = StatusTool.ENABLE

  def init_lock(self):
    self._initialized = StatusTool.IS_INITIALIZED

  def fina_lock(self):
    self._finalized = StatusTool.IS_FINALIZED

  def isInitialized(self):
    if self._initialized is StatusTool.IS_INITIALIZED:
      return True
    else:
      return False

  def isFinalized(self):
    if self._finalized is StatusTool.IS_FINALIZED:
      return True
    else:
      return False

  def alive(self):
    return True


class AkuandubaService( AkuandubaTool, Thread ):

  def __init__(self, name):
    AkuandubaTool.__init__(self, name)
    # Threading support
    self._useSafeThread = True
    self._statusThread  = StatusThread.STOP
    self._queue         = NotSet
    self._stopThread    = False
    self._max_fifo      = MAX_FIFO


  def setQueueLength( self, v ):
    self._max_fifo = v


  def initialize(self):
    if self.isSafeThread():
      MSG_INFO( self, "Initializing safe thread for %s", self.name())
      self._queue = Queue( self._max_fifo )
      self.forceRunThread()
    self.enable()
    return StatusCode.SUCCESS


  def execute(self, context):
    self.setContext(context)
    if self.isSafeThread() and self.statusThread() == StatusThread.RUNNING:
      pass
    return StatusCode.SUCCESS


  def finalize(self):
    if self.isSafeThread() and self.statusThread() == StatusThread.RUNNING:
      MSG_INFO( self, "Sending stop signal...")
      self.forceStopThread()
      self.do_run=False
      MSG_INFO( self, "Thread is finalized.")
    return StatusCode.SUCCESS


  def isSafeThread(self):
    return self._useSafeThread


  def forceStopThread(self):
    self._stopThread = True


  def forceRunThread(self):
    self._stopThread = False


  def statusThread(self):
    if (self._status is StatusTool.DISABLE):
      return StatusThread.STOP
    elif self._stopThread:
      return StatusThread.STOP
    else:
      return StatusThread.RUNNING


  def _put(self, obj):
    self._queue.put(obj)


  def _get(self, timeout = None):
    return self._queue.get(timeout = timeout)


  def start(self):
    if not self.isSafeThread():
      MSG_ERROR( self, 'You can not call the start method since you not enable the thread support.')
      return StatusCode.FAILURE
    else:
      MSG_DEBUG( self, "Starting safe thread with name: %s", self.name())
      super().start()
      return StatusCode.SUCCESS


  def run(self):
    pass


  def alive(self):
    return True

class AkuandubaDataframe (Logger):

  def __init__(self, name):
    Logger.__init__(self)
    self._name = name
    self._decoration = dict()
    self._context = NotSet
    self._lock = Lock()

  def acquire (self, timeout = -1):
    return self._lock.acquire(timeout = timeout)

  def release (self):
    return self._lock.release()

  def name (self):
    return self._name

  def setContext( self, context):
    self._context=context

  def getContext(self):
    return self._context

  def initialize(self):
    return StatusCode.SUCCESS

  def execute(self):
    return StatusCode.SUCCESS

  def finalize(self):
    return StatusCode.SUCCESS

  def setDecor(self, key, v):
    self._decoration[key] = v

  def getDecor(self,key):
    try:
      return self._decoration[key]
    except KeyError:
      MSG_WARNING( self, 'Decoration %s not found',key)

  def clearDecorations(self):
    self._decoration = dict()

  def decorations(self):
    return self._decoration.keys()