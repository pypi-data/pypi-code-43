import sys
from .run_shell import run_shell
from .load_all_build_dirs_from_env import load_all_build_dirs_from_env

def api_build(files_build_compose=[], env_vars={}, args=[]):
  build_dirs = []

  service = False
  if len(args) > 0 and args[0][:1] != '-':
    service = args[0]

  if service:
    serviceKey = 'STACKD_BUILD_DIR_'+service.upper().replace('-','_')
    if serviceKey in env_vars:
      build_dirs.append(env_vars[serviceKey])
    else:
      if 'STACKD_BUILD_DIR' in env_vars and env_vars['STACKD_BUILD_DIR'] != '':
        build_dirs.append(env_vars['STACKD_BUILD_DIR'])
  else:
    if 'STACKD_BUILD_DIR' in env_vars and env_vars['STACKD_BUILD_DIR'] != '':
      build_dirs.append(env_vars['STACKD_BUILD_DIR'])
    build_dirs = load_all_build_dirs_from_env(env_vars, build_dirs)

  if len(build_dirs) == 0:
    build_dirs.append('.')

  parameters = env_vars['STACKD_BUILD_PARAMETERS']

  for build_dir in build_dirs:
    print('stackd build from '+build_dir)

    process = run_shell([
      'docker-compose',
      list(map(lambda c: ['-f' ,c], files_build_compose)),
      parameters,
      'build',
      args,
    ], cwd=build_dir)

    if(process.returncode != 0):
      sys.exit(process.returncode)
