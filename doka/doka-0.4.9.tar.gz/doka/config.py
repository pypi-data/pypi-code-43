from pathlib import Path


class Config:
    STORAGE_DIR = Path.home().joinpath(*['.doka'])


doka_config = Config()
