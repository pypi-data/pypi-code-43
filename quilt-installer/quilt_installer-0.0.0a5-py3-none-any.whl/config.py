from appdirs import user_data_dir
import boto3
from botocore import UNSIGNED
from botocore.client import Config as BotocoreConfig
from pathlib import Path
from ruamel import yaml
import uuid

APP_NAME = "Quilt"
APP_AUTHOR = "QuiltData"
BASE_DIR_PATH = Path(user_data_dir(APP_NAME, APP_AUTHOR))
TELEMETRY_CONFIG_PATH = BASE_DIR_PATH / "installer_telemetry.yaml"

TELEMETRY_DISABLE_ENVVAR_NAME = "DISABLE_QUILT_TELEMETRY"
TELEMETRY_CLIENT_VERSION = Path(Path(__file__).parent, "VERSION").open().read()
TELEMETRY_CLIENT_TYPE = "installer-cli-python"
TELEMETRY_USER_AGENT = "QuiltCli"
TELEMETRY_URL = "https://q3p9cwyrt8.execute-api.us-east-1.amazonaws.com/Prod/metrics/installer"
TELEMETRY_SCHEMA_VERSION = "installer-progress-v0"

CONFIG_YAML_S3_BUCKET = "quilt-marketplace"
CONFIG_YAML_S3_KEY = "releases/production/quilt3.0/installer_config.yaml"

INSTALLER_CONFIG_SCHEMA_VERSION = 1





class ConfigConsts:
    def __init__(self,
                 cfn_template_url,
                 subscribe_prompt,
                 install_success_message,
                 install_failed_open_ticket_message):
        self.cfn_template_url = cfn_template_url
        self.subscribe_prompt = subscribe_prompt
        self.install_success_message = install_success_message
        self.install_failed_open_ticket_message = install_failed_open_ticket_message


def retrieve_config_yaml_from_s3(s3_loc=None):
    if s3_loc is None:
        # Pull the default, publicly-readable installer_config.yaml from s3
        s3_client = boto3.client('s3', config=BotocoreConfig(signature_version=UNSIGNED))
        bucket = CONFIG_YAML_S3_BUCKET
        key = CONFIG_YAML_S3_KEY
    else:
        assert s3_loc.startswith("s3://")
        s3_client = boto3.client('s3')
        s3_loc = s3_loc.replace("s3://", '')
        bucket = s3_loc.split("/")[0]
        key = '/'.join(s3_loc.split("/")[1:])

    response = s3_client.get_object(Bucket=bucket, Key=key)
    yml = yaml.safe_load(response["Body"])
    return yml

def retrieve_config_yaml_from_file(config_file_path):
    with Path(config_file_path).open() as f:
        config_yaml = yaml.safe_load(f)
    return config_yaml





def get_cross_session_id(verbose=False):

    def vlog(*s):
        if verbose:
            print(*s)

    if TELEMETRY_CONFIG_PATH.exists():
        vlog(f"Installer telemetry config file exists! ({TELEMETRY_CONFIG_PATH})")
        with open(TELEMETRY_CONFIG_PATH, 'r') as f:
            y = yaml.safe_load(f)
        if "device_id" in y.keys():
            vlog(f'Installer telemetry config file had an existing cross_session_id! ({y["cross_session_id"]})')
            return y["cross_session_id"]

    else:
        y = {}

    y["cross_session_id"] = str(uuid.uuid4())
    vlog(f'Could not find existing cross_session_id, creating a new one. ({y["cross_session_id"]})')

    with open(TELEMETRY_CONFIG_PATH, 'w') as f:
        vlog(f'Saving new cross_session_id to installer telemetry config file')
        yaml.safe_dump(y, f, default_flow_style=False)

    return y["cross_session_id"]
