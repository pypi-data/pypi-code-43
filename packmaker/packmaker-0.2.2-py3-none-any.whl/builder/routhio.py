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

import hashlib
import json
import os
import shutil
import urllib.parse

from .base import BaseBuilder
from ..download import HttpDownloader, MavenDownloader
from ..forge import Forge
from ..minecraft import Minecraft

##############################################################################


class RouthioBuilder (BaseBuilder):

    build_subloc = 'routhio'

    MAVEN_REPOS = ('https://libraries.minecraft.net/',
                   'https://repo1.maven.org/maven2/',
                   'https://files.minecraftforge.net/maven/'
                   )

    ##########################################################################

    def do_build(self):
        manifest = {'title': self.packlock.get_metadata('title'),
                    'name': self.packlock.get_metadata('name'),
                    'version': self.packlock.get_metadata('version'),
                    'gameVersion': self.packlock.get_metadata('minecraft_version'),
                    'minimumVersion': 2,
                    'objectsLocation': 'objects',
                    'librariesLocation': 'libraries',
                    'tasks': []
                    }

        copytasks = self.copy_local_files(self.build_location('objects'), self.packlock.yield_clientonly_files())
        modtasks, features = self.process_mods()

        if features:
            manifest['features'] = features

        manifest['tasks'] = modtasks
        manifest['tasks'].extend(copytasks)

        version_manifest = self.get_minecraft_version_manifest()
        self.process_forge(version_manifest)
        manifest['versionManifest'] = version_manifest

        routhio = self.packlock.get_extraopt('routhio')
        if routhio is not None and 'launch' in routhio:
            manifest['launch'] = routhio['launch']

        self.log.info('Writing the pack manifest file...')
        with open(os.path.join(self.build_location(), '{}.json'.format(self.packlock.get_metadata('name'))), 'w') as mf:
            mf.write(json.dumps(manifest, indent=2, sort_keys=True))

        if routhio is not None and 'html' in routhio:
            self.log.info('Copy launcher html files ...')
            self.copy_files(files_iterator=routhio['html'])

        pkgfilename = os.path.join(self.release_location(),
                                   '{}-{}-routhio.{}'.format(self.packlock.get_metadata('name'),
                                                             self.packlock.get_metadata('version'),
                                                             self.release_extension))
        self.log.info('Packaging the modpack: {} ...'.format(pkgfilename))
        self.release_pkg(pkgfilename)

    ##########################################################################

    def copy_local_files(self, dest, files_iterator):
        self.log.info('Copying local files ...')
        tasks = []
        for fileloc in files_iterator:
            for root, dirs, files in os.walk(fileloc['location']):
                for file in files:
                    full_filename = os.path.join(root, file)

                    sha1hash = self.calc_sha1(full_filename)
                    sha1dir = os.path.join(sha1hash[0:2], sha1hash[2:4])

                    dest_directory = os.path.join(dest, sha1dir)
                    dest_filename = os.path.join(dest_directory, sha1hash)

                    if not os.path.exists(dest_directory):
                        os.makedirs(dest_directory)

                    shutil.copy2(full_filename, dest_filename)

                    tasks.append({"type": 'file',
                                  "to": os.path.join(root[len(fileloc['location']):], file),
                                  "size": os.path.getsize(full_filename),
                                  "location": os.path.join(sha1dir, sha1hash),
                                  "hash": sha1hash
                                  })
        return tasks

    ##########################################################################

    def process_mods(self):
        tasks = []
        features = []
        self.download_mods(self.packlock.yield_clientonly_mods(include_optional=True))
        for mod in self.packlock.yield_clientonly_mods(include_optional=True):
            localfile = '{}/{}'.format(self.cache_location('mods'), mod.fileName)
            if not os.path.exists(localfile):
                raise Exception('Missing local copy of mod even after downloading: {}'.format(localfile))

            sha1hash = self.calc_sha1(localfile)
            task = {'type': 'url',
                    'to': os.path.join('mods', mod.fileName),
                    'location': mod.downloadUrl,
                    'hash': sha1hash,
                    'size': os.path.getsize(localfile)
                    }

            moddef = self.packlock.get_mod(mod.slug)
            if moddef.optional:
                task['when'] = {'features': [mod.name], 'if': 'requireAny'}
                feature = {'name': mod.name,
                           'description': moddef.description,
                           'recommendation': moddef.recommendation,
                           'selected': moddef.selected
                           }
                features.append(feature)

            tasks.append(task)
        return tasks, features

    ##########################################################################

    def calc_sha1(self, filename):
        h = hashlib.sha1()
        with open(filename, 'rb') as hf:
            data = hf.read(65536)
            while data:
                h.update(data)
                data = hf.read(65536)
        return h.hexdigest()

    ##########################################################################

    def get_minecraft_version_manifest(self):
        mc = Minecraft(self.packlock.get_metadata('minecraft_version'))
        version_manifest = mc.get_version_manifest()

        # tidy up a bit
        version_manifest.pop('logging', None)
        version_manifest.pop('downloads', None)

        return version_manifest

    ##########################################################################

    def process_forge(self, version_manifest):
        downloader = HttpDownloader(self.cache_location('forge'))
        forgedl = Forge(self.packlock.get_metadata('minecraft_version'),
                        self.packlock.get_metadata('forge_version'),
                        downloader)
        self.log.info('Downloading forge installer: {}'.format(forgedl.installer_filename()))
        forgeprofile = forgedl.get_install_profile()

        self.log.info('Finding maven repositories for dependent libraries ...')
        mavenDownloader = MavenDownloader(self.cache_location('library'), self.MAVEN_REPOS)
        for library in forgeprofile['versionInfo']['libraries']:
            # cleanup the library entry a bit
            library.pop('checksums', None)
            library.pop('serverreq', None)
            library.pop('clientreq', None)

            if library['name'].startswith('net.minecraftforge:forge:'):
                universal_url = forgedl.universal_download_url()
                universal_path = urllib.parse.urlparse(universal_url).path[1:]

                downloads = {'artifact': {'path': universal_path,
                                          'url': universal_url,
                                          }}
                library['downloads'] = downloads
                library.pop('url', None)

            else:
                # Find a maven repository hosting this library if necessary
                library['url'] = mavenDownloader.find_maven_repo(library['name'])

            version_manifest['libraries'].append(library)

        for override in ('mainClass', 'minecraftArguments'):
            if override in forgeprofile['versionInfo']:
                version_manifest[override] = forgeprofile['versionInfo'][override]

##############################################################################
# THE END
