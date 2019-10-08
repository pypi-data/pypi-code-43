import os
import configparser
import logging

config = configparser.ConfigParser()
config.optionxform = str  # So capitals stay capitals

# File containing variables:
duodata_CONFIG = os.path.join(os.path.expanduser('~'), '.duodata_data.cfg')


if os.path.exists(duodata_CONFIG):
    logging.info('Reading %s...' % duodata_CONFIG)
    config.read(duodata_CONFIG)
else:
    logging.error('Missing config-file: %s' % duodata_CONFIG)

# Directory waar data wordt opgeslagen
duodata_data_dir = config.get('algemeen', 'duodata_data_dir')

# Google API key
google_api_key = config.get('algemeen', 'google_api_key')
