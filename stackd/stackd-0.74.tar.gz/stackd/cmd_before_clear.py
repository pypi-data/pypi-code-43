from .run_shell import run_shell

def cmd_before_clear(env_vars={}):

  if 'STACKD_BEFORE_CLEAR_SCRIPT' in env_vars:
    script = env_vars['STACKD_BEFORE_CLEAR_SCRIPT']
  else:
    script = False

  if script:

    print("running before-clear script: "+script)
    process = run_shell([script], env=env_vars)

    return process