import sys
from .cmd_before_clear import cmd_before_clear

def api_before_clear(env_vars={}):

  process = cmd_before_clear(env_vars)
  if(process.returncode != 0):
      sys.exit(process.returncode)