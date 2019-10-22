import yaml
import subprocess

from .docker_compose_config import docker_compose_config
from .run_shell import run_shell

def autocreate_networks(files_compose, args=[]):
  yaml_dump = docker_compose_config(files_compose)
  config = yaml.safe_load(yaml_dump)
  if(config['networks']):
    for network_key,network_def in config['networks'].items():
      if 'external' in network_def and network_def['external']:
        if 'name' in network_def:
          network_name = network_def['name']
        else:
          network_name = network_key

        networkLs = subprocess.check_output([
          'docker','network','ls',
          '--filter', 'name='+network_name,
          '-q',
        ]).decode("utf-8").strip()

        if networkLs:
          continue

        if 'driver' in network_def:
          network_driver = network_def['driver']
        else:
          network_driver = 'overlay'
          
        print(
          'Automatic creation of missing external network "'+network_name+
          '" with driver "'+network_driver+'"'
        )

        process = run_shell([
          'docker','network','create',
          '--driver', network_driver,
          network_name,
          args,
        ])
        if(process and process.returncode != 0):
          return process


  return True