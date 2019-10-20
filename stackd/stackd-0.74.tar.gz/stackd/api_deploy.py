import sys
from .cmd_deploy import cmd_deploy

def api_deploy(files_compose=[], env_vars={}, args=[]):
  process = cmd_deploy(files_compose, env_vars, args)
  if(process.returncode != 0):
    sys.exit(process.returncode)
