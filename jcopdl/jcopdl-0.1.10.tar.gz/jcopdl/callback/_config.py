class Config:
    def __init__(self):
        pass

    def __repr__(self):
        params = [f"{k}={v}" for k, v in sorted(self.__dict__.items())]
        return f"Config({', '.join(params)})"


def set_config(config_dict):
    config = Config()
    config.__dict__ = config_dict
    return config
