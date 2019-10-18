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

from ..curse.curseforge import Curseforge
from ..framew.cmdapplication import Subcommand
from ..framew.config import ConfigError
from ..framew.outputter import ListOutputter

##############################################################################


class SearchCommand (Subcommand):
    """
    Search curseforge for mods.
    """

    name = 'search'

    def setup(self):
        super(SearchCommand, self).setup()
        self.setup_api()
        self.outputter = ListOutputter()

    def setup_api(self):
        authn_token = self.config.get('curseforge::authentication_token')
        if authn_token is None:
            raise ConfigError('No curseforge authentication token')
        self.api = Curseforge(authn_token)

    def get_cmdline_parser(self):
        parser = super(SearchCommand, self).get_cmdline_parser()
        parser.add_argument('searchstring', nargs='+', help='search string')
        self.outputter.add_argument_group(parser)
        return parser

    def run_command(self, arguments):
        results = ((mod['name'], mod['id'], mod['slug'])
                   for mod in self.api.yield_addons_by_criteria(gameId=432, sectionId=6,
                                                                gameVersions='1.12.2',
                                                                searchFilter=' '.join(arguments.searchstring)))

        self.outputter.produce_output(arguments, ('name', 'id', 'slug'), results)

##############################################################################
# THE END
