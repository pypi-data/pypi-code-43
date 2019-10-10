__all__ = ['AkuandubaWatchdog']

# Imports
from Akuanduba.core import Logger, NotSet, AkuandubaService, AkuandubaDataframe, AkuandubaTool
from Akuanduba.core.messenger.macros import *
from Akuanduba.core.constants import *
from Akuanduba.core import StatusCode, StatusTool, StatusThread
from collections import OrderedDict
from copy import deepcopy
from threading import Lock, Timer
from time import time

#
# Watchdog class
#
class AkuandubaWatchdog (AkuandubaService):

  # Init
  def __init__ (self, name = 'AkuandubaWatchdog', use_linux_watchdog = False):

    # Super init
    AkuandubaService.__init__(self, name)

    # Name
    self._name = name

    # Defaults to always send keep-alive
    self.__sendKeepAlive = True
    
    # Stores information about using Linux wdt or not
    self._useLinuxWatchdog = use_linux_watchdog

    # Messaging
    MSG_INFO(self, "Creating the AkuandubaWatchdog...")

    # Modules dict
    self._modules = OrderedDict()

    # Default parameters for every module
    defaultDictForEveryMethod = {
      'enable'      : DEFAULT_METHOD_ENABLE,
      'timeout'     : DEFAULT_METHOD_TIMEOUT,
      'action'      : DEFAULT_METHOD_ACTION
    }
    self.__defaultParameters = {
      # 'initialize'  : deepcopy(defaultDictForEveryMethod),
      'execute'     : deepcopy(defaultDictForEveryMethod),
      'run'         : deepcopy(defaultDictForEveryMethod),
      'lock'        : deepcopy(defaultDictForEveryMethod),
    }
    self.__acceptedActions = ['reset', 'terminate']
    self.__acceptedMethods = ['execute', 'run', 'lock']

    # Reset timers
    self.__resetTimers = True

    # Lock
    self.__lock = Lock ()

  # Overwriting __add__ method in order to ease manipulation
  def __add__ (self, module):

    # Checking if input type and length are correct
    if not ((issubclass(type(module), AkuandubaDataframe)) or (issubclass(type(module), AkuandubaService)) or (issubclass(type(module), AkuandubaTool)) or (len(module) == 2)):
      MSG_ERROR (self, "Failed to add module to watchdog. Check usage:")
      MSG_ERROR (self, "wd += (module, params_dict)")
      MSG_ERROR (self, "wd += module")
      return self

    # Split into module and params_dict
    params_dict = deepcopy(self.__defaultParameters)
    custom_params_dict = {}
    try:
      if (len(module) == 2):
        custom_params_dict = module[1]
        module = module[0]
    except:
      pass

    # Checking type of module
    if (issubclass(type(module), AkuandubaDataframe)):
      MSG_INFO (self, "- Adding {} dataframe to the watchdog...".format(module.name()))
    elif (issubclass(type(module), AkuandubaService)):
      MSG_INFO (self, "- Adding {} service to the watchdog...".format(module.name()))
    elif (issubclass(type(module), AkuandubaTool)):
      MSG_INFO (self, "- Adding {} tool to the watchdog...".format(module.name()))
    else:
      MSG_ERROR (self, "Failed to add module to watchdog. Supported modules must inherit either from AkuandubaDataframe, AkuandubaService or AkuandubaTool")
      return self
    
    # Parsing params_dict
    # methods = ['initialize', 'execute', 'run', 'lock']
    methods = self.__acceptedMethods
    methods_param = ['enable', 'timeout']
    methods_type = [bool, int]
    # Iterate methods
    for method in methods:
      # If custom method
      if (method in custom_params_dict):
        # Iterate method params
        for i in range (len(methods_param)):
          method_param = methods_param [i]
          # If custom method param
          if (method_param in custom_params_dict[method]):
            # Check type
            if (type(custom_params_dict[method][method_param]) == methods_type[i]):
              # If okay, change it
              params_dict[method][method_param] = custom_params_dict[method][method_param]
            else:
              MSG_ERROR (self, "Type {} not accepted for param {} on method \"{}\"".format(type(custom_params_dict[method][method_param]), method_param, method))
              return self
        # Checking action
        if ('action' in custom_params_dict[method]):
          # Check accepted actions
          if (custom_params_dict[method]['action'] in self.__acceptedActions):
            # If okay, change it
            params_dict[method]['action'] = custom_params_dict[method]['action']
          else:
            MSG_ERROR (self, "Action \"{}\" not accepted on method \"{}\"".format(custom_params_dict[method]['action'], method))

    # Reviewing needed keys according to each class
    if (issubclass(type(module), AkuandubaDataframe)):
      MSG_DEBUG (self, "Removing unnecessary information from params_dict")
      del params_dict['execute']
      del params_dict['run']
    elif (issubclass(type(module), AkuandubaService)):
      MSG_DEBUG (self, "Removing unnecessary information from params_dict")
      del params_dict['lock']
    elif (issubclass(type(module), AkuandubaTool)):
      MSG_DEBUG (self, "Removing unnecessary information from params_dict")
      del params_dict['lock']
      del params_dict['run']

    # Adding module to dict
    MSG_DEBUG (self, "Acquiring lock for adding new module")
    self.__lock.acquire()

    if module.name() in self._modules.keys():
      MSG_ERROR (self, "Failed to add module to watchdog. Key {} already in wd's dict".format(module.name()))
      return self
    self._modules[module.name()] = params_dict
    MSG_INFO (self, " * Module {} added to the watchdog successfully".format(module.name()))

    MSG_DEBUG (self, "Releasing lock after adding new module")
    self.__lock.release()

    return self

  # Pretty print collection
  def printCollection (self):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint (self._modules)

  # Feeding this watchdog
  def feed (self, name, method):
    if name in self._modules.keys():
      MSG_DEBUG (self, "Feeding the {}'s method \"{}\" WDT...".format(name, method))
      try:
        self._modules[name][method]['wdt'].cancel()
      except KeyError:
        pass
      self._modules[name][method]['wdt'] = Timer(self._modules[name][method]['timeout'], self.__handler, [name, method])
      self._modules[name][method]['wdt'].start()

  # Resetting all timers
  def resetTimers (self):

    # Acquiring lock
    MSG_DEBUG (self, "Acquiring lock for resetting")
    self.__lock.acquire()

    # Resetting
    MSG_INFO (self, "Resetting all watchdog timers")
    for key in self._modules.keys():
      for method in self._modules[key].keys():
        try:
          self._modules[key][method]['wdt'].cancel
        except KeyError:
          pass
        self._modules[key][method]['wdt'] = Timer(self._modules[key][method]['timeout'], self.__handler, [key, method])
        self._modules[key][method]['wdt'].start()

    # Releasing lock
    MSG_DEBUG (self, "Releasing lock after resetting")
    self.__lock.release()

    # Resetting flag
    self.__resetTimers = False

  # Force this module to keep sending keep-alives
  def forceKeepAliveFlag (self, module):

    MSG_WARNING (self, "Module {} forced this Watchdog to keep sending keep-alives".format(module.name()))
    self.__sendKeepAlive = True

  # Enables Linux watchdog
  def enableLinuxWatchdog (self):
    self._useLinuxWatchdog = True

  # Method that writes into wdt file
  def __wdt_write (self, value, count=0):
    import os
    from time import sleep

    if (count > 0):
      MSG_WARNING (self, "This is the retry attempt #{} to write on the WDT file".format(count + 1))

    # Break condition
    if (count >= WDT_WRITE_ATTEMPTS):
      MSG_ERROR (self, "Tried to write into the WDT file too many times. Rebooting system in {} seconds...".format(WDT_WRITE_FAIL_REBOOT_TIMEOUT))
      sleep(WDT_WRITE_FAIL_REBOOT_TIMEOUT)
      os.system("reboot")

    # Default operation
    try:
      fd = os.open(WDT_FILENAME, os.O_WRONLY|os.O_NOCTTY)
      f = open(fd, WDT_FILE_OPTIONS, buffering = 0)
      f.write(value)
      f.close()
    except OSError:
      MSG_WARNING (self, "WDT file could not be opened, will retry in 1 second (count = {})".format(count))
      sleep(1)
      self.__wdt_write(value, count + 1)

  # Method that keeps Linux alive by writing into file /dev/watchdog
  def __wdt_keepalive (self):
    self.__wdt_write(b".")

  # Method that disables Linux wdt
  def __wdt_stop (self):
    self.__wdt_write(b"V")

  # Finalizing all timers
  def finalizeTimers (self):

    # Acquiring lock
    MSG_DEBUG (self, "Acquiring lock for finalizing")
    self.__lock.acquire()

    # Resetting
    MSG_INFO (self, "Finalizing all watchdog timers")
    for key in self._modules.keys():
      for method in self._modules[key].keys():
        try:
          self._modules[key][method]['wdt'].cancel
        except KeyError:
          pass

    # Releasing lock
    MSG_DEBUG (self, "Releasing lock after finalizing")
    self.__lock.release()

  # Handler for this implementation
  def __handler (self, name, method):
    MSG_WARNING(self, "{}'s method {} triggered the watchdog!!! This will shutdown soon...".format(name, method))
    self.__sendKeepAlive = False

  # Terminate framework
  def terminateFramework (self):
    self.getContext().getHandler("EventStatus").forceTerminate()

  # Initialize
  def initialize (self):

    # Initialize thread, as every service runs as a thread
    if self.isSafeThread():
      MSG_INFO( self, "Initializing safe thread for %s", self._name)
      self.forceRunThread()

    if self.start().isFailure():
      MSG_FATAL( self, "Impossible to initialize the %s service", self._name)
      return StatusCode.FAILURE

    # Lock the initialization. After that, this tool can not be initialized once again
    self.init_lock()
    return StatusCode.SUCCESS

  # Enable
  def enable (self):
    
    # Call super method
    super().enable()

    # Initializing
    self.initialize()

  # Execute
  def execute (self, context):

    # Always return SUCCESS
    return StatusCode.SUCCESS

  # Finalize
  def finalize(self):

    super().finalize()

    # Always return SUCCESS
    return StatusCode.SUCCESS

  # Run
  def run( self ):
    from time import sleep

    # Main loop
    while self.statusThread() == StatusThread.RUNNING:

      # This assures that when a module forces the Watchdog to send keep-alives again, it works
      if (self._useLinuxWatchdog):
        while self.__sendKeepAlive:
          # Reset timers
          if (self.__resetTimers):
            self.resetTimers()

          # Keeps RPi alive
          self.__wdt_keepalive()

        MSG_WARNING (self, "Watchdog stopped sending keep-alives...")
        sleep(1)

      # NOP
      pass

Watchdog = AkuandubaWatchdog("AkuandubaWatchdog")