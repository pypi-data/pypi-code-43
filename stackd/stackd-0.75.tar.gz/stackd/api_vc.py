import sys
from .cmd_vc import cmd_vc

def api_vc(env_vars={}):

  process = cmd_vc(env_vars)
  if(process.returncode != 0):
      sys.exit(process.returncode)