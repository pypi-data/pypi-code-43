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
GMSaaS entry point
"""

import sys

import click

import gmsaas
from .auth import auth
from .config import config
from .recipes import recipes
from .instances import instances
from .logzip import logzip
from ..logger import LOGGER


def get_loggable_args(args):
    """
    Return the args list to log, critical data are removed.
    """
    command = None
    subcommand = None
    subcommand_idx = 0
    for idx, arg in enumerate(args):
        if command:
            subcommand = arg
            subcommand_idx = idx
            break
        if not arg.startswith("-"):
            command = arg
            continue
    if command == "auth" and subcommand == "login":
        # Remove information related to authentication
        args = args[: subcommand_idx + 1]
    return args


@click.group()
@click.version_option(version=gmsaas.__version__)
@click.pass_context
def main(ctx):
    """
    Command line utility for Genymotion SaaS
    """
    LOGGER.info("==== START args: %s ====", get_loggable_args(sys.argv[1:]))
    ctx.ensure_object(dict)


main.add_command(auth)
main.add_command(config)
main.add_command(instances)
main.add_command(recipes)
main.add_command(logzip)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
