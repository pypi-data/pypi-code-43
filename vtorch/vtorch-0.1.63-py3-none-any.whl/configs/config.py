import os
import json
import logging
from vtorch.common import Registrable


class Config(Registrable):
    def __init__(self, experiment_name: str, logs_dir: str = "logs", version: int = None):
        self.logs_dir = logs_dir
        self.experiment_name = experiment_name
        self.version = version

    @classmethod
    def read(cls, config_path: str) -> 'Config':
        with open(config_path, "r", encoding="utf-8") as f:
            config_file = json.load(f)
        if "experiment_name" not in config_file:
            config_file["experiment_name"] = os.path.splitext(os.path.basename(config_path))[0]
        return cls(**config_file)

    def logging_path(self) -> str:
        if self.version is not None:
            return os.path.join(self.logs_dir, f"version_{self.version}", self.experiment_name)
        return os.path.join(self.logs_dir, self.experiment_name)

    def logger(self, mode: str = 'w') -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        logs_path = self.logging_path()
        if not os.path.exists(logs_path):
            os.makedirs(logs_path)

        fh = logging.FileHandler(os.path.join(logs_path, "log.log"), mode=mode, encoding='utf-8')

        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(module)s : %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger
