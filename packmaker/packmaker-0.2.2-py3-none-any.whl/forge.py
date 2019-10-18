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
import zipfile

##############################################################################


class Forge (object):

    FORGE_REPO_URL = 'https://files.minecraftforge.net/maven/'

    ##########################################################################

    def __init__(self, minecraft_version, forge_version, downloader):
        super(Forge, self).__init__()
        self.minecraft_version = minecraft_version
        self.forge_version = forge_version
        self.full_version = '{}-{}'.format(minecraft_version, forge_version)
        self.downloader = downloader
        self.install_profile = None

    ##########################################################################

    def installer_filename(self):
        return 'forge-{}-installer.jar'.format(self.full_version)

    ##########################################################################

    def installer_path(self):
        return 'net/minecraftforge/forge/{}/{}'.format(self.full_version,
                                                       self.installer_filename())

    ##########################################################################

    def installer_download_url(self):
        return '{}/{}'.format(Forge.FORGE_REPO_URL, self.installer_path())

    ##########################################################################

    def universal_filename(self):
        return 'forge-{}-universal.jar'.format(self.full_version)

    ##########################################################################

    def universal_path(self):
        return 'net/minecraftforge/forge/{}/{}'.format(self.full_version,
                                                       self.universal_filename())

    ##########################################################################

    def universal_download_url(self):
        return '{}/{}'.format(Forge.FORGE_REPO_URL, self.universal_path())

    ##########################################################################

    def get_install_profile(self):
        if self.install_profile is None:
            installer_filename = self.get_installer_jar()
            with zipfile.ZipFile(installer_filename, 'r') as installerjar:
                with installerjar.open('install_profile.json', 'r') as installf:
                    self.install_profile = json.load(installf)
        return self.install_profile

    ##########################################################################

    def get_installer_jar(self):
        return self.downloader.download(self.installer_download_url())

##############################################################################
# THE END
