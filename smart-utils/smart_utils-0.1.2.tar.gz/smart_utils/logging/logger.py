import logging.config
import yaml
from yaml.scanner import ScannerError
from yaml.parser import ParserError
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from smart_utils.logging.config import ConfigGetter

DEFAULT_FORMAT = '%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s  - %(message)s'
logging.basicConfig(format=DEFAULT_FORMAT, level=logging.INFO)


class LoggerConstructor:

    def __init__(self,getter:ConfigGetter, environment):

        self.getter = getter
        self.environment = environment

    def __load_configuration(self,yml_config):
        
        try:
            logging_config = yaml.safe_load(yml_config)      
            logging.config.dictConfig(logging_config)
            logging.info("Loaded setting of .yml")
            return "main"
        except (ValueError, ScannerError,ParserError):
            logging.error("Configuration failed to load, review yml. Getting generic logger")        

    def _activate_sentry(self,sentry_dsn):
    
        try:
            sentry_sdk.init(
                environment = self.environment,
                dsn= sentry_dsn,
                integrations=[ 
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
                ]
            )
            return True
        except Exception as e:
            logging.error("Error to activate Sentry {}".format(e))
            return False


    def generate_logger(self):

        yml_config,sentry_dsn = self.getter.get_config()
        logging_name = None
        if yml_config:
            logging_name = self.__load_configuration(yml_config)
            if sentry_dsn and logging_name:
                if self._activate_sentry(sentry_dsn):
                    logging.info("Activate Sentry")
        return logging.getLogger(logging_name)



