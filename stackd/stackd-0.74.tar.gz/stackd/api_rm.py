import sys
from .cmd_rm import cmd_rm

def api_rm(env_vars, args=[]):

  process = cmd_rm(env_vars, args)

  if(process.returncode != 0):
      sys.exit(process.returncode)