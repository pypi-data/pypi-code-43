from .run_shell import run_shell

def cmd_after_clear(env_vars={}):

  if 'STACKD_AFTER_CLEAR_SCRIPT' in env_vars:
    script = env_vars['STACKD_AFTER_CLEAR_SCRIPT']
  else:
    script = False

  if script:

    print("running afer-clear script: "+script)
    process = run_shell([script], env=env_vars)

    return process