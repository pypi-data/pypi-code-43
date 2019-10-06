import configparser


class Config:
    """
    Static class to manage config data from a config.ini file
    """
    _api_manager: dict = {}
    _config_parser: configparser.ConfigParser

    @staticmethod
    def add_config(config_path):
        """
        Add a config.ini file and save its contents to the Config instance
        :param config_path: path to the config.ini file
        """
        cp = configparser.ConfigParser()
        Config._config_parser = cp
        if not len(cp.read(config_path)) == 0:
            if 'api_manager' in cp:
                Config._api_manager = cp['api_manager']
            else:
                raise ValueError("Config file is missing an 'api_manager' section")
        else:
            raise ValueError("Config file not found for path: " + config_path)

    @staticmethod
    def get_api_url():
        """
        :return: return API url from config as string
        """
        api_url = Config._api_manager["url"]
        # if the url is missing a trailing /, add it. That way the url format is consistent
        if api_url[-1] != "/":
            api_url += "/"
        return api_url

    @staticmethod
    def get_job_token():
        """
        :return: return job token from config as string, return None if not found
        """
        if "job_token" in Config._api_manager:
            return Config._api_manager["job_token"]
        return None

    @staticmethod
    def get_config_parser() -> configparser.ConfigParser:
        """
        :return: return config parser of config.ini file
        """
        return Config._config_parser
