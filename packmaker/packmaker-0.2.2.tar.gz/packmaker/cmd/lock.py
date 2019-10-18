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
import json

from ..curse.curseforge import Curseforge
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.log import getlog
from ..packdef import PackDefinition

##############################################################################


class LockCommand (Subcommand):
    """
    Lock the modpack. Find mod download urls, generate a packmaker.lock file.
    """

    name = 'lock'

    default_packmaker_yml = 'packmaker.yml'

    def setup(self):
        super(LockCommand, self).setup()
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

    def get_cmdline_parser(self):
        parser = super(LockCommand, self).get_cmdline_parser()
        parser.add_argument('packdef',
                            nargs='*',
                            default=[LockCommand.default_packmaker_yml],
                            help='modpack definition file')
        return parser

    def run_command(self, parsed_args):

        log = getlog()
        log.info('Loading curseforge database ...')
        with open(self.db_filename, 'r') as cf:
            db = json.load(cf)

        log.info('Reading pack definition ...')
        pack = PackDefinition(parsed_args.packdef)
        pack.load()

        packlock = pack.get_packlock()
        packlock.set_all_metadata(pack)

        log.info('Resolving mods...')
        for moddef in pack.get_all_mods():
            if moddef.slug in db:
                modid = db[moddef.slug]['id']
                modname = db[moddef.slug]['name']
                modauthor = db[moddef.slug]['authors'][0]['name']
                modwebsite = db[moddef.slug]['websiteUrl']
            else:
                log.info('Cannot find mod in local db: {}\n  Manually searching...'.format(moddef.slug))

                searchresults = list(({'name': mod['name'], 'id': mod['id'], 'slug': mod['slug'],
                                       'authors': mod['authors'], 'websiteUrl': mod['websiteUrl']}
                                      for mod in self.api.yield_addons_by_criteria(gameId=432, sectionId=6,
                                                                                   gameVersions='1.12.2',
                                                                                   searchFilter=moddef.slug)))

                if len(searchresults) < 1:
                    raise Exception('Cannot find a mod named \'{}\''.format(moddef.slug))
                elif len(searchresults) > 1:
                    log.info('  Multiple search results found ({}). Using the first one'.format(len(searchresults)))

                searchresult = searchresults[0]
                log.info('  Found it! ... {}'.format(searchresult['slug']))
                modname = searchresult['name']
                modid = searchresult['id']
                modauthor = searchresult['authors'][0]['name']
                modwebsite = searchresult['websiteUrl']

            latestTimestamp = datetime.datetime(2000, 1, 1,
                                                tzinfo=datetime.timezone.utc)
            modfile_found = None
            for modfile in self.api.get_addon_files(modid):
                if pack.minecraft_version not in modfile['gameVersion']:
                    continue
                if moddef.version == 'latest':
                    timestamp = dateutil.parser.parse(modfile['fileDate'])
                    if timestamp > latestTimestamp:
                        modfile_found = modfile
                        latestTimestamp = timestamp

                elif modfile['fileName'] == moddef.version:
                    modfile_found = modfile

            if modfile_found is None:
                raise Exception('Cannot find a mod file for {}'.format(moddef.slug))

            packlock.add_resolved_mod(moddef, {'projectId': modid,
                                               'name': modname,
                                               'author': modauthor,
                                               'website': modwebsite,
                                               'fileId': modfile_found['id'],
                                               'fileName': modfile_found['fileName'],
                                               'downloadUrl': modfile_found['downloadUrl']
                                               })

        log.info('Adding files...')
        for filesdef in pack.files:
            packlock.add_files(filesdef)

        log.info('Adding extra options (if any)...')
        if pack.routhio is not None:
            packlock.add_extraopt('routhio', pack.routhio)

        log.info('Writing pack lock...')
        packlock.save()

        log.info('Done.')

##############################################################################
# THE END
