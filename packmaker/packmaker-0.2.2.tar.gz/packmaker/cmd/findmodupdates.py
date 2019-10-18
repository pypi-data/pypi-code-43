# vim:set ts=4 sw=4 et nowrap syntax=python ff=unix:
#
# Copyright 2019 Mark Crewson <mark@crewson.net>
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

import datetime
import dateutil.parser

from ..curse.curseforge import Curseforge
from ..builder.base import BaseBuilder
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.log import getlog
from ..framew.outputter import ListOutputter

##############################################################################


class FindModUpdatesCommand (Subcommand):
    """
    Search curseforge for newer/updated versions of mods.
    """

    name = 'findmodupdates'

    def setup(self):
        super(FindModUpdatesCommand, self).setup()
        self.setup_api()
        self.builder = BaseBuilder()
        self.outputter = ListOutputter()

    def setup_api(self):
        authn_token = self.config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def get_cmdline_parser(self):
        parser = super(FindModUpdatesCommand, self).get_cmdline_parser()
        self.builder.add_cmdline_args(parser)
        self.outputter.add_argument_group(parser)
        return parser

    def run_command(self, parsed_args):
        self.builder.setup_build(parsed_args)

        newmods = []

        getlog().info('Searching for newer versions of mods ...')
        for resolvedmod in self.builder.packlock.get_all_mods():
            try:
                modfile_found = None
                latestTimestamp = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
                for modfile in self.api.get_addon_files(resolvedmod.projectId):
                    if self.builder.packlock.get_metadata('minecraft_version') not in modfile['gameVersion']:
                        continue
                    timestamp = dateutil.parser.parse(modfile['fileDate'])
                    if timestamp > latestTimestamp:
                        modfile_found = modfile
                        latestTimestamp = timestamp

                if modfile_found is None:
                    raise Exception('Cannot find a mod file for {}'.format(resolvedmod.name))

                if modfile_found['id'] != resolvedmod.fileId:
                    newmods.append((resolvedmod.fileName, modfile_found['fileName']))
            except KeyError:
                newmods.append(('{} [NEW]'.format(resolvedmod.name), ''))

        self.outputter.produce_output(parsed_args,
                                      ('current version', 'new version'),
                                      ((m[0], m[1]) for m in newmods))

##############################################################################
# THE END
