from .cmd_exec import cmd_exec

def api_bash(env_vars={}, args=[]):
  cmd_exec(env_vars, args, options=['-it'], entrypoint='bash')
