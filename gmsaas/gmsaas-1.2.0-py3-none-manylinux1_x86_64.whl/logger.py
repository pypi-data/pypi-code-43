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
Application logger
"""

import logging
import os
import sys
import click

import gmsaas

from .settings import CONFIG_DIR, get_gmsaas_log_path


def get_logger(logger_name=gmsaas.__application__, version=gmsaas.__version__):
    """
    Create and configure a logger using a given name.
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)

    application_str = logger_name
    if version:
        application_str += " " + version
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s "
            "[{application}:%(process)d] "
            "[%(levelname)s] "
            "%(message)s".format(application=application_str)
        ),
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    file_log_handler = logging.FileHandler(get_gmsaas_log_path())
    file_log_handler.setLevel(logging.DEBUG)
    file_log_handler.setFormatter(formatter)

    local_logger = logging.getLogger(logger_name)
    local_logger.setLevel(logging.DEBUG)
    local_logger.addHandler(file_log_handler)

    if "GM_LOG_TO_STDERR" in os.environ:
        console_log_handler = logging.StreamHandler(sys.stdout)
        console_log_handler.setLevel(logging.DEBUG)
        console_log_handler.setFormatter(formatter)
        local_logger.addHandler(console_log_handler)

    return local_logger


LOGGER = get_logger()


def echo_info(message):
    """
    Print message in stdout and log it
    """
    LOGGER.info(message)
    click.echo(message=message)
