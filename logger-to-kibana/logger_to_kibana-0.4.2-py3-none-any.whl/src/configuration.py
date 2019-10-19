from localconfig import config
import os

config_location = os.getenv('LOGGER_TO_KIBANA_CONFIG', "settings.ini")
print("Configuration loaded from", config_location)

config.read(config_location)
