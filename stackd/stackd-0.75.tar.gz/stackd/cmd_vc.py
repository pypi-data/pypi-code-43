import subprocess

from .run_shell import run_shell

def cmd_vc(env_vars={}):

  process = run_shell([
    'docker-stack-volumes-cleanup',
    env_vars['STACKD_STACK_NAME'],
  ])
  return process