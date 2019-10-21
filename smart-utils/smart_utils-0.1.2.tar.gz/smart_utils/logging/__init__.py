from os import getenv
from  smart_utils.logging.logger import LoggerConstructor
from smart_utils.logging.config import ConfigGetterAws
import logging

APP_NAME = getenv('APP_NAME', "default")
ENVIRONMENT = getenv('sc_environment', "default")

## CUSTOM LEVEL

INIT_LVL = 21
PROGRESS_LVL = 22
EVENT_LVL = 23
FINISHED_LVL = 24
RESULT_LVL = 26

logging.addLevelName(INIT_LVL, "INIT")
logging.addLevelName(PROGRESS_LVL, "PROGRESS")
logging.addLevelName(EVENT_LVL, "EVENT")
logging.addLevelName(FINISHED_LVL, "FINISHED")
logging.addLevelName(RESULT_LVL, "RESULT")

def init(self, message, *args, **kws):
    self._log(INIT_LVL, message, args, **kws)

def progress(self, message, *args, **kws):
    self._log(PROGRESS_LVL, message, args, **kws)

def event(self, message, *args, **kws):
    self._log(EVENT_LVL, message, args, **kws) 

def finished(self, message, *args, **kws):
    self._log(FINISHED_LVL, message, args, **kws)

def result(self, message, *args, **kws):
    self._log(RESULT_LVL, message, args, **kws)

logging.Logger.init = init
logging.Logger.progress = progress
logging.Logger.event = event
logging.Logger.finished = finished
logging.Logger.result = result


Logger = LoggerConstructor(ConfigGetterAws(APP_NAME), ENVIRONMENT).generate_logger()
