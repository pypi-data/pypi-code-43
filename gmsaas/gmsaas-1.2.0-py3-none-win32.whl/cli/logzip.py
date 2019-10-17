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
Cli for command logzip
"""

import click

from gmsaas.errors import LogzipError
from gmsaas.logger import echo_info
from gmsaas.saas.logcollector import LogCollector


@click.command("logzip")
def logzip():
    """
    Zip all `gmsaas` log files into a ZIP archive
    """
    collector = LogCollector()
    try:
        archive_path = collector.process()
    except Exception as exception:
        raise LogzipError(exception)

    echo_info("`{}` generated.".format(archive_path))
