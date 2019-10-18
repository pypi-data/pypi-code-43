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

import os

import yaml
try:
    yamlload = yaml.full_load
except AttributeError:
    yamlload = yaml.load

from .packlock import PackLock

##############################################################################


class PackDefinition (object):

    def __init__(self, filenames):
        super(PackDefinition, self).__init__()
        self.definition_filenames = filenames
        self.name = None
        self.title = None
        self.version = None
        self.authors = []
        self.icon = None
        self.news = None
        self.minecraft_version = None
        self.forge_version = None
        self.routhio = None
        self.mods = {}
        self.files = []

    def load(self):
        for filename in self.definition_filenames:
            self.load_one(filename)

    def load_one(self, filename):
        with open(filename, 'r') as pf:
            packtext = pf.read()
        packdict = yamlload(packtext)
        self.populate(packdict)

    def populate(self, packdict):
        if 'name' in packdict:
            self.name = packdict['name']
        if 'title' in packdict:
            self.title = packdict['title']
        if 'version' in packdict:
            self.version = packdict['version']
        if 'authors' in packdict:
            self.authors.extend(packdict['authors'])
        if 'icon' in packdict:
            self.icon = packdict['icon']
        if 'news' in packdict:
            self.news = packdict['news']
        if 'minecraft' in packdict:
            self.minecraft_version = packdict['minecraft']
        if 'forge' in packdict:
            self.forge_version = packdict['forge']
        if 'routhio' in packdict:
            self.routhio = packdict['routhio']

        if 'mods' in packdict:
            for mod in packdict['mods']:
                slug, moddef = mod.popitem()
                self.mods[slug] = ModDefinition(slug, moddef)

        if 'files' in packdict:
            self.files.extend(packdict['files'])

    def get_mod(self, slug):
        return self.mods[slug]

    def get_all_mods(self):
        return self.mods.values()

    def get_packlock(self):
        lockfile = os.path.splitext(self.definition_filenames[0])[0] + '.lock'
        return PackLock(lockfile)

##############################################################################


class ModDefinition (object):

    default_version = 'latest'
    default_clientonly = False
    default_serveronly = False
    default_optional = False
    default_recommendation = 'starred'
    default_selected = False
    default_description = 'a mod'

    def __init__(self, slug, moddict):
        super(ModDefinition, self).__init__()
        self.slug = slug
        if moddict is not None:
            self.version = moddict.get('version', ModDefinition.default_version)
            self.clientonly = moddict.get('clientonly', ModDefinition.default_clientonly)
            self.serveronly = moddict.get('serveronly', ModDefinition.default_serveronly)
            self.optional = moddict.get('optional', ModDefinition.default_optional)
            self.recommendation = moddict.get('recommendation', ModDefinition.default_recommendation)
            self.selected = moddict.get('selected', ModDefinition.default_selected)
            self.description = moddict.get('description', ModDefinition.default_description)
        else:
            self.version = ModDefinition.default_version
            self.clientonly = ModDefinition.default_clientonly
            self.serveronly = ModDefinition.default_serveronly
            self.optional = ModDefinition.default_optional
            self.recommendation = ModDefinition.default_recommendation
            self.selected = ModDefinition.default_selected
            self.description = ModDefinition.default_description

        if self.recommendation not in ('starred', 'avoid'):
            raise Exception('mod recommendation for "{}" must be either "starred" or "avoid"'.format(self.slug))

##############################################################################
# THE END
