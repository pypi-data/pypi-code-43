from smart_utils.aws.aws import AWSClient
from os import getenv
from abc import ABCMeta, abstractmethod
import logging


ACCESS_KEY = getenv('AWS_ACCESS_KEY_ID', "N/A")
SECRET_KEY = getenv('AWS_SECRET_ACCESS_KEY', "N/A")


class ConfigGetter:
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_config(self):
        pass


class ConfigGetterAws(ConfigGetter):
    
    def __init__(self,app_name):

        self.app_name = app_name
        self.client = AWSClient(ACCESS_KEY,SECRET_KEY, "ssm")
        self.sentry_dsn_name = "SENTRY_DSN_" + app_name
    
    
    def get_config(self):
        
        try:
            yml_config =  self.client.get_parameter(self.app_name)
            sentry_dsn = self.client.get_parameter(self.sentry_dsn_name)
            if not yml_config and not self.app_name == "default":
                yml_config = self.client.get_parameter("default")
                sentry_dsn = None
                logging.warning("Configuration {} not found, default was obtained".format(self.app_name))
        except Exception as e:
            logging.warning("Error in the ssm-AWS process: {}, configuration-generic was obtained". format(e))
            yml_config = None 
            sentry_dsn = None
        finally:
            return yml_config, sentry_dsn
