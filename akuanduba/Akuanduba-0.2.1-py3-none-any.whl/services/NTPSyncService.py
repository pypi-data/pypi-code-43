__all__ = ['NTPSyncService']

# Mandatory imports
from Akuanduba.core import Logger, NotSet, AkuandubaService
from Akuanduba.core.messenger.macros import MSG_INFO, MSG_WARNING, MSG_DEBUG, MSG_FATAL, MSG_ERROR
from Akuanduba.core.constants import REF_TIME_1970, DEFAULT_UPDATE_DELAY
from Akuanduba.core import StatusCode, StatusTool, StatusThread
from Akuanduba.core.Watchdog import Watchdog
from datetime import datetime
import pytz
from threading import Timer

#
#   Service that syncs system time with an NTP server
#
class NTPSyncService( AkuandubaService ):

  #
  # Init
  #
  def __init__(self, name, ntp_server = 'a.st1.ntp.br', timezone = 'America/Sao_Paulo', updateDelay = None):

    AkuandubaService.__init__(self, name)
    self._ntpServer = ntp_server
    self._timezone = timezone
    self._updateDelay = updateDelay if updateDelay is not None else DEFAULT_UPDATE_DELAY
    self._name = name
    self.__setSystemClock = True

  #
  # Initializing this service
  #
  def initialize(self):

    # Initialize thread
    super().initialize()

    # Starting the thread.
    if self.start().isFailure():
      MSG_FATAL( self, "Impossible to initialize the %s service", self._name)
      return StatusCode.FAILURE

    # Lock the initialization. After that, this tool can not be initialized once again
    self.init_lock()
    return StatusCode.SUCCESS

  #
  # Execute
  #
  def execute( self, context ):

    return StatusCode.SUCCESS

  #
  # Finalize
  #
  def finalize(self):

    super().finalize()
    return StatusCode.SUCCESS

  #
  # This runs as a thread
  #
  def run( self ):
    
    # Loop
    while self.statusThread() == StatusThread.RUNNING:

      # Feeding the wdt
      Watchdog.feed(self._name, 'run')

  #
  # Method that requests time to NTP server
  #
  def __getTimeNTP (self):

    import socket
    import struct
    client = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    data = '\x1b' + 47 * '\0'
    client.sendto (data.encode(), (self._ntpServer, 123))
    try:
      data, _ = client.recvfrom (1024)
      if (data):
        t = struct.unpack ('!12I', data)[10]
        t -= REF_TIME_1970
      else:
        MSG_WARNING (self, "Couldn't get data from NTP Server \"{}\"".format(self._ntpServer))
    except:
      MSG_WARNING (self, "Couldn't get data from NTP Server \"{}\"".format(self._ntpServer))

    return datetime.fromtimestamp(t, pytz.timezone(self._timezone)).strftime('%Y-%m-%d %H:%M:%S')

  #
  # Method that sets system time
  #
  def __set_time (self):

    try:
      MSG_WARNING (self, "Attention! System time will now be set.")
      import os
      os.system("sudo timedatectl set-time '{}'".format(self.__getTimeNTP()))
      Watchdog.forceKeepAliveFlag(self)
      self.__setSystemClock = False
      MSG_WARNING (self, "Configured system time successfully!")
    except:
      MSG_ERROR (self, "Failed to set system time!")

    return True

  #
  # Timer
  #
  def __timer (self):

    MSG_WARNING (self, "Attention! System time will be reviewed soon")
    self.__setSystemClock = True

    # Waits until clock is set
    while (self.__setSystemClock):
      pass

    # Calls set_time
    self.__set_time()

    # Timing next action
    Timer(self._updateDelay, self.__thread_timer).start()
    return StatusCode.SUCCESS