import logging
import json
import os
from .rpc import RuntimeRpc
from featurize_jupyterlab import package_manager

logger = None
config = None
rpc = None


class RuntimeLoggingHandler(logging.StreamHandler):

    def __init__(self, rpc, identity):
        self.rpc = rpc
        self.identity = identity
        super().__init__()

    def emit(self, record):
        self.rpc.log(self.identity, record)


def init_config(config_file=None):
    global config
    with open(config_file if config_file else './config.json', 'r') as f:
        config = json.loads(f.read())


def init_logger():
    global logger
    logging_format = '%(levelname)s %(asctime)s %(message)s'
    logging.basicConfig(
        format=logging_format,
        datefmt="%m-%d %H:%M:%S",
        level=logging.DEBUG
    )

    logger = logging.getLogger(f'runtime{os.getpid()}')
    handler = RuntimeLoggingHandler(rpc, config.get('identity'))
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def init_rpc():
    global rpc
    rpc = RuntimeRpc(config['server_addr'], config['identity'])


def init_packages():
    global config
    for package_name in config['enabled_package'].split(','):
        package_manager.add_package(package_name)


def init_process_env(config_file=None):
    init_config(config_file)
    init_rpc()
    init_logger()
    init_packages()
