import sys
from .run_shell import run_shell

def cmd_rm(env_vars, args=[]):

  # process = run_shell(['docker','stack','rm',env_vars['STACKD_STACK_NAME'],args])

  # in future
  # process = run_shell(['docker','stack','rm','--detach=false',env_vars['STACKD_STACK_NAME'],args])

  process = run_shell(['docker-stack-rm',env_vars['STACKD_STACK_NAME'],args])

  return process