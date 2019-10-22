import os
import logging.config
from pathlib import Path
from functools import wraps

import yaml

def contendo_logging_setup(
    default_path='{}/contendo_logging.yaml'.format(Path(__file__).parent),
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    def set_config_level(config, level):
        map = {logging.DEBUG: 'DEBUG', logging.INFO: 'INFO', logging.WARNING: 'WARNING', logging.ERROR: 'ERROR', logging.FATAL: 'FATAL'}
        for key, value in config.items():
            if key=='level':
                config[key] = map[level]
            elif type(value)==dict:
                set_config_level(value, level)
            else:
                continue

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        set_config_level(config, default_level)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def contendo_function_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func.__globals__['logger'] = logging.getLogger(func.__name__)
        return func(*args, **kwargs)
    return wrapper

def contendo_classfunction_logger(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        func.__globals__['logger'] = logging.getLogger('{}.{}'.format(type(self).__name__, func.__name__))
        return func(self, *args, **kwargs)
    return wrapper

if __name__ == '__main__':
    contendo_logging_setup(default_level=logging.WARNING)
