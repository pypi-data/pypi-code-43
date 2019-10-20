from .cmd_clear import cmd_clear
from .cmd_deploy import cmd_deploy

def api_reset(files_compose=[], env_vars={}, args=[]):
  cmd_clear(env_vars)
  cmd_deploy(files_compose, env_vars, args)