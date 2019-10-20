from .cmd_rm import cmd_rm
from .cmd_vc import cmd_vc
from .cmd_before_clear import cmd_before_clear
from .cmd_after_clear import cmd_after_clear

def cmd_clear(env_vars={}):

  process = cmd_before_clear(env_vars)
  if(process and process.returncode != 0):
      return process

  process = cmd_rm(env_vars)
  if(process.returncode != 0):
      return process

  process = cmd_vc(env_vars)
  if(process.returncode != 0):
      return process

  process = cmd_after_clear(env_vars)
  if(process and process.returncode != 0):
      return process