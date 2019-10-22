import yaml
import os
from shutil import copyfile

from .paths import get_bundle_dir
from .parse_yaml import parse_yaml

def dep_iter_vars(env_vars, immutable_vars):
  for var_key, value in immutable_vars:
    if('file' in value):
      file = value.get('file')
      file = os.path.expandvars(file) # expand env vars
      if file[0] != '/':
        bundle_dir = get_bundle_dir()
        config_dirname = os.path.dirname(file)
        config_dirpath = bundle_dir + '/' + config_dirname
        if not os.path.exists(config_dirpath):
          os.makedirs(config_dirpath)
        config_basename = os.path.basename(file)
        copyfile(file, config_dirpath+'/'+config_basename)


def build_stack_compose_dependencies(files_compose=[], env_vars={}):
  for file in files_compose:
    yaml_file = parse_yaml(file)

    if 'secrets' in yaml_file:
      dep_iter_vars(env_vars, yaml_file['secrets'].items())

    if 'configs' in yaml_file:
      dep_iter_vars(env_vars, yaml_file['configs'].items())
