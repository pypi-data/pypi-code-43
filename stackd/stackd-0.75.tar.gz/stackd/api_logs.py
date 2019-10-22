import sys
import subprocess

from .run_shell import run_shell

def api_logs(files_compose=[], env_vars={}, args=[]):
  if len(args):
    fullServiceName = env_vars['STACKD_STACK_NAME']+'_'+args.pop(0)
    process = run_shell(['docker','service','logs',fullServiceName,args])
  else:
    services = subprocess.check_output([
      'docker','stack','services',env_vars['STACKD_STACK_NAME'],
      '--format', '{{.Name}}'
    ]).decode("utf-8").strip().split("\n")
    process = run_shell(['docker-service-logs',services,args])
  if(process.returncode != 0):
      sys.exit(process.returncode)