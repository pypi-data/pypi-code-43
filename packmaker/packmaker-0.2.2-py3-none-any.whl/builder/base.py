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
import tarfile
import zipfile

from ..download import HttpDownloader
from ..framew.log import getlog
from ..packlock import PackLock

##############################################################################


class BaseBuilder (object):

    build_subloc = None
    cache_subloc = None
    release_subloc = None

    release_extensions = {'zip': 'zip',
                          'tgz': 'tar.gz'
                          }

    default_packmaker_lock = 'packmaker.lock'

    ##########################################################################

    def __init__(self):
        super(BaseBuilder, self).__init__()
        self.log = getlog()

    ##########################################################################

    def add_cmdline_args(self, parser):
        parser.add_argument('--build-dir', '-b', default='build',
                            help='base directory for build artifacts')
        parser.add_argument('--release-dir', '-r', default=None,
                            help='base directory for release artifacts')
        parser.add_argument('--cache-dir', default=None,
                            help='base directory for cached artifacts')
        parser.add_argument('--release-format', choices=('zip', 'tgz'), default='zip',
                            help='archive format for release package')
        parser.add_argument('lockfile', nargs='*', default=[BaseBuilder.default_packmaker_lock],
                            help='modpack lock file')

    ##########################################################################

    def setup_build(self, parsed_args):
        self.build_dir = parsed_args.build_dir
        if parsed_args.release_dir is None:
            self.release_dir = os.path.join(self.build_dir, 'release')
        else:
            self.release_dir = parsed_args.release_dir
        if parsed_args.cache_dir is None:
            self.cache_dir = os.path.join(self.build_dir, 'cache')
        else:
            self.cache_dir = parsed_args.cache_dir

        self.release_format = parsed_args.release_format
        self.release_extension = self.release_extensions[self.release_format]

        self.packlock_filenames = parsed_args.lockfile
        self.load_packfiles()
        self.mods_downloader = HttpDownloader(self.cache_location('mods'))

    ##########################################################################

    def do_build(self):
        pass

    ##########################################################################

    def build_location(self, subloc=None):
        loc = self.build_dir
        if self.build_subloc is not None:
            loc = os.path.join(loc, self.build_subloc)
        if subloc is not None:
            loc = os.path.join(loc, subloc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    ##########################################################################

    def cache_location(self, subloc=None):
        loc = self.cache_dir
        if self.cache_subloc is not None:
            loc = os.path.join(loc, self.cache_subloc)
        if subloc is not None:
            loc = os.path.join(loc, subloc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    ##########################################################################

    def release_location(self, subloc=None):
        loc = self.release_dir
        if self.release_subloc is not None:
            loc = os.path.join(loc, self.release_subloc)
        if subloc is not None:
            loc = os.path.join(loc, subloc)
        if not os.path.exists(loc):
            os.makedirs(loc)
        return loc

    ##########################################################################

    def load_packfiles(self):
        for filename in self.packlock_filenames:
            if not os.path.exists(filename):
                raise Exception('Cannot find packmaker definition: {}'.format(filename))

        self.log.debug('Reading pack lockfile(s)  ({}) ...'.format(','.join(self.packlock_filenames)))
        self.packlock = PackLock(self.packlock_filenames)
        self.packlock.load()

    ##########################################################################

    def copy_files(self, dest=None, files_iterator=None):
        if dest is None:
            dest = self.build_location()
        if files_iterator is None:
            files_iterator = self.packlock.files
        for files in files_iterator:
            self.__copy_tree(files['location'], dest)

    ##########################################################################

    def copy_mods(self, dest, mod_iterator=None):
        if mod_iterator is None:
            mod_iterator = self.packlock.get_all_mods()
        for mod in mod_iterator:
            modfile = self.mods_downloader.download(mod.downloadUrl, mod.fileName)
            localfile = os.path.join(dest, mod.fileName)
            shutil.copy2(modfile, localfile)

    ##########################################################################

    def download_mods(self, mod_iterator=None):
        self.log.debug('Downloading mods ...')
        if mod_iterator is None:
            mod_iterator = self.packlock.get_all_mods()
        for mod in mod_iterator:
            self.mods_downloader.download(mod.downloadUrl, mod.fileName)

    ##########################################################################

    def release_pkg(self, dest, source=None):
        if source is None:
            source = self.build_location()
        if self.release_format == 'zip':
            self.__zip_tree(source, dest)
        elif self.release_format == 'tgz':
            self.__targz_tree(source, dest)
        else:
            raise Exception('Unknown release format: {}'.format(self.release_format))

    ##########################################################################

    @staticmethod
    def __copy_tree(source, dest):
        names = os.listdir(source)
        if not os.path.exists(dest):
            os.makedirs(dest)
        for name in names:
            srcname = os.path.join(source, name)
            dstname = os.path.join(dest, name)
            try:
                if os.path.isdir(srcname):
                    BaseBuilder.__copy_tree(srcname, dstname)
                else:
                    shutil.copy2(srcname, dstname)
            except OSError:
                raise

    ##########################################################################

    @staticmethod
    def __zip_tree(source, dest):
        with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    # bad attempt at preventing the zipfile from including itself
                    if file == os.path.basename(dest):
                        continue
                    zipf.write(os.path.join(root, file),
                               os.path.join(root[len(source):], file))

    @staticmethod
    def __targz_tree(source, dest):
        with tarfile.open(dest, 'w:gz') as tarf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    # bad attempt at preventing the tarfile from including itself
                    if file == os.path.basename(dest):
                        continue
                    tarf.add(os.path.join(root, file),
                             os.path.join(root[len(source):], file))

##############################################################################
# THE END
