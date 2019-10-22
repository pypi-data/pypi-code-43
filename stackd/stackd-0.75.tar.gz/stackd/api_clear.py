import sys

from .cmd_clear import cmd_clear
from .printError import printError

def api_clear(env_vars={}):
  process = cmd_clear(env_vars)
  if(process and process.returncode != 0):
      printError('ERROR: command failed with exit code '+str(process.returncode))
      sys.exit(process.returncode)