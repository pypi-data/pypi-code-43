from os import getenv
from  smart_utils.logging.logger import LoggerConstructor
from smart_utils.logging.config import ConfigGetterAws



APP_NAME = getenv('APP_NAME', "default")
ENVIRONMENT = getenv('sc_environment', "default")


Logger = LoggerConstructor(ConfigGetterAws(APP_NAME), ENVIRONMENT).generate_logger()
