from typing import Optional
from aws_cf_custom_resources.config_params import ConfigurationParameters


class GlobalConfigManager:
    __config_params: Optional[ConfigurationParameters] = None

    @staticmethod
    def set_params(config_params: ConfigurationParameters) -> None:
        if GlobalConfigManager.__config_params:
            raise ValueError('Configuration parameters already set.')

        GlobalConfigManager.__config_params = config_params

    @staticmethod
    def get_params() -> ConfigurationParameters:
        if not GlobalConfigManager.__config_params:
            raise ValueError('Configuration parameters not set!')

        return GlobalConfigManager.__config_params
