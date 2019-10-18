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
import shutil
import zipfile

from .base import BaseBuilder
from ..download import HttpDownloader, MavenDownloader
from ..forge import Forge
from ..minecraft import Minecraft

##############################################################################


class LocalBuilder (BaseBuilder):

    build_subloc = 'local'

    MAVEN_REPOS = ('https://libraries.minecraft.net/',
                   'https://repo1.maven.org/maven2/',
                   'https://files.minecraftforge.net/maven/'
                   )

    ##########################################################################

    def do_build(self):
        self.downloader = HttpDownloader(self.cache_location())

        self.log.info('Copying local files ...')
        self.copy_files(files_iterator=self.packlock.yield_clientonly_files())

        self.log.info('Copying mod files ...')
        self.copy_mods(self.build_location('mods'), self.packlock.yield_clientonly_mods())

        mc = Minecraft(self.packlock.get_metadata('minecraft_version'))

        self.log.info('Copying minecraft client ...')
        self.copy_minecraft_client(mc)

        self.log.info('Copying forge ...')
        self.copy_forge(mc)

    ##########################################################################

    def copy_minecraft_client(self, mc):
        mc.download_client(self.downloader.subdownloader('minecraft'))

        manifest = mc.get_version_manifest()

        # Copy the minecraft client library into place.

        cached_lib = os.path.join(self.cache_location('minecraft'), 'versions', manifest['id'], 'client.jar')
        local_lib = os.path.join(self.build_location('libraries'), 'com', 'mojang', 'minecraft', manifest['id'],
                                 'minecraft-{}-client.jar'.format(manifest['id']))

        if not os.path.exists(os.path.dirname(local_lib)):
            os.makedirs(os.path.dirname(local_lib))

        shutil.copy2(cached_lib, local_lib)

        # Copy the minecraft libraries into place.

        for lib in mc.get_libraries():
            cached_lib = os.path.join(self.cache_location('minecraft'), 'libraries', lib.get_path())

            if lib.must_extract():
                localdir = self.build_location('natives')
                if not os.path.exists(localdir):
                    os.makedirs(localdir)

                with zipfile.ZipFile(cached_lib, 'r') as extractedlib:
                    for name in extractedlib.namelist():
                        excluded = False
                        for exclude in lib.extract_excludes():
                            if name.startswith(exclude):
                                excluded = True
                                break
                        if excluded:
                            continue
                        extractedlib.extract(name, path=localdir)

            else:
                localdir = os.path.join(self.build_location('libraries'), os.path.dirname(lib.get_path()))
                if not os.path.exists(localdir):
                    os.makedirs(localdir)

                local_lib = os.path.join(self.build_location('libraries'), lib.get_path())
                shutil.copy2(cached_lib, local_lib)

        # Copy the minecraft assets into place.

        assetIndexDir = os.path.join(self.build_location('assets'), 'indexes')
        if not os.path.exists(assetIndexDir):
            os.makedirs(assetIndexDir)

        assetIndexFile = '{}.json'.format(manifest['assets'])

        cached_assetIndexFile = os.path.join(self.cache_location('minecraft'), 'assets', 'indexes', assetIndexFile)
        local_assetIndexFile = os.path.join(self.build_location('assets'), 'indexes', assetIndexFile)
        shutil.copy2(cached_assetIndexFile, local_assetIndexFile)

        for key, val in mc.get_assets_index()['objects'].items():
            h = val['hash']
            path = '{}/{}'.format(h[0:2], h)

            cached_assetfile = os.path.join(self.cache_location('minecraft'), 'assets', 'objects', path)
            local_assetfile = os.path.join(self.build_location('assets'), 'objects', path)

            if not os.path.exists(os.path.dirname(local_assetfile)):
                os.makedirs(os.path.dirname(local_assetfile))

            shutil.copy2(cached_assetfile, local_assetfile)

    ##########################################################################

    def copy_forge(self, mc):
        mc.get_version_manifest()

        forgedl = Forge(self.packlock.get_metadata('minecraft_version'),
                        self.packlock.get_metadata('forge_version'),
                        self.downloader.subdownloader('forge'))

        self.log.info('Downloading forge installer: {}'.format(forgedl.installer_filename()))
        forge_fullfilename = forgedl.get_installer_jar()

        with zipfile.ZipFile(forge_fullfilename, 'r') as forgejar:

            forgelib_dir = os.path.dirname(os.path.join(self.build_location('libraries'), forgedl.universal_path()))
            if not os.path.exists(forgelib_dir):
                os.makedirs(forgelib_dir)
            forgejar.extract(forgedl.universal_filename(), path=forgelib_dir)

        forgeprofile = forgedl.get_install_profile()

        self.log.info('Finding maven repositories for dependent libraries ...')
        mavenDownloader = MavenDownloader(self.cache_location('library'), self.MAVEN_REPOS)
        for library in forgeprofile['versionInfo']['libraries']:
            if library['name'].startswith('net.minecraftforge:forge:'):
                continue

            group, artifact, version = library['name'].split(':')
            library_filename = '{}-{}.jar'.format(artifact, version)

            cached_library = os.path.join(self.cache_location('library'), library_filename)
            if not os.path.exists(cached_library):
                mavenDownloader.download_library_from_repo(group, artifact, version, library_filename)
            else:
                self.log.info('  [cached]   : {}'.format(library_filename))

            local_library = os.path.join(self.build_location('libraries'),
                                         group.replace('.', '/'),
                                         artifact, version, library_filename)
            if not os.path.exists(os.path.dirname(local_library)):
                os.makedirs(os.path.dirname(local_library))

            shutil.copy2(cached_library, local_library)

##############################################################################
# THE END
