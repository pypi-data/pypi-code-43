import sys
from .cmd_after_clear import cmd_after_clear

def api_after_clear(env_vars={}):

  process = cmd_after_clear(env_vars)
  if(process.returncode != 0):
      sys.exit(process.returncode)