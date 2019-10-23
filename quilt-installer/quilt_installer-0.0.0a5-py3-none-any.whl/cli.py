#!/usr/bin/env python3
import json
import os

import click

from .config import TELEMETRY_DISABLE_ENVVAR_NAME
from .session_log import SessionLog
from .install_flow import install as _install

@click.group()
def cli():
    pass

@cli.command()
@click.option('--dev-mode', is_flag=True, help=f"Run in development mode. Disables anonymous metric collection. "
                                               f"Metrics can also be disabled by setting the environment variable "
                                               f"{TELEMETRY_DISABLE_ENVVAR_NAME}=True")
@click.option('--config-yaml', default=None, help="Path to config YAML file for development. Can be either a local "
                                                  "file or a file on s3 in the form 's3://MYBUCKET/MYKEY/yaml'")
def install(dev_mode, config_yaml):
    if dev_mode:
        disable_telemetry = True
    else:
        disable_telemetry = bool(os.environ.get(TELEMETRY_DISABLE_ENVVAR_NAME, False))

    _install(installer_config_yaml_loc=config_yaml, disable_telemetry=disable_telemetry)



@cli.group()
def utils():
    pass

@utils.command(help="Decode and view a base64 encoded debug string")
@click.argument('debug-string', required=True, type=str)
def decode_debug_str(debug_string):
    s = SessionLog.decode_base64(debug_string)
    print(json.dumps(s, indent=4))


# if __name__ == '__main__':
#     cli()
