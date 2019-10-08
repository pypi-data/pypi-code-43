import configparser
import os

from news2play.common import utils

# default config
storage_conf = "./storage/conf"
storage_data = "./storage/data"
storage_log = "./storage/logs"

configfile_name = os.path.join(storage_conf, 'news2play.ini')

# Check if there is already a configuration file
if not os.path.isfile(configfile_name):
    print(f"{utils.bcolor.WARNING}Use default configuration.{utils.bcolor.ENDC}")
    # Create the configuration file as it doesn't exist yet
    cfg_file = open(configfile_name, 'w')

    # Add content to the file
    config = configparser.ConfigParser()

    config.add_section('audio')
    config.set('audio', 'type', 'mp3')

    config.add_section('aws')
    config.set('aws', 'region_name', 'us-east-2')
    config.set('aws', 'role_arn', 'arn:aws:iam::595543519941:role/news2play')
    config.set('aws', 'polly_voice', 'Kendra')
    config.set('aws', 's3_bucket', 'carplayfilebucket')

    config.add_section('azure')
    config.set('azure', 'tts_voice', 'en-US-JessaNeural')
    config.set('azure', 'tts_voice_style', 'empathy')

    config.write(cfg_file)
    cfg_file.close()
else:
    print(f'''{utils.bcolor.WARNING}Use config file "{configfile_name}" for configuration.{utils.bcolor.ENDC}''')

# Load the configuration file
with open(configfile_name) as f:
    config_info = f.read()

config = configparser.ConfigParser()
config.read_string(config_info)

audio_type = config['audio']['type']

# aws config
region_name = config['aws']['region_name']
role_arn = config['aws']['role_arn']

polly_voice = config['aws']['polly_voice']
s3_bucket = config['aws']['s3_bucket']

# Azure config
azure_voice = config['azure']['tts_voice']
azure_voice_style = config['azure']['tts_voice_style']
