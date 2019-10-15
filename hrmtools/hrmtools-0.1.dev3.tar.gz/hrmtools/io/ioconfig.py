""" function to find and open config files """
import os
from .. import config
import yaml

def find_config(config_name):
    for conf_dir in config.config_path:
        f = os.path.join(conf_dir, config_name)
        if os.path.exists(f):
            return f
    raise IOError('Could not find %r in any of the directories: %r'%(config_name, config.config_path))

def load_yaml(config_name):
    with open(find_config(config_name)) as f:
        d = yaml.load(f.read())
    return d
    

        
    
    