# Copyright 2019 Genymobile
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Cli for subcommand config
"""


import click

from gmsaas.logger import echo_info
from ..storage import get_config_storage

SDK_PATH_KEY = "android-sdk-path"
VALID_KEYS = (SDK_PATH_KEY,)


@click.group()
def config():
    """
    Manage your Genymotion Cloud SaaS configuration properties
    """


@click.command("set")
@click.argument("entry", type=click.Choice(VALID_KEYS))
@click.argument("value")
def config_set(entry, value):
    """
    Set a Genymotion Cloud SaaS configuration property
    """
    storage = get_config_storage()
    storage.put(entry, value)


@click.command("get")
@click.argument("entry", type=click.Choice(VALID_KEYS))
def config_get(entry):
    """
    Print the value of a Genymotion Cloud SaaS configuration property
    """
    storage = get_config_storage()
    value = storage.get(entry)

    echo_info(str(value))


@click.command("list")
def config_list():
    """
    List all Genymotion Cloud SaaS configuration and their values
    """
    storage = get_config_storage()
    props = storage.get_all()
    output = []
    for key in sorted(set(props.keys()).union(VALID_KEYS)):
        value = props.get(key, "")
        output.append("{}={}".format(key, value))
    echo_info("\n".join(output))


config.add_command(config_set)
config.add_command(config_get)
config.add_command(config_list)
