import subprocess
import shlex
from .flatten import flatten

def run_shell(cmd, env=None, cwd=None):
  if not isinstance(cmd, list):
    cmd = [cmd]
  cmd = flatten(cmd)
  cmd = ' '.join(cmd)
  cmd = shlex.split(cmd)
  proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env, cwd=cwd)
  try:
    while True:
      output = proc.stdout.readline()
      if output.decode('utf-8').strip() == '' and proc.poll() is not None:
        break
      if output:
        output = output.decode('utf-8')
        output = "\n".join(output.splitlines())
        print(output)
  except KeyboardInterrupt:
    proc.terminate()
  return proc