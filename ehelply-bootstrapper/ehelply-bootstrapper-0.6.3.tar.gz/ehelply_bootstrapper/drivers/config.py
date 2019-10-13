from ehelply_bootstrapper.drivers.driver import Driver
from ehelply_bootstrapper.utils.connection_details import ConnectionDetails
from ehelply_bootstrapper.utils.config import load_config
from typing import List


class Config(Driver):
    def __init__(self, config_path: str, configs: List[str] = None, connection_details: ConnectionDetails = None,
                 dev_mode: bool = False, verbose: bool = False):
        super().__init__(connection_details, dev_mode, verbose)
        self.config_path: str = config_path
        self.configs: List[str] = configs

    def setup(self):
        load_config(self.config_path, self.configs)
