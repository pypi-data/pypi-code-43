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

import json

from ..curse.curseforge import Curseforge
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.log import getlog

##############################################################################


class UpdateDbCommand (Subcommand):
    """
    Download and compile a new mods database from curseforge.
    """
    name = 'updatedb'

    batchsz = 1000

    def setup(self):
        super(UpdateDbCommand, self).setup()
        self.setup_api()
        self.setup_db()

    def setup_api(self):
        authn_token = self.config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def setup_db(self):
        db_filename = self.config.get('curseforge::moddb_filename')
        if db_filename is None:
            raise ConfigError('No moddb_filename parameter in configuration')
        self.db_filename = db_filename

    def run_command(self, parsed_args):
        moddict = {}
        processedIDs = []

        log = getlog()

        log.info('Scanning for list of possible mods...')
        for addon in self.api.yield_addons_by_criteria(gameId=432,
                                                       sectionId=6,
                                                       sort='LastUpdated',
                                                       pageSize=UpdateDbCommand.batchsz):
            processedIDs.append(addon['id'])

        log.info('\nReading mods information...')
        chunks = [processedIDs[i:i + UpdateDbCommand.batchsz] for i in range(0, len(processedIDs), UpdateDbCommand.batchsz)]
        for chunkIDs in chunks:
            addons = self.api.get_addons(chunkIDs)
            for mod in addons:
                if not mod:
                    continue
                moddict[mod['slug']] = {'id': mod['id'],
                                        'name': mod['name'],
                                        'slug': mod['slug'],
                                        'authors': mod['authors'],
                                        'websiteUrl': mod['websiteUrl']
                                        }

        log.info('Writing mods database...')
        db = json.dumps(moddict)
        with open(self.db_filename, 'w') as dbfile:
            dbfile.write(db)

        log.info('Done.')

##############################################################################
# THE END
